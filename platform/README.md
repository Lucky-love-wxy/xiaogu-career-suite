# 小谷上线平台（platform/）

和小谷 agent 核心（`../web/`）分开放的平台层（2026-10-14 起）：账号（邀请码 + 验证码，阿里云短信）、额度、按每次模型调用计费、停止开关、埋点、后台看板 `/admin`、用户记忆文档和基本情况卡片的存储、截图识别、页面（`static/`）和部署脚本（`deploy/`）。平台通过 `import agent` 调用核心，核心不依赖平台。

| 文件 | 作用 |
|---|---|
| app.py | FastAPI 服务入口：页面、全部 /api 接口、上线检查（生产配置不满足就拒绝启动） |
| store.py | SQLite：用户、邀请码、额度账本、会话、卡片、记忆、计量、后台看板 |
| auth.py | 登录：验证码发送器（控制台 / 阿里云短信） |
| ocr.py | 截图识别（RapidOCR，用完即退的子进程） |
| static/ | 用户端、登录、后台、协议页面 |
| deploy/ | 部署脚本、systemd、nginx、环境变量示例、上线手册 RUNBOOK.md |

# 小谷上线版（app.py）

`app.py` 是给真实用户用的服务：账号（邀请码 + 验证码）、额度（注册送 100 credits；1 credit = 后台实际消耗 ¥0.02，按实际消耗扣到 0.01 credit，界面显示两位小数）、按每次模型调用计费、四层停止开关、埋点、后台看板 `/admin`。`server.py` 保留为本机模拟环境，两者共用 `agent.py`。

```bash
cd /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch && XIAOGU_ENV=dev XIAOGU_PROVIDER=deepseek XIAOGU_MODEL=deepseek-flash XIAOGU_ADMIN_TOKEN=dev-admin .venv/bin/python platform/app.py --port 8781
```

依赖：`platform/requirements.txt`（运行）、`platform/requirements-dev.txt`（测试）。环境变量见 `platform/deploy/env.example`，上线步骤见 `platform/deploy/RUNBOOK.md`，设计见 `notes/2026-10-05-launch-platform-design.md`。

---

# 小谷 Web Agent · 模拟环境

服务端执行小谷 harness，DeepSeek 只负责在证据范围内写措辞。设计见 `notes/2026-10-03-web-agent-sim.md`。

```bash
python3 /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/web/server.py --port 8780
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

## 截图识别（2026-10-13）

`POST /api/ocr` `{"image": "base64 或 data:image/...;base64,..."}` → `{"text"}`。要登录，不扣额度；只收 PNG / JPG / WebP，单张 ≤ 6MB。引擎 RapidOCR（`platform/ocr.py`，模型随 pip 包自带，不联网）。每张图在一个用完即退的子进程里识别（峰值约 650MB，退出即还；常驻会只涨不退），同一时间只跑一个，每张约 1.2 秒。图片不落盘、不写日志；识别结果只回填输入框，用户核对后自己发送，所以下游流程不区分文字是粘贴的还是识别的。前端入口：「+」菜单「从截图识别文字」、输入框粘贴图片、拖进输入框；一次最多 6 张，按顺序拼接。设计见 `notes/2026-10-13-图片识别.md`。

## 基本情况卡片（2026-10-14）

`GET /api/me/profile` → `{profile, fields, required, done_message}`：字段、可选值、必填项都由服务端给，前端不写死第二份。`POST /api/me/profile` `{"profile": {...}}` 保存（只收 `agent.CARD_FIELDS` 里的字段和可选值；必填项缺了返回 400）；提交空对象即清空（删行）。卡片存在 `user_profile` 表，每轮由 `Platform.run` 现读后传给 `agent.handle(card=...)`，放在请求上下文里，不写进会话状态。回答里带 `action: "profile_card"` 时，前端在回答下放「填写基本情况」按钮。设计见 `notes/2026-10-14-基本情况卡片与对话标注修复.md`。

## 简历表单（R1，beta，2026-10-17）

`GET /api/me/resume` → `{form, questions, kinds, basics, education, head, limits, card_experience, done_message}`：六问的编号和文字、各栏上限由服务端给（`web/resume_tools.py` 的 `FORM_*`）。`POST /api/me/resume` `{"form": {...}}` 保存，经 `rt.clean_form` 清洗；没有任何一段写了「具体怎么做」返回 400；提交空对象即清空（删行）。表单存在 `user_resume` 表，每轮由 `Platform.run` 现读后传给 `agent.handle(resume_form=...)`，不写进会话状态。入口在「+」菜单，跟后台开关 `task.polish` 走（`/api/meta` 的 `tasks.polish`），关时不显示；表单提交后前端发 `done_message`，由规则直接路由到美化，模型只写每段要点、按段检查。设计见 `notes/2026-10-16-简历lab.md`。

## 用户记忆文档与上下文压缩（2026-10-14）

每个用户一份记忆文档（`user_memory` 表），跨对话记住三类：聊天里说过的情况和偏好（新说法覆盖时旧值留在 previous）、给过的每一批方向（代码在出候选时记）、用户的反馈和行动（选了哪个方向、贴过的 JD 由代码记；“不喜欢”“投了没回音”等来自模型输出的可选 `feedback` 字段，类别固定）。平台层每轮读出、传给 `agent.handle(memory=...)` 原地追加、结束后存回；和卡片一样不进会话状态。提示词只放当前情况、最近 3 批方向和各自之后的反馈、更早的摘要。不给用户看、不做删除界面；用户要求删除时后台调 `Store.delete_memory`。用户开到第 10、20……个对话时，新对话第一轮末尾提醒一次；用户回复「清理记忆」由代码压缩（留最近 3 批，更早的合成摘要，旧对话不删），不调模型不扣费。

一个对话满 12 轮时，把最早 6 轮压成不超过 300 字的要点（模型压缩，失败则用户原话拼接），只留最近 6 轮原文。每条消息最多 2000 字。设计见 `notes/2026-10-14-用户记忆文档.md`。

## 未做

真实牛客/脉脉抓取、账号与持久化（简历成品页只存在内存里，重启服务就没了）、部署、简历文件上传（PDF/Word 解析）、语音前端本身、成品页“读回解析”自检（用解析器把成品读回来确认字段都识别对，调研文档 1.5 节建议的做法）。`scripts/package.py` 不打包本目录。
