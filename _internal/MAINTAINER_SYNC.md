# 维护者：skills 镜像同步

权威在本仓 `06_agent_skills/`；内部私有仓 `runtime-guard-test` 的 `analysis/skill/` 为镜像（可短暂滞后）。

```bash
export RG_DOCS=/path/to/runtime-guard-docs
export RG_TEST=/path/to/runtime-guard-test
rsync -a --delete \
  --exclude VERIFY_HANDOFF.md \
  "$RG_DOCS/06_agent_skills/" "$RG_TEST/analysis/skill/"
```

- 脚本 CLI / skill 契约变更：先改本仓，再回写镜像。
- `_internal/` 不 rsync；VERIFY 交接件仅留本仓 `_internal/` 或内部文档树。
