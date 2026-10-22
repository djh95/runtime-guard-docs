#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Inspect one runtime_guard KV dump ``.pt`` file (CPU tensor payload)."""

from __future__ import annotations

import argparse
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, required=True, help="Path to a *.pt dump from dump_kv")
    parser.add_argument("--max-print", type=int, default=8, help="Leading tensor values to print")
    args = parser.parse_args(argv)

    try:
        import torch
    except ImportError:
        print("torch is required to inspect KV dumps")
        return 2

    path = args.path
    if not path.is_file():
        print(f"Missing file: {path}")
        return 1

    obj = torch.load(path, map_location="cpu", weights_only=False)
    if not isinstance(obj, dict):
        print(f"Unexpected payload type={type(obj)}")
        return 1

    tensor = obj.get("tensor")
    print(f"path={path}")
    print(f"req_id={obj.get('req_id')} layer={obj.get('layer')} source={obj.get('source')}")
    print(
        f"rank_tag={obj.get('rank_tag')} num_kv_heads={obj.get('num_kv_heads')} "
        f"block_ids={obj.get('block_ids')}"
    )
    if not hasattr(tensor, "shape"):
        print(f"tensor missing or not a Tensor: {type(tensor)}")
        return 1

    flat = tensor.detach().float().reshape(-1)
    finite = flat.isfinite()
    n = int(flat.numel())
    n_finite = int(finite.sum().item()) if n else 0
    n_nan = int(flat.isnan().sum().item()) if n else 0
    n_inf = int(flat.isinf().sum().item()) if n else 0
    print(f"shape={tuple(tensor.shape)} dtype={tensor.dtype} numel={n}")
    print(f"finite={n_finite} nan={n_nan} inf={n_inf}")
    if n_finite:
        vals = flat[finite]
        print(f"min={vals.min().item():.6g} max={vals.max().item():.6g} mean={vals.mean().item():.6g}")
    head = flat[: max(0, args.max_print)].tolist()
    print(f"head={head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
