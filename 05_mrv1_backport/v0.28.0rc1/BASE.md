# BASE — `v0.28.0rc1` (MRV1)

| 项 | 值 |
|----|-----|
| **Release 目录** | `v0.28.0rc1` |
| **上游 checkout** | tag v0.28.0.rc1 (note the dot before rc) |
| **BASE short** | `96df62310` |
| **BASE full** | `96df623103f921df1a4488170d106f36689acb59` |
| **Runner** | **Model Runner V1 only**（本包不接 V2） |
| **Patch** | `patches/0001-runtime-guard-mrv1-wiring.patch` |
| **包版本** | `mrv1-rg.2`（见 ../CHANGELOG.md） |

```bash
git checkout 96df623103f921df1a4488170d106f36689acb59
bash ../apply_patch.sh --release v0.28.0rc1 "$(pwd)"
```
