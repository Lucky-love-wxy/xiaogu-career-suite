# Glassdoor 职位 × 简历匹配机制拆解（试探性获取）

## 元数据

- 日期：2026-10-12
- 任务名：Glassdoor 职位与简历如何匹配（学习用，后续可能用 Rust 重写同构匹配器）
- 所属项目：学习 / 参考小谷「看懂岗位 → 按 JD 改简历」主流程
- 触发类型：设计（调研阶段，尚未进入匹配器设计）
- 关联 Principle：暂停编号（见全局 CLAUDE.md 暂停项）

## 0. 前提校正

- 匹配算法在服务器端执行，浏览器里只能看到前端代码和接口返回的结果字段，看不到算法本身。「逆向」最多能拿到输入输出，原理只能靠公开资料推断。
- Glassdoor 现在就是 Indeed：2025-07 Recruit 宣布并入，2025-11 起新用户必须用 Indeed 账号登录，2026-07-01 Glassdoor LLC 法律上并入 Indeed, Inc.，适用 Indeed 的服务条款和隐私政策。所以第一手原理资料应当看 Indeed，驱动匹配的简历大概率是 Indeed Profile 上那份。
- 服务条款：DevTools 里看自己账号的请求可以；用脚本重放私有接口、批量抓取不做。

## 1. 三层获取状态

| 层 | 内容 | 状态 |
|---|---|---|
| L1 一手观察 | 登录态职位页的网络请求：简历解析字段、匹配信号 | 未拿到。Chrome 扩展未连接；内置浏览器无登录态，且被 Cloudflare「Humans only」拦截（不绕） |
| L2 公开资料 | Indeed 官方对匹配流水线的描述 | 已拿到，见第 2 节 |
| L3 同构实现 | 用 Rust 写最小匹配器 | 未开始。本机没有 Rust 工具链；L1 的输入输出样例还没拿到 |

## 2. 市场调研 / 公开资料（按可信度分级）

### 2.1 Indeed 官方（一手，但来自新闻稿，没有实现细节）

来源：Indeed 新闻稿《How Indeed job matching works》

三段式流水线：
1. Understanding（建表示）
   - 求职者：技能、经验、偏好，加上搜索、投递等行为；通过 Indeed Profile 和 Career Scout（AI 职业教练）收集
   - 职位：要求、技能、资质、地点，以及隐含属性（如「team leadership」「remote work」）
   - 统一分类体系：900 个职业（覆盖数千个职位名称），10,000 多个属性（技能 / 执照 / 工作环境 / 排班 / 福利 / 薪资）。能区分上下文，例如儿科护理和急症护理、白班和夜班
   - 资质字段：技能、证书、执照、学位、专业
   - 偏好字段：职位名称、公司、薪资、地点、远程类型、雇佣类型、排班、行业
2. Finding the fit（匹配）
   - 先过硬过滤：缺必需执照、只接受远程但职位要求全职坐班 → 直接剔除
   - 再排序：用点击、收藏、忽略等行为数据预测最合适的职位
   - 雇主侧：Matched Candidates 先按 must-have 条件筛 3.5 亿多份可检索档案，再优先展示活跃候选人
3. Feedback loop（双边反馈）
   - 投递、进入面试、被忽略、录用都作为信号回流；重训频率和方法未披露

未披露：是否用向量（embedding）、排序模型架构、训练目标，以及怎么从简历里抽取资质。

### 2.2 Indeed 官方：匹配解释（the「why」）

来源：Indeed《How Indeed uses AI to provide better matching context》；OpenAI 客户案例页

- Invite to Apply 的输入：简历、Indeed Profile、其他资质
- 原先的模型只给简短解释，现在用微调过的 GPT 生成「为什么你的背景 / 过往经验适合这个职位」，和 Indeed 自有的匹配模型及市场数据结合
- few-shot 太费 token，微调小模型后 token 减少 60%；用 GPT-4 做数据增强，人工标注建立评测基准
- A/B 测试结果（自报）：开始投递数 +20%，面试和录用 +13%；消息量从每天 100 万涨到 2000 万
- 结论：解释层和匹配层是分开的。先由匹配模型决定推荐哪些职位，再由 LLM 生成理由

### 2.3 历史资料（2016，已过时，只看演进）

来源：Indeed 工程博客《Building a Large-Scale ML Pipeline for Job Recommendations》

- 当时主要靠点击流做协同过滤，没有用简历内容：先用 Mahout 做 user-user，太慢；后来改成 MinHash 近似计算用户点击集合的 Jaccard 相似度，相似用户互相推荐职位
- 离线（Hadoop，每天跑）和在线（memcache 存当天点击，增量更新签名）两套结合
- 推荐带来的点击占比从 3% 涨到 14%

