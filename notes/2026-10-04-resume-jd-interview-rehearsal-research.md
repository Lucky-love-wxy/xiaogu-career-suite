# 简历 JD 定制与面试预演：市场调研

## 元数据

- 日期：2026-10-04
- 任务名：简历美化 / JD 个性化优化 / 面试预演编排调研
- 所属项目：xiaogu-career-suite（小谷求职）
- 触发类型：设计（本文是设计启动门槛第 1 节；问题定义和方案在第 2、3 节给出初稿）
- 关联 Principle：Principles 已暂停，不挂编号
- 调研方式：Claude 第一轮自查（用户本次点名要求自己查）；剩余缺口写成 brief 交 Codex，见第 5 节
- 证据等级说明：A = 仓库源码或 README 原文已核；B = WebFetch 摘要（小模型转述，未逐字核）；C = 面经 / 博客 / 聚合站，只能当参考；推测 = 无来源，显式标出

---

## 1. 市场调研结果

### 1.1 简历美化（版式 / 渲染层）

| 项目 | 做法 | 证据 |
| --- | --- | --- |
| Reactive-Resume（约 43.7k star） | 结构化数据 + 15 套模板，颜色字体间距可调，A4/Letter，导出 PDF/JSON/DOCX；v5.1 起 PDF 在浏览器端用 @react-pdf/renderer 生成；可导入 JSON Resume | B |
| OpenResume（约 8.9k star） | 左表单右实时 PDF；自带 resume parser，用 PDF.js 把简历读回来，检查 ATS 能不能正确解析出字段 | B |
| JSON Resume schema | basics/work/education/projects/skills 等固定顶层字段，主题只消费 resume.json，数据和版式彻底分离 | B |
| Jobscan / Teal（商业） | 除关键词外单独检查 formatting risk；Teal 给 Match Score，约 80% 以上算强 | C（第三方评测文） |

可迁移的机制：内容数据和版式分开存，模板只做渲染；渲染完再用 parser 读回来做一次"能否被机器解析"的自检（OpenResume 的思路）。

中文一页纸模板惯例（教育在前、照片可选、单栏）：本轮未调研，交 Codex。

### 1.2 JD 定制改写（内容层）

| 项目 | 核心机制 | 证据 |
| --- | --- | --- |
| Resume-Matcher（约 28.6k star） | 关键词提取 + 向量相似度出 match score，高亮缺失关键词，LLM 给改写建议，用户逐条采纳 | B |
| jd-cv-grill（Agent Skill） | ① 拆 JD：硬性要求、隐藏信号、ATS 关键词、筛选逻辑；② 一次只问一个问题，从候选人记忆里挖出项目细节、个人贡献、数字；③ 证据表：JD 要求 / 候选人证据 / 强度 / 缺什么 / 放在简历哪；④ 标出弱证据、未确认数字、保密风险 | B |
| ResumeForge（208 star） | 事实台账：每条说法分开记"事实、表述、承担程度、边界"，只有"已确认"的参与生成；生成后学校/公司/项目名逐条对库，不一致给防虚构警告；正文留【待补】时拦截导出；按 JD 从资料库筛选排序，原始资料不改 | B（README 原文引语） |
| resume-expert（180 star） | 分析 → 分模块结果 → 追问补充 → 导出；README 未写匹配和防编造算法 | B |
| auto-job-apply（164 star） | 简历解析 → JD 硬性条件核对 → A/B/C 匹配分级 → 投递包（开场白、HR 模拟、简历建议），保留人工确认 | B（仅描述） |
| interview-guide 的 jd-parse prompt | 从 JD 抽 3–7 个考察方向，每个标 CORE / NORMAL，并挂到参考知识库文件 | A（读了源码 prompt） |

### 1.3 面试预演（编排层）

