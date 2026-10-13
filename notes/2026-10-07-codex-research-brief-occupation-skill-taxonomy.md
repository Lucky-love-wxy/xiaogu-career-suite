# Codex 调研 Brief：职业树 + 技能树骨架（对齐 ISCO / ESCO / O*NET / 职业分类大典）

## 元数据
- 下发日期：2026-10-07
- 任务名：职业树 + 技能树骨架调研与映射试点
- 所属项目：小谷求职 Skill 群（/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch）
- 触发类型：调研（Claude 写 brief，Codex 执行，Claude 审证据）；是后续「职业库 v3 重构」设计的第 1 节市场调研输入
- 设计方：Claude；执行方：Codex
- 上游文档：
  - /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/notes/2026-10-05-career-db-v2.md（第 1 节已列过 O*NET / ESCO / 大典，但 ESCO「未读原文」、大典「官方 PDF 未打开」——本 brief 补齐）
  - /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/notes/2026-10-06-codex-research-brief-role-cards.md（岗位卡片证据标准，本 brief 沿用）
  - /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/docs/research/role-cards-2026-10.md（170 张卡只有 4 张有从业者证据）
- 交付落点：
  - 主报告：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/docs/research/occupation-skill-taxonomy-2026-10.md
  - 映射表：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/data/careerdb/node_mapping_standards.csv
  - O*NET 可迁移性对照：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/data/careerdb/onet_transfer_check.csv
  - ESCO 技能挂接试点：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/data/careerdb/esco_skill_pilot.csv
  - 来源表：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/docs/research/occupation-skill-taxonomy-2026-10-sources.csv（url, 标题, 发布方, 版本/日期, 访问日期, 支撑哪条结论）
  - 原始下载（标准数据包、PDF、页面快照）：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/evidence/taxonomy-2026-10/（evidence/ 已在 .gitignore）
  - 脚本：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/scripts/taxonomy/
  - 恢复入口：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/tasks/research-2026-10/start.md 追加一节

## 状态与交接（新会话先读这一节）
- 当前状态（2026-10-07）：brief 已定稿，待用户交给 Codex；Codex 未开始。
- 下一步：
  1. 用户：把本文件路径交给 Codex，说「按这份 brief 执行，交付到元数据里的落点」。
  2. Codex：先读第 6 节已有材料，再按第 2–5 节执行。
  3. Claude：交付后按第 8 节逐条验收，结论写进第 9 节。
- 判断是否已交付：看 docs/research/occupation-skill-taxonomy-2026-10.md 是否存在。

## 0. 这份调研服务哪个决策

用户 2026-10-07 定的方向：职业库从「BOSS 行业 → 类别 → 岗位」改成「职业树（A 大类 → B 职业小类 → C 细分）+ 技能树」，职业对技能多对多，行业、专业都作为独立的多对多维度。目标是换专业、换行业时复用同一棵职业树，不再从零搭层级。

现有树的问题（库内证据）：BOSS 分类第一层是行业，同一职业散在多个行业下；例如药学类专业连到「项目经理/主管（互联网/AI）」，药企项目经理被挂到互联网下。见 /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/docs/research/careerdb-all-v1.md。

调研要回答四个问题，每个问题最后落一个可执行结论：
1. 职业树骨架用哪套标准（ISCO-08 / ESCO / 大典 2022），层级怎么对齐，能不能拿到机器可读数据、许可是否允许我们用在产品里。
2. 现有 195 个有样本的岗位节点能映射到这套骨架的比例是多少；映射不上的是哪些、为什么（中国特有岗位 / 节点本身混杂 / 粒度不一致）。
3. 用户的假设「O*NET 的工作内容在中国差不多，只有工时和待遇差别大」在我们的 P1 岗位上成立到什么程度。
4. ESCO 技能挂到我们的岗位上，可用性和中文化成本有多大；社招数据能否合规补到发展路径维度。

不是写一篇「国际职业分类综述」。

## 1. 范围约束
- 小谷用户：刚求职的大学生，校招为第一优先级。
- 用户 2026-10-06 决定：医院/学术路线（提问树 A 支：医生、护士、医技）不做岗位卡调研，但本次映射仍要覆盖它们（骨架要完整）。
- 第 3、4 节的试点只做 P1 岗位（/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/data/careerdb/research_queue.csv 中 tier=P1，50 个）。

## 2. 标准结构调研（每套都要填满下表字段，查不到写「未找到」）