### 2.4 第三方 / 推测（不是 Indeed 的资料，只作通用做法参考）

- 面试题指南：召回（倒排索引）→ learning-to-rank 排序（特征：文本相关性、新鲜度、距离、薪资匹配），评价指标是 apply-through rate；简历和职位嵌入同一向量空间，用 HNSW 召回近邻。这是二手资料，不能当作 Indeed 线上架构
- CareerBERT（arXiv 2503.02056）：简历和 ESCO 职业映射到同一个嵌入空间，学术工作
- arXiv 2107.00221：大规模职位-候选人嵌入两阶段推荐，来自 CareerBuilder，不是 Indeed

## 2.5 L1 一手观察（职位侧，未登录，Playwright，2026-10-12 16:24–16:27）

Playwright 用自己独立的 Chromium profile（/Users/lucky_wang/Library/Caches/ms-playwright-mcp/mcp-chrome-89368e8），和用户的 Chrome 不是同一个。Cloudflare 验证等几秒后自动放行。只读取了页面已有的缓存 `window.appCache` 和页面自己发出的请求，一共看了 1 个搜索结果页和 1 个职位详情页。原始数据：/Users/lucky_wang/Documents/codex/outputs/glassdoor_match_20261012/observations/jobs-side-unauth.json（只有公开职位数据）。

职位侧（实测）：
- 每个职位都挂着 Indeed 的分类体系：`header.indeedJobAttribute.extractedJobAttributes` 有 35–97 个属性，每个属性是 5 位 ID 加名称（如 `FGY89`=SQL、`X62BT`=Python、`8G9AU`=Bachelor's degree in statistics、`Y4JG9`=Entry level、`EY33Q`=Health insurance）。技能、学历、福利、级别都在同一张属性表里，和官方说的「10,000+ 属性」对得上。
- `indeedJobAttribute.skills` 是其中的技能子集（10–14 个 ID）。详情页还有 `skillsLabel`、`education`/`educationLabel`（如 Bachelor's degree）、`yearsOfExperienceLabel`（如 "2"）。
- 两套职业编码同时存在：`occupations`（Indeed 的 5 位职业 ID，每个职位 3 个）和 `goc`/`gocId`（Glassdoor 职业码，如 "data analyst" 100116）、`normalizedJobTitle`。
- JD 原文在 `job.descriptionFragmentsText`。页面上的「Minimum Qualifications / Preferred Qualifications」只存在于 JD 原文里，结构化字段里没看到必需和加分的区分。

用户侧（只看到空位）：
- 详情页有 `jobDetailsData.profileAttributes`，未登录时是 `[]`。推测登录后这里放的是你的简历被解析成的同一套属性 ID，匹配 = 职位属性 ID 和你的属性 ID 求交集（推测，需要登录态验证）。
- 全局缓存里有 `resumeStatus.hasResume`、`isLoggedIn`，未登录时分别是 false 和 false。
- 详情页按钮：「Is my resume a good match?」（说明文字：Use AI to find out how well the skills on your resume fit this job description）和「Tailor my resume NEW」。这是 Glassdoor 自己做的「AI 判断匹配度 + 按 JD 改简历」，和小谷主流程直接重合，是最该研究的竞品功能。

反馈回路（实测）：搜索页向 `/graph` 发 `trackEvents` mutation，事件类型 `JOB_SEEN`（曝光）带 `jobTrackingKeys`，另有 `JAVASCRIPT_DETECTION`。这就是官方说的点击、忽略等行为信号在前端的入口。

## 2.6 开源里接近这套设计的项目（2026-10-12 用 gh API / HF API 拉取，星数为当日值）

对照的骨架（来自 2.1 和 2.5）：JD → 属性 ID ｜ 简历 → 同一套属性 ID ｜ 硬过滤 ｜ 打分排序 ｜ 匹配 / 缺口解释 ｜ 行为反馈。

### 最接近的一整套：Tabiya（MIT，非营利，面向发展中国家青年就业）

三个仓库拼起来，和 Glassdoor / Indeed 的结构几乎一一对应：

