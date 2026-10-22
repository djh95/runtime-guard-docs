# SPDX-License-Identifier: Apache-2.0
"""Shared helpers for native ``dump_kv`` analysis scripts."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def load_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"report is not a JSON object: {path}")
    return data


def report_detail(report: dict[str, Any]) -> dict[str, Any]:
    detail = report.get("detail")
    return detail if isinstance(detail, dict) else {}


def token_n(detail: dict[str, Any]) -> tuple[int, int, int]:
    """Prefer id lists; fall back to *_token_count when lists absent/empty."""
    prompt_ids = detail.get("prompt_token_ids")
    output_ids = detail.get("output_token_ids")
    if isinstance(prompt_ids, list) and prompt_ids:
        n_prompt = len(prompt_ids)
    else:
        n_prompt = int(detail.get("prompt_token_count") or 0)
    if isinstance(output_ids, list) and output_ids:
        n_output = len(output_ids)
    else:
        n_output = int(detail.get("output_token_count") or 0)
    return n_prompt, n_output, n_prompt + n_output


def token_id_labels(detail: dict[str, Any], n_total: int) -> tuple[list[Any], int | None]:
    """Return (labels_per_position, n_prompt_or_None)."""
    prompt_ids = detail.get("prompt_token_ids")
    output_ids = detail.get("output_token_ids")
    if isinstance(prompt_ids, list) and isinstance(output_ids, list) and (prompt_ids or output_ids):
        labels = list(prompt_ids) + list(output_ids)
        return labels[:n_total] if n_total else labels, len(prompt_ids)
    return list(range(n_total)), None


def block_ids_from_detail(detail: dict[str, Any], report: dict[str, Any] | None = None) -> list[int]:
    raw = detail.get("block_ids")
    if raw is None and report is not None:
        raw = report.get("block_ids")
    if not isinstance(raw, list):
        return []
    return [int(x) for x in raw]


def report_dump_attempted(report: dict[str, Any]) -> bool:
    """Prefer ``dump_attempted``; accept legacy ``dump_armed``."""
    if "dump_attempted" in report:
        return bool(report.get("dump_attempted"))
    return bool(report.get("dump_armed"))


def _first_pt_subdir(parent: Path) -> Path | None:
    if not parent.is_dir():
        return None
    if any(parent.glob("*.pt")):
        return parent
    for child in sorted(parent.iterdir()):
        if child.is_dir() and any(child.glob("*.pt")):
            return child
    return None


def resolve_kv_dump_dir(
    report: dict[str, Any],
    *,
    report_dir: Path | None = None,
    rank: str | None = None,
) -> Path:
    """Resolve ``.../wave_N/<rank_tag>/`` (config layout) from a report.

    ``dump_dir`` may be a req root (preferred) or a legacy ``.../wave_N`` path.
    Arm wave in the report is only a hint: deferred dumps often land on a later
    ``wave_*``. Always prefer a directory that already contains ``*.pt``.
    """
    rank_tag = str(rank if rank is not None else (report.get("rank") or "")).strip()
    itype = str(report.get("incident_type") or "unknown")
    arm_wave = report.get("dump_arm_wave")
    try:
        arm_wave_i = int(arm_wave) if arm_wave is not None else None
    except (TypeError, ValueError):
        arm_wave_i = None

    def _has_pt(base: Path) -> bool:
        return base.is_dir() and any(base.rglob("*.pt"))

    def _finish(base: Path) -> Path:
        if rank_tag:
            ranked = base / rank_tag
            hit = _first_pt_subdir(ranked) or _first_pt_subdir(base)
            return hit or ranked
        hit = _first_pt_subdir(base)
        return hit or base

    def _wave_sort_key(p: Path) -> tuple[int, str]:
        name = p.name
        if name.startswith("wave_") and name[5:].isdigit():
            return (int(name[5:]), name)
        return (-1, name)

    def _req_root_from_hint(hint: Path) -> Path:
        # .../<req>/wave_N → req root; otherwise treat hint as req root.
        if hint.name.startswith("wave_"):
            return hint.parent
        return hint

    def _pick_wave(req_root: Path) -> Path | None:
        if not req_root.is_dir():
            return None
        waves = [p for p in req_root.glob("wave_*") if p.is_dir()]
        with_pt = [p for p in waves if _has_pt(p)]
        if not with_pt:
            # Flat legacy: .pt directly under req root / rank.
            if _has_pt(req_root):
                return req_root
            if arm_wave_i is not None:
                return req_root / f"wave_{arm_wave_i}"
            return None
        if arm_wave_i is not None:
            preferred = req_root / f"wave_{arm_wave_i}"
            if preferred in with_pt:
                return preferred
        # Newest wave with tensors (deferred drain often > arm wave).
        return sorted(with_pt, key=_wave_sort_key)[-1]

    req_roots: list[Path] = []

    def _add_root(path: Path | None) -> None:
        if path is None:
            return
        root = _req_root_from_hint(path)
        if root in req_roots:
            return
        # Skip empty synthetic manual incident dirs; keep if they already have .pt.
        if "__manual_trigger__" in str(root) and not _has_pt(root):
            return
        req_roots.append(root)

    dump_dirs = report.get("dump_dirs")
    if isinstance(dump_dirs, list):
        for raw in dump_dirs:
            if raw:
                _add_root(Path(str(raw)))
    if report.get("dump_dir"):
        _add_root(Path(str(report["dump_dir"])))

    detail = report.get("detail") if isinstance(report.get("detail"), dict) else {}
    req_ids: list[str] = []
    rows = detail.get("requests") if isinstance(detail, dict) else None
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict) and row.get("req_id"):
                rid = str(row["req_id"]).strip()
                if rid and rid != "__manual_trigger__" and rid not in req_ids:
                    req_ids.append(rid)
    rid0 = str(report.get("req_id") or "").strip()
    if rid0 and rid0 != "__manual_trigger__" and rid0 not in req_ids:
        req_ids.insert(0, rid0)

    # Infer dump root from an existing dump_dir hint (may differ from report_dir/kv_cache).
    dump_root: Path | None = None
    if report.get("dump_dir"):
        hint = _req_root_from_hint(Path(str(report["dump_dir"])))
        # hint = <dump_root>/<type>/<req_id>
        if hint.parent.name == itype or hint.parent.name == str(report.get("incident_type") or ""):
            dump_root = hint.parent.parent
        elif hint.name.startswith("wave_"):
            dump_root = hint.parent.parent.parent
    if dump_root is None and report_dir is not None:
        dump_root = Path(report_dir) / "kv_cache"

    if dump_root is not None:
        for rid in req_ids:
            _add_root(dump_root / itype / rid)

    for root in req_roots:
        wave = _pick_wave(root)
        if wave is not None and _has_pt(wave):
            return _finish(wave)
    for root in req_roots:
        wave = _pick_wave(root)
        if wave is not None:
            return _finish(wave)

    if not req_roots:
        if report_dir is None and not report.get("dump_dir"):
            raise ValueError("resolve_kv_dump_dir needs report['dump_dir'] or report_dir=")
        fallback_id = req_ids[0] if req_ids else (rid0 or "unknown")
        if dump_root is None:
            if report_dir is None:
                raise ValueError("resolve_kv_dump_dir needs report['dump_dir'] or report_dir=")
            dump_root = Path(report_dir) / "kv_cache"
        req_roots = [dump_root / itype / fallback_id]

    root = req_roots[0]
    if arm_wave_i is not None:
        return _finish(root / f"wave_{arm_wave_i}")
    return _finish(root)


def assert_block_capacity(n_blocks: int, n_tokens: int, block_size: int) -> None:
    if n_tokens <= 0:
        return
    if n_blocks <= 0:
        raise ValueError("n_blocks empty; cannot map tokens to KV slots")
    cap = n_blocks * block_size
    if cap < n_tokens:
        raise ValueError(f"block capacity {cap} < num_tokens {n_tokens} (blocks={n_blocks} size={block_size})")


_RANK_TAG_RE = re.compile(r"^dp(\d+)_tp(\d+)_pp(\d+)_cp(\d+)$")


def parse_rank_tag(tag: str) -> dict[str, int] | None:
    """Parse ``dp<d>_tp<t>_pp<p>_cp<c>`` into ``{dp,tp,pp,cp}`` ints (None on mismatch)."""
    m = _RANK_TAG_RE.match(str(tag).strip())
    if not m:
        return None
    return {"dp": int(m.group(1)), "tp": int(m.group(2)), "pp": int(m.group(3)), "cp": int(m.group(4))}


def _rank_component(rank_tag: str, payload_val: Any, key: str) -> int:
    """Prefer the explicit payload field; fall back to parsing ``rank_tag``."""
    try:
        if payload_val is not None:
            return int(payload_val)
    except (TypeError, ValueError):
        pass
    parsed = parse_rank_tag(rank_tag)
    if parsed is not None:
        return parsed[key]
    return 0


@dataclass
class NativeLayerDump:
    path: Path
    layer: str
    req_id: str
    block_ids: list[int]
    source: str
    tensor: Any  # torch.Tensor
    rank_tag: str = ""
    num_kv_heads: int | None = None
    tp_rank: int = 0
    pp_rank: int = 0
    cp_rank: int = 0
    dp_rank: int = 0


def load_native_pt(path: Path) -> NativeLayerDump:
    import torch

    obj = torch.load(path, map_location="cpu", weights_only=False)
    if not isinstance(obj, dict) or "tensor" not in obj:
        raise ValueError(f"{path}: expected dump_kv dict with 'tensor'")
    n_heads = obj.get("num_kv_heads")
    rank_tag = str(obj.get("rank_tag") or "")
    return NativeLayerDump(
        path=path,
        layer=str(obj.get("layer") or path.stem),
        req_id=str(obj.get("req_id") or ""),
        block_ids=[int(x) for x in (obj.get("block_ids") or [])],
        source=str(obj.get("source") or ""),
        tensor=obj["tensor"],
        rank_tag=rank_tag,
        num_kv_heads=int(n_heads) if n_heads is not None else None,
        tp_rank=_rank_component(rank_tag, obj.get("tp_rank"), "tp"),
        pp_rank=_rank_component(rank_tag, obj.get("pp_rank"), "pp"),
        cp_rank=_rank_component(rank_tag, obj.get("cp_rank"), "cp"),
        dp_rank=_rank_component(rank_tag, obj.get("dp_rank"), "dp"),
    )


def load_kv_dir(kv_dir: Path) -> dict[str, NativeLayerDump]:
    """Load all ``*.pt`` under a wave/rank dump dir, keyed by ``layer`` name."""
    if not kv_dir.is_dir():
        raise FileNotFoundError(f"kv dir missing: {kv_dir}")
    out: dict[str, NativeLayerDump] = {}
    for path in sorted(kv_dir.glob("*.pt")):
        dump = load_native_pt(path)
        # Last write wins if duplicate layer names.
        out[dump.layer] = dump
    if not out:
        raise FileNotFoundError(f"no .pt files under {kv_dir}")
    return out


def discover_rank_dirs(wave_dir: Path) -> dict[str, Path]:
    """Map ``rank_tag -> dir`` for every ``{rank_tag}/*.pt`` shard under a wave dir.

    Config layout is ``<wave_N>/<rank_tag>/{req_id}_{layer}_req.pt``. A
    single-rank (TP=DP=PP=CP=1) dump still lands under ``dp0_tp0_pp0_cp0``.
    """
    if not wave_dir.is_dir():
        return {}
    out: dict[str, Path] = {}
    for child in sorted(wave_dir.iterdir()):
        if child.is_dir() and any(child.glob("*.pt")):
            out[child.name] = child
    return out


def stitch_tp_heads(dumps: list[NativeLayerDump], *, tp_size: int | None = None) -> NativeLayerDump:
    """Concatenate per-TP-rank KV head shards along the head dim (``dim=-2``).

    Each TP rank holds a contiguous slice of ``num_kv_heads``; ascending
    ``tp_rank`` order reconstructs the natural head order. The result is
    ``[n_blocks, block_size, H, head_dim]`` with ``H`` the total heads.
    """
    import torch

    if not dumps:
        raise ValueError("no dumps to stitch")
    ordered = sorted(dumps, key=lambda d: d.tp_rank)
    if tp_size is not None and len(ordered) != tp_size:
        present = [d.tp_rank for d in ordered]
        raise ValueError(f"expected tp_size={tp_size} shards, got tp_ranks={present}")
    base = ordered[0]
    if base.tensor.dim() < 3:
        raise ValueError(f"layer={base.layer}: tensor has no head dim (dim={base.tensor.dim()})")
    for d in ordered[1:]:
        if d.layer != base.layer:
            raise ValueError(f"layer mismatch in stitch: {base.layer} vs {d.layer}")
        if list(d.block_ids) != list(base.block_ids):
            raise ValueError(f"layer={base.layer}: block_ids differ across TP ranks")
        if d.tensor.shape[:2] != base.tensor.shape[:2]:
            raise ValueError(
                f"layer={base.layer}: block dims differ across TP ranks "
                f"({tuple(d.tensor.shape[:2])} vs {tuple(base.tensor.shape[:2])})"
            )
        if d.tensor.dim() != base.tensor.dim() or d.tensor.shape[3:] != base.tensor.shape[3:]:
            raise ValueError(f"layer={base.layer}: head_dim/trailing dims differ across TP ranks")
    stitched = torch.cat([d.tensor for d in ordered], dim=-2)
    return NativeLayerDump(
        path=base.path,
        layer=base.layer,
        req_id=base.req_id,
        block_ids=list(base.block_ids),
        source=base.source,
        tensor=stitched,
        rank_tag=base.rank_tag,
        num_kv_heads=int(stitched.shape[-2]),
        tp_rank=0,
        pp_rank=base.pp_rank,
        cp_rank=base.cp_rank,
        dp_rank=base.dp_rank,
    )


def stitch_kv_dir(wave_dir: Path, *, tp_size: int | None = None) -> dict[str, NativeLayerDump]:
    """Stitch all ``{rank_tag}/*.pt`` shards under a wave dir into per-layer tensors.

    Groups ``.pt`` files by ``layer`` across rank dirs, then concatenates TP
    head shards (``stitch_tp_heads``). Layers present on exactly one rank (e.g.
    TP=1, or a rank-local source) pass through unchanged.
    """
    rank_dirs = discover_rank_dirs(wave_dir)
    if not rank_dirs:
        raise FileNotFoundError(f"no rank dirs with *.pt under {wave_dir}")
    by_layer: dict[str, list[NativeLayerDump]] = {}
    for _tag, rdir in rank_dirs.items():
        for layer, dump in load_kv_dir(rdir).items():
            by_layer.setdefault(layer, []).append(dump)
    stitched: dict[str, NativeLayerDump] = {}
    for layer, dumps in by_layer.items():
        if len(dumps) == 1:
            stitched[layer] = dumps[0]
        else:
            stitched[layer] = stitch_tp_heads(dumps, tp_size=tp_size)
    return stitched


@dataclass
class LayerCompare:
    layer: str
    cos: float
    maxdiff: float
    shape_target: tuple[int, ...]
    shape_ref: tuple[int, ...]
    slots: int | None = None  # token slots actually compared (None = full tensor)


@dataclass
class StitchedCompare:
    target_dir: Path
    ref_dir: Path
    common_layers: list[str]
    missing_in_target: list[str]
    extra_in_target: list[str]
    layers: list[LayerCompare]
    cos_thresh: float
    max_tokens: int | None = None
    written_only: bool = False

    @property
    def all_clean(self) -> bool:
        return bool(self.layers) and all(cos_is_clean(l.cos, self.cos_thresh) for l in self.layers)


def _last_written_slot(tensor: Any) -> int:
    """Last token-slot index (dim=1) holding any nonzero value; -1 if all zero."""
    nz = tensor != 0
    nz = nz.any(dim=-1).any(dim=-1)  # [n_blocks, block_size]
    idx = nz.nonzero()
    return int(idx[:, 1].max().item()) if idx.numel() else -1


def _compare_slots(t: Any, r: Any, max_tokens: int | None, written_only: bool) -> int | None:
    """Token slots to compare on 4-D [n_blocks, block_size, H, D] tensors.

    Unwritten paged-KV slots are zero on both sides; with a short wave only a
    handful of slots carry signal, so a full-block cosine is dominated by the
    few written slots and amplifies bf16 TP noise. Explicit ``max_tokens``
    wins; ``written_only`` auto-slices to the last nonzero slot (either side).
    """
    if max_tokens is not None:
        return max(1, int(max_tokens))
    if not written_only:
        return None
    if t.dim() != 4 or r.dim() != 4:
        return None
    k = max(_last_written_slot(t), _last_written_slot(r))
    return None if k < 0 else k + 1


def compare_stitched_kv(
    *,
    target_dir: Path,
    ref_dir: Path,
    cos_thresh: float = 0.999,
    max_tokens: int | None = None,
    written_only: bool = False,
) -> StitchedCompare:
    """Stitch two dump dirs and compare per-layer (cosine + maxdiff).

    ``missing_in_target`` / ``extra_in_target`` surface PP partial coverage:
    a PP>1 dump only has the last stage's layers, so it will be a strict subset
    of a PP=1 reference. Pass ``max_tokens`` / ``written_only`` to restrict the
    comparison to the written token slots (see ``_compare_slots``).
    """
    target = stitch_kv_dir(target_dir)
    ref = stitch_kv_dir(ref_dir)
    t_set = set(target)
    r_set = set(ref)
    common = sorted(t_set & r_set, key=_natural_key)
    missing = sorted(r_set - t_set, key=_natural_key)
    extra = sorted(t_set - r_set, key=_natural_key)
    layers: list[LayerCompare] = []
    for name in common:
        t = target[name].tensor
        r = ref[name].tensor
        if t.shape != r.shape:
            layers.append(LayerCompare(name, float("nan"), float("inf"), tuple(t.shape), tuple(r.shape)))
            continue
        slots = _compare_slots(t, r, max_tokens, written_only)
        if slots is not None and t.dim() == 4:
            slots = min(slots, t.shape[1])
            t_cmp, r_cmp = t[:, :slots], r[:, :slots]
        else:
            slots = None
            t_cmp, r_cmp = t, r
        layers.append(
            LayerCompare(
                name,
                cosine(t_cmp, r_cmp),
                maxdiff(t_cmp, r_cmp),
                tuple(t.shape),
                tuple(r.shape),
                slots=slots,
            )
        )
    return StitchedCompare(
        target_dir=target_dir,
        ref_dir=ref_dir,
        common_layers=common,
        missing_in_target=missing,
        extra_in_target=extra,
        layers=layers,
        cos_thresh=cos_thresh,
        max_tokens=max_tokens,
        written_only=written_only,
    )


def cosine(a: Any, b: Any) -> float:
    a = a.double().flatten()
    b = b.double().flatten()
    na, nb = a.norm(), b.norm()
    return float(a @ b / (na * nb)) if na > 0 and nb > 0 else float("nan")


def cos_is_clean(c: float, thresh: float) -> bool:
    """True when similarity is at/above threshold (NaN counts as divergent)."""
    return not math.isnan(c) and c >= thresh


def cos_is_bad(c: float, thresh: float) -> bool:
    return not cos_is_clean(c, thresh)


def _cos_rank_key(c: float) -> float:
    """Sort key so NaN ranks worse than any finite cosine (Python ``min`` skips NaN otherwise)."""
    return float("-inf") if math.isnan(c) else c


def argmin_layer_cos(layer_cos: dict[str, float]) -> tuple[str, float]:
    """Return ``(layer, cos)`` with the worst cosine; NaN always wins as worst."""
    if not layer_cos:
        raise ValueError("layer_cos is empty")
    name = min(layer_cos, key=lambda k: _cos_rank_key(layer_cos[k]))
    return name, layer_cos[name]


def maxdiff(a: Any, b: Any) -> float:
    return float((a.double() - b.double()).abs().max())


def gather_token_rows(
    dump: NativeLayerDump,
    *,
    n_tokens: int,
    block_size: int,
    head: int | None = 0,
) -> Any:
    """Return tensor shaped ``(N, D)`` for the first ``n_tokens`` sequence positions.

    Config ``dump_kv`` layout is ``[n_blocks, block_size, num_heads, head_dim]``
    (selected ``block_ids`` order, sequence starts at offset 0 of block 0).
    Legacy flat ``[n_tokens_or_slots, ...]`` along dim0 is still accepted.
    """
    import torch

    t = dump.tensor
    if not hasattr(t, "dim"):
        raise TypeError(f"layer={dump.layer}: not a tensor")

    n_blocks_meta = len(dump.block_ids) if dump.block_ids else int(t.shape[0])
    if t.dim() >= 2 and int(t.shape[1]) == int(block_size):
        # Preferred: [n_blocks, block_size, ...]
        assert_block_capacity(int(t.shape[0]), n_tokens, block_size)
        rows = [t[i // block_size, i % block_size] for i in range(n_tokens)]
        stacked = torch.stack(rows, dim=0)
    else:
        # Legacy concatenated rows along dim0.
        if t.shape[0] < n_tokens:
            raise ValueError(
                f"layer={dump.layer}: tensor length {t.shape[0]} < num_tokens {n_tokens}"
            )
        if dump.block_ids:
            assert_block_capacity(n_blocks_meta, n_tokens, block_size)
        stacked = t[:n_tokens]

    if stacked.dim() == 3:
        # [N, num_heads, head_dim]
        h = 0 if head is None else int(head)
        stacked = stacked[:, h, :]
    elif stacked.dim() > 3:
        stacked = stacked.reshape(stacked.shape[0], -1)
    return stacked.double()


def _natural_key(name: str) -> tuple:
    parts = re.split(r"(\d+)", name)
    return tuple(int(p) if p.isdigit() else p for p in parts)


def matched_layers(buggy: dict[str, NativeLayerDump], ref: dict[str, NativeLayerDump]) -> list[str]:
    names = sorted(set(buggy) & set(ref), key=_natural_key)
    if not names:
        raise ValueError(
            f"no common layer names (buggy={len(buggy)} ref={len(ref)}); "
            f"buggy sample={list(buggy)[:5]} ref sample={list(ref)[:5]}"
        )
    return names


def token_id_sequence(detail: dict[str, Any]) -> tuple[list[int], list[int]]:
    """Return (prompt_token_ids, output_token_ids) from report detail."""
    prompt = detail.get("prompt_token_ids")
    output = detail.get("output_token_ids")
    if not isinstance(prompt, list) or not isinstance(output, list):
        raise ValueError("report detail missing prompt_token_ids/output_token_ids lists")
    return [int(x) for x in prompt], [int(x) for x in output]


def validate_matching_token_ids(
    buggy_detail: dict[str, Any],
    ref_detail: dict[str, Any],
    *,
    strict: bool = True,
) -> None:
    """Ensure buggy/ref reports describe the same force-fed token sequence."""
    b_prompt, b_output = token_id_sequence(buggy_detail)
    r_prompt, r_output = token_id_sequence(ref_detail)
    if b_prompt != r_prompt or b_output != r_output:
        msg = (
            "buggy/ref report token ids differ "
            f"(prompt {len(b_prompt)} vs {len(r_prompt)}, "
            f"output {len(b_output)} vs {len(r_output)})"
        )
        if strict:
            raise ValueError(msg)
        print(f"[warn] {msg}; using buggy report for token labels")


@dataclass
class TokenLayerCos:
    token_idx: int
    token_id: Any
    role: str
    min_cos: float
    min_layer: str
    layer_cos: dict[str, float]
    layer_maxdiff: dict[str, float]


@dataclass
class KvSimilarityAnalysis:
    n_tokens: int
    n_prompt: int | None
    layers: list[str]
    cos_thresh: float
    per_token: list[TokenLayerCos]
    first_bad_idx: int | None

    @property
    def first_bad(self) -> TokenLayerCos | None:
        if self.first_bad_idx is None:
            return None
        return self.per_token[self.first_bad_idx]


def token_role(i: int, n_prompt: int | None) -> str:
    if n_prompt is None:
        return "pos"
    return "prompt" if i < n_prompt else f"out[{i - n_prompt}]"


def compare_kv_dumps(
    *,
    buggy_dir: Path,
    ref_dir: Path,
    detail: dict[str, Any],
    report: dict[str, Any] | None = None,
    num_tokens: int | None = None,
    block_size: int = 128,
    head: int = 0,
    cos_thresh: float = 0.99,
) -> KvSimilarityAnalysis:
    """Per-token min-over-layers cosine; locate first token below ``cos_thresh``."""
    n_p, n_o, n_from_report = token_n(detail)
    n_tokens = num_tokens if num_tokens is not None else n_from_report
    if n_tokens <= 0:
        raise ValueError("no token count/ids in report; pass num_tokens")
    labels, n_prompt = token_id_labels(detail, n_tokens)
    block_ids = block_ids_from_detail(detail, report)

    buggy = load_kv_dir(buggy_dir)
    ref = load_kv_dir(ref_dir)
    layers = matched_layers(buggy, ref)
    sample = buggy[layers[0]]
    ids = block_ids or sample.block_ids
    n_blocks = len(ids) if ids else int(sample.tensor.shape[0])
    assert_block_capacity(n_blocks, n_tokens, block_size)

    cb = {
        name: gather_token_rows(buggy[name], n_tokens=n_tokens, block_size=block_size, head=head)
        for name in layers
    }
    cr = {
        name: gather_token_rows(ref[name], n_tokens=n_tokens, block_size=block_size, head=head)
        for name in layers
    }

    per_token: list[TokenLayerCos] = []
    first_bad_idx: int | None = None
    for i in range(n_tokens):
        layer_cos: dict[str, float] = {}
        layer_maxdiff: dict[str, float] = {}
        for name in layers:
            layer_cos[name] = cosine(cb[name][i], cr[name][i])
            layer_maxdiff[name] = maxdiff(cb[name][i], cr[name][i])
        min_layer, min_cos = argmin_layer_cos(layer_cos)
        tok = labels[i] if i < len(labels) else i
        per_token.append(
            TokenLayerCos(
                token_idx=i,
                token_id=tok,
                role=token_role(i, n_prompt),
                min_cos=min_cos,
                min_layer=min_layer,
                layer_cos=layer_cos,
                layer_maxdiff=layer_maxdiff,
            )
        )
        if first_bad_idx is None and cos_is_bad(min_cos, cos_thresh):
            first_bad_idx = i

    return KvSimilarityAnalysis(
        n_tokens=n_tokens,
        n_prompt=n_prompt,
        layers=layers,
        cos_thresh=cos_thresh,
        per_token=per_token,
        first_bad_idx=first_bad_idx,
    )


def format_kv_similarity_tables(
    analysis: KvSimilarityAnalysis,
    *,
    buggy_dir: Path,
    ref_dir: Path,
) -> str:
    """Human-readable two-table report (Table1 per-token min cos; Table2 first bad)."""
    lines: list[str] = []
    n_layers = len(analysis.layers)
    lines.append("=" * 78)
    lines.append(
        f"TABLE 1  逐 token: min-over-{n_layers}-layers cos (阈值 {analysis.cos_thresh:.2f})"
    )
    lines.append(f"         buggy={buggy_dir} ref={ref_dir}")
    lines.append("=" * 78)

    seg_start: int | None = None
    for row in analysis.per_token:
        if cos_is_clean(row.min_cos, analysis.cos_thresh):
            if seg_start is None:
                seg_start = row.token_idx
            continue
        if seg_start is not None:
            lines.append(f"token {seg_start}-{row.token_idx - 1}  clean")
            seg_start = None
        lines.append(
            f"token {row.token_idx:<4d} tok={row.token_id!s:<6} {row.role:<7} "
            f"min_cos={row.min_cos:.4f}  @{row.min_layer}"
        )
    if seg_start is not None:
        lines.append(f"token {seg_start}-{analysis.n_tokens - 1}  clean")

    if analysis.first_bad_idx is None:
        lines.append("")
        lines.append("无坏点：KV 在匹配层上全部一致 → 问题可能在采样/后处理")
        return "\n".join(lines)

    bad = analysis.first_bad
    assert bad is not None
    lines.append("")
    lines.append("=" * 78)
    lines.append(
        f"TABLE 2  第一坏点 token {bad.token_idx} "
        f"(tok={bad.token_id}, {bad.role}) 逐层 cos / maxdiff"
    )
    lines.append("=" * 78)
    lines.append(f"{'layer':<40} {'cos':<12} {'maxdiff':<12}")
    prev_ok = True
    for name in analysis.layers:
        c = bad.layer_cos[name]
        md = bad.layer_maxdiff[name]
        mark = ""
        is_bad = cos_is_bad(c, analysis.cos_thresh)
        if prev_ok and is_bad:
            mark = "  <-- 首发散层"
        if is_bad:
            prev_ok = False
        lines.append(f"{name:<40} {c:<12.4f} {md:<12.4e}{mark}")
    return "\n".join(lines)


def analysis_to_json(analysis: KvSimilarityAnalysis) -> dict[str, Any]:
    """Serialize analysis for ``--json-out``."""
    first_bad = None
    if analysis.first_bad is not None:
        fb = analysis.first_bad
        first_bad = {
            "token_idx": fb.token_idx,
            "token_id": fb.token_id,
            "role": fb.role,
            "min_cos": fb.min_cos,
            "min_layer": fb.min_layer,
            "layers": [
                {"layer": name, "cos": fb.layer_cos[name], "maxdiff": fb.layer_maxdiff[name]}
                for name in analysis.layers
            ],
        }
    return {
        "n_tokens": analysis.n_tokens,
        "n_prompt": analysis.n_prompt,
        "cos_thresh": analysis.cos_thresh,
        "layers": analysis.layers,
        "first_bad": first_bad,
        "per_token": [
            {
                "token_idx": row.token_idx,
                "token_id": row.token_id,
                "role": row.role,
                "min_cos": row.min_cos,
                "min_layer": row.min_layer,
            }
            for row in analysis.per_token
        ],
    }
