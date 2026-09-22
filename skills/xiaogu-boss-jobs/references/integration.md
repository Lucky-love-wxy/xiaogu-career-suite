# boss-agent-cli 集成契约

## 依赖

- 上游项目：<https://github.com/can4hou6joeng4/boss-agent-cli>
- 运行前总是读取本机 `boss schema`；README 只作说明。
- 命令使用参数数组执行，不使用 shell 拼接 JD、公司名或筛选条件。

## 输入与输出

上游成功信封通常是 `{"ok": true, "data": ...}`，搜索 `data` 可能直接为列表，也可能含 `jobs/items/jobList/list/result`。适配器兼容这些已观察结构。

规范化结果遵循 `_xiaogu-runtime/references/job-document.schema.json`。`source_snapshot` 是私有审计材料，展示时移除联系人、访问 ID 和平台内部字段。

## 错误

保留上游的 `code`、`recoverable`、`recovery_action`、`hints.next_actions` 与 `hints.operator_actions`。Agent 可执行只读的 `next_actions`；需要扫码、登录、解除平台风险的 `operator_actions` 交给用户。

不要把自动投递加入恢复动作。恢复只继续用户原来授权的读取任务。
