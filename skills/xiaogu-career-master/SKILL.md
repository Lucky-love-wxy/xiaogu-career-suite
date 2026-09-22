---
name: xiaogu-career-master
description: 小谷求职的唯一自然语言入口。用户只说一句“帮我看这个岗位”“按 JD 改简历”“复盘面试”等话，就自动选择并串联岗位检索、岗位理解、简历和面试 Skill；适用于不知道该用哪个 Skill 的新手，不自动投递或发送消息。
---

# 小谷｜一句话求职 Harness

用户不需要记住任何 Skill 名称。先理解用户要解决的问题，再自动调用已安装的 Skill；材料够就直接做，缺关键材料时只问一个最短问题。

## 每次启动

1. 检查当前能发现哪些小谷 Skill。核心清单是：`xiaogu-career-suite`、`xiaogu-resume`、`xiaogu-interview-review`、`xiaogu-boss-jobs`。旧版 `xiaogu-jd-decoder` 和 `xiaogu-job-reality` 只作为兼容能力。
2. 运行确定性路由器帮助弱模型稳定判断：

   ```bash
   python3 scripts/route_request.py --query "用户原话" --context-json '{"has_job_description": true}'
   ```

   `context-json` 只描述当前会话或工作区里确实已有的材料。没有材料时传 `{}`；不能因为用户说了“这份 JD”或“我的经历”就当作正文已经存在。

3. 根据 `pipeline` 连续执行。不要让用户再次选择 Skill，也不要要求用户把同一份材料重复粘贴。
4. 如果所需 Skill 没有安装，准确说明缺哪个 Skill；可以完成的前置步骤继续完成。

详细路由和小白交互规则见 [references/harness-contract.md](references/harness-contract.md)。

## 一次完整流程

1. **找岗位**：使用 `xiaogu-boss-jobs`，先检查登录和权限，只读搜索。
2. **看懂岗位**：优先使用 `xiaogu-career-suite`，同时完成职业数据库检索、JD 拆解、黑话解释和核实问题。旧拆分 Skill 只在核心 Skill 缺失时兼容使用。
3. **判断职业现实**：使用 `xiaogu-career-suite` 从职业数据库召回相近职业；未命中就明确未知。
4. **决定是否值得继续**：根据工作内容、指标、资源、风险和候选人的真实偏好，列出核实问题，不替用户拍板。
5. **做岗位版简历**：使用 `xiaogu-resume`，只调用已确认经历，生成版本并保存证据关系。
6. **记录申请阶段**：通过 `career_workspace.py` 管理状态：`collected → reviewing → shortlisted → resume_ready → applied → interview → offer`。
7. **面试后复盘**：使用 `xiaogu-interview-review`，逐题回到原话，生成下一次准备卡。
8. **继续下一轮**：读取旧岗位、简历版本和复盘产物，不重复覆盖历史。

## 面向用户的最简回答

- 先直接给本轮结果，不展示内部路由过程。
- 用一句话说明已经分析了什么。
- 明确仍不知道的关键内容。
- 最后只给用户一个下一步动作。

只有用户询问实现细节时，才展示 Skill 名称、脚本、状态机和文件路径。

## 事实边界

- `jd_disclosed` 是招聘方公开写出的内容。
- `candidate_confirmed` 是候选人确认的经历。
- `reference` 是职业数据库中的相似岗位参考。
- `inference` 是待核实解释。
- `unknown` 是材料没有提供的信息。
- `conflict` 是 JD、数据库或不同材料之间的明确冲突。

未命中、未登录、缺逐字稿或缺候选人证据时，停止依赖步骤，保留已完成结果，并只询问当前最先需要补的一项。

默认不调用投递、打招呼、批量沟通、交换联系方式等动作。用户如果之后明确要求某个具体外部动作，仍需按上游工具的确认门禁执行。
