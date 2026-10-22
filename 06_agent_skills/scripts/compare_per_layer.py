#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Per-layer KV cosine between two native ``dump_kv`` dirs.

Complement to ``locate_first_divergence`` (token-first). This aggregates by layer:
min/mean cos over tokens, bad-token count, worst token.
"""

from __future__ import annotations

import argparse
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

        print(f"{'layer':<40} {'min_cos':>8} {'mean_cos':>8} {'n_bad':>6} {'worst':>6}")
        print("-" * 78)
        for name in layers:
            b = gather_token_rows(buggy[name], n_tokens=n_tokens, block_size=args.block_size, head=args.head)
            r = gather_token_rows(ref[name], n_tokens=n_tokens, block_size=args.block_size, head=args.head)
            cos_vals = [cosine(b[i], r[i]) for i in range(n_tokens)]
            min_c = min(cos_vals)
            mean_c = sum(cos_vals) / len(cos_vals)
            n_bad = sum(1 for c in cos_vals if c < args.cos_thresh)
            worst = cos_vals.index(min_c)
            print(f"{name:<40} {min_c:8.4f} {mean_c:8.4f} {n_bad:6d} {worst:6d}")
    except Exception as exc:
        print(f"[err] {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