| Glassdoor / Indeed（实测或官方） | Tabiya 对应仓库 | 说明（来自 README 和源码） |
|---|---|---|
| `extractedJobAttributes`（JD → 5 位属性 ID） | tabiya-tech/tabiya-livelihoods-classifier（★7，Python，2026-10-08 仍在更新） | 实体链接：从 JD 里抽出职业、技能、资质、经验、领域五类实体，再用向量检索链接到 ESCO 条目。两步：抽取 → 相似度检索 |
| `profileAttributes`（简历 → 同一套 ID） | tabiya-tech/compass（★14，Python） | 用 AI 聊天问出求职者的经历，包括非正式工作，填进一个「技能钱包」。面向没有正式简历的人，和小谷的大学生用户很像 |
| 硬过滤 + 排序 + 缺口 | tabiya-tech/matching-engine（★0，FastAPI + React，2026-10-12 当天还在推送） | `S_total = U_hat × P_hat`。U_hat 是技能和偏好带来的效用；P_hat 是成功概率，由 gate（门槛）、essential fit（必需技能满足度）、readiness、市场机会组成。输出三样：推荐职位、推荐职业、技能缺口建议 |
| 分类体系 | tabiya-tech/taxonomy-model-application（★20）、tabiya-open-dataset | 基于 ESCO（13,896 个技能），可以本地化，多语言共用同一套 ID |

源码里值得学的细节（`backend/app/services/cosine_similarity/skill_score.py`）：
- 职位技能分 `essential_skills` 和 `optional_skills`，必需和加分是分开存的。Glassdoor 的结构化字段里没看到这个区分（见 2.5）。
- 技能先按名称解析到统一 ID，再查每个 ID 的向量，用余弦相似度做软匹配，而不是 ID 精确求交集。这样「Pandas」和「Python 数据分析」能部分匹配上。这一点修正了第 3 节「匹配 = ID 求交集」的推测：精确交集太脆，实际系统大概率是软匹配（Indeed 怎么做未知）。
- 有两条召回路线：`/match` 走完整打分；`/match_v2` 用 BM25 × 向量余弦融合排序，再接一个 cross-encoder 重排。
- 用 Langfuse 记录每个阶段：retrieval → embedding → shortlist → rerank → preference_scoring → skill_gaps。阶段名本身就是一份流水线说明。

### 分环节的替代件

| 环节 | 项目 | 状态 | 用处 |
|---|---|---|---|
| JD / 简历 → 标准技能 | nestauk/ojd_daps_skills（★162，MIT，2025-06 后没再更新） | 稳定但不活跃 | 从招聘文本抽技能短语，映射到 ESCO 或 Lightcast Open Skills，也可以换成自己的 toy 分类表。适合拿来理解「抽取 → 映射」两步 |
| 同上 | AnasAito/SkillNER（★214，MIT，2024-01 后停更） | 停更 | 基于规则加词表的技能抽取，代码短，适合入门读 |
| 同上 | KonstantinosPetrakis/esco-skill-extractor（★32，MIT） | 小项目 | 从 JD 或简历抽 ESCO 技能和 ISCO 职业，接口最简单 |
| 职位名 / 技能向量 | TechWolf/JobBERT-v2（Hugging Face，MIT，月下载约 3 万） | 活跃 | 把职位名映射到向量空间，用来做职位名归一（对应 Glassdoor 的 `normalizedJobTitle`） |
| 同上 | TechWolf/ConTeXT-Skill-Extraction-base（HF） | 活跃 | 从句子里抽技能，并和技能分类表做相似度匹配 |
| 简历 → 职业的嵌入匹配 | julianrosenberger/careerbert（★16，论文代码） | 学术 | 简历和 ESCO 职业放进同一个向量空间（两塔思路） |
| 人岗匹配模型合集 | RUCAIBox/RecBole-PJF（★73，人大，2024-03 后停更） | 学术，停更 | 实现了 PJFNN、BPJFNN、APJFNN（招聘场景的能力感知匹配）、BERT 双塔、IPJF（可解释人岗匹配）、SHPJF（结合搜索历史）。有几篇论文的数据来自国内招聘平台。想看「行为信号怎么进模型」就读这个 |
| 通用推荐 / 排序 | recommenders-team/recommenders（★21.9k，MIT，微软出身） | 活跃 | 双塔、learning-to-rank 等通用推荐算法的 notebook 教程 |
| 改简历 / 解释层（LLM） | srbhr/Resume-Matcher（★28.6k）、career-ops-hq/career-ops（★74k） | 活跃 | 已在 /Users/lucky_wang/Documents/Claude/notes/2026-10-12-小谷-开源案例借鉴点.md 拆过，这里不重复。它们对应 Glassdoor 的「Tailor my resume」，而不是底层的属性匹配 |

### 如果用 Rust 写（检索层可以直接用现成的 Rust 项目）

| 项目 | 星数 | 对应环节 |
|---|---|---|
| quickwit-oss/tantivy | ★16.2k，MIT | 全文检索库（Rust 版 Lucene）：BM25 召回 |
| qdrant/qdrant | ★35k，Apache-2.0 | 向量数据库：技能 / 职位向量召回，能带过滤条件（等于把硬过滤和向量召回一起做） |
| meilisearch/meilisearch | ★59.5k | 搜索引擎，支持关键词和向量混合搜索 |

