# 第三方来源说明

小谷 Web Agent 的简历和模拟面试功能参照了以下开源项目。凡改编自代码或提示词的地方都在源码注释里写明了来源。

| 项目 | 许可证 | 用在哪里 | 方式 |
|---|---|---|---|
| [Resume-Matcher](https://github.com/srbhr/Resume-Matcher) | Apache-2.0 | `web/resume_tools.py`：关键词覆盖率口径、真实性规则、新数字 / 新技能检查 | 改编，按中文重写匹配和数字规则 |
| [Reactive-Resume](https://github.com/AmruthPillai/Reactive-Resume) | MIT | `web/resume_tools.py`：结构化简历与模板分离、单栏模板的 ATS 安全判断、学生版栏目顺序 | 参照设计，代码自写 |
| [interview-guide](https://github.com/Snailclimb/interview-guide) | AGPL-3.0 | `web/interview.py`：考察方向分级、题目只出自简历、难度配比、每题一条追问、四维加权评分、放弃作答记 0 分 | 只迁移机制，提示词和代码均为自写，未复制原文 |
| [Multi-Agent-Mock-Interview](https://github.com/XUZIAa/Multi-Agent-Mock-Interview) | GPL-3.0 | `web/README.md` 模拟面试接口：状态机在服务端、语音端只做转写与朗读 | 只参考分工思路，无代码 |

Resume-Matcher 按 Apache License 2.0 授权（仓库 LICENSE 未填具体版权人，原作者为 srbhr 及贡献者）。
Reactive-Resume 版权声明：Copyright (c) 2026 Amruth Pillai，按 MIT License 授权。
