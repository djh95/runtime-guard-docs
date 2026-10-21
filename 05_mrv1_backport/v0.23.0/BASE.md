# BASE — `v0.23.0` (MRV1)

| 项 | 值 |
|----|-----|
| **Release 目录** | `v0.23.0` |
| **上游 checkout** | tag v0.23.0 (post1 compatible) |
| **BASE short** | `5cb98caaa` |
| **BASE full** | `5cb98caaadeff42b5b62b996e34bb2aaa29d20fd` |
| **Runner** | **Model Runner V1 only**（本包不接 V2） |
| **Patch** | `patches/0001-runtime-guard-mrv1-wiring.patch` |
| **包版本** | `mrv1-rg.2`（见 ../CHANGELOG.md） |

```bash
git checkout 5cb98caaadeff42b5b62b996e34bb2aaa29d20fd
bash ../apply_patch.sh --release v0.23.0 "$(pwd)"
```
