# Anomaly repro status — 2026-10-16/17 (origin-faithful)

**Rev:** `2026-10-18T0330+08` — **S126–S128 skills-done v5.0**；S123–S125 skills-done v4.9；**S45 FAIL+GAP**；**S44 INVALID**；S21 HARD.

## Recent PASS

| ID | Layers | Host | Skills |
|----|--------|------|--------|
| S123 | 100/33/48 | 160 | skills-done v4.9 |
| S124 | 132/0/48 | 160 | skills-done v4.9（precision=0 OK） |
| S125 | 100/48/48 | 160 | skills-done v4.9（logits_finite） |
| **S126** | **16/48/48** | 160 `8,9` | **skills-done v5.0** hidden-zeros |
| **S127** | **16/48/48** | 160 `10,11` | **skills-done v5.0** embed-zeros |
| **S128** | **58/28/48** | 160 `12,13` | **skills-done v5.0** cos/sin-zeros |

## FAIL+GAP / INVALID / Parked

- **S45** FAIL+GAP · **S44** INVALID · **S21** HARD · S27 BLOCKED · S01/S07 FAIL+GAP

## Skills poll checklist (162)

Hash-poll CHANGE on:
1. `docs/anomaly-skills-handoff.md` rev **2026-10-18T0330+08** — Inbox empty (S126–S128 DONE)
2. `docs/anomaly-repro-status-20261016.md` rev **2026-10-18T0330+08** — S126–S128 skills-done v5.0
