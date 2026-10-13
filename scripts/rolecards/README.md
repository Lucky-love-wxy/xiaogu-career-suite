# 岗位证据卡片流水线

Python 3 标准库，无网络、模型或第三方依赖。研究schema独立于小谷运行时；不直接修改 occupations 或分类器。

从项目根目录运行：

```bash
python3 scripts/rolecards/build.py snapshot
python3 scripts/rolecards/build.py build
python3 scripts/rolecards/build.py validate
python3 scripts/rolecards/verify_delivery.py
```

`snapshot`只在本批初次冻结时运行，已有快照会拒绝覆盖。`build`与`validate`可重复运行，覆盖本批生成文件，不联网。`verify_delivery`还需要已有的原HTML缓存；原10-06批次需4个输入JSON及7个正文；当前还需10-07/08补充annex及引用正文，具体输入清单见最新reproduction.json，不固定为11文件。

输入：`evidence/role-cards-2026-10/inputs.json`冻结队列、映射样本、脱敏正文和提问树；`curation.json`保存5试点人工综合的陈述与逐字支持片段；`quality-decisions.json`保存不改变上游分类的隔离判断；`practitioner-annex.json`保存本人经历陈述、适用范围与来源路径，`build_practitioners.py`从已保存正文离线生成该补充输入。

输出：`data/careerdb/role_cards/role_<节点SHA前12位>.json`；`docs/research/role-cards-2026-10.md`；evidence下的样本摘要、覆盖清单、删除审计与核验结果。

字段为陈述数组，含`text / kind / evidence_ids / quotes`。`sample_count`另含分母、匹配ID和计数规则；建议问题标`suggested_question`。名称分类是元数据，不假装岗位实际工作证据。仅当≥3 JD、≥2不同作者且本人经历适用整卡范围时标`full`。本批CRC与PV满足样本门槛；full不证明行业代表性、实名认证或每个字段完整。MSL及CT算法仅补对应子类，整卡仍`partial`。

职责过滤采用明确动作前缀、要求段停止、宣传/个人信息剔除；多岗位标题、没有正文的人工索引、科研学术混合节点隔离。过滤可能漏掉合法任务，因此留空/不足4条均写入missing；不放宽规则填空。

验收检查：引用存在、逐字片段在冻结正文中、原HTML文本归一匹配、元数据和URL绑定、数值与文本可复算、拒绝四种篡改、171输出文件两次隔离生成哈希一致。语义正确性仍需只读审阅，引用存在本身不证明总结准确。

本批无需commit/tag/push；evidence受既有gitignore保护，恢复时必须保留该本地证据目录。新增本人正文以独立补充输入保存，不覆盖招聘快照；不能把旧发表日期标成新发布日期。

TikHub本批最多10次总请求，实际10次成功、US$0.10，额度已耗尽；不充值、不重试、不再调用。浏览器适配器不含Key，Key只在任务页内存使用后清除。离线复现不需要账号或Key。

2026-10-07/08增量：`build_expansion.py`从`evidence/practitioner-2026-10/curated.json`构建补充annex并调用原build/validate；`verify_expansion.py`核对170卡原JD字段和推广/过期/海外边界。当前4328条陈述、171产物隔离重建一致；不改运行时。

当前`evidence_level`保留历史证据门槛，`evidence_level_basis`明确标注；`longform_practitioner_author_n`和`longform_evidence_level`按当前800/500字门槛独立计算，旧短文不计长文作者。新本人证据要求具体时间线/场景，来源字数及片段均复核；标准O*NET来源只支撑海外任务，不计中国作者。

`reading_policy.py`只维护共享本地ledger，不发送网络。操作者必须检查reserve调用成功后才发请求，complete实际页检查后才记录阅读，读完才下一请求；规则模块不能自动约束独立工具调用。14个否定用例及独立契约审阅通过，但真实执行有历史脉脉超额及本轮休息检查后误发1次，不能据模块PASS声称全程合规。

新增TikHub预算是另一个批次US$1.00/100总尝试；实际23尝试/22成功/1未知，扣费US$0.22，剩余77次/保守US$0.77。余额及Key清理见新目录billing/manifest；不得沿用已关闭target/Key，未知长度不付费探长。新旧预算分开。
