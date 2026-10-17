# Anomaly repro status — 2026-10-16/17 (origin-faithful)

**Rev:** `2026-10-18T0225+08` — **S120–S122 skills-done v4.8**（S121 precision=0 OK）；S117–S119 skills-done v4.7；**S45 FAIL+GAP**；**S44 INVALID**；S21 HARD.

## Recent PASS

| ID | Layers | Host | Skills |
|----|--------|------|--------|
| S117 | 58/34/48 | 160 | skills-done v4.7 |
| S118 | 58/33/48 | 160 | skills-done v4.7 |
| S119 | 102/41/48 | 160 | skills-done v4.7 |
| **S120** | **100/48/48** | 160 `8,9` | **skills-done v4.8** RMSNorm-weight=zeros |
| **S121** | **58/0/48** | 160 `10,11` | **skills-done v4.8** SwiGLU-input-abs（precision=0 OK） |
| **S122** | **16/16/48** | 160 `12,13` | **skills-done v4.8** logits-abs |

## FAIL+GAP / INVALID / Parked

- **S45** FAIL+GAP · **S44** INVALID · **S21** HARD · S27 BLOCKED · S01/S07 FAIL+GAP

## Skills poll checklist (162)

Hash-poll CHANGE on:
1. `docs/anomaly-skills-handoff.md` rev **2026-10-18T0225+08** — Inbox empty (S120–S122 DONE)
2. `docs/anomaly-repro-status-20261016.md` rev **2026-10-18T0225+08** — S120–S122 skills-done v4.8
