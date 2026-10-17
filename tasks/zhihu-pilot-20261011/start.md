# 知乎五岗位试点恢复入口
任务标识：zhihu-pilot-20261011
本文件：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/tasks/zhihu-pilot-20261011/start.md
最后更新时间：2026-10-11，Asia/Shanghai

## 目标与授权
用户要求完成 notes/2026-10-11-codex-research-brief-zhihu-pilot.md；决策是知乎能否作为从业者证据第二主力。
范围：CRA、医药代表、医学写作、医疗器械注册、算法工程师；只读百度发现、单一自建Chrome tab逐篇读取已加载知乎回答。限频见 ../../docs/research/practitioner-collection-policy.md。
不改岗位卡/运行时/提示词/测试；不读专栏/评论/私密资料；不点击扩展/滚动加载；不commit/push；不发送消息。没有新的用户修正。

## 状态：采集、分析与本地交付完成；协议验收未全通过
- 百度11次、知乎5页、正文17篇；合格2、半合格1、不合格14；明确本人经历6/17。
- 候选：CRA1、医疗器械注册1合格；医药代表1半合格（qualifies=false）。医学写作只找到2017年本人历史文本；算法所读全为2021年。
- 建议：暂作补充渠道，尚不支持第二主力；不得把便利样本比例视为全平台比例。
- 正文/搜索/页面/账本/验证：../../evidence/zhihu-pilot-2026-10/；均在gitignore evidence/内。
- 报告：../../docs/research/zhihu-pilot-2026-10.md
- 逐篇表：../../docs/research/zhihu-pilot-2026-10-answers.csv
- 本地重建与核验：python3 tasks/zhihu-pilot-20261011/build_deliverables.py（无网络调用）
- 原文、日期、去空白Unicode计数与引用匹配已自检；验证 CONTENT_PASS_PROTOCOL_NEEDS_CHANGES。没有独立review，Claude未签收。
- 未观察到平台限流/验证；自建tab 523DF0D9F0B8955709ACB04183A3E16A 已关闭，用户原tab未操作。

## 剩余验收与恢复边界
1. 首个CRA页停留165.393秒，原始5857字要求175.71秒，少10.317秒；账本保留偏差，不能宣称时长通过。后续隐私最小化不改原时长审计口径。
2. 第一条百度导航缺精确调用前时间，有任务开始/采集时间界限与页面证据；不能补造时间。
3. Claude按brief第8节独立审证据与第9节回填尚未执行；未授权向其他聊天发送消息。
本轮采集无需继续；上述偏差不能通过补造历史或形式化重新打开修复。若后续再采，需沿规则另批执行，保留本轮真实偏差。下一步先审核现有证据，不直接入卡或放量。
