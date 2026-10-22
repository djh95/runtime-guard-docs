#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify a runtime_guard report against its per-request KV dump folder (Step 5.5).

Config ``dump_kv`` writes::

    <report_dir>/kv_cache/<incident_type>/<req_id>/wave_N/<rank_tag>/*.pt

each ``.pt`` is a dict with keys ``req_id``, ``block_ids``, ``layer``, ``rank_tag``,
``num_kv_heads``, ``tensor``, ...

Checks (token counts are informational only):
  1. report has req_id / incident_type
  2. block capacity vs token N (when block_size known)
  3. KV files exist and tensors are finite-ish
  4. file count / layers present
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    from ._lib import report_dump_attempted, resolve_kv_dump_dir
except ImportError:
    from _lib import report_dump_attempted, resolve_kv_dump_dir  # type: ignore


def _load_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"report is not a JSON object: {path}")
    return data


def _token_n(detail: dict[str, Any]) -> tuple[int, int, int]:
    prompt_ids = detail.get("prompt_token_ids") or []
    output_ids = detail.get("output_token_ids") or []
    n_prompt = len(prompt_ids) if isinstance(prompt_ids, list) else int(detail.get("prompt_token_count") or 0)
    n_output = len(output_ids) if isinstance(output_ids, list) else int(detail.get("output_token_count") or 0)
    return n_prompt, n_output, n_prompt + n_output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True, help="runtime_guard report_*.json")
    parser.add_argument(
        "--kv-dir",
        type=Path,
        default=None,
        help=("rank dir that DIRECTLY contains *.pt (…/wave_N/<rank_tag>/); a higher-level "
              "dir (dump root / wave dir) is auto-drilled to its rank dirs; "
              "default: dump_dir/rank or kv_cache/<type>/<req>/wave_*/<rank>"),
    )
    parser.add_argument("--report-dir", type=Path, default=None, help="Override report root for default kv-dir")
    parser.add_argument("--block-size", type=int, default=128)
    parser.add_argument("--min-files", type=int, default=1, help="Minimum expected .pt files")
    args = parser.parse_args(argv)

    try:
        import torch
    except ImportError:
        print("torch is required")
        return 2

    report = _load_report(args.report)
    detail = report.get("detail") if isinstance(report.get("detail"), dict) else {}
    req_id = str(report.get("req_id") or "")
    itype = str(report.get("incident_type") or args.report.parent.name)
    ok = True

    print("[1] report basics")
    print(f"    path={args.report}")
    print(
        f"    incident_type={itype} req_id={req_id or '-'} "
        f"dump_attempted={report_dump_attempted(report)} "
        f"dump_arm_wave={report.get('dump_arm_wave')} rank={report.get('rank')}"
    )
    if not req_id:
        print("    [FAIL] missing req_id")
        ok = False

    n_prompt, n_output, n_total = _token_n(detail)
    print("[2] token 数（信息）")
    print(f"    prompt={n_prompt} output={n_output} N={n_total}")
    if detail.get("prompt_token_count") not in (None, n_prompt):
        print(f"    [note] prompt_token_count={detail.get('prompt_token_count')} vs ids len={n_prompt}")
    if detail.get("output_token_count") not in (None, n_output):
        print(f"    [note] output_token_count={detail.get('output_token_count')} vs ids len={n_output}")

    block_ids = list(detail.get("block_ids") or report.get("block_ids") or [])
    print("[3] block 容量")
    if block_ids:
        cap = len(block_ids) * args.block_size
        status = "OK" if (n_total == 0 or cap >= n_total) else "FAIL"
        if status == "FAIL":
            ok = False
        print(f"    block_ids={block_ids} cap={cap} N={n_total} → {status}")
    else:
        print("    [WARN] no block_ids in report (include_block_ids off?)")

    if args.kv_dir is not None:
        kv_dir = args.kv_dir
    else:
        report_dir = args.report_dir
        if report_dir is None:
            report_dir = args.report.parent.parent if args.report.parent.name == itype else args.report.parent
        try:
            kv_dir = resolve_kv_dump_dir(report, report_dir=report_dir)
        except ValueError:
            kv_dir = report_dir / "kv_cache" / itype / (req_id or "_missing_req_")

    print("[4] KV files")
    print(f"    kv_dir={kv_dir}")
    rank_dirs: list[Path] = []
    if not kv_dir.is_dir():
        print("    [FAIL] kv dir missing — dump_kv not in on_trigger, quota blocked, or path mismatch")
        ok = False
    else:
        # A rank dir directly holds *.pt; if a higher-level dir was given
        # (dump root / wave dir), drill to the rank dirs beneath it.
        if any(kv_dir.glob("*.pt")):
            rank_dirs = [kv_dir]
        else:
            rank_dirs = sorted({p.parent for p in kv_dir.rglob("*.pt")})
            if rank_dirs:
                print(f"    note: no .pt directly under kv_dir — drilled to {len(rank_dirs)} rank dir(s)")
    if kv_dir.is_dir() and not rank_dirs:
        print("    [FAIL] no .pt files found under kv_dir (expected >= 1)")
        ok = False

    all_pts: list[Path] = []
    all_layers: list[str] = []
    for rd in rank_dirs:
        pts = sorted(rd.glob("*.pt"))
        all_pts.extend(pts)
        print(f"    rank_dir={rd} files={len(pts)}")
        if len(pts) < args.min_files:
            print(f"    [FAIL] expected >= {args.min_files} .pt files")
            ok = False

        print("[5] tensor health")
        for path in pts:
            try:
                obj = torch.load(path, map_location="cpu", weights_only=False)
            except Exception as exc:
                print(f"    [FAIL] load {path.name}: {exc}")
                ok = False
                continue
            if not isinstance(obj, dict) or "tensor" not in obj:
                print(f"    [FAIL] {path.name}: expected dict with 'tensor'")
                ok = False
                continue
            tensor = obj["tensor"]
            layer = str(obj.get("layer") or path.stem)
            all_layers.append(layer)
            if not hasattr(tensor, "reshape"):
                print(f"    [FAIL] {path.name}: bad tensor type {type(tensor)}")
                ok = False
                continue
            flat = tensor.detach().float().reshape(-1)
            n = int(flat.numel())
            n_nan = int(flat.isnan().sum().item()) if n else 0
            n_inf = int(flat.isinf().sum().item()) if n else 0
            flag = "OK" if n_nan == 0 and n_inf == 0 else "WARN"
            if n_nan or n_inf:
                print(f"    [{flag}] {path.name} shape={tuple(tensor.shape)} nan={n_nan} inf={n_inf}")
            else:
                print(f"    [OK] {path.name} shape={tuple(tensor.shape)} finite={n}")
            dump_blocks = obj.get("block_ids")
            if block_ids and dump_blocks and list(dump_blocks) != list(block_ids):
                print(f"    [WARN] {path.name} block_ids != report block_ids")

    print("[6] layers")
    base_layers = {re.sub(r"\[\d+\]$", "", name) for name in all_layers}
    print(f"    layers={len(base_layers)} kv_files={len(all_pts)} ({len(set(all_layers))} unique layer/KV names)")
    if all_pts and not all_layers:
        ok = False

    print()
    print("=" * 60)
    print("结论:", "PASS — report/KV 基本一致，可继续 ref 对比" if ok else "FAIL — 先修路径/配额/on_trigger")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
