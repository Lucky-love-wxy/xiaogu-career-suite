# 小谷 agent 核心（web/）

服务端执行 harness 的核心，不含账号、额度、页面（那些在 `../platform/`，2026-10-14 起分开）。

| 文件 | 作用 |
|---|---|
| agent.py | 路由（规则 + 模型分类）、证据包、提示词、校验与重写、渲染；基本情况卡片、用户记忆文档、城市产业资料、12 轮压缩上下文 |
| resume_tools.py | 简历识别、关键词覆盖率、不编造校验、单栏排版 |
| interview.py | 题库模式模拟面试状态机 |
| server.py | 早期的本机模拟服务（只用标准库，页面读 `../platform/static/`），已不作为主入口 |

平台层通过 `agent.Agent().handle(session_id, message, card=..., memory=..., off=...)` 调用核心。测试在 `../tests/`。
