#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Score OpenAI-style completion samples for anomaly precision / GAP signals.

Used when Guard reports are empty (FAIL+GAP) or when validating the precision
layer of a three-layer anomaly run (trigger / precision / detect).

Typical inputs::

    samples/completion_*.json   # OpenAI completions response
    fail-evidence/Sxx/sample_*.json
    c_000.json with {"text": "..."} or choices[0].text

Does **not** invent detectors — only offline heuristics for evidence triage.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


_CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
_HANGUL_RE = re.compile(r"[\u1100-\u11ff\u3130-\u318f\uac00-\ud7af]")
_ARABIC_RE = re.compile(r"[\u0600-\u06ff]")
_LATIN_RE = re.compile(r"[A-Za-z]")
_DIGIT_RUN_RE = re.compile(r"\d{8,}|(\d)\1{5,}")
_XXXX_RE = re.compile(r"(x{4,}|X{4,}|\*{4,})")
_CTX_ECHO_RE = re.compile(r"ctx\d+_|ref=\d+", re.I)
# S36 temp-scale blowup: unique garbled prose with id=/id0=/#digits echo.
_ID_ECHO_RE = re.compile(r"(?i)\bid\s*\d*\s*[:=]|#\d{5,}")
_ZWSP_RE = re.compile(r"[\u200b-\u200f\u202a-\u202e\ufeff]")
# S32 FIA FULL-graph pad (#7144): unique pad-slot echo (w12_56 …) / underscore-digit pad.
_PAD_WN_RE = re.compile(r"(?:^|\s)w\d+_\d+(?:\s+w\d+_\d+){3,}")
_PAD_UNDERSCORE_RE = re.compile(r"(?:_\d+){6,}|^(?:_0){4,}")
# S37-ish: sparse "." / newline-dot collapse that short-chunk repeat can miss.
_DOT_COLLAPSE_RE = re.compile(r"(?:\.\s*){10,}|(?:\n\n\.\n\n){4,}")


def extract_text(obj: Any) -> str | None:
    """Pull completion text from common dump shapes."""
    if isinstance(obj, str):
        return obj
    if not isinstance(obj, dict):
        return None
    if isinstance(obj.get("text"), str):
        return obj["text"]
    choices = obj.get("choices")
    if isinstance(choices, list) and choices:
        c0 = choices[0]
        if isinstance(c0, dict) and isinstance(c0.get("text"), str):
            return c0["text"]
        if isinstance(c0, dict) and isinstance(c0.get("message"), dict):
            content = c0["message"].get("content")
            if isinstance(content, str):
                return content
    detail = obj.get("detail")
    if isinstance(detail, dict) and isinstance(detail.get("output_text"), str):
        return detail["output_text"]
    return None


