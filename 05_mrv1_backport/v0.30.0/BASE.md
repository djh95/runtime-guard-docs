# BASE — `v0.30.0` (MRV1)

| 项 | 值 |
|----|-----|
| **Release 目录** | `v0.30.0` |
| **上游 checkout** | same BASE as 05_v030_backport / v0.30-rg.2 (6d25ba2b3 on releases/v0.30.0, Guard pre-merge) |
| **BASE short** | `6d25ba2b3` |
| **BASE full** | `6d25ba2b3c123bf963966cd583e985979d7a8a7d` |
| **Runner** | **Model Runner V1 only**（本包不接 V2） |
| **Patch** | `patches/0001-runtime-guard-mrv1-wiring.patch` |
| **包版本** | `mrv1-rg.1`（见 ../CHANGELOG.md） |

```bash
git checkout 6d25ba2b3c123bf963966cd583e985979d7a8a7d
bash ../apply_patch.sh --release v0.30.0 "$(pwd)"
```
