#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compare buggy vs ref native ``dump_kv`` dirs with two reports.

For each token position, compute cosine similarity per matched layer, take the
minimum across layers (Table 1), then print per-layer cos/maxdiff at the first
token below ``--cos-thresh`` (Table 2).

Example::

  python -m vllm_ascend.runtime_guard.analysis.scripts.compare_kv_similarity \\
    --buggy-dir ./runtime/report/kv_cache/token_repeat/bad_req/wave_N/<rank_tag>/ \\
    --ref-dir   ./runtime/report/kv_cache/manual_trigger/ref_req/wave_N/<rank_tag>/ \\
    --buggy-report ./runtime/report/token_repeat/report_bad.json \\
    --ref-report   ./runtime/report/manual_trigger/report_ref.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from ._lib import (
        analysis_to_json,
        compare_kv_dumps,
        format_kv_similarity_tables,
        load_report,
        report_detail,
        validate_matching_token_ids,
    )
except ImportError:
    from _lib import (  # type: ignore
        analysis_to_json,
        compare_kv_dumps,
        format_kv_similarity_tables,
        load_report,
        report_detail,
        validate_matching_token_ids,
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--buggy-dir", type=Path, required=True, help="buggy side .../wave_N/<rank_tag>/")
    p.add_argument("--ref-dir", type=Path, required=True, help="ref side .../wave_N/<rank_tag>/")
    p.add_argument("--buggy-report", type=Path, required=True, help="buggy incident report_*.json")
    p.add_argument("--ref-report", type=Path, required=True, help="ref incident report_*.json")
    p.add_argument("--num-tokens", type=int, default=None, help="override token count N")
    p.add_argument("--block-size", type=int, default=128)
    p.add_argument("--head", type=int, default=0, help="KV head index when tensor is [N,H,D]")
    p.add_argument("--cos-thresh", type=float, default=0.99)
    p.add_argument(
        "--allow-token-mismatch",
        action="store_true",
        help="warn instead of fail when buggy/ref token ids differ",
    )
    p.add_argument("--json-out", type=Path, default=None, help="write structured result JSON")
    args = p.parse_args(argv)

    try:
        import torch  # noqa: F401
    except ImportError:
        print("torch is required", file=sys.stderr)
        return 2

    try:
        buggy_report = load_report(args.buggy_report)
        ref_report = load_report(args.ref_report)
        buggy_detail = report_detail(buggy_report)
        ref_detail = report_detail(ref_report)
        validate_matching_token_ids(
            buggy_detail,
            ref_detail,
            strict=not args.allow_token_mismatch,
        )
        analysis = compare_kv_dumps(
            buggy_dir=args.buggy_dir,
            ref_dir=args.ref_dir,
            detail=buggy_detail,
            report=buggy_report,
            num_tokens=args.num_tokens,
            block_size=args.block_size,
            head=args.head,
            cos_thresh=args.cos_thresh,
        )
    except Exception as exc:
        print(f"[err] {exc}", file=sys.stderr)
        return 1

    print(
        f"[info] buggy_report={args.buggy_report} req_id={buggy_report.get('req_id')} "
        f"ref_report={args.ref_report} req_id={ref_report.get('req_id')} "
        f"n_tokens={analysis.n_tokens} layers={len(analysis.layers)}"
    )
    print(format_kv_similarity_tables(analysis, buggy_dir=args.buggy_dir, ref_dir=args.ref_dir))

    if args.json_out is not None:
        payload = analysis_to_json(analysis)
        payload["buggy_dir"] = str(args.buggy_dir.resolve())
        payload["ref_dir"] = str(args.ref_dir.resolve())
        payload["buggy_report"] = str(args.buggy_report.resolve())
        payload["ref_report"] = str(args.ref_report.resolve())
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[info] wrote {args.json_out.resolve()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