def _script_flags(text: str) -> dict[str, bool]:
    has_cjk = bool(_CJK_RE.search(text))
    has_hangul = bool(_HANGUL_RE.search(text))
    has_arabic = bool(_ARABIC_RE.search(text))
    has_latin = bool(_LATIN_RE.search(text))
    has_digit = any(ch.isdigit() for ch in text)
    # "Other" letters / symbols often show up as mixed-script garbage.
    other = 0
    for ch in text:
        cat = unicodedata.category(ch)
        if ch.isspace() or cat.startswith("P") or cat.startswith("Z"):
            continue
        if "LATIN" in unicodedata.name(ch, "") or ch.isdigit():
            continue
        if _CJK_RE.match(ch) or _HANGUL_RE.match(ch) or _ARABIC_RE.match(ch):
            continue
        other += 1
    scripts = sum([has_cjk, has_hangul, has_arabic, has_latin])
    return {
        "has_cjk": has_cjk,
        "has_hangul": has_hangul,
        "has_arabic": has_arabic,
        "has_latin": has_latin,
        "has_digit": has_digit,
        "has_misc_symbol": other >= max(2, len(text) // 40),
        "n_scripts": scripts,
    }


def score_text(text: str) -> dict[str, Any]:
    """Heuristic labels for one completion string."""
    flags = _script_flags(text)
    labels: list[str] = []
    mixed = flags["n_scripts"] >= 2
    # Symbol / control soup (excludes normal CJK/Latin/Hangul/Arabic letters).
    weird_ratio = 0.0
    if text:
        weird = 0
        for ch in text:
            if ch.isspace() or ch.isalnum():
                continue
            if _CJK_RE.match(ch) or _HANGUL_RE.match(ch) or _ARABIC_RE.match(ch):
                continue
            if ch in ".,;:!?-'\"()[]、。，《》「」":
                continue
            weird += 1
        weird_ratio = weird / max(len(text), 1)
    # Ordinary CN+EN prose → mixed_script; S01/S07 soup → garbage_mixed_script.
    latin_words = re.findall(r"[A-Za-z]{3,}", text)
    garbage = mixed and (
        flags["n_scripts"] >= 3
        or flags["has_misc_symbol"]
        or weird_ratio >= 0.08
        or (flags["has_digit"] and len(latin_words) >= 4 and flags["has_cjk"])
    )
    if garbage:
        labels.append("garbage_mixed_script")
    elif mixed:
        labels.append("mixed_script")
    if _DIGIT_RUN_RE.search(text):
        labels.append("digits")
    if _XXXX_RE.search(text):
        labels.append("xxxx_collapse")
    if _CTX_ECHO_RE.search(text):
        labels.append("ctx_echo")
    if _ID_ECHO_RE.search(text):
        labels.append("id_echo")
    if _ZWSP_RE.search(text):
        labels.append("zwsp")
    # Graph-pad / FIA FULL pad echo (S32 #7144): unique per-req garbage, not identical mode.
    if _PAD_WN_RE.search(text) or _PAD_UNDERSCORE_RE.search(text):
        labels.append("pad_echo")
        if "repeat" not in labels:
            labels.append("repeat")
    if _DOT_COLLAPSE_RE.search(text):
        if "repeat" not in labels:
            labels.append("repeat")
    # S43 embed-scale: pure newline/whitespace collapse (`.` does not match `\n`).
    if len(text) >= 8 and re.fullmatch(r"[\n\r\t ]+", text):
        labels.append("newline_collapse")
        if "repeat" not in labels:
            labels.append("repeat")
    # Local token-ish repeat: same 1–4 char chunk ≥6 times.
    if re.search(r"(.{1,4})\1{5,}", text) and "repeat" not in labels:
        labels.append("repeat")
    # S36-class unique garbled prose: latin + digits + fragmentation (id echo / high weird / many short lines).
    if (
        "id_echo" in labels
        or (
            flags["has_latin"]
            and flags["has_digit"]
            and len(text) >= 40
            and (
                weird_ratio >= 0.04
                or text.count("\n") >= 3
                or len(re.findall(r"(?i)\bid\b", text)) >= 2
            )
        )
    ) and not any(
        lab in labels
        for lab in ("garbage_mixed_script", "token0_collapse", "pad_echo")
    ):
        # Mark unique-garbage precision without claiming detector GAP.
        if "unique_garbage" not in labels:
            labels.append("unique_garbage")
    # Phrase / sentence loop (S28 rope style flip): same ≥10-char unit ≥3 times.
    # Short-chunk `repeat` may miss English phrase echo that token_repeat still catches.
    if re.search(r"(.{10,100}?)\1{2,}", text):
        labels.append("phrase_repeat")
        if "repeat" not in labels:
            labels.append("repeat")
    # Softcap / unstable-softmax overflow often collapses to token0 → "!!!!…" (S20).
    if re.fullmatch(r"!{8,}", text.strip()) or (
        len(set(text.strip())) == 1 and len(text.strip()) >= 8 and text.strip()[0] in "!?.0"
    ):
        if "repeat" not in labels:
            labels.append("repeat")
        labels.append("token0_collapse")
    if not labels and len(text.strip()) >= 8:
        # Dense non-space weirdness without clear English words.
        words = re.findall(r"[A-Za-z]{3,}", text)
        if flags["has_misc_symbol"] and len(words) < 3:
            labels.append("non_ascii_junk")
    return {
        "n_chars": len(text),
        "labels": labels,
        "flags": flags,
        "weird_ratio": round(weird_ratio, 3),
        "preview": text[:160].replace("\n", "\\n"),
    }


def load_sample_texts(path: Path) -> list[tuple[str, str]]:
    """Return list of (source_id, text)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list[tuple[str, str]] = []
    if isinstance(data, list):
        for i, item in enumerate(data):
            t = extract_text(item)
            if t is not None:
                out.append((f"{path.name}[{i}]", t))
        return out
    t = extract_text(data)
    if t is not None:
        out.append((path.name, t))
    return out


def score_dir(sample_dir: Path, pattern: str = "*.json") -> dict[str, Any]:
    paths = sorted(sample_dir.glob(pattern))
    if not paths and sample_dir.is_file():
        paths = [sample_dir]
    rows: list[dict[str, Any]] = []
    texts: list[str] = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            pairs = load_sample_texts(path)
        except Exception as exc:  # noqa: BLE001 — triage tool, keep going
            rows.append({"source": path.name, "error": str(exc)})
            continue
        for sid, text in pairs:
            scored = score_text(text)
            scored["source"] = sid
            rows.append(scored)
            texts.append(text)

    ctr = Counter(texts)
    identical_mode_count = ctr.most_common(1)[0][1] if ctr else 0
    label_ctr: Counter[str] = Counter()
    for row in rows:
        for lab in row.get("labels") or []:
            label_ctr[lab] += 1

    precision_hits = sum(1 for r in rows if r.get("labels"))
    identical_across = bool(texts) and identical_mode_count == len(texts) and len(texts) >= 2
    # Pure bang/`!` or short-char repeat / digit collapse is what token_repeat catches
    # (S20 overflow, S23/S24 weight·quant always-on). Do NOT mark as detector GAP.
    repeatish = (
        label_ctr.get("repeat", 0)
        + label_ctr.get("xxxx_collapse", 0)
        + label_ctr.get("token0_collapse", 0)
        + label_ctr.get("digits", 0)
        + label_ctr.get("phrase_repeat", 0)
        + label_ctr.get("ctx_echo", 0)
        + label_ctr.get("pad_echo", 0)
        + label_ctr.get("id_echo", 0)
        + label_ctr.get("unique_garbage", 0)
        + label_ctr.get("newline_collapse", 0)
    )
    only_repeatish = precision_hits > 0 and repeatish >= precision_hits and not (
        label_ctr.get("garbage_mixed_script", 0) or label_ctr.get("mixed_script", 0)
    )
    gap = None
    if only_repeatish or (repeatish and not label_ctr.get("garbage_mixed_script", 0)):
        gap = None
    elif label_ctr.get("garbage_mixed_script", 0) and not repeatish:
        # Finite mixed garbage with no repeat signal — logits_finite/token_repeat often miss (S01/S07).
        gap = "finite_garbage_or_identical — logits_finite/token_repeat likely miss"
    elif identical_across and label_ctr.get("mixed_script", 0) and not repeatish:
        gap = "finite_garbage_or_identical — logits_finite/token_repeat likely miss"
    elif identical_across and precision_hits and not repeatish:
        gap = "finite_garbage_or_identical — logits_finite/token_repeat likely miss"
    elif label_ctr.get("garbage_mixed_script", 0) and repeatish:
        # Mixed batch: some repeat (detectable) + some garbage — do not claim wholesale miss.
        gap = None
    return {
        "n_files": len(paths),
        "n_samples": len(texts),
        "n_unique": len(ctr),
        "identical_mode_count": identical_mode_count,
        "identical_across_requests": identical_across,
        "precision_hits": precision_hits,
        "label_counts": dict(label_ctr.most_common()),
        "mode_preview": (ctr.most_common(1)[0][0][:160] if ctr else None),
        "samples": rows[:40],
        # GAP hint for current shipped detectors (do not implement detectors here).
        "detector_gap_hint": gap,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample-dir",
        type=Path,
        required=True,
        help="Directory of completion_*.json / sample_*.json (or a single JSON file)",
    )
    parser.add_argument("--pattern", default="*.json")
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args(argv)

    summary = score_dir(args.sample_dir, args.pattern)
    print(
        f"samples={summary['n_samples']} unique={summary['n_unique']} "
        f"identical_mode={summary['identical_mode_count']} "
        f"precision_hits={summary['precision_hits']}"
    )
    print(f"identical_across_requests={summary['identical_across_requests']}")
    print(f"label_counts={summary['label_counts']}")
    if summary.get("detector_gap_hint"):
        print(f"detector_gap_hint={summary['detector_gap_hint']}")
    if summary.get("mode_preview"):
        print(f"mode_preview={summary['mode_preview']!r}")
    for row in summary["samples"][:12]:
        if "error" in row:
            print(f"  [err] {row['source']}: {row['error']}")
        else:
            print(f"  {row['source']}: labels={row['labels']} preview={row['preview']!r}")

    if args.json_out is not None:
        args.json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
