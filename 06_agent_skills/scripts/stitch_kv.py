#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Stitch multi-rank ``dump_kv`` shards and verify TP/DP/PP completeness.

The product ``dump_kv`` action writes one ``{rank_tag}/*.pt`` per (rank, layer)::

    <report_dir>/kv_cache/<incident_type>/<req_id>/wave_N/
        request_info.json
        dp0_tp0_pp0_cp0/<req_id>_layer_0_req.pt
        dp0_tp1_pp0_cp0/<req_id>_layer_0_req.pt   # TP shard (head dim split)
        ...

This script:
  * stitches TP head shards back into one ``[n_blocks, block_size, H, head_dim]``
    tensor (concat along ``dim=-2`` in ascending ``tp_rank`` order);
  * reports DP/TP/PP/CP coverage and any missing TP ranks;
  * compares a stitched dump against a reference (e.g. TP=2 vs TP=1, or PP=2
    partial vs PP=1 full) and flags missing/extra layers from PP sharding.

Usage::

    python -m vllm_ascend.runtime_guard.analysis.scripts.stitch_kv --dump-dir <wave_N>
    python -m vllm_ascend.runtime_guard.analysis.scripts.stitch_kv \
        --target <wave_N> --ref <wave_N_ref> [--cos-thresh 0.999] \
        [--max-tokens N | --written-only] [--json-out out.json]

Note: layer file names contain ``[0]``/``[1]`` (K/V) — with shell globs these
brackets are character classes; match by substring, not glob.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    from ._lib import (
        compare_stitched_kv,
        discover_rank_dirs,
        parse_rank_tag,
        stitch_kv_dir,
    )
except ImportError:
    from _lib import (  # type: ignore
        compare_stitched_kv,
        discover_rank_dirs,
        parse_rank_tag,
        stitch_kv_dir,
    )


def _natural_key(name: str) -> tuple:
    parts = re.split(r"(\d+)", name)
    return tuple(int(p) if p.isdigit() else p for p in parts)


def _rank_sizes(rank_dirs: dict[str, Path]) -> tuple[int, int, int, int]:
    dp: set[int] = set()
    tp: set[int] = set()
    pp: set[int] = set()
    cp: set[int] = set()
    for tag in rank_dirs:
        parsed = parse_rank_tag(tag)
        if parsed is None:
            continue
        dp.add(parsed["dp"])
        tp.add(parsed["tp"])
        pp.add(parsed["pp"])
        cp.add(parsed["cp"])
    return (
        max(dp) + 1 if dp else (1 if rank_dirs else 0),
        max(tp) + 1 if tp else (1 if rank_dirs else 0),
        max(pp) + 1 if pp else (1 if rank_dirs else 0),
        max(cp) + 1 if cp else (1 if rank_dirs else 0),
    )


def _dump_verify(dump_dir: Path, tp_size: int | None) -> int:
    rank_dirs = discover_rank_dirs(dump_dir)
    if not rank_dirs:
        print(f"[FAIL] no {dump_dir}/*/ *.pt rank dirs found")
        return 1
    dp_size, tp_detected, pp_size, cp_size = _rank_sizes(rank_dirs)
    eff_tp = tp_size if tp_size is not None else tp_detected

    print(f"dump_dir={dump_dir}")
    print(f"rank_dirs={len(rank_dirs)}  dp_size={dp_size} tp_size={eff_tp} "
          f"pp_size={pp_size} cp_size={cp_size}")
    print("rank_tags:")
    for tag in sorted(rank_dirs):
        print(f"    {tag}")

    stitched = stitch_kv_dir(dump_dir, tp_size=tp_size)
    layers = sorted(stitched, key=_natural_key)
    present_tp = sorted({parse_rank_tag(tag)["tp"] for tag in rank_dirs if parse_rank_tag(tag) is not None})
    missing_tp = sorted(set(range(eff_tp)) - set(present_tp))
    print(f"layers={len(layers)}")
    for layer in layers:
        d = stitched[layer]
        shape = tuple(d.tensor.shape)
        heads = d.num_kv_heads
        print(f"    {layer:<28} shape={shape} heads={heads}")
    print()
    if missing_tp:
        print(f"结论: INCOMPLETE — 缺 TP rank {missing_tp}（期望 tp_size={eff_tp}，实际 {present_tp}）")
        return 1
    print(f"结论: OK — {len(rank_dirs)} rank shards 拼成 {len(layers)} 层，TP 头维已拼接")
    return 0


