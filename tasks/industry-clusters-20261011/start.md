# 官方产业集群调研

任务标识 industry-clusters-20261011；工作区规则 /Users/lucky_wang/Documents/codex/AGENTS.md。
原始要求：完成 /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/notes/2026-10-11-codex-research-brief-industry-clusters.md。详细范围及验收以该文件为准。
最新修正：用户“继续”，持续完成原目标；没有改变范围。
授权：官方公开来源只读采集、原文归档、本项目研究报告/名单/对应/来源表；不访问招聘网站、不改运行时/职业库/岗位卡、不commit/push、不代填Claude第9节。

状态：研究交付已完成，独立review PASS；不宣称全国现行全量已完成，Claude最终验收尚未进行。

交付：
- 报告 ../../docs/research/industry-clusters-2026-10.md
- 名单 ../../data/careerdb/industry_clusters.csv：20完整来源单元545条，跨年与层级有重叠。
- 对应 ../../data/careerdb/role_cluster_links.csv：50岗，387条件对应，22岗未找到。
- 来源 ../../docs/research/industry-clusters-2026-10-sources.csv：49条含原文件SHA。
- 原文 ../../evidence/industry-clusters-2026-10/；SHA256-all.json；各组summary.md。
- 验证 validation.json PASS；10原条号/页抽查；独立审阅 review.md PASS。
- 样本 sample-cities.json/csv：623，28缺原城市，固定3输入SHA；不是招聘数量。

决定：只收齐可核完整源单元；名单原行业文字作为依据，岗位雇主行业全部推测。生物医药外包不直接等于临床研究。官方手册与正式认定分开，年鉴编排不任意转载。

剩余与边界：66战略/23生物/创新型全国/178高新区原始完整表、部分历史和现行状态未核；江苏广东专门药械原表未找到；澄海入选官方消息已正文核实，但原名单41及条号未取得；袜业名单条号未找到。相关“未找到”结论已按brief报告，不伪造补齐。
外部路径阻塞：MIIT 403/CDP攻击提示、NDRC robots403、Kaiping robots403等已停站，不能跨工具绕过。证书失败未关闭TLS验证。

复现：python3 tasks/industry-clusters-20261011/sample_cities.py → build_tables.py → write_report.py → validate.py（已有原文件即可，无需网络重跑）。需变更输入时重新标日期/范围后再生成；不无故重抓阻断站。
下一步：Claude按brief第8节审核材料并写其第9节；用户手工招聘量回来后才能对照岗位地域分布，不属于本次抓取授权。
最后更新：2026-10-11 20:12 CST
