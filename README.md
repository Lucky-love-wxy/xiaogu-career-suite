# 小谷求职 Skill 群

小谷求职 Skill 群把求职过程拆成几个可以检查的步骤：找岗位、看懂 JD、理解岗位现实、准备岗位版简历、面试后复盘。最外层的 Harness 由 `xiaogu-career-master` 承担：用户只需要说一句自然语言，它就自动选择并串联对应 Skill。系统配有一份小型职业数据库和行业黑话词典，优先做确定性检索；没有查到的内容会标为未知，不让模型凭感觉补全。

## 当前包含

- `xiaogu-boss-jobs`：通过 `boss-agent-cli` 只读搜索和读取 BOSS 直聘职位，规范化为 JobDocument。
- `xiaogu-career-suite`：新版岗位理解核心，一次完成职业检索、JD 拆解、黑话解释、岗位现实和核实问题。
- `xiaogu-jd-decoder`：旧版兼容 Skill，把招聘原句拆成事实、字面解释、待核实假设和问题。
- `xiaogu-job-reality`：旧版兼容 Skill，从职业索引召回相近岗位并输出岗位现实卡。
- `xiaogu-resume`：根据已确认经历生成岗位版本，不编造数字和经历。
- `xiaogu-interview-review`：根据真实逐字稿逐题复盘，生成下一次练习。
- `xiaogu-career-master`：面向新手的唯一 Harness 入口，识别一句话意图、串起流程并管理岗位状态。

## 一句话使用

安装完成后，用户无需说 Skill 名称，可以直接说：

- “帮我看看这个算法工程师岗位每天到底做什么。”
- “把这份 JD 里的行业黑话翻译成人话。”
- “根据这份 JD 和我的经历改一版简历。”
- “这是刚才的面试逐字稿，帮我找出最该改的三个问题。”
- “我现在求职进行到哪一步，下一步做什么？”

Harness 会自动选择 `xiaogu-career-suite`、`xiaogu-resume`、`xiaogu-interview-review` 或 `xiaogu-boss-jobs`。一句话包含多个任务时，它会按依赖顺序连续调用。

完整的新手说明见 [`docs/workbuddy/一句话使用小谷.md`](docs/workbuddy/一句话使用小谷.md)。需要调研脉脉等外部页面时，另见 [`docs/optional-web-access.md`](docs/optional-web-access.md)。

## 数据和检索

事实源在 `database/`：

- `jargon.json`：46 条高频招聘黑话，包含字面含义、露骨翻译、最坏情况、可观察的危险信号、核实问题和合格回答标准。
- `occupations.json`：当前收集的 9 个职业卡，包括算法工程师、推荐算法工程师、数据工程师、嵌入式软件工程师、SRE、业务后端工程师、产品经理、亚马逊运营、内容审核员。
- `taxonomy.json`：职业层级。

```bash
python3 scripts/xiaogu_search.py jargon --query "结果导向、弹性工作"
python3 scripts/validate_jargon.py
python3 scripts/xiaogu_search.py occupation --query "推荐算法工程师，负责模型和线上实验"
python3 scripts/xiaogu_search.py analyze --query "推荐算法工程师，结果导向，快速迭代"
```

输出里的 `matched` 只表示数据库命中，不表示公司一定会按风险假设执行。`index_miss` 表示当前数据库没有足够证据。

## 安装到 WorkBuddy

在 GitHub 仓库页面下载 ZIP，解压后通过 WorkBuddy 的“添加技能 → 上传技能”上传 `skills/` 下的 Skill 文件夹。第一次至少安装 `xiaogu-career-master` 和 `xiaogu-career-suite`；需要改简历时安装 `xiaogu-resume`，需要复盘时安装 `xiaogu-interview-review`，需要真实搜索 BOSS 时安装 `xiaogu-boss-jobs`。`xiaogu-jd-decoder` 和 `xiaogu-job-reality` 只用于兼容旧版。

## 本地自检

```bash
python3 skills/xiaogu-job-reality/scripts/self_test.py
python3 skills/xiaogu-career-suite/scripts/search.py analyze --query "算法工程师，结果导向"
python3 skills/xiaogu-career-master/scripts/route_request.py --query "根据产品经理 JD 和我的项目经历改简历"
python3 -m py_compile $(find . -name '*.py' -not -path './.git/*')
python3 scripts/xiaogu_search.py analyze --query "算法工程师，负责模型训练和线上实验"
```

## 边界

本项目不保存 BOSS Cookie、token 或用户简历隐私，不自动投递、不自动发消息、不替用户确认公司事实。职业数据库是参考索引，不能替代对目标团队的核实。HypeFade 只提供“原文定位、分层解释、点击展开”的交互参考，没有复制其词典或文案。

## 目录

```text
skills/                 Harness、核心岗位理解与兼容拆分 Skill
database/               可审计的 JSON 事实源
_xiaogu-runtime/        JobDocument、工作区和确定性处理器
scripts/                统一检索与打包脚本
docs/                   架构与 WorkBuddy 教学
examples/               可直接运行的示例
tests/                  回归测试
```
