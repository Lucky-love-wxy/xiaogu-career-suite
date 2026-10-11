# 小谷上线版（app.py）

`app.py` 是给真实用户用的服务：账号（邀请码 + 验证码）、额度（注册送 500 credits，1 credit = ¥0.01）、按每次模型调用计费、四层停止开关、埋点、后台看板 `/admin`。`server.py` 保留为本机模拟环境，两者共用 `agent.py`。

```bash
cd /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch && XIAOGU_ENV=dev XIAOGU_PROVIDER=deepseek XIAOGU_BASE_URL=https://new.tornadorouter.com/v1 XIAOGU_KEYCHAIN=xiaogu-relay XIAOGU_ADMIN_TOKEN=dev-admin .venv/bin/python web/app.py --port 8781
```

依赖：`web/requirements.txt`（运行）、`web/requirements-dev.txt`（测试）。环境变量见 `deploy/env.example`，上线步骤见 `deploy/RUNBOOK.md`，设计见 `notes/2026-10-05-launch-platform-design.md`。

---

# 小谷 Web Agent · 模拟环境

服务端执行小谷 harness，DeepSeek 只负责在证据范围内写措辞。设计见 `notes/2026-10-03-web-agent-sim.md`。

```bash
python3 /Users/lucky_wang/Documents/codex/xiaogu-career-suite/web/server.py --port 8780
```

打开 http://127.0.0.1:8780 。只监听本机。本机 8765、8770 已被其他服务占用。

- 模型：默认读取钥匙串 `xiaogu-deepseek` 或环境变量 `DEEPSEEK_API_KEY`，用 `deepseek-v4-pro`（2026-10-05 起默认；`XIAOGU_MODEL=deepseek-flash` 可切回，Pro 单价约 Flash 3.96 倍、账号并发 500）；都没有时自动用离线模拟模型，界面会标明。`--provider mock` 强制离线。
- 从业者来源：当前全部来自 `examples/algorithm-engineer-mock/live_sources.json` 的模拟帖子，只对推荐算法/算法工程师岗位返回；界面左上可切换来源状态。
- 运行记录面板显示路由、本地检索、来源状态和每次校验结果。
- 本地运行日志：每轮一行写入 `web/logs/trace-日期.jsonl`（用户原话、路由、意图、模型原始输出、最终回答、已知信息表）。只在本机，已加入 .gitignore；不含 key 和系统提示词。

## 保证了什么

| 以前靠提示词 | 现在由代码保证 |
|---|---|
| 是否按路由走、缺材料先问 | `route_request.route()` 在服务端执行；缺材料直接返回一个问题，不调模型 |
| 最终回答逐字等于渲染器输出 | 服务端只返回 `render_response.render()` 的结果 |
| 跨轮沿用 JD / 经历 / 逐字稿 | 会话对象保存材料，生成路由 context |
| 不编引文和链接 | 模型只能给证据编号，正文与链接由服务端回填；未知编号、文本里带网址都判错重写 |
| 校验失败怎么办 | 最多重写 3 次，仍失败返回“受阻”，不静默换成模拟回答 |

## 简历美化 / JD 定制 / 模拟面试（2026-10-05）

设计见 `notes/2026-10-05-resume-interview-modules.md`，按各方向 star 最高的开源项目取机制（署名见 `THIRD_PARTY_NOTICES.md`）。

- 简历美化：贴整份简历（有栏目标题）且会话里没有招聘说明 → 结构化 + 轻度润色 + 单栏排版，回答下方出现“打开排版好的简历”按钮，页面可打印 / 存 PDF。代码在 `resume_tools.py`。
- JD 定制改写：会话里已有招聘说明时贴简历或说“按这个岗位改简历” → 抽 JD 关键词（只留原文里有的词）→ 改前 / 改后覆盖率（代码算）→ 只在已有证据处换说法。找不到依据的要求和新对上的词都列进“仍需确认”。只有零散经历、没有整份简历时仍走原来的要点生成。
- 两者的真实性检查：不许新数字（日期除外）、新英文技能名、“主导 / 负责人”这类拔高说法；学校、公司、项目名、角色必须在原文出现过；电话、邮箱直接取原文。不通过就带错误重写，最多 3 次。
- 模拟面试（题库模式）：说“模拟面试”开始，5 道题（基础 2 / 进阶 2 / 深入 1），每题固定追问 1 次；“跳过”换题、“结束”打分；“不知道 / 不会”记 0 分不追问。答题过程不调模型，即时响应。四项分由模型给，加权总分由代码算。练完的问答写进会话，可直接说“复盘这场面试”。代码在 `interview.py`。

### 模拟面试接口（给以后的语音前端）

和网页聊天走同一个状态机。语音端只负责：把用户的话转成文字传 `text`，把返回的 `say` 读出来。

| 请求 | 说明 |
|---|---|
| `POST /api/interview/start` `{"session_id": 可选, "role": 可选岗位名}` | 开始；会话里已有招聘说明 / 简历时会据此出题。没有任何材料且没给 role 时返回追问（`status: needs_input`），可直接用 answer 回答岗位名。已有进行中的面试时返回 409（用 answer 继续，或 answer 传“结束”） |
| `POST /api/interview/answer` `{"session_id", "text"}` | 提交一句回答；返回下一句 `say`。没有进行中的面试返回 409 |
| `GET /api/interview/state?session_id=` | 当前第几题、主问题还是追问、当前问题文本 |

返回体：`{"session_id", "say": 可朗读纯文本, "status", "practice": {"active", "question", "total", "stage"}}`。`practice.active` 变成 false 即面试结束，此时 `say` 是打分结果。

## 未做

真实牛客/脉脉抓取、账号与持久化（简历成品页只存在内存里，重启服务就没了）、部署、简历文件上传（PDF/Word 解析）、语音前端本身、成品页“读回解析”自检（用解析器把成品读回来确认字段都识别对，调研文档 1.5 节建议的做法）。`scripts/package.py` 不打包本目录。
