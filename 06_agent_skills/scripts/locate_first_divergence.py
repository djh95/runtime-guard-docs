#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Locate first KV divergence between two native ``dump_kv`` dirs (two tables).

Reads runtime_guard per-request dumps::

    <kv_dir>/*.pt   # each: {req_id, block_ids, layer, tensor, ...}

Table 1 — per token: min cosine over matched layers.  
Table 2 — at first bad token: per-layer cosine + maxdiff.

Assumes sequence starts at offset 0 of ``block_ids[0]`` (vLLM full-block convention).

For two reports (buggy + ref), prefer ``compare_kv_similarity`` instead.
"""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from ._lib import (
        compare_kv_dumps,
        format_kv_similarity_tables,
        load_report,
        report_detail,
    )
except ImportError:  # `python path/to/script.py`
    from _lib import (  # type: ignore
        compare_kv_dumps,
        format_kv_similarity_tables,
        load_report,
        report_detail,
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--buggy-dir", type=Path, required=True, help="buggy dump_kv dir (*.pt)")
    p.add_argument("--ref-dir", type=Path, required=True, help="ref dump_kv dir (*.pt)")
    p.add_argument("--report", type=Path, default=None, help="report_*.json (token N + labels)")
    p.add_argument("--num-tokens", type=int, default=None, help="N when no report / override")
    p.add_argument("--block-size", type=int, default=128)
    p.add_argument("--head", type=int, default=0, help="KV head index when tensor is [N,H,D]")
    p.add_argument("--cos-thresh", type=float, default=0.99)
    args = p.parse_args(argv)

    try:
        import torch  # noqa: F401
    except ImportError:
        print("torch is required")
        return 2

    detail: dict = {}
    report = None
    if args.report:
        report = load_report(args.report)
        detail = report_detail(report)
    elif args.num_tokens is None or args.num_tokens <= 0:
        print("[err] need --report or --num-tokens")
        return 1

    try:
        analysis = compare_kv_dumps(
            buggy_dir=args.buggy_dir,
            ref_dir=args.ref_dir,
            detail=detail,
            report=report,
            num_tokens=args.num_tokens,
            block_size=args.block_size,
            head=args.head,
            cos_thresh=args.cos_thresh,
        )
    except Exception as exc:
        print(f"[err] {exc}")
        return 1

    print(format_kv_similarity_tables(analysis, buggy_dir=args.buggy_dir, ref_dir=args.ref_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
