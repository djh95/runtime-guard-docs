#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Prepare ref-run inputs from a runtime_guard report (no msprobe).

Writes a small JSON the operator / agent can use to force-feed the same
``prompt_token_ids + output_token_ids`` on a clean service with ``dump_kv`` armed
(manual_trigger or detector), producing a second ``kv_cache/.../<req_id>/`` dir
for ``locate_first_divergence`` / ``compare_per_layer``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from ._lib import load_report, report_detail, token_n
except ImportError:
    from _lib import load_report, report_detail, token_n  # type: ignore


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--out", type=Path, default=Path("ref_inputs.json"))
    args = p.parse_args(argv)

    try:
        report = load_report(args.report)
    except Exception as exc:
        print(f"[err] {exc}")
        return 1
    detail = report_detail(report)
    prompt = detail.get("prompt_token_ids")
    output = detail.get("output_token_ids")
    if not isinstance(prompt, list) or not isinstance(output, list):
        print(
            "[err] report missing prompt_token_ids/output_token_ids — "
            "enable save_sensitive_info (or equivalent) when capturing"
        )
        return 1
    n_p, n_o, n_tot = token_n(detail)
    payload = {
        "source_report": str(args.report.resolve()),
        "incident_type": report.get("incident_type"),
        "req_id": report.get("req_id"),
        "prompt_token_ids": prompt,
        "output_token_ids": output,
        "force_feed_token_ids": list(prompt) + list(output),
        "n_prompt": n_p,
        "n_output": n_o,
        "n_total": n_tot,
        "block_ids": detail.get("block_ids"),
        "notes": [
            "Run a CLEAN engine (same model/TP/mode) with dump_kv on_trigger for manual_trigger.",
            "Force-feed force_feed_token_ids (do not re-tokenize text).",
            "Prefer 3-pass if diagnosing prefill vs decode path: "
            "prefill(prompt+output[:-1]), decode(output[-1]), optional full prefill.",
            "Collect ref kv_cache dir, then:",
            "  locate_first_divergence --buggy-dir <bad> --ref-dir <ref> --report <this report>",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.out.resolve()}")
    print(f"n_prompt={n_p} n_output={n_o} n_total={n_tot}")
    print("next: arm dump_kv on clean service, force-feed force_feed_token_ids, then locate_first_divergence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
