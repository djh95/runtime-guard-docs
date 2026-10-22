#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Summarize runtime_guard anomaly report JSON files (post-capture Step 5).

Compatible with::

    <report_dir>/<incident_type>/report_*.json

Also accepts a flat directory of ``report_*.json`` / legacy ``anomaly_*.log``.

Anomaly fail-evidence aliases (same JSON schema as reports)::

    sample_report.json / report_sample.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

KNOWN_DETECTORS = (
    # Shipped on feat/runtime-guard-config (DETECTOR_SECTIONS).
    "logits_finite",
    "token_repeat",
    "output_substring",
    "spec_acceptance",
    "manual_trigger",
    # Legacy / not shipped — still recognized when reading old reports.
    "token_logprob",
    "slot_consistency",
    "kv_slot_token",
    "kv_slot_order",
    "kv_state",
)

# fail-evidence often renames one report for archival.
_REPORT_ALIASES = (
    "sample_report.json",
    "report_sample.json",
)


def _iter_report_files(report_dir: Path, incident_type: str | None) -> list[Path]:
    if incident_type:
        roots = [report_dir / incident_type]
    else:
        roots = [report_dir]
    files: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        files.extend(root.glob("report_*.json"))
        files.extend(root.glob("*/report_*.json"))
        files.extend(root.glob("anomaly_*.log"))
        files.extend(root.glob("*/anomaly_*.log"))
        for alias in _REPORT_ALIASES:
            files.extend(root.glob(alias))
            files.extend(root.glob(f"*/{alias}"))
    # Unique, newest first.
    uniq = {p.resolve(): p for p in files}
    return sorted(uniq.values(), key=lambda p: p.stat().st_mtime, reverse=True)


def _load(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except Exception as exc:
        print(f"[warn] skip {path}: {exc}")
        return None


def _token_len(detail: dict[str, Any], ids_key: str, count_key: str) -> int:
    ids = detail.get(ids_key)
    if isinstance(ids, list):
        return len(ids)
    count = detail.get(count_key)
    try:
        return int(count) if count is not None else 0
    except (TypeError, ValueError):
        return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-dir",
        "--dir",
        dest="report_dir",
        type=Path,
        default=Path("runtime/report"),
        help="runtime_guard report root",
    )
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--incident-type", type=str, default=None)
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Print prompt/output token id lengths and truncated lists when present",
    )
    args = parser.parse_args(argv)

    paths = _iter_report_files(args.report_dir, args.incident_type)
    if not paths:
        print(f"No reports under {args.report_dir.resolve()}")
        return 1

    print(
        f"{'file':<48} {'type':<16} {'req_id':<14} {'prompt':>6} {'output':>6} "
        f"{'blocks':>6} {'dump':>5}"
    )
    print("-" * 110)
    type_counter: Counter[str] = Counter()
    shown = 0
    for path in paths:
        if shown >= args.limit:
            break
        data = _load(path)
        if data is None:
            continue
        detail = data.get("detail") if isinstance(data.get("detail"), dict) else {}
        itype = str(data.get("incident_type") or path.parent.name)
        req_id = str(data.get("req_id") or "-")
        n_prompt = _token_len(detail, "prompt_token_ids", "prompt_token_count")
        n_output = _token_len(detail, "output_token_ids", "output_token_count")
        n_blocks = len(detail.get("block_ids") or data.get("block_ids") or [])
        dump = "Y" if (
            data.get("dump_attempted") if "dump_attempted" in data else data.get("dump_armed")
        ) else "N"
        rel = path.name if path.parent == args.report_dir else f"{path.parent.name}/{path.name}"
        print(
            f"{rel[:48]:<48} {itype[:16]:<16} {req_id[:14]:<14} "
            f"{n_prompt:6d} {n_output:6d} {n_blocks:6d} {dump:>5}"
        )
        if args.detail:
            out_ids = detail.get("output_token_ids")
            if isinstance(out_ids, list) and out_ids:
                print(f"    output_token_ids ({len(out_ids)}): {out_ids[:32]}{'...' if len(out_ids) > 32 else ''}")
        type_counter[itype] += 1
        shown += 1

    print()
    print(f"report_dir={args.report_dir.resolve()} shown={shown}/{len(paths)}")
    print("incident_type counts:")
    for name, count in type_counter.most_common():
        mark = "  " if name in KNOWN_DETECTORS else "? "
        print(f"  {mark}{name:<24} {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