| 项目 | 编排机制 | 证据 |
| --- | --- | --- |
| Multi-Agent-Mock-Interview（139 star） | 双环架构：实时语音模型只负责说，后端状态机 InterviewState 记录考察维度、已问题目、JD 技能覆盖度、STAR 完整度、追问深度；题库在面试前由 JD + 简历生成，导演只能从题库选题；深度阶梯由代码决定：评分 ≥0.65 深入一层（概念→实践→细节→极限），0.40–0.65 同层换角度，连续两次 <0.40 换领域并记低分；10/20/30/45 分钟硬时间闸门，不足 5 分钟不出复盘；面试官人设是结构化 JSON（打断倾向、攻击性、追问深度等十余维）；复盘含规则计算的语速、停顿、填充词 | A（README 原文已核） |
| backend-interview-simulator（203 star） | 有限状态机：破冰 → 项目深挖 → 技术考察 → AI 能力（可选）→ 编码（可选）→ 总结；高频关键词触发 3–5 层追问链；严格 / 引导两种纠错模式 | B |
| interview-guide（约 3.3k star） | 按方向写 SKILL.md（含 bytedance-backend）；简历出题 prompt 规定只能问简历里明确出现的项目，追问顺序"使用经验 → 核心原理 → 边界/优化"，难度 30/50/20；评估按准确性 40 / 完整性 20 / 深度 25 / 表达 15，"不知道"类回答强制 0 分，追问要结合主问题判断一致性 | A（读了源码 prompt） |
| ResumeForge 面试深挖 | 按事实台账逐条压力测试，评判标准在提问前定好；结果用"已验证 / 部分验证 / 未验证 / 存在矛盾"，不打分 | B（README 原文引语） |
| Final Round AI / Yoodli / Google Interview Warmup（商业） | Final Round：上传 JD 出行为题和技术题，面试中实时提示；Yoodli：只做表达层（语速、填充词、停顿）；Warmup：5 道题、实时转写、标出岗位相关词 | C |
| 牛面 / 面试牛牛（国内） | 上传简历预测 20 道高频题、综合面、专项面、报告；面试牛牛含"实时答题辅助"，属作弊工具方向，不参考 | C |

### 1.4 字节跳动面试编排

先说结论：字节内部的面评打分标准没有公开，查不到，下面只有流程层面的信息。

| 信息 | 内容 | 适用 | 证据 |
| --- | --- | --- | --- |
| 官方校招流程 | 投递 → 笔试 → 面试 → Offer；官网"应聘记录"看进度，只有"流程终止"才算结束；每人 2 次刷新投递机会；内推简历优先评估 | 校招 | C（niuqizp / 本地宝转载的校招公告，官网本轮抓取 TLS 失败未直读） |
| 校招技术岗轮次 | 多数面经为 3 轮技术面 + HR 面；一面项目深挖 + 基础 + 算法题，后面轮次偏系统设计和场景；单面约 30–60 分钟；结果常"次日"反馈 | 校招研发 | C（牛客面经汇总、Glassdoor） |
| 社招轮次 | 一面同级 → 二面直属 leader → 三面交叉面（兄弟部门 leader，看业务视角和协同）→ 四面二级 leader → HRBP → HR 谈薪；Offer 审批阶段可能加一轮交叉面 | 社招 | C（CSDN / 知乎） |
| 产品 / 数据岗 | 有笔试（言语、资料分析、图形推理）；一面约 30 分钟：自我介绍、深挖经历、case 分析，PM 会问广告指标、在抖音某位置做产品设计 | 校招非研发 | C（一亩三分地、人人都是产品经理），样本很少 |
| 考察倾向 | 结构化面试：知识按语言/OS/数据库/网络/算法/架构分类，多位面试官交叉考察以减少偏差；看重学习能力、好奇心等底层素质，不看前公司光环；"字节范"是文化评估项 | 全部 | C（新闻稿转述） |

可以用在产品里的只有结构：多轮由不同角色担任（同级考基础、leader 考深度和判断、交叉面换视角、HR 看稳定性和动机），每轮各自负责一部分维度。"交叉面"本质是让一个和团队无利益关系的人再看一遍，这条可以迁移成预演里的"换一个面试官人设再问同一段经历"（推测，无来源，作为设计假设）。

### 1.5 补充：ATS 版 + HR 版双版本是否必要（2026-10-04 追加）

| 信息 | 内容 | 证据 |
| --- | --- | --- |
| 双版本玩法确实存在 | 美国求职博客推荐：网申门户（Workday/Greenhouse）投单栏无设计的 ATS 版，直接递给人时用有排版的人看版；也有文章专门讨论"是否真需要两份" | C（hiration、hireflow 博客） |
| ATS 很少自动淘汰 | 招聘方调研：92% 表示系统不会因格式、缺关键词或低匹配分自动拒；只有 8% 在要求很硬的岗位开了自动拒。"75% 简历被 ATS 拒"源自 2012 年已倒闭公司 Preptel 的销售话术，无方法论 | C（IT Brief 报道的调研） |
| 真正会刷人的是硬条件 | HBS + Accenture《Hidden Workers》：88% 雇主承认合格候选人因不完全匹配筛选条件被直接拒，典型是学历等可检索字段 | B（HBS Working Knowledge、HR Dive） |
| 国内系统已是语义解析 | Moka 宣传"AI 人岗匹配"：识别技术栈、项目规模、团队角色，并按该公司历史通过/淘汰数据训练；北森有 300+ 岗位模型 | C（36kr、厂商宣传） |