def _compare(
    target: Path,
    ref: Path,
    cos_thresh: float,
    json_out: Path | None,
    max_tokens: int | None,
    written_only: bool,
) -> int:
    cmp = compare_stitched_kv(
        target_dir=target,
        ref_dir=ref,
        cos_thresh=cos_thresh,
        max_tokens=max_tokens,
        written_only=written_only,
    )
    print(f"target={target}")
    print(f"ref={ref}")
    print(f"common_layers={len(cmp.common_layers)}  missing_in_target={len(cmp.missing_in_target)} "
          f"extra_in_target={len(cmp.extra_in_target)}")
    if cmp.missing_in_target:
        print(f"  missing (PP 部分覆盖): {cmp.missing_in_target}")
    if cmp.extra_in_target:
        print(f"  extra (target 独有): {cmp.extra_in_target}")
    slice_note = ""
    if max_tokens is not None:
        slice_note = f"  compare: first {max_tokens} token slots (--max-tokens)"
    elif written_only:
        slice_note = "  compare: written token slots only (--written-only; see per-layer slots col)"
    if slice_note:
        print(slice_note)
    print()
    print(f"{'layer':<28} {'cos':>10} {'maxdiff':>12} {'slots':>6}  target_shape / ref_shape")
    print("-" * 86)
    bad = 0
    for l in cmp.layers:
        mark = "" if l.cos >= cos_thresh else "  <-- 不一致"
        if l.cos < cos_thresh:
            bad += 1
        slots = str(l.slots) if l.slots is not None else "-"
        print(f"{l.layer:<28} {l.cos:10.6f} {l.maxdiff:12.4e} {slots:>6}  "
              f"{l.shape_target} / {l.shape_ref}{mark}")

    payload = {
        "target": str(target),
        "ref": str(ref),
        "cos_thresh": cos_thresh,
        "max_tokens": max_tokens,
        "written_only": written_only,
        "common_layers": cmp.common_layers,
        "missing_in_target": cmp.missing_in_target,
        "extra_in_target": cmp.extra_in_target,
        "layers": [
            {
                "layer": l.layer,
                "cos": l.cos,
                "maxdiff": l.maxdiff,
                "slots": l.slots,
                "shape_target": list(l.shape_target),
                "shape_ref": list(l.shape_ref),
            }
            for l in cmp.layers
        ],
        "all_clean": cmp.all_clean,
    }
    if json_out is not None:
        json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\njson_out={json_out}")

    print()
    if cmp.all_clean and bad == 0:
        print("结论: PASS — 拼接后与标杆一致（TP 头维拼接正确 / PP 部分覆盖层匹配）")
        return 0
    print(f"结论: FAIL — {bad} 层 cos < {cos_thresh}（或 shape 不一致），需排查分片顺序/覆盖")
    return 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dump-dir", type=Path, default=None, help="wave_N dir → stitch + completeness report")
    p.add_argument("--target", type=Path, default=None, help="stitched dump to compare (with --ref)")
    p.add_argument("--ref", type=Path, default=None, help="reference dump (e.g. TP=1 / PP=1 baseline)")
    p.add_argument("--tp-size", type=int, default=None, help="Expected TP size for completeness check")
    p.add_argument(
        "--cos-thresh",
        type=float,
        default=0.999,
        help="cosine threshold (default 0.999; cross-TP bf16 reduction noise sits ~0.999-0.9999, 0.9999 over-flags)",
    )
    p.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="compare only the first N token slots (block dim); unwritten paged slots are zero on both sides",
    )
    p.add_argument(
        "--written-only",
        action="store_true",
        help="auto-slice each layer to its written token slots (last nonzero slot + 1)",
    )
    p.add_argument("--json-out", type=Path, default=None, help="Write compare result JSON here")
    args = p.parse_args(argv)

    try:
        import torch  # noqa: F401
    except ImportError:
        print("torch is required")
        return 2

    if args.dump_dir is not None:
        return _dump_verify(args.dump_dir, args.tp_size)
    if args.target is not None and args.ref is not None:
        return _compare(args.target, args.ref, args.cos_thresh, args.json_out, args.max_tokens, args.written_only)
    p.error("use --dump-dir OR (--target + --ref)")


if __name__ == "__main__":
    raise SystemExit(main())
