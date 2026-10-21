# BASE — `v0.26.0rc1` (MRV1)

| 项 | 值 |
|----|-----|
| **Release 目录** | `v0.26.0rc1` |
| **上游 checkout** | tag v0.26.0rc1 |
| **BASE short** | `f2f74a16c` |
| **BASE full** | `f2f74a16c3c50a76f4349d807918e83edec1e35c` |
| **Runner** | **Model Runner V1 only**（本包不接 V2） |
| **Patch** | `patches/0001-runtime-guard-mrv1-wiring.patch` |
| **包版本** | `mrv1-rg.1`（见 ../CHANGELOG.md） |

```bash
git checkout f2f74a16c3c50a76f4349d807918e83edec1e35c
bash ../apply_patch.sh --release v0.26.0rc1 "$(pwd)"
```