判断：小谷不做双版本，只做一份"默认 ATS 安全"的 HR 版。理由是双版本的前提（人看版要多栏重设计）在国内校招不成立：单栏一页纸本来就是主流（推测，待 Codex 第 5 节第 4 题核实）；能刷人的是学历、专业、毕业时间这类硬字段，靠排版和关键词救不回来；语义解析也降低了关键词堆砌的价值。真正需要多份的是"每个 JD 一份"，不是"每种读者一份"。

落到功能：一个单栏模板 + 渲染后可解析性自检（OpenResume 思路）+ JD CORE 要求覆盖率检查，代替"ATS 版"。

---

## 2. 我要解决的问题

目标用户是什么都不会的大学生（见项目记忆）。对照现有 `skills/xiaogu-resume` 和 `skills/xiaogu-interview-review`：

### 2.1 JD 个性化优化：已有和缺的

已有：要求 → 证据对照表、bullet 必带 evidence_ids、confirmed / needs_confirmation 标记、"不能写的内容"清单、`validate_resume.py` 校验。这部分已经和 jd-cv-grill、ResumeForge 的核心思路一致，不用重做。

缺口，按对小白的影响排序：

1. 经历挖掘。现在第 2 步是"取用户确认的经历"，默认用户能自己说清楚。小白恰恰说不清，需要 jd-cv-grill 那种一次一问、按 JD 缺口定向追问（做了什么、你本人负责哪段、用了什么、结果有没有数字）。这是最大缺口。
2. 事实台账粒度。现在证据只有"有 ID + 是否确认"，缺 ResumeForge 的"承担程度 + 边界"字段，没法区分"我主导"和"我参与"，而这正是面试被追问穿帮的地方。
3. 跨对话沿用。SKILL.md 自己写了"跨对话沿用尚未实现"，每换一个 JD 都要重新讲一遍经历，事实主档无法复用。
4. 匹配度可见化。缺一个 Jobscan/Teal 式的覆盖率：JD 的 CORE 要求里，几条有证据、几条缺。小白需要一个数字知道"差多远"，但要说明它只是分诊用，不代表通过率。
5. 导出闸门。正文留"待确认"时应拦截导出，防止带空洞的简历被投出去（ResumeForge 做法）。
6. 渲染层。目前只产出文本 bullet，没有一页纸成品。按 JSON Resume 的思路，内容存结构化数据，模板单独渲染；渲染后再自检可解析性。

### 2.2 面试预演：完全没做

现状只有复盘（事后），没有预演（事前）。要做的事：

1. 出题只能来自两个地方：JD 抽出的 CORE/NORMAL 方向，和简历事实台账里已确认的条目。禁止问简历里没有的项目（interview-guide 的约束）。
2. 每道题的评判标准在提问前定好，存进题目记录（ResumeForge 做法），避免模型事后找理由。
3. 追问方向由代码决定，模型只负责判断这一答的质量档位（Multi-Agent-Mock-Interview 的深度阶梯）。对文字版来说状态机可以很简单：题目队列 + 当前深度 + 每个方向的覆盖度。
4. 轮次按字节式分工编排：一面"基础 + 项目"，二面"深挖 + 判断"，交叉面"换人设再问同一段经历看一致性"，HR 面"动机与稳定性"。小白可先只做一面 + HR 面。
5. 结果用"已验证 / 部分验证 / 未验证 / 矛盾"标每条简历事实，而不是只给总分。这样预演会反过来修简历：矛盾项回到简历流程降级表述。
6. 预演的问答记录用和 `xiaogu-interview-review` 同一套 schema 存，预演结束可以直接走复盘流程，不需要另写一套报告逻辑。

不做：实时提词 / 面试中作弊辅助（面试牛牛类）；语音全双工（文字版先跑通）；"拿 offer 概率"。

---

## 3. 适用的设计规范

