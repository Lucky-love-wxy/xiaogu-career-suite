# 小谷求职 Skill 群

小谷求职 Skill 群把求职过程拆成几个可以检查的步骤：找岗位、看懂 JD、理解岗位现实、准备岗位版简历、面试后复盘。它配有一份小型职业数据库和行业黑话词典，优先做确定性检索；没有查到的内容会标为未知，不让模型凭感觉补全。

## 当前包含

- `xiaogu-boss-jobs`：通过 `boss-agent-cli` 只读搜索和读取 BOSS 直聘职位，规范化为 JobDocument。
- `xiaogu-jd-decoder`：把招聘原句拆成事实、字面解释、待核实假设和问题。
- `xiaogu-job-reality`：从职业索引召回相近岗位，输出容易理解的工作内容、交付物、指标、风险和核实问题。
- `xiaogu-resume`：根据已确认经历生成岗位版本，不编造数字和经历。
- `xiaogu-interview-review`：根据真实逐字稿逐题复盘，生成下一次练习。
- `xiaogu-career-master`：串起流程并管理岗位状态，不自动投递或发消息。

## 数据和检索

事实源在 `database/`：

- `jargon.json`：行业黑话、字面含义、待核实假设、核实问题。
- `occupations.json`：当前收集的 9 个职业卡，包括算法工程师、推荐算法工程师、数据工程师、嵌入式软件工程师、SRE、业务后端工程师、产品经理、亚马逊运营、内容审核员。
- `taxonomy.json`：职业层级。

```bash
python3 scripts/xiaogu_search.py jargon --query "结果导向、弹性工作"
python3 scripts/xiaogu_search.py occupation --query "推荐算法工程师，负责模型和线上实验"
python3 scripts/xiaogu_search.py analyze --query "推荐算法工程师，结果导向，快速迭代"
```

输出里的 `matched` 只表示数据库命中，不表示公司一定会按风险假设执行。`index_miss` 表示当前数据库没有足够证据。

## 安装到 WorkBuddy

在 GitHub 仓库页面下载 ZIP，解压后通过 WorkBuddy 的“添加技能 → 上传技能”上传 `skills/` 下需要的 Skill 文件夹。初次使用建议全部上传；如果平台一次只能传一个，至少上传 `xiaogu-jd-decoder`、`xiaogu-job-reality`、`xiaogu-resume`、`xiaogu-interview-review` 和 `xiaogu-career-master`。需要真实搜索 BOSS 时再上传 `xiaogu-boss-jobs`，并按其说明完成用户自己的登录。

## 本地自检

```bash
python3 skills/xiaogu-job-reality/scripts/self_test.py
python3 -m py_compile $(find . -name '*.py' -not -path './.git/*')
python3 scripts/xiaogu_search.py analyze --query "算法工程师，负责模型训练和线上实验"
```

## 边界

本项目不保存 BOSS Cookie、token 或用户简历隐私，不自动投递、不自动发消息、不替用户确认公司事实。职业数据库是参考索引，不能替代对目标团队的核实。HypeFade 只提供“原文定位、分层解释、点击展开”的交互参考，没有复制其词典或文案。

## 目录

```text
skills/                 六个用户可安装 Skill
database/               可审计的 JSON 事实源
_xiaogu-runtime/        JobDocument、工作区和确定性处理器
scripts/                统一检索与打包脚本
docs/                   架构与 WorkBuddy 教学
examples/               可直接运行的示例
tests/                  回归测试
```