GitHub 上没找到用 Rust 写的完整简历匹配项目（搜 `resume job matching language:Rust` 结果为 0）。Rust 版的价值在于自己把 Tabiya 的打分逻辑用 Rust 重写一遍，检索层直接接 tantivy / qdrant。

### 和小谷职业树 + 技能树的对应（2026-10-12 补）

小谷的设计（/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/docs/research/occupation-skill-taxonomy-2026-10.md）：ISCO 大类 → ISCO 4 位职业 → ESCO 职业 URI 加中国细分；技能用 ESCO 的 13,939 个技能，职业和技能之间有 essential/optional 关系。这和 Tabiya 的骨架相同：Tabiya 也是 ESCO，13,896 个技能，必需和加分分开。

小谷 10-08 那轮卡在三处，Tabiya 都有现成的对应件：

| 小谷卡住的地方 | Tabiya 对应件 | 能不能直接用 |
|---|---|---|
| 195 个本地节点映射到 ESCO，候选都出来了，人工认可数是 0 | tabiya-tech/tabiya-esco-localization（★0，2026-05）：把国家职业分类映射到 ESCO，流程是向量匹配 → LLM 校验 → 人工复核，Kenya 有完整示例 | 流程可以照搬；它用 Gemini 向量和 Supabase，换成自己的模型要改代码 |
| 中文 JD 抽技能并挂到 ESCO | tabiya-livelihoods-classifier：抽取加链接两步 | 目前只登记了英语和西班牙语，没有中文。中文要自己训练或换成 LLM 抽取 |
| 没有中文技能名（ESCO 没有官方中文） | 没有现成方案 | 小谷已有 395 个试点技能的建议译名，仍然只能自己审 |

结论：这个设计能实现，开源有现成参照。真正的工作量在中文这一层（大典对齐、中文技能名、中文 JD 抽取），匹配和打分部分有代码可以抄。

### 没找到的

- Indeed 自己的开源（GitHub 组织 indeedeng）里没有匹配、排序相关的仓库，只有 A/B 测试框架 proctor、工作流引擎 iwf 之类的基础设施。
- 名字里带「resume / job matching / skill gap」的小仓库很多（★1–3），大多是课程作业，没有收进来。

## 3. 推断出的匹配骨架（L3 重写的蓝本，状态：推测）

```
简历/档案 ──解析──> 结构化资质(技能/证书/学位/年限) + 偏好
职位 JD  ──解析──> 要求(必需/加分) + 隐含属性
          │
          ▼ 归一化到统一分类体系(职业 × 属性)
硬过滤：必需执照/证书缺失、远程/地点/雇佣类型冲突 → 剔除
          │
          ▼
打分排序：资质重合度 + 文本/语义相似度 + 行为信号(点击/收藏/忽略/投递)
          │
          ▼
解释：列出匹配上的技能和资质，LLM 生成「为什么适合你」
          │
          ▼
反馈：投递/面试/录用/忽略 → 回到排序模型
```

对小谷有用的一点：用户能看到的「匹配度」主要由「分类体系归一化 + 硬过滤 + 资质重合」决定，行为信号只影响排序。所以「按 JD 改简历」的杠杆在于让简历里的技能、证书用词能对齐到 JD 的分类体系（推测，有待 L1 验证）。

## 4. 待办（阻塞项）

- [ ] L1：用户在哪个浏览器登录；Chrome 扩展连上后，打开 3 个职位详情页，只读网络请求（graphql / api / job），原始 JSON 存到 scratchpad
- [ ] 确认 Indeed Profile 上已上传简历，否则不会出现匹配信号
- [ ] L3 技术栈：学 Rust 还是复用小谷现有技术栈；如果用 Rust，需要用户同意安装 rustup
- [x] 深度调研、L1 观察、Rust 实现已写成 Codex brief：/Users/lucky_wang/Documents/Claude/notes/2026-10-12-glassdoor职位简历匹配-codex-brief.md
- 2026-10-12 补充：Playwright（独立浏览器，无登录态）访问 glassdoor.com 返回 HTTP 403 Cloudflare 拦截，结论和内置浏览器相同。L1 只能用用户自己登录的 Chrome（CDP 或 Claude in Chrome 扩展）
- 2026-10-12 前提更正：用户说的「Rust 逆向 Adobe」出处是 @echelon 2026-10-03 推文，内容是用 Rust vibe code 了 Adobe 7 个应用的开源替代品（ArtCraft），属于从零重写，不是逆向
