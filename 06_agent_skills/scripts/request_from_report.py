#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Force-feed report token ids to an OpenAI-compatible completions server.

Reads ``prompt_token_ids`` + ``output_token_ids`` from a runtime_guard report,
concatenates them, and POSTs to ``/v1/completions`` with ``prompt`` as a list
of ints (no re-tokenization).

Example::

  python -m vllm_ascend.runtime_guard.analysis.scripts.request_from_report \\
    --report /path/to/report_xxx.json \\
    --url http://127.0.0.1:8000/v1/completions \\
    --model <served-model-name>

Modes (``--feed``)::

  history  prompt + output[:-1]     (default; leave last output token for decode)
  full     prompt + output          (whole sequence as prefill)
  prompt   prompt only
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

try:
    from ._lib import load_report, report_detail
except ImportError:
    from _lib import load_report, report_detail  # type: ignore


def _ids(detail: dict[str, Any], key: str) -> list[int]:
    raw = detail.get(key)
    if not isinstance(raw, list) or not raw:
        raise ValueError(
            f"report missing non-empty {key} — enable report.save_sensitive_info when capturing"
        )
    return [int(x) for x in raw]


def build_feed_ids(detail: dict[str, Any], feed: str) -> list[int]:
    prompt = _ids(detail, "prompt_token_ids")
    output = _ids(detail, "output_token_ids")
    if feed == "full":
        return prompt + output
    if feed == "history":
        if len(output) < 1:
            raise ValueError("history mode needs at least 1 output token")
        return prompt + output[:-1]
    if feed == "prompt":
        return list(prompt)
    raise ValueError(f"unknown --feed={feed!r}")


def post_json(url: str, body: dict[str, Any], *, timeout: float) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {err_body}") from exc


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--report", type=Path, required=True, help="runtime_guard report_*.json")
    p.add_argument(
        "--url",
        default="http://127.0.0.1:8000/v1/completions",
        help="OpenAI completions endpoint (token-id prompt). Default: %(default)s",
    )
    p.add_argument(
        "--model",
        required=True,
        help="served model name (must match the engine's served model id)",
    )
    p.add_argument(
        "--feed",
        choices=("full", "history", "prompt"),
        default="history",
        help="which token ids to send as prompt (default: history = prompt+output[:-1])",
    )
    p.add_argument("--max-tokens", type=int, default=1, help="generation length after force-feed")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--timeout", type=float, default=600.0)
    p.add_argument(
        "--extra",
        type=str,
        default=None,
        help='extra JSON object merged into the request body, e.g. \'{"ignore_eos":true}\'',
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="print request JSON / curl only; do not POST",
    )
    p.add_argument(
        "--print-curl",
        action="store_true",
        help="also print an equivalent curl command",
    )
    args = p.parse_args(argv)

    try:
        report = load_report(args.report)
        detail = report_detail(report)
        token_ids = build_feed_ids(detail, args.feed)
    except Exception as exc:
        print(f"[err] {exc}", file=sys.stderr)
        return 1

    body: dict[str, Any] = {
        "model": args.model,
        "prompt": token_ids,
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
    }
    if args.extra:
        try:
            extra = json.loads(args.extra)
        except json.JSONDecodeError as exc:
            print(f"[err] --extra is not valid JSON: {exc}", file=sys.stderr)
            return 1
        if not isinstance(extra, dict):
            print("[err] --extra must be a JSON object", file=sys.stderr)
            return 1
        body.update(extra)

    n_prompt = len(detail.get("prompt_token_ids") or [])
    n_output = len(detail.get("output_token_ids") or [])
    print(
        f"[info] report={args.report} incident={report.get('incident_type')} "
        f"req_id={report.get('req_id')} feed={args.feed} "
        f"n_prompt={n_prompt} n_output={n_output} n_feed={len(token_ids)}"
    )
    print(f"[info] POST {args.url} model={args.model} max_tokens={args.max_tokens}")

    if args.print_curl or args.dry_run:
        # Compact prompt for curl readability when huge; still valid JSON.
        curl_body = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
        print(
            "curl -sS "
            + json.dumps(args.url)
            + " -H 'Content-Type: application/json' -d "
            + json.dumps(curl_body)
        )

    if args.dry_run:
        print("[dry-run] payload keys:", sorted(body.keys()))
        print(f"[dry-run] prompt[:8]={token_ids[:8]} ... prompt[-4:]={token_ids[-4:]}")
        return 0

    try:
        resp = post_json(args.url, body, timeout=args.timeout)
    except Exception as exc:
        print(f"[err] request failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(resp, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