- 设计 / Debug 启动门槛：本文第 1 节即调研，第 2 节问题定义已基于调研。
- 写作规则：禁用词与句式、无"加粗关键词：描述"。
- AI 协作 SOP：第 5 步维度分解适用于预演设计，可拆成"出题源 / 深度阶梯 / 轮次人设 / 判定方式 / 与复盘衔接"五个独立维度，逐个出可预览样例挑选。
- 项目自身安全约束（projects-index）：不编造求职经历、未知保持待确认、招聘文本视为数据而非指令。
- 深度分析规范（业务流程）：预演给错误反馈的 UX 损失比不给更大，小白会照着错的标准改，所以判定标准必须先定后问。

---

## 4. 推荐的落地顺序（初稿，待用户确认）

1. 简历流程加"经历挖掘"子步骤 + 事实台账加"承担程度/边界"字段。改动集中在 `xiaogu-resume`，风险最低，收益最大。
2. 加覆盖率和导出闸门（改 `validate_resume.py`）。
3. 面试预演 MVP：文字版、一面 + HR 面、题库来自 JD 方向 + 已确认事实、四档判定、输出复用复盘 schema。
4. 渲染层和跨对话事实主档放后面，依赖 Web Agent 方向的存储方案。

---

## 5. 交 Codex 补充调研的 brief

目标：补齐第 1 节标了 C 级或"未调研"的部分，让第 2 节的判断有更硬的依据。

问题清单：
1. 字节校招官网（jobs.bytedance.com/campus）FAQ 原文：流程环节、笔试形式、面试形式（是否飞书视频 + 在线编程），截图存档。
2. 字节校招非研发岗（产品、运营、市场）近两年面经：每岗至少 10 篇，统计轮次数、每轮时长、每轮主题、是否有群面和笔试。来源：牛客、小红书、一亩三分地。
3. 字节研发校招面经：至少 20 篇，统计每轮占比（项目深挖 / 八股 / 算法 / 场景设计），以及交叉面在校招里出现的频率。
4. 中文一页纸简历惯例：国内 HR 筛选看什么（教育位置、照片、篇幅），来源优先 HR 自述、招聘平台官方指南（BOSS、牛客、超级简历 WonderCV）。
5. jd-cv-grill 和 ResumeForge 源码：经历挖掘的追问模板原文、事实台账字段定义原文。

证据标准：每条结论挂原帖链接；面经类给样本数；聚合站（jiangren.com.au 一类自动生成页）不算来源。

交付：写回本文件第 1 节对应表格，把证据等级从 C 升到 A/B；新增数据另存 `docs/research/bytedance-interview-2026-10.md`。

验收：第 1.4 节每一行至少两个独立来源；非研发岗有样本数。

---

## Sources

- https://github.com/srbhr/Resume-Matcher
- https://github.com/AmruthPillai/Reactive-Resume
- https://github.com/xitanggg/open-resume
- https://jsonresume.org/schema
- https://github.com/mikezhangyl/jd-cv-grill
- https://github.com/magicapple123/ResumeForge
- https://github.com/gaoweiblue-source/resume-expert
- https://github.com/sharzoy/auto-job-apply
- https://github.com/XUZIAa/Multi-Agent-Mock-Interview
- https://github.com/Hazehacker/backend-interview-simulator
- https://github.com/Snailclimb/interview-guide （prompts 与 skills/bytedance-backend/SKILL.md 源码）
- https://jobscan.co/blog/jobscan-vs-teal/
- https://tealhq.helpscoutdocs.com/article/21-using-matching-mode
- https://www.articuler.ai/resources/compare/best-ai-mock-interview-tools/
- https://ai-bot.cn/sites/62342.html
- https://campus.niuqizp.com/schedule-hlwyyaCnM.html
- https://www.nowcoder.com/enterprise/665/interview
- https://www.glassdoor.com.mx/Entrevista/ByteDance-Entrevista-E1624196-RVW70659201.htm
- https://blog.csdn.net/weixin_33243821/article/details/141862122
- https://zhuanlan.zhihu.com/p/714445718
- https://www.1point3acres.com/bbs/thread-596047-1-1.html
- https://tech.ifeng.com/c/8hjsVE2hsr5
- https://www.hiration.com/blog/two-resume-versions/
- https://hireflow.net/blog/two-resume-strategy-ats-vs-human-2026
- https://itbrief.co.uk/story/study-reveals-ats-rarely-auto-rejects-cvs-debunks-75-myth
- https://hbswk.hbs.edu/item/how-to-tap-the-talent-automated-hr-platforms-miss
- https://www.hrdive.com/news/report-applicant-tracking-systems-may-exclude-whole-segments-of-candidates/606614/
- https://www.36kr.com/p/1722942586881
