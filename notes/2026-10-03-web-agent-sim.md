# 小谷 Web Agent 模拟环境 · 启动文档

## 元数据

- 日期：2026-10-03
- 任务名：自建 Web Agent（DeepSeek API + 小谷 harness）模拟环境
- 所属项目：xiaogu-career-suite
- 触发类型：设计
- 关联 Principle：P1；feedback_research_before_build；feedback_research_division_codex；feedback_evidence_based_claims

## 1. 市场调研结果

状态：已有部分有依据结论；产品形态与框架选型的完整调研已下发 Codex（notes/2026-10-03-codex-research-brief-web-agent.md），**定稿前必须回填**。本轮只做模拟环境原型，不做上线决策。

### 1.1 已有依据

- 用户侧：超 86% 的 2026 届毕业生春招用过生成式 AI，37.25% 每天用；72% 用 AI 润色简历，48% 用 AI 生成面试题清单（前程无忧，2026-04-09，见 docs/research/job-seeker-core-questions-2026-10-03.md）。即目标用户已经习惯通用 AI 聊天框，小谷的对手首先是通用 AI。
- 竞品：效招（Joblytic）是一体化 SaaS，岗位、简历、进度、日历在同一数据系统，公开样例给匹配百分比但无公开计算方法（docs/research/joblytic-competitor-2026-09-22.md）。
- 宿主现状：WorkBuddy 版本的 GUI 验收因 ScreenCaptureKit -3812 未完成；Skill 指令不能强制宿主逐字输出渲染器结果，「当前未实现主机级输出拦截」（docs/testing/beginner-acceptance-2026-10-01.md）。
- 模型：DeepSeek API 兼容 OpenAI 格式，base_url `https://api.deepseek.com`，模型 `deepseek-flash` / `deepseek-v4-pro`，支持 `response_format: json_object`（api-docs.deepseek.com，2026-10-03 读取）。

### 1.2 Codex部分调研回填（2026-10-05）

- 见[Web Agent调研](../docs/research/web-agent-2026-10.md)：八国内工具公开入口中六有AI公开资料，实际AI交互仍未验证；不能称六AI实际体验全部完成。
- 三方案：Chainlit当前Apache-2.0、assistant-ui MIT、Vercel AI SDK Apache-2.0。聊天UI和工具trace不替代Python服务端路由/事实校验/renderer；流式partial不是最终已校验对象。部署与中文社区活跃度尚未实测。
- DeepSeek官方当前Flash=V4.1-Flash、Pro=V4-Pro-0813；6000输入未缓存+1000输出估算Flash非高峰$0.0015/高峰$0.003，Pro$0.00594/$0.01188，未含额外thinking与重试。账号并发2500/500；JSON可能空内容，需服务端失败处理。
- 4.1/4.2影响详见报告；尚未改运行时、选定新框架或调用真实模型。W1六AI实际界面、未知价格、中文社区统计与实际运行仍待补，不作上线依据。

## 2. 我要解决的问题

在 Skill 宿主（WorkBuddy、Codex）里，harness 的三件关键事情只能靠模型自觉，测过也无法保证：
1. 是否按路由走、是否先问缺的材料；
2. 最终回答是否逐字等于渲染器输出（契约本身承认没有主机级拦截）；
3. 同一会话里的 JD、经历能否跨轮沿用。

自建 Web Agent 把这三件从「提示词约束」变成「代码保证」：路由、校验、渲染、会话材料由服务端执行，模型只负责在给定证据内写内容。模拟环境的目标是先证明这一点可行，并能离线、可重复地演示和回归。

## 3. 适用的设计规范

- 前端风格：日式简约（留白、克制、Typography 主导），聊天产品不用科技暗色。
- 小谷事实边界与输出契约（output-contract.md、phrasing.md）原样复用，不另起格式。
- 凭证：DeepSeek key 只从环境变量或 macOS 钥匙串读取，不进对话、不进仓库。
- AI 协作 SOP：关键决策点（产品形态、上线范围）不由 agent 拍板。

## 4. 方案

### 4.1 架构

```text
浏览器（单页，日式简约）
  │  POST /api/chat {session_id, message}
  ▼
server.py（Python 标准库 ThreadingHTTPServer，无第三方依赖）
  ├─ session：保存本会话已出现的 JD / 经历 / 逐字稿 → 生成路由 context
  ├─ route_request.route()            ← 现有确定性路由，原样 import
  ├─ missing_inputs 非空 → 直接产出 needs_input，不调模型
  ├─ 工具层：search.py analyze、analyze_job.py → 真实本地检索
  ├─ 实时来源：模拟环境读 examples/.../live_sources.json（标注模拟）
  ├─ LLM（DeepSeek，JSON 模式）：系统提示 = 对应 SKILL.md + phrasing.md + 证据包
  ├─ render_response.validate() 失败 → 把错误回喂模型重写，最多 2 次
  └─ 返回 render() 的 stdout 原文 + trace（路由、工具、校验次数）
```

### 4.2 模型提供方

- `deepseek`：真实 API，读 `DEEPSEEK_API_KEY` 或钥匙串 `xiaogu-deepseek`。
- `mock`：无 key 时的确定性替身，直接用工具结果拼 response，用于离线演示和测试；界面明确显示「模拟模型」。

### 4.3 不做

- 不接真实牛客/脉脉抓取（等 Codex Q2–Q4）；不做账号、持久化数据库、部署上线；不做简历文件解析。

## 5. 2026-10-05 调整（用户指示）

- 默认模型改为 `deepseek-v4-pro`（V4-Pro-0813），`XIAOGU_MODEL=deepseek-flash` 可切回。实测：JSON 模式 + thinking disabled 单次调用 0.8 s；两条完整对话一次通过校验，2.0 s / 3.2 s。成本约 Flash 3.96 倍（Codex W3），质量对比尚未做。
- 前端去掉阶段列表，改为单行状态「正在处理 · 阶段名 · N 秒」，只反映程序在哪一步；回答收到校验后完整文本再逐字显示（约 60 字/秒，长文最多约 6 秒）。不流式显示模型原始输出，因为未校验内容不能上屏。
