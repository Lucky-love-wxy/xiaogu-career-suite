---
name: xiaogu-boss-jobs
description: 使用 boss-agent-cli 搜索和读取 BOSS 直聘职位，并规范化为小谷私有 JobDocument。适用于找职位、筛选岗位、读取 JD；不负责自动投递或发送消息。
---

# 小谷｜BOSS 岗位获取

目标是取得用户有权查看的岗位信息，并交给 JD 解码或 Master。把平台返回和用户登录状态当作外部事实，不能因命令存在就声称已读取职位。

## 工作流

1. 先运行 `boss schema`，实际 schema 是能力真源；再运行 `boss doctor` 和 `boss status`。不要依赖记忆中的参数。
2. 未安装时给出 `uv tool install boss-agent-cli`；浏览器内核按上游当前说明安装。未登录时由用户亲自执行 `boss login` 或完成二维码/浏览器步骤；不要索取 Cookie、token 或把凭据写进工作区。
3. 将用户给出的岗位、城市、薪资、经验、学历、行业和福利条件转成一次有界搜索。先展示结果摘要；只对用户选择的少量岗位读取详情。
4. 使用 `scripts/boss_jobs.py` 运行只读搜索或规范化已保存信封：

   ```bash
   python3 scripts/boss_jobs.py search "AI 产品经理" --city 上海 --output /安全路径/jobs.json
   python3 scripts/boss_jobs.py detail <security_id> --job-id <job_id> --output /安全路径/job.json
   python3 scripts/boss_jobs.py normalize --input boss-output.json --output jobs.json
   ```

5. 把 JobDocument 交给 `xiaogu-jd-decoder`。私有 `security_id`、`job_id` 只保存在本地工作区，不放进报告、分享包或版本库。

## 停止条件

- `AUTH_REQUIRED`：转述上游 `operator_actions`，等待用户完成登录。
- `ACCOUNT_RISK`、`ENVIRONMENT_RISK` 或安全页：停止当前自动化，保留已取得结果和恢复命令；不改指纹、不循环重试。
- 空结果：说明实际筛选条件和时间，不把空结果解释成市场没有岗位。
- `boss-agent-cli` 输出不是合法 JSON：停止并报告命令、退出码和脱敏错误。

本 Skill 默认不调用 `apply`、`greet`、`batch-greet`、`exchange`、聊天回复或任何招聘者侧写操作。用户另行明确授权具体岗位和动作时，仍按上游确认门禁执行。

字段契约和错误处理见 [references/integration.md](references/integration.md)。
