# 基础架构草案

用户可见 Skill：

1. `xiaogu-boss-jobs`：读取 boss-agent-cli schema，搜索和读取职位，规范化为私有 JobDocument；不自动投递。
2. `xiaogu-jd-decoder`：三级翻译、真实需求拆解、原句证据、缺项/冲突与核实问题。
3. `xiaogu-resume`：从经过用户确认的 Evidence 生成岗位版本，保留事实和版本关系。
4. `xiaogu-interview-review`：从真实逐字稿生成逐题复盘、缺口、知识卡候选和训练动作。
5. `xiaogu-career-master`：管理岗位、简历版本、申请阶段、面试轮次和反馈闭环。

共享运行层：`runtime/` 的 JSON Schema、确定性 Python 处理器和工作区目录；不作为独立用户概念。
