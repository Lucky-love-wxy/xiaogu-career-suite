# 岗位卡片调研（2026-10-06）

**部分验收：招聘证据草稿已补入一批真实公开本人分享，整体170岗位调研仍未完成。** 所有本人经历仅适用所引作者与细分岗位，不作为行业普遍体验。

## 完成边界

简报的5试点已形成带引用草稿与流水线。P1/P2/P3全部节点有JSON；这是岗位覆盖，不能冒充170岗位完整研究。用户已指定脉脉、牛客并授权CDP，追加TikHub小红书及现有余额上限US$0.10。本轮通过CDP公开取证与TikHub App V2获取详情；搜索摘要不入卡。

| 批次 | 有卡片 | full | full比例 | 3份以上可用JD | 日常职责达到4条 |
|---|---:|---:|---:|---:|---:|
| P1 | 50 | 6 | 12.0% | 36 | 39 |
| P2 | 45 | 0 | 0.0% | 37 | 31 |
| P3 | 75 | 0 | 0.0% | 8 | 21 |

以上full列沿用历史证据门槛；按新长文门槛的full共1张。各卡独立longform字段及新批报告说明门槛，不能把旧短文full当本次长文验收。

## 口径和证据限制

- 库内样本按冻结映射节点、唯一URL计数；名称含多岗位分隔符的页面隔离，不把PM/BD等职责计入CRC。人工补证只有索引记录时不合并为正文，也不把社招混入校招统计。
- 学历统计来自上游归一字段；专业来自上游专业类归类，均不是独立复核后的录用门槛。结构字段与正文可能冲突，保留原文而不替雇主解决。
- 校招页面、实习标签和“经验不限”是三种不同证据。只计出现次数，不从缺少经验要求推出接受无经验。证书未系统抽取，保持未知。
- 除5试点人工精修外，其余165张为自动聚合草稿，未完成逐张语义精修。不可直接向产品用户展示为完整职业解释。
- 原始库有存档职位及来源日期；本轮未重新访问这些JD。accessed_at为空，snapshot_at不是抓取日期。
- 指标、发展、风险和误解缺从业者证据就留空；招聘中的培训/晋升宣传不当实际发展证据。
- 字段采用{text, kind, evidence_ids, quotes}，保留来源性质；这是一份研究schema，不改运行时职业索引契约。
- 正文输入只复制脱敏行；原HTML路径与SHA256用于追溯。新搜索结果为候选，不算已核原文，不用自动摘要填卡。

## 五张试点

| 岗位 | 文件 | 保留JD | 隔离样本 | 证据状态 |
|---|---|---:|---:|---|
| 医学事务/医学信息 | [JSON](../../data/careerdb/role_cards/role_c0c760f18848.json) | 17 | 5 | partial：2名本人作者 |
| 临床协调员 | [JSON](../../data/careerdb/role_cards/role_bd628efdd859.json) | 13 | 5 | full：2名本人作者 |
| 医学理赔/核保 | [JSON](../../data/careerdb/role_cards/role_9532388099aa.json) | 4 | 4 | partial：2名本人作者 |
| 药物警戒 | [JSON](../../data/careerdb/role_cards/role_c040cd053783.json) | 5 | 6 | full：2名本人作者 |
| 医学AI/生物医学大模型 | [JSON](../../data/careerdb/role_cards/role_8f7c7258beb3.json) | 9 | 2 | partial：0名本人作者 |

## 验证与离线复现

- 全量引用、逐字片段、计数由 validate 核验；删除条目 0 条。见 evidence/role-cards-2026-10/validation.json 与 deleted-claims.json。
- scripts/rolecards/build.py build 仅读 evidence 输入，重建170张卡片、样本摘要及本报告，补证还需practitioner-annex.json及其引用的正文快照；10-07增量还需practitioner-2026-10/practitioner-annex.json及对应新正文。validate 对真实输出检查，不读取运行时或调用模型。
- 已额外对原HTML缓存核对1401个支持片段，实体解码并去空白后全部匹配；见html-binding-check.json。这不冒充本轮新抓取或原HTML字节逐字匹配。
- 幂等哈希与人工抽查记录见 evidence/role-cards-2026-10/reproduction.json、spot-check.md；独立只读审阅见 tasks/research-2026-10/review-role-cards-2026-10.md。

```bash
python3 scripts/rolecards/build.py build
python3 scripts/rolecards/build.py validate
```

## 2026-10-06原始从业者补证与费用

