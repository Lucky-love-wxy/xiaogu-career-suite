# Codex 调研 Brief：小谷自建 Web Agent

- 下发日期：2026-10-03
- 设计方：Claude；执行方：Codex
- 上游：notes/2026-10-03-web-agent-sim.md 第 1.2 节
- 交付落点：`docs/research/web-agent-2026-10.md`

## 问题

**W1 国内求职 AI 的 Web 产品形态**：至少 6 个（例：效招、牛客 AI 面试/简历、BOSS 直聘 AI 功能、职徒简历、超级简历、多面鹅）。每个记录：入口形态（聊天框 / 表单向导 / 工作台）、首屏要用户做什么、是否要求登录、免费额度与价格、是否展示信息来源。截图存 evidence。

**W2 开源 chat-agent 框架**：比较 3–5 个可做「对话 + 侧边结构化面板」的方案（例：Chainlit、Open WebUI、Vercel AI SDK chat 模板、assistant-ui、LobeChat）。记录：许可证、是否支持服务端强制输出格式、是否支持工具调用 trace 展示、部署复杂度、中文社区活跃度。

**W3 DeepSeek 成本与限制**：`deepseek-flash` 与 `deepseek-v4-pro` 的官方价格、并发/限流、JSON 模式与 thinking 模式的已知问题；按「一轮岗位理解 ≈ 输入 6k token、输出 1k token」估算单次成本。只用官方文档。

## 证据标准与验收

- 一手来源优先，每条附 URL + 访问日期；厂商自述与实测分开。
- 查不到写「未找到」。
- 结尾「对设计的影响」：哪些结论改变 4.1 架构或 4.2 模型选择。
