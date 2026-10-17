# Anomaly repro status — 2026-10-16/17 (origin-faithful)

**Rev:** `2026-10-18T0255+08` — **S123–S125 skills-done v4.9**（S124 precision=0 OK；S125 `logits_finite`）；S120–S122 skills-done v4.8；**S45 FAIL+GAP**；**S44 INVALID**；S21 HARD.

## Recent PASS

| ID | Layers | Host | Skills |
|----|--------|------|--------|
| S120 | 100/48/48 | 160 | skills-done v4.8 |
| S121 | 58/0/48 | 160 | skills-done v4.8（precision=0 OK） |
| S122 | 16/16/48 | 160 | skills-done v4.8 |
| **S123** | **100/33/48** | 160 `8,9` | **skills-done v4.9** RMSNorm-bias=-weight |
| **S124** | **132/0/48** | 160 `10,11` | **skills-done v4.9** penalty-skip（precision=0 OK） |
| **S125** | **100/48/48** | 160 `12,13` | **skills-done v4.9** residual-leak-sub（`logits_finite`） |

## FAIL+GAP / INVALID / Parked

- **S45** FAIL+GAP · **S44** INVALID · **S21** HARD · S27 BLOCKED · S01/S07 FAIL+GAP

## Skills poll checklist (162)

Hash-poll CHANGE on:
1. `docs/anomaly-skills-handoff.md` rev **2026-10-18T0255+08** — Inbox empty (S123–S125 DONE)
2. `docs/anomaly-repro-status-20261016.md` rev **2026-10-18T0255+08** — S123–S125 skills-done v4.9