- CRC与PV各有2不同作者昵称的具体本人经历，达到3JD+2作者门槛；full不是实名认证、行业代表性或全部字段完整。MSL两名作者只覆盖医学事务节点的子类，因此整卡仍partial。
- 6篇小红书图文详情加1篇牛客CT物理算法本人分享入卡；脉脉4篇已核正文分别是招募宣传、岗位介绍、历史二手案例和JD合集，未计本人数量。牛客帖子带内推，已保留动机说明。
- 小红书仅采用文字正文，图片未审阅；不调用用户资料或评论接口，不保存作者ID/头像/联系方式。每岗位最多保留10候选；搜索候选不当详情正文。
- TikHub成功请求10次：搜索4次、详情6次；[官方单价](https://tikhub.io/xiaohongshu-api)US$0.01，余额9.67→9.57美元，减少US$0.10，达到本次授权上限。免费额度0.05未变化；日统计回读仍8次/0.08，未作为追加请求依据。详见tikhub/manifest.json与billing.json。未充值，Key未持久化，任务窗口Key已清除。
- CRC考证建议、作息、加班和PV个人合规率意见不变成统一录用门槛/考勤/公式。核保只有新发现的候选，详情未读；不能把保险销售分享当核保员经历。

| 本人来源 | 适用范围 | 日期 |
|---|---|---|
| [Day20\|\| 三甲护士转行CRC \|两个月了!](https://www.xiaohongshu.com/explore/6a395b6f000000002103ef20) | 该作者入职CRC两个月的经历，不代表所有公司/护理转行成功率 | 2026-06-22 |
| [CRC Day1](https://www.xiaohongshu.com/explore/6a98f3ce0000000012024a76) | 该作者CRC首日经历，不推断长期工时、晋升或医学授权 | 2026-09-03 |
| [howto｜药企PV打工人怎么过一周？](https://www.xiaohongshu.com/explore/6a887f840000000024027ef0) | 该作者药企PV的一周；不推广其周末休息为行业规则 | 2026-08-22 |
| [PVer的日常（六十五）](https://www.xiaohongshu.com/explore/67a778500000000018009fb4) | 本人计算个例合规率时的口径讨论；个人意见不是法规或统一KPI | 2025-02-08 |
| [MSL的一周小结：想出去见专家，结果一直坐](https://www.xiaohongshu.com/explore/6aad41bd000000000b034a94) | 该作者MSL内部文档与专家拜访的时间拉扯 | 2026-09-18 |
| [MSL：我的8月小结🧩](https://www.xiaohongshu.com/explore/6a9587cd000000002503838b) | 该作者换岗后一个月MSL活动与多城行程 | 2026-08-31 |
| [秋招别把自己限制的太死](https://www.nowcoder.com/discuss/663692185128222720) | 2024年CT物理算法子类自述，末尾内推，身份未认证 | 2024-09-12 |

本批补证独立只读审阅见 tasks/research-2026-10/review-role-practitioners-2026-10.md；历史招聘草稿PASS不替代本批审阅。

2026-10-07增量作者、海外任务证据及独立预算见 [从业者放量报告](practitioner-evidence-2026-10.md)；以上7源与US$0.10均指10-06批次，不合并为本轮费用。

## 尚未通过的验收

不足3份JD的岗位89个，可核职责少于4条的岗位79个。尚有162岗位缺2名本人作者；混合节点即使有2名MSL作者也保持partial。未覆盖的体验/metrics/growth/risks留空。部分节点不足3JD，未联网补抓；部分节点职责不足4条。P3只完成库内聚合草稿，未做外部研究。候选检索尚未覆盖全部岗位。没有宣布完整调研完成。

## 对设计的影响

以下设计建议主要由招聘原文推出；新增本人分享仅按对应细分范围补证，未补证岗位的实际体验仍待复核；不修改提问树或build.py。来源ID均可在对应JSON的evidence和inputs.json中定位。

1. CRC雇主在医院外不等于工作地点在医院外。现有样本明确研究中心与医生、受试者协作，入口应分别问“是否做诊疗”与“是否接受医院驻点”，不能合为一道问题。来源：[CRC卡](../../data/careerdb/role_cards/role_bd628efdd859.json)，v885nazzz / v8Y5MZLaa。
2. “医学事务/医学信息”混有MSL、医学内容、技术轮岗与多岗位合集。先隔离合集，再按实质职责分卡；B1“围绕临床试验”不足以覆盖全部上市产品医学事务。来源：[医学事务卡](../../data/careerdb/role_cards/role_c0c760f18848.json)，v8U5ZCNnZ / vyYNL5LNL；合集v885NtCMN已隔离。
3. “医学理赔/核保”当前可核正文主要为理赔。不能用理赔样本推断核保日常；设计应把投保前风险评估与出险后案件审核分开，核保仍待补证。来源：[理赔卡](../../data/careerdb/role_cards/role_9532388099aa.json)，v8s5nztnM / vYY5tMaCz；核保划分仅为待核设计建议。
4. 医学AI节点至少包含AIDD、AI化学实验、模型应用开发、医学标注和推广工作，门槛不能混合计数后当统一要求。建议按交付物和任务分组，再讨论是否细分节点。来源：[医学AI卡](../../data/careerdb/role_cards/role_8f7c7258beb3.json)，v8kNLZMaZ / vYl5M55zN / vrm5aatLZ / vrk5ntMZa / vYm55aMCZ。
5. 队列P1仍有“科研岗（博士后/研究助理）”，与brief背景“不调研学术路线”存在范围张力。本轮将该节点全部正文隔离，卡片仅保留元数据；企业研发助理需逐份分离后再纳入。来源：inputs.json中queue节点、question_tree的B7；quality-decisions.json。
6. AIDD例的结构学历字段与正文博士要求存在冲突。这说明仅用结构化门槛做提问树排除存在风险，应保留冲突并要求招聘方确认，不能直接判本科/硕士可进。来源：医学AI卡 evidence v8kNLZMaZ正文“博士学历”与inputs同ID education=硕士；本轮未解决上游冲突。
