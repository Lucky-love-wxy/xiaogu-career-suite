# Glassdoor / Indeed 职位 × 简历匹配机制拆解 + Rust 同构实现 brief（交 Codex 执行）

## 元数据
- 日期：2026-10-12
- 任务名：搞清 Glassdoor（现属 Indeed）怎么把职位和简历匹配起来，并用 Rust 写一个同构的最小匹配器供用户学习代码细节
- 所属项目：学习项目（参考小谷「看懂岗位 → 按 JD 改简历」主流程）
- 触发类型：调研 + 实现（Claude 写 brief，Codex 执行，Claude 审证据）
- 关联 Principle：暂停编号
- 交付落点：`/Users/lucky_wang/Documents/codex/outputs/glassdoor_match_20261012/`
  - `report.md`（主报告）
  - `sources.csv`（url, 标题, 作者/机构, 发布日期, 一手/二手/推测, 支撑哪条论断）
  - `observations/`（L1 登录态观察的脱敏原始 JSON 和截图）
  - `matcher/`（Rust crate，`cargo test` 能通过）

## 状态与交接（新会话先读这一节）

- 当前状态（2026-10-12）：brief 已定稿，等用户交给 Codex；Codex 尚未开始。
- 下一步谁做：
  1. 用户：把本文件路径交给 Codex，说「按这份 brief 执行，交付到元数据里的落点」。开始前确认 Chrome 已登录 Glassdoor / Indeed，且 Indeed Profile 上已上传简历；执行任务 B 时用户要在场，自己点两个 AI 按钮。
  2. Codex：先读第 5 节已有材料，按第 1–4 节执行，交付第 6 节的内容。
  3. Claude（交付后任一会话）：按第 7 节逐条验收，结论写进第 8 节回填区。
- 判断是否已交付：看 `/Users/lucky_wang/Documents/codex/outputs/glassdoor_match_20261012/report.md` 是否存在。

## 0. 先校正两个前提（报告开头要写清楚）

1. 匹配算法跑在服务器上。浏览器里只能看到前端代码和接口返回的结果字段，看不到算法本身。所以本任务的「逆向」= 观察输入输出 + 公开资料推断原理 + 自己重写一个同构实现，不是还原 Glassdoor 的真实代码。
2. 用户提到的「用 Rust 逆向 Adobe」，出处已确认：X 用户 @echelon 2026-10-03 的推文，原意是用 Rust「vibe code」了 Adobe 7 个应用的开源替代品（ArtCraft 团队的 PhotoCraft / VectorCraft / FilmCraft / LightCraft / PrintCraft / EffectCraft / DesignCraft）。这是照着 Adobe 产品的功能和交互从零重写，不是逆向 Adobe 的代码。本任务的任务 D 正好是同一种做法：照着 Glassdoor / Indeed 的可见行为和公开资料，从零写一个功能相似的匹配器。Rust 在两边都只是实现语言。

## 1. 任务 A：公开资料深挖（L2）

要回答的问题：
1. Indeed / Glassdoor 匹配流水线的每一段具体怎么做：简历和 JD 的解析与资质抽取、职业 × 属性分类体系（官方说 900 个职业、10,000+ 属性）怎么构建和归一化、硬过滤规则、排序模型（特征、目标、是否用 embedding / 两塔 / LLM）、反馈回路。
2. 用户在界面上看到的「匹配」信号是怎么生成的：Indeed 职位页上的 profile insights / 技能和资质对照（「你的档案匹配这些要求」类提示）、Glassdoor 职位页的对应功能、Invite to Apply 里 GPT 生成的「why」。
3. 2025-07 合并之后，Glassdoor 的职位推荐和匹配是否已经完全走 Indeed 的系统，有没有官方说法。

来源优先级：
1. 一手：Indeed 工程博客（engineering.indeedblog.com）、Indeed / Recruit 的论文（RecSys、KDD、SIGIR、WWW、arXiv，按作者单位筛）、Indeed / Recruit 的专利（Google Patents 搜 assignee）、Indeed 官方新闻稿和帮助中心、Indeed 技术人员的公开演讲。
2. 招聘信息：Indeed 的 ML / Ranking / Matching 岗位 JD，从中反推技术栈（标为「推断」）。
3. 第三方：面试题指南、行业分析。只能当线索，不能当结论。

去重：第 5 节笔记里已有的内容（三段式流水线、900/10,000、GPT 解释 +20%、2016 MinHash）不要重复展开，只补增量；若有新资料推翻已有说法，单列「修正项」。