| 字段 | 说明 |
|---|---|
| 版本与发布日期 | 当前最新版本号 |
| 层级结构 | 每层名称、编码位数、各层条目数（以官方数据包实际计数为准，不抄二手数字） |
| 每个职业带哪些字段 | 定义、任务、技能、知识、工作情境、入职门槛分级等 |
| 职业与技能的关系 | 是否多对多；有无 essential / optional 之分 |
| 数据怎么拿 | 下载地址、格式（CSV/RDF/API）、是否需要注册 |
| 语言 | 是否有官方中文；没有的话列出现有可用的中文对照来源 |
| 许可 | 能否在商业产品中使用、署名要求（引原文条款） |
| 与其他标准的对照表 | 官方 crosswalk（如 ESCO↔ISCO、O*NET-SOC↔ISCO、大典↔ISCO）是否存在、覆盖率 |
| 数据来源方法 | 条目是专家编写、在职者问卷，还是招聘数据抽取 |

必须覆盖：
1. ISCO-08（国际劳工组织）
2. ESCO（欧盟，职业 + 技能两张表）
3. O*NET（美国，重点看 Content Model 里的 Tasks、Work Context、Job Zones，以及它们的数据来源是不是在职者问卷）
4. 中华人民共和国职业分类大典（2022 版）：四层结构各层数量、是否有机器可读版本、细类条目里「主要工作任务」写到什么粒度、是否标注数字职业/绿色职业；版权和使用限制
5. 简短扫描（每个不超过半页）：Lightcast Open Skills、LinkedIn Skills Graph（公开资料范围内）、国内招聘平台公开的技能标签体系（BOSS / 猎聘 / 智联有无公开结构）。只回答「能不能替代 ESCO 技能表、为什么」。

最后给一个推荐：A/B/C 三层分别对齐哪套标准的哪一层，理由，以及推荐方案的主要风险。

## 3. 映射试点：195 个有样本节点 → 标准编码

输入：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/data/careerdb/cards.json 中 sample_n > 0 的节点（共 195 个，可用 stats.json 的 nodes_with_samples 核对）。

输出 node_mapping_standards.csv，每个节点一行，字段：
- node（现有路径）、name、sample_n
- isco_code、isco_title
- esco_uri、esco_title（可多个，用 | 分隔）
- dadian_code、dadian_title（大典细类；拿不到机器可读版时，至少把 P1 节点手工对上）
- onet_soc、onet_title
- match_type：exact / broader（我们的节点比标准细）/ narrower（我们的节点比标准粗，需要拆）/ none
- confidence：high / medium / low
- reason：一句话依据（引用标准条目的定义原文，单处不超过 30 字）
- issue：映射不上或需拆分时的原因分类（中国特有 / 节点混杂 / 粒度不一致 / 其他）

要求：
- 先用脚本做名称与定义的候选召回，再逐条判断；不得只靠名称相似度定 exact。
- 判断节点是否混杂时，读该节点在 /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/data/careerdb/postings_mapped.jsonl 里的原始岗位名。已知例子：「临床医生（科室未细分）」184 个样本里混有病理医师、口腔医师、中医医师，应标 narrower。
- 报告里给出统计：各 match_type 数量与比例；按 issue 分类列出全部映射不上的节点。

## 4. O*NET 可迁移性对照（检验用户假设）

从 P1 中挑 10 个在 O*NET 有明确对应职业的岗位（报告里说明挑选理由，要覆盖医药相关和通用岗位两类），每个岗位：
1. 列出 O*NET 该职业的 Tasks（按 importance 或 core/supplemental 取前 10–15 条，附 O*NET 链接与数据版本）。
2. 与我们库里该节点的招聘职责原文（cards.json duties + postings 原文）逐条比对，标注：中国样本中出现 / 未出现 / 中国样本有而 O*NET 没有。
3. 对 Work Context 里与工时、强度、对外接触相关的条目，只记录 O*NET 的数值，并标注「中国侧无对应证据」或给出中国侧来源（不许用常识推断中国情况）。

输出 onet_transfer_check.csv（岗位, O*NET 职业, 任务原文, 中国样本状态, 中国样本证据 URL）。

报告里给出结论：任务层重合比例（按岗位列）；哪些岗位因制度差异（如医药代表备案制、规培、事业编）内容本身不同；O*NET 哪些字段可以当作我们从业者调研的「问题清单」直接复用。

## 5. ESCO 技能挂接试点 + 社招可行性

### 5.1 ESCO 技能
对第 4 节同一批 10 个岗位，用第 3 节映射到的 ESCO 职业，取出其 essential / optional skills，输出 esco_skill_pilot.csv（岗位, ESCO 职业, 技能 URI, 技能英文名, 关系类型, 中国样本 JD 是否提到, 证据 URL, 建议中文名）。

报告回答：
- 每个岗位 ESCO 技能中，有多少在中国样本 JD 里能找到对应表述。
- 我们库内实际用到的 ESCO 技能总数估算，以及只翻译这一部分的中文化工作量。
- 两个岗位共享技能的例子（至少 3 组，其中 1 组是医学专业转通用岗位），说明技能层能不能支撑「转岗迁移」的推荐。

