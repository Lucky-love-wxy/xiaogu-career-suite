# 小谷求职 Skill 群

- 任务目录：`/Users/lucky_wang/Documents/codex/xiaogu-career-suite`
- 规则入口：`/Users/lucky_wang/Documents/codex/AGENTS.md`
- 原始目标：完成可打包给用户的基础求职 Skill 群，使用 boss-agent-cli 获取 BOSS 职位；理解招聘需求并参考 HypeFade 设计行业黑话翻译；封装小谷面试复盘和简历 Skill；以 Master 串成可安装闭环。
- 验收：五个 Skill 均有有效 `SKILL.md`；共享岗位/证据/申请状态契约；boss-agent-cli 适配器可规范化真实 JSON 信封与错误；JD 解码器有确定性后处理和回归样例；简历不编造；复盘可追溯逐字稿；Master 能从岗位搜索结果推进到复盘；安装器和离线演示可运行；生成可分发压缩包；说明需要用户完成的 BOSS 登录动作。
- 授权：可读取公开网页/仓库，创建和验证本地项目、安装包；未授权自动投递、发送消息、发布、部署或修改用户 BOSS 账号。
- 当前阶段：职业现实解码 Skill 已完成弱模型兼容升级，等待并入完整 Skill 群。
- 已完成：既有小谷飞书主文档与附件已读取；候选开源生态已核验；HypeFade 既有取证和透明 JD 产品规划已定位；`xiaogu-job-reality` 已包含 9 个首批职业条目、职业层级、确定性召回与分析器、输出契约和 fail-closed 校验器。所有输出区分 `jd_fact`、`reference`、`inference`、`unknown`、`conflict`；索引未命中仍保留 JD 原句；伪造引用、数字偷换、类型错误和 JD/索引冲突均有回归覆盖。`python3` 与 `python3 -S` 下 26 项行为测试通过。
- 下一步：用真实 JD 扩充职业条目与别名；再按原始验收实现 BOSS 适配、简历、复盘和 Master 编排。
- 最后更新：2026-09-22 18:54
