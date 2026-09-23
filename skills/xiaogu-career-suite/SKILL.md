---
name: xiaogu-career-suite
description: 一句话看懂岗位与 JD：先检索职业数据库和行业黑话词典，再解释真实工作、招聘要求与核实问题。适用于“这个岗位做什么”“帮我看 JD”“这句招聘话什么意思”“这岗位值得继续了解吗”；不替公司背书，不生成录用概率。
---

# 小谷｜岗位理解核心

这是岗位理解的统一入口。用户不需要知道 `xiaogu-jd-decoder` 或 `xiaogu-job-reality` 的名字，只要把岗位名称、JD 或招聘话术交进来即可。

## 处理顺序

1. 用本 Skill 自带的检索器查询职业数据库和行业黑话词典：

   ```bash
   python3 scripts/search.py analyze --query "岗位名称和 JD 原文"
   ```

2. 有 JD 原文时运行确定性拆解器，并保存 JSON：

   ```bash
   python3 scripts/analyze_job.py --query "岗位名称和 JD 原文" --output /tmp/xiaogu-job-card.json
   python3 scripts/validate_card.py /tmp/xiaogu-job-card.json
   ```

   只有验证返回 `valid` 才能继续改写。拆解器负责原句抽取、未知字段、否定边界和显式冲突；模型不能把职业参考覆盖成公司事实。
3. 先复述 JD 明确写出的事实，再使用命中的数据库条目解释；两者不能混为公司事实。
4. 输出一份人话版岗位说明：一句话、每天做什么、交付物、常见指标、成长、风险。
5. 将黑话拆成字面意思、露骨翻译、最坏情况、可观察的危险信号、可直接询问招聘方的问题，以及什么回答才算具体。详细字段见 [references/jargon-contract.md](references/jargon-contract.md)。
6. 最多给三个核实问题，优先工作占比、考核指标、资源权限、薪资结构和关键工作安排。

## 固定证据标签

- `jd_fact`：招聘方原文明确写出；面向用户显示为“JD 明确”。
- `reference`：职业数据库或黑话词典中的参考。
- `inference`：根据材料提出、仍需核实的解释。
- `unknown`：材料和数据库都没有提供。
- `conflict`：JD 与参考资料或不同材料互相冲突。

检索返回 `index_miss` 时，只能解释用户提供的原句，并说明需要补充什么；不能用模型常识冒充数据库命中。不得补造薪资、工时、团队人数、任务比例、管理风格或录用概率。

## 默认输出

1. 这个岗位一句话在做什么
2. JD 明确事实
3. 职业数据库参考
4. 行业黑话翻译
5. 每天的工作、交付物与指标
6. 待核实推断与当前未知
7. 最值得问招聘方的三个问题

黑话部分不能只写“可能存在压力”这类模糊话。必须指出压力可能具体落在工时、指标、资源、权限、薪资结构或岗位边界中的哪一项，同时保留“需要核实”的证据边界。

需要制作简历时把结果交给 `xiaogu-resume`；需要面试复盘时交给 `xiaogu-interview-review`。旧版 `xiaogu-jd-decoder` 和 `xiaogu-job-reality` 可以保留，但新流程优先使用本 Skill。

## 外部从业者信息

用户明确要求查脉脉、职场社区或从业者分享时，读取 [references/external-research.md](references/external-research.md)。只有目标环境已经安装联网 Skill 并具备页面访问条件时才执行；联网 Skill 本身不提供账号、登录态或绕过平台风控的能力。
