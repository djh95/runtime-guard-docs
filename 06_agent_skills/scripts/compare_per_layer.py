#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Per-layer KV compare between two native ``dump_kv`` dirs.

Complement to ``locate_first_divergence`` (token-first). Numeric gate first
(NaN / Inf / zero-norm → ``数值问题``, no cosine); then aggregate min/mean cos
over *clean* token cells only.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

try:
    from ._lib import (
        assert_block_capacity,
        block_ids_from_detail,
        cosine,
        gather_token_rows,
        load_kv_dir,
        load_report,
        matched_layers,
        report_detail,
        token_n,
        vector_numeric_issue,
    )
except ImportError:
    from _lib import (  # type: ignore
        assert_block_capacity,
        block_ids_from_detail,
        cosine,
        gather_token_rows,
        load_kv_dir,
        load_report,
        matched_layers,
        report_detail,
        token_n,
        vector_numeric_issue,
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--buggy-dir", type=Path, required=True)
    p.add_argument("--ref-dir", type=Path, required=True)
    p.add_argument("--report", type=Path, default=None)
    p.add_argument("--num-tokens", type=int, default=None)
    p.add_argument("--block-size", type=int, default=128)
    p.add_argument("--head", type=int, default=0)
    p.add_argument("--cos-thresh", type=float, default=0.99)
    args = p.parse_args(argv)

    try:
        import torch  # noqa: F401
    except ImportError:
        print("torch is required")
        return 2

    detail: dict = {}
    if args.report:
        report = load_report(args.report)
        detail = report_detail(report)
        _, _, n_from_report = token_n(detail)
        n_tokens = args.num_tokens if args.num_tokens is not None else n_from_report
        block_ids = block_ids_from_detail(detail, report)
    else:
        n_tokens = args.num_tokens or 0
        block_ids = []
    if n_tokens <= 0:
        print("[err] need --report with tokens or --num-tokens")
        return 1

    try:
        buggy = load_kv_dir(args.buggy_dir)
        ref = load_kv_dir(args.ref_dir)
        layers = matched_layers(buggy, ref)
        sample = buggy[layers[0]]
        ids = block_ids or sample.block_ids
        n_blocks = len(ids) if ids else int(sample.tensor.shape[0])
        assert_block_capacity(n_blocks, n_tokens, args.block_size)

        print(
            f"{'layer':<40} {'min_cos':>8} {'mean_cos':>8} {'n_bad':>6} "
            f"{'n_issue':>8} {'worst':>6}"
        )
        print("-" * 90)
        for name in layers:
            b = gather_token_rows(
                buggy[name], n_tokens=n_tokens, block_size=args.block_size, head=args.head
            )
            r = gather_token_rows(
                ref[name], n_tokens=n_tokens, block_size=args.block_size, head=args.head
            )
            cos_vals: list[float] = []
            n_issue = 0
            for i in range(n_tokens):
                issue = vector_numeric_issue(b[i], r[i])
                if issue is not None:
                    n_issue += 1
                    continue
                cos_vals.append(cosine(b[i], r[i]))
            if not cos_vals:
                print(
                    f"{name:<40} {'—':>8} {'—':>8} {'—':>6} {n_issue:8d} "
                    f"{'数值问题':>6}"
                )
                continue
            min_c = min(cos_vals)
            mean_c = sum(cos_vals) / len(cos_vals)
            n_bad = sum(1 for c in cos_vals if not math.isnan(c) and c < args.cos_thresh)
            # worst among clean tokens only (original token index)
            worst = -1
            worst_c = float("inf")
            ci = 0
            for i in range(n_tokens):
                if vector_numeric_issue(b[i], r[i]) is not None:
                    continue
                c = cos_vals[ci]
                ci += 1
                if c < worst_c:
                    worst_c = c
                    worst = i
            print(
                f"{name:<40} {min_c:8.4f} {mean_c:8.4f} {n_bad:6d} "
                f"{n_issue:8d} {worst:6d}"
            )
    except Exception as exc:
        print(f"[err] {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