## 2. 任务 B：登录态一手观察（L1）

前提：用户已在自己的 Chrome 登录 Glassdoor / Indeed，Indeed Profile 上有简历。浏览器操作走 web-access skill 的 CDP 入口（`node /Users/lucky_wang/.agents/skills/web-access/scripts/cdp.mjs ...`，命令写绝对路径、单条、不接管道，否则会退回审批）。Playwright 独立浏览器未登录时能过 Cloudflare，但拿不到用户侧数据，所以不要用它代替用户的 Chrome。

做法：
1. 一共只打开 6 个职位详情页：Glassdoor 3 个、Indeed 3 个。尽量选和用户简历相关的岗位，也挑 1 个明显不相关的作对照。
2. 只被动读取：页面自己发出的网络请求（重点看 graphql / api / job 相关）及响应体、`__NEXT_DATA__` / Apollo 缓存等页面已有状态、页面上的匹配提示文字。每页截一张图。
3. 职位侧已由 Claude 未登录实测（见第 5 节笔记 2.5 节：`indeedJobAttribute` 的 5 位属性 ID、`skills`/`skillsLabel`、`occupations`、`goc`、`JOB_SEEN` 埋点），不要重复，只补登录后多出来的东西。重点回答：
   - 登录后 `appCache.jobViewPage.jobDetailsData.profileAttributes`（未登录时是 `[]`）里放的是什么？是不是用户简历被解析成的同一套 5 位属性 ID？和职位的 `indeedJobAttribute.skills` 有没有交集或差集的字段？
   - 「Is my resume a good match?」和「Tailor my resume」两个按钮：点了之后发了什么请求、返回了什么结构（分数？命中 / 缺失技能？LLM 生成的文字？）。这两个按钮可能会上传或选择简历、把简历发给 Glassdoor 的 AI、自动保存改过的版本，所以由用户本人来点，弹出的上传、选择、保存提示也由用户处理；Codex 只记录网络请求和页面状态。如果按钮要求上传简历，Codex 停下来交给用户。
   - 相关和不相关岗位，以上返回有什么区别。
   - 搜索结果页登录后有没有个性化排序或匹配标签（比如「Your job matches」页）。

红线：
- 不自己构造请求去调它的接口，不批量翻页，不写抓取脚本。超过 6 个页面就停。
- 遇到 Cloudflare 或人机验证就停下交给用户，不绕。
- 不登出、不改账号设置、不投递、不改简历。
- 落盘前脱敏：姓名、电话、邮箱、住址、用户 ID、token、cookie 全部替换成占位符。observations 目录里不允许出现真实个人信息。

## 3. 任务 C：ArtCraft（Rust 重写 Adobe）作为参照

出处：@echelon 2026-10-03 推文，ArtCraft 官网有「Crafting Apps / Seven apps. One craft.」页面和 GitHub 仓库链接。Codex 找到 GitHub 仓库后说清楚：
1. 它是怎么「重写」的：参照了 Adobe 的什么（功能清单、界面、快捷键、文件格式），有没有读 Adobe 的代码。以仓库 README / 作者说明为准，没写就标「未说明」。
2. 它的仓库结构、模块划分（挑一个应用，比如 PhotoCraft）。任务 D 的 crate 结构可以参考它的 Rust 工程组织方式。
3. 文件格式兼容（如 PSD 读写）如果有，是基于公开规范还是逆向。这一点只说明原理，不展开。

这一节控制在半页以内，目的是让用户分清「重写」和「逆向」，不展开成 ArtCraft 测评。

## 4. 任务 D：Rust 同构匹配器（L3）

环境：本机目前没装 Rust。用户已同意用 Rust，Codex 用官方 rustup（https://rustup.rs）装到用户目录，不用 sudo，不改系统级配置。装之前在报告里写一句安装方式和占用空间。

要求：
1. 按第 1 节查到的流水线拆模块，每个模块一个文件：
   - `parse`：简历和 JD 文本 → 结构化资质（技能 / 证书 / 学位 / 年限 / 偏好）。先用规则加词典，不调外部 API
   - `taxonomy`：同义词、别名归一到标准技能 ID（小型词表即可，比如 30–50 个技能，参考 ESCO / O*NET 的结构）
   - `filter`：硬过滤（必需证书缺失、远程 / 地点 / 雇佣类型冲突）
   - `score`：打分。资质重合度（必需项权重高于加分项）、文本相似度（TF-IDF 余弦即可）；行为信号留接口但不实现，注释里写清楚为什么本地拿不到
   - `explain`：输出命中了哪些要求、缺哪些（模板生成，不接 LLM）