### 5.2 社招可行性
只评估，不批量抓：
- 来源：BOSS 直聘、猎聘、智联、前程无忧。每个来源查 robots.txt 和用户协议中关于抓取的条款（引原文、附访问日期），是否支持按经验年限（1–3 年 / 3–5 年）筛选，未登录能看到哪些字段。
- 已知：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/evidence/careerdb-2026-10-05/boss-cli/t1.json 是一次 BOSS 搜索尝试，报 NETWORK_ERROR（浏览器连接被关闭），之后未重试。报告里说明失败原因是否可恢复。
- 合规可行的来源，对 5 个 P1 岗位各取 1–3 年、3–5 年两档、每档最多 1 页，验证能否提取「职级名称、薪资区间、经验要求、新增的能力要求」四个字段。结果只作发展路径与薪资区间证据，单独存放，不混进校招统计。

## 6. 已有材料（先读，只交增量）
- /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/notes/2026-10-05-career-db-v2.md 第 1 节
- /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/docs/research/major-destinations-2026-10.md（提到过大典官方 PDF）
- /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/docs/research/role-cards-2026-10.md
- /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/evidence/careerdb-2026-10-05/boss-position-tree.json（BOSS 分类树）

已有结论被推翻或修正时，在报告中单列「修正项」。

## 7. 证据与合规要求
- 标准的层级数量、许可条款、字段定义一律以官方原始文件或数据包为准，附 URL、版本、访问日期；二手文章只能当入口。
- 下载的标准数据包与 PDF 存到 evidence/taxonomy-2026-10/，记录 SHA256。
- 抓取沿用岗位卡 brief 的规则：不使用登录态，不绕验证码，遵守 robots，单站请求间隔 ≥ 3 秒；不碰脉脉。
- 查不到写「未找到」，不用常识补齐；推测必须显式标「推测」。
- 中文写作，直接陈述，不用 emoji，不用「加粗关键词：描述」格式。

## 报告结构（occupation-skill-taxonomy-2026-10.md）
1. 一段话结论：职业树骨架推荐方案 + 195 节点可映射比例 + 用户假设是否成立 + 社招能否补。
2. 四套标准对照表（第 2 节字段）。
3. 推荐骨架与风险。
4. 映射统计与映射不上的节点清单。
5. O*NET 可迁移性结论。
6. ESCO 技能试点结论与中文化成本。
7. 社招可行性。
8. 修正项。
9. 未解决问题。

## 8. 验收条件（Claude 逐条核）
- 第 2 节表格五套全部填满，层级数量和许可条款都有官方来源；抽查 3 条链接内容与引用一致。
- 明确回答 ESCO 是否有官方中文、大典是否有机器可读版本，并有出处。
- node_mapping_standards.csv 恰好 195 行；exact 匹配抽查 10 条，依据合理；「临床医生（科室未细分）」标为 narrower。
- onet_transfer_check.csv 覆盖 10 个岗位，每个岗位的中国侧状态都有证据 URL 或明确写「未出现」。
- 第 4 节的 Work Context 没有任何用常识推断的中国侧结论。
- esco_skill_pilot.csv 覆盖同一批 10 个岗位，给出中文化工作量估算和至少 3 组共享技能例子。
- 社招部分每个来源都有 robots / 用户协议原文与访问日期；未批量抓取。
- sources.csv 与正文引用一一对应。

## 9. 回填区（Codex 交付后由 Claude 填写）

### 中期审查（Claude，2026-10-07 22:20；Codex 额度用尽中断）
- 未验收：主报告 docs/research/occupation-skill-taxonomy-2026-10.md 未生成；社招可行性未见产出。
- 已核实事实（tasks/research-2026-10/taxonomy-2026-10/start.md）：ESCO 最新 1.2.1（2025-12-10），28 种语言，无中文；分类数据 CC BY 4.0（API 软件是 EUPL 1.2，两者不能混）；ESCO 下载需填邮箱，未提交；O*NET 最新 31.0（2026-08）；大典发布页 405，编码 0/195 未取得。
- node_mapping_standards.csv：195 行全部 provisional，final_accepted 0；ISCO 候选 146/195；broader 92 / narrower 55 / none 48，exact 0；「临床医生（科室未细分）」= narrower/节点混杂（混西医、口腔、中医、宠物医生及经营岗）。
- onet_transfer_check.csv：10 岗 × O*NET 前 10 任务，中国样本出现 54/100；期刊编辑 8、药品注册 7、生物信息 7 高，医药市场 3、医药代表 4、保险理赔 4、英语翻译 4 低。注意「未出现」只表示 5–14 份 JD 里没写，不等于中国不做。
- esco_skill_pilot.csv：10 岗共 529 条技能关系，JD 提到率低（如药品注册 4/34），中文建议名未审。
