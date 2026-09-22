# 小谷求职 Harness 架构

## 目标

用户不需要理解 Skill、脚本或状态机。只要说一句“帮我看岗位”“改简历”或“复盘面试”，系统就判断意图、调用对应能力，并给出一个清晰的下一步。

## 五层结构

| 层 | 用户是否需要知道 | 作用 |
|---|---|---|
| 一句话入口 | 需要 | 用户用自然语言说出问题，不选择 Skill |
| Harness | 不需要 | `xiaogu-career-master` 识别意图、检查安装、排列调用顺序、管理状态 |
| 业务 Skill | 不需要 | `xiaogu-career-suite`、`xiaogu-resume`、`xiaogu-interview-review`、`xiaogu-boss-jobs` 完成具体任务 |
| 确定性运行层 | 不需要 | Python 检索、意图路由、Schema 校验和工作区状态，帮助能力较弱的模型稳定执行 |
| 用户资料层 | 需要知道存放位置 | 保存岗位原文、候选人事实、简历版本、逐字稿和复盘；推断不能进入事实主档 |

## 一句话如何被处理

```text
用户原话
  ↓
xiaogu-career-master
  ├─ 找岗位 → xiaogu-boss-jobs
  ├─ 看岗位 / JD / 黑话 → xiaogu-career-suite
  ├─ 改简历 → xiaogu-career-suite → xiaogu-resume
  ├─ 复盘面试 → xiaogu-career-suite → xiaogu-interview-review
  └─ 不知道下一步 → 读取工作区状态并选择当前动作
```

`route_request.py` 为小模型提供确定性兜底。它只决定调用顺序，不替业务 Skill 生成事实。

## 小白交互约束

1. 材料够就直接执行，不问“是否继续”。
2. 缺材料时一次只问最先缺的一项。
3. 默认不向用户展示 Skill 名称、命令和 JSON。
4. 每轮最后只给一个下一步动作。
5. 一个岗位的材料沿用，不要求用户重复粘贴。

## 核心与兼容层

- `xiaogu-career-suite` 是新版岗位理解核心。
- `xiaogu-jd-decoder`、`xiaogu-job-reality` 是旧版兼容 Skill，可以保留但不再要求新用户理解。
- `xiaogu-career-master` 是唯一总入口，不承担数据库内容生成，也不替下游 Skill 编造结果。

## 外部信息边界

招聘网站和职场社区是外部来源。Harness 只有在目标环境同时具备联网工具、用户访问权限和可读取页面时才能取得信息。安装一个 Skill 不会自动提供浏览器、登录态或绕过平台风控的能力。外部读取失败时，保留本地流程，并让用户提供公开链接、合法导出、截图或复制文本。