2. 每个模块开头用中文注释写：对应公开资料里的哪一段、证据等级（官方 / 第三方 / 推测）、和真实系统可能不一样的地方。函数和变量用英文命名。
3. 测试数据：职位侧直接用 `/Users/lucky_wang/Documents/codex/outputs/glassdoor_match_20261012/observations/jobs-side-unauth.json` 的真实结构（`extractedJobAttributes` 是 5 位 ID 加名称，`skills` 是它的子集），`taxonomy` 模块的 ID 形式照它来；用户侧按 L1 登录后观察到的 `profileAttributes` 结构造脱敏 fixtures。另外人工构造 5 对以上简历-JD。`cargo test` 覆盖：别名归一、硬过滤剔除、必需项缺失时降分、相关岗位分数高于不相关岗位。
4. 依赖尽量少：标准库加 serde / serde_json 足够，其他依赖要在报告里说明理由。
5. 附 `matcher/README.md`：怎么运行（绝对路径命令）、建议的阅读顺序（给 Rust 新手）、每个模块对应报告的哪一节。

## 5. 已有材料（先读，只交增量）

- `/Users/lucky_wang/Documents/Claude/notes/2026-10-12-glassdoor职位简历匹配逆向.md`（Claude 的试探性获取：三段式流水线、分类体系、GPT 解释、2016 MinHash、第三方资料分级）
- `/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/notes/2026-10-07-codex-research-brief-occupation-skill-taxonomy.md` 及其交付物 `/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/docs/research/occupation-skill-taxonomy-2026-10.md`（小谷的职业树 + 技能树对齐 ISCO/ESCO/大典。taxonomy 模块可以借用，别重新调研分类体系）

- 同一份笔记的 2.6 节「开源里接近这套设计的项目」：任务 D 以 tabiya-tech/matching-engine 为参考实现。必需 / 加分技能分开存（`essential_skills` / `optional_skills`）、技能 ID 加向量的软匹配、`U_hat × P_hat` 打分、技能缺口输出，这几点照它的思路用 Rust 重写；检索层可以接 tantivy（BM25）。不要再从零调研开源同类。

## 6. 交付格式（report.md）

1. 一段话结论：Glassdoor / Indeed 匹配的骨架是什么，用户界面上的匹配提示主要由哪几个因素决定，对「按 JD 改简历」意味着什么。
2. 前提校正（第 0 节两条，加上 ArtCraft 参照，半页以内）。
3. 流水线逐段拆解：每段写「已知（附来源）/ 推断（附依据）/ 未知」三栏。
4. L1 观察结果：字段结构表、匹配信号的返回形式、相关 / 不相关岗位对比，附脱敏 JSON 路径和截图路径。
5. 匹配器设计：模块和真实系统的对应关系、主动做的简化、测试结果（贴 `cargo test` 输出）。
6. 对小谷的可借鉴点：最多 5 条，每条写清楚改小谷的哪个环节。
7. 修正项：对第 5 节已有材料的修正。
8. 未解决问题。

写作要求：中文，直接陈述，不用 emoji，不用「加粗关键词：描述」格式，文件路径一律写绝对路径。

## 7. 验收条件（Claude 审核时逐条核）

- 报告里每条关于 Indeed / Glassdoor 内部机制的论断都标了等级（官方 / 第三方 / 推断），sources.csv 和正文一一对应；抽查 5 条链接，能打开且内容与引用一致。
- 至少有 3 条第 5 节笔记之外的新一手来源（论文、专利、工程博客、官方文档任一类）。
- L1：6 个页面都有记录；observations 里 grep 不到真实姓名、邮箱、电话、token、cookie；没有出现自己构造的接口请求。
- ArtCraft：给出 GitHub 仓库链接；说清它参照了 Adobe 的什么、有没有读 Adobe 代码（来自作者原话，或标「未说明」）。
- matcher：Claude 在本机执行 `cargo test` 全部通过；五个模块齐全，每个模块头部有证据等级注释；相关岗位分数高于不相关岗位的测试存在且通过。
- 对小谷的借鉴点每条都指到具体环节，不写空话。

## 8. 回填区（Codex 交付后由 Claude 填写）

- 交付日期：
- 审核结论：
- 被剔除条目及原因：
- 用户决定采纳的借鉴点：
