# 公司背调试点 2026-10-12

- 状态：研究交付完成；部分验收（资料/执行证据缺口），无待执行已授权网络请求。
- 任务规则：/Users/lucky_wang/Documents/codex/AGENTS.md；原始任务：完成 notes/2026-10-12-codex-research-brief-company-check.md。
- 范围：6 张卡片、6 类渠道实测、推荐流程、Tavily 用量与余额、设计影响；不改运行时代码，不登录、不付费、不充值。
- 授权：用户要求完成 brief；Tavily 钥匙串 key 仅进程内读取，本轮最多 60 次 API 调用。
- 验收：结论对应 URL、短摘、访问日及 SHA256 快照；缺失字段明确未找到；实测耗时与成功率有分母。
- 初创筛选：本地 2723 条样本，算法/AI/医学AI/大模型关键词筛得 79 条。候选百川智能及北京人形机器人创新中心，待核验成立期与融资。
- 已完成：42次basic搜索+3次usage=45次API请求，起始余额1000；接口结束/复核已用27、余额973，与响应累计42 credits不一致，报告并列保留。6卡、报告、来源/渠道CSV已保存；43来源短摘、283证据manifest；9项本地守卫/数据验证通过；独立只读review及复核PASS，见review.md。
- 执行偏差：qcc HTTP567和HTTP200混淆脚本风控页未被初版脚本即时封停，发生同站后续访问；已封停qcc.com全部子域，补识别规则，相关样本排除合规成功率。gsxt robots 521、看准IR robots403停站；天眼查六页均只有登录壳，无企业正文，未登录。
- 证据目录：../../evidence/company-check-2026-10/
- 交付：../../docs/research/company-check-pilot-2026-10.md；../../data/companies/；../../scripts/companycheck/README.md。
- 剩余缺口：工商企业正文、字节集团法律名称强来源、两家初创未上市强确认、两家初创实际付费客户；Tavily计费差异原因；不能追溯首次采集过程完全合规。当天已封停qcc、gsxt、天眼查、看准IR，不继续该路径。
- 下一步：用户读报告；如另行授权生产接入，须单独验证匿名取证/站点停止/成本限制与运行时契约。本轮不接入运行时，不commit/push，不自动创建后续任务。
- 展示：尝试open -a Cursor打开报告，系统返回Unable to find application named 'Cursor'；未使用其他编辑器。
- 最后更新：2026-10-12（Asia/Shanghai）
