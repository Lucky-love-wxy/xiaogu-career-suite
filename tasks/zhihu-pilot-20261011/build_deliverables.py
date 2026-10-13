"""Build and validate local pilot artifacts. No network calls or role-card writes.
Run: python3 tasks/zhihu-pilot-20261011/build_deliverables.py
Input: evidence/zhihu-pilot-2026-10/*.json. Output: report, CSV, verification.json.
Dependency: Python standard library. Re-running replaces only this pilot's outputs.
"""
import csv
import datetime as dt
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / 'evidence/zhihu-pilot-2026-10'
D = ROOT / 'docs/research'
roles = ['临床监查员（CRA）', '医药代表', '医学写作', '医疗器械注册', '算法工程师']
titles = ['当一名 CRA 的体验如何？', '做一个医药代表是怎样的一个感受？', '医学专员(medical writer)的职业发展路线是什么样子？', '有人来谈谈医疗器械注册这个工作吗？', '算法岗和开发岗有什么区别？']
queries = ['知乎 CRA 工作是什么体验', '知乎 医药代表 工作是什么体验', '知乎 医学写作 工作是什么体验', '知乎 医疗器械注册 工作是什么体验', '知乎 算法工程师 入职一年 离职']
answers = [(f, json.loads(f.read_text())) for f in sorted(E.glob('answer-*.json'))]
ledger = json.loads((E / 'access-ledger.json').read_text())
ledger['controls']['cdp_eval_calls'] = 33
ledger['controls']['count_note'] = '33次只读DOM控制，包括2次输出截断后的缩小读取；不调用fetch/点击/滚动。另有about:blank创建与tab关闭各1次；check-deps 1次。'
(E / 'access-ledger.json').write_text(json.dumps(ledger, ensure_ascii=False, indent=2))
headers = ['岗位','搜索词','问题标题','问题链接','回答链接','作者昵称','发布或编辑日期','日期类型（发布/编辑）','正文字数','本人在岗（是/否/不确定）','覆盖维度','推广动机','判定','不合格原因','请求序号','原文文件']
with (D / 'zhihu-pilot-2026-10-answers.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    for path, a in answers:
        idx = roles.index(a['role'])
        motive = '有：微信进群、培训及求职资料导流' if path.name == 'answer-05.json' else ('有：机构APP内容合作转载' if path.name == 'answer-02.json' else ('有：个人内容角落推广，无课程收费或联系导流' if path.name == 'answer-14.json' else '无明确商业导流'))
        writer.writerow(dict(zip(headers,[a['role'],queries[idx],titles[idx],a['question_url'],a['answer_url'],a['author'].strip('\u200b\n '),a['date_local'],a['date_type'],a['body_character_count'],a['first_person'],' / '.join(a['dimensions']),motive,a['judgment'],a['rejection_reason'],a['request_sequence'],'evidence/zhihu-pilot-2026-10/'+path.name])))

qualified = [a for _, a in answers if a['judgment'] == '合格']
half = [a for _, a in answers if a['judgment'] == '半合格']
personal = [a for _, a in answers if a['first_person'] == '是']
started = dt.datetime.fromisoformat(ledger['started_at'])
finished = dt.datetime.fromisoformat(ledger['collection_finished_at'])
minutes = (finished-started).total_seconds()/60
table = []
for role in roles:
    aa = [a for _, a in answers if a['role'] == role]
    c = Counter(a['judgment'] for a in aa)
    qa = [a for a in aa if a['judgment'] == '合格']
    dates = '；'.join(a['date_local']+'（'+a['date_type']+'）' for a in qa) or '无合格；所读 '+min(a['date_local'] for a in aa)+'—'+max(a['date_local'] for a in aa)
    reasons = {'临床监查员（CRA）':'第三人称科普；机构转载且过旧','医药代表':'经验归属不确定；旧文；微信导流','医学写作':'全部过旧且不足800字','医疗器械注册':'短篇感受；旧岗位科普','算法工程师':'全部2021年；部分泛化比较'}[role]
    median = str(qa[0]['body_character_count']) if qa else '不适用'
    table.append(f'| {role} | 1 | {len(aa)} | {c["合格"]} | {c["半合格"]} | {c["不合格"]} | {reasons} | {median} | {dates} |')

report = f'''# 知乎职业体验长回答五岗位试点

2026-10-11｜执行采集结束，分析与交付完成；时长账本存在一处偏差，尚未通过 Claude 独立验收。

## 1. 结论与决策

本轮百度检索11次、知乎正文页打开5次，逐篇读到17个回答。CRA：合格1 / 半合格0；医药代表：0 / 1；医学写作：0 / 0；医疗器械注册：1 / 0；算法工程师：0 / 0。合计合格2、半合格1、不合格14。明确本人在岗经历6/17（35.3%）；经验归属不确定2/17，其余9/17未提供本人在岗经历。本人比例包括过旧或过短的个人讲述，不等于合格率（2/17，11.8%）。这些是该便利样本的比例，不能推断知乎总体。

建议暂将知乎作为**补充渠道**，尚不支持与小红书并列为第二主力。它能补到医疗器械注册的近期本人长叙事，也有CRA个人工作讲述；本轮没有近期合格医学写作或算法工程师样本。医药代表近期样本仍需确认经验归属。发现入口、年代和可加载内容影响了结果；不能把本轮缺口说成平台上不存在。

报告与逐篇表属于本次增量；不改变历史原文或岗位卡的既有状态。所有身份均为作者自述、未独立认证。候选不是入卡结论。

## 2. 岗位结果

| 岗位 | 问题页数 | 读过回答 | 合格 | 半合格 | 不合格 | 主要原因 | 合格字数中位数 | 合格日期／无合格时所读日期范围 |
|---|---:|---:|---:|---:|---:|---|---:|---|
{chr(10).join(table)}

问题页打开的是外部搜索实际发现的完整链接，4个为特定回答入口、医学写作为问题入口；每页只读取已加载的默认回答，分别3、3、5、3、3篇。没有切换排序、点“查看全部”、点“阅读全文”或下拉加载，因此不代表这些问题的全部回答。未加载的回答没有纳入分母。算法页主题为岗位比较，是搜索发现后的替代样本，偏离优先体验标题，可能降低本人叙事比例。

字数为保存正文去空白后的Unicode字符数，本批无话题标签；不计题目、作者、日期、图片文字。折叠回答也只读已经在DOM内加载的正文，不补取隐藏接口。作者简介和推广联系方式按隐私要求移除，原文件标明删除位置；脱敏条目采用保存文本可复算字数，且均已排除。CSV逐行绑定对应正文文件，缺口不填0。

日期同时保存dateCreated/dateModified。首回答有可见发布标签；另一些折叠回答的日期来自已加载AnswerItem元数据，未靠摘要日期入选。正文展示标签缺失时明确采用元数据，编辑日期不当首次发布时间。CRA候选最后编辑于2025-03-07，首次发布2024-11-14；注册候选发布于2025-10-31。

### 两篇合格与一篇半合格

- [CRA个人回顾](https://www.zhihu.com/question/597894539/answer/30801381533)：1406字，作者自述入行多年，包含沟通、会议、现场监查、作息等内容。只采工作自述，不采对具体人员机构的未核指控；关于高薪双休的假设不作为入门薪资事实。本人在岗=是。
- [注册与体系个人叙事](https://www.zhihu.com/question/511536316/answer/1967587276629452557)：1544字，作者自述8年混合岗位经历。注册段有研发功能变更、老板催证的本人叙事场景；场景有戏剧化表达且未独立认证。只支持个人沟通场景，不能据此推出法规周期或整个岗位的工时、薪资；体系部分不映射到注册专岗。个人内容角落推广已标记，无加微信、课程或收费内推导流。
- [医药代表近期叙事](https://www.zhihu.com/question/301742682/answer/49436158271)：954字，2024-12-06发布。第一人称标题与大量第二人称泛化讲述混用，无法充分确认各段属于作者实际经历，记半合格且qualifies=false、claims为空；不入卡，不把文中代理收入倍数当个人已证实收入。

## 3. 与已有小红书／牛客原文对照

只以现有[原文汇总](practitioner-originals-2026-10.md)及其范围说明比较；未重新请求这两个平台。历史“入库／full”标签不代表满足本轮800字或此前新增长文口径。

| 岗位 | 既有材料及时间 | 本轮知乎差异 | 不能据此推断 |
|---|---|---|---|
| CRA | 小红书第13篇，2026-07-07；新手访视、翻旧监查报告、与CRC/PV/PM沟通，原CRA经历时间不明且转GCP，半入库 | 知乎2025-03最后编辑；多年个人回顾，补会议协调和不固定作息，1406字；缺精确一天时间分配 | 两者岗位场景不同，不合成一个统一日程；新发文也未必描述当年工作 |
| 医药代表 | 小红书第14/15篇，2026-04-22／09-30；带教首次拜访与当日业绩未达标，具体一天或互动，历史已入库 | 知乎较新样本2024-12，叙述更长、覆盖市场开拓到代理发展，但经验归属不确定；另两篇2020—2022，只是当时情况 | 篇幅长不等于证据更强；不能以知乎补入门薪资或代理收益 |
| 算法工程师 | 牛客第8篇2026-09-10，搜广推一年回顾、mentor与模型特征迭代；小红书第9篇2024-11-07，SQL/Spark、周会、夜间修bug时间表 | 知乎3篇全部2021年；主答569原始展示字符、去空白557字，有本人入职不到一年身份，主要讨论算法与开发关系；缺近期日程样本 | 不能用旧比较文替代近期作息、当前技术需求或薪资 |

两篇知乎合格回答分别1406、1544字，均比本轮短篇更充分，但仍缺可靠入门薪资和前三年明确时间线。没有对应医药代表／算法工程师合格知乎样本，因此这两岗不能完成“合格对合格”的比较；上表只说明所读文本差异。

## 4. 成本、访问状态与协议偏差

采集账本起止为16:27:07至{finished.astimezone(dt.timezone(dt.timedelta(hours=8))).strftime('%H:%M:%S')}（Asia/Shanghai），共{minutes:.2f}分钟，含规定阅读停留与本地判定，不含前置读简报和最终整理。研究页面导航16次：百度搜索11、知乎页打开5。另有33次只读DOM控制、about:blank创建及关闭各1次；共51次CDP控制调用，环境check-deps另1次。此口径不是浏览器内部HTTP请求数，图片、资源加载等内部请求未计量。

每产出1篇合格：8次研究页面导航、{minutes/2:.2f}分钟采集时间；其中百度5.5次、知乎页2.5次。若按全部CDP控制算为25.5次/篇。平台付费接口调用0次。搜索11/15、知乎页5/25，正文阅读17/60；本轮未观察到验证码、登录墙、403/429或频繁操作，未触发停站。未单独探测robots/条款，沿用简报提供的10-11 robots事实；本轮不产生产品运行时接入授权或建议。

已知后续同站导航间隔均超过5秒；第一条百度导航未记录精确调用前时间，仅保留任务开始和search-01采集时间界限，不能对这一项宣称精确时序验收。首次CRA页停留165.393秒，三篇当时5857字按比例应175.71秒，少10.317秒。此偏差已写账本，没有补造时间，也没有为补账再访问页面。其余页面累计停留与当时三／五篇字数要求相符。采集连续少于20分钟，未触及5分钟暂停阈值。任务标签页已关闭，用户原标签页未操作。

两个工具输出曾因过长截断，随后缩小DOM读取范围并逐篇保存；这是本地输出预算问题，未重新导航或换访问路径，未把截断文字当完整证据。所有17篇最终保存文本均可读取。采集合规验收因上述时长与首条精确时间缺口**未全通过**，不影响已保存正文、日期、引用的可核验性，但本轮不能用作完全合规效率基线。

## 5. 冷门医药岗

医学写作：查到[2017年本人入行一年多讲述](https://www.zhihu.com/question/50770074/answer/160962197)，去空白758字，明确自述外资CRO offer与一年感受；其余4篇为短评或入职选择提问。本轮未找到近期合格本人长回答。两组检索还出现旧专栏，按范围未打开；不能据此断言知乎无近期材料。

医疗器械注册：本轮查到1篇2025年1544字本人混合岗位叙事，可以补注册段个人场景；另有2026年253字本人入行感受，细节密度不足不列半合格，及2022年908字泛化岗位介绍，均排除。第二组搜索只出现旧专栏与不对应注册岗的公司话题，未打开。事实支持“能找到本人讲述”，不能推出这个渠道对所有注册细分岗位都稳定有效。

## 6. 放量估算与下一步

将“50个重点岗位”明确为每岗先获得1篇合格，若强行按本轮2/17产出率线性外推（**情景估算，不是预测**），约需425篇已加载回答、125次知乎页打开、275次百度搜索、400次研究导航、{minutes/2*50/60:.2f}小时采集时间。每天60篇正文的理论下限是8天；百度每小时15次会要求约19小时分散搜索，另每20分钟须暂停5分钟。若仍保持本次五岗一轮≤25篇、搜索≤15次的限制，需拆多轮并重新明确放量范围，不能直接照估算批量执行。

由于按岗位产出不均、仅5页、入口非随机、年代效应，以及本轮节奏偏差，该外推不能保证50岗覆盖，也不能作预算承诺。若每岗目标两名独立作者，线性情景翻倍为850篇正文、至少15天，去重及冷门缺口会进一步增加成本。

建议先保留补充渠道定位，交Claude审核两篇合格与一篇半合格候选；如后续仍要检验第二主力，应另做合规小批次，重点补医药代表本人归属及算法近期体验入口，先验证近期样本的稳定产出，再决定放量。本次不自动续采、不改岗位卡、不部署、不commit/push。

## 7. 交付与验收对账

- 报告：本文件；逐篇表：[answers.csv](zhihu-pilot-2026-10-answers.csv)，17行。
- 候选：[candidates.json](../../evidence/zhihu-pilot-2026-10/candidates.json)，2条qualifies=true、1条false半合格；每篇独立作者。
- 正文与页面状态：[证据目录](../../evidence/zhihu-pilot-2026-10/)，17篇正文、5页状态、11组搜索；原始正文只留evidence，已受.gitignore排除。
- 请求账本：[access-ledger.json](../../evidence/zhihu-pilot-2026-10/access-ledger.json)；本地核验：[verification.json](../../evidence/zhihu-pilot-2026-10/verification.json)。
- 正文逐字引用、字符计数、日期界限、无推广导流合格项、行数与文件对应由本地脚本核验；这是证据化自检，未独立review。Claude验收和brief第9节回填未执行，也未发送消息。
- 原下注：本人在岗≥40%在本样本**不成立**（35.3%）；CRA/药代/算法各≥1合格**不成立**（1/0/0）；两个冷门岗合计≤1合格**成立**（0+1）。小样本与搜索选择偏差须随结论保留；以上是执行方对账，未代替Claude签收。
'''
(D/'zhihu-pilot-2026-10.md').write_text(report)

checks = []
def check(name, ok, detail=''):
    checks.append({'check': name, 'pass': bool(ok), 'detail': detail})
check('csv_and_body_count', sum(1 for _ in csv.DictReader((D/'zhihu-pilot-2026-10-answers.csv').open(encoding='utf-8-sig'))) == len(answers) == 17)
for path, a in answers:
    check('unicode_count:'+path.name, a['body_character_count'] == len(re.sub(r'\s','',a['body'])))
    if a['judgment']=='合格':
        check('recent_personal_long:'+path.name, a['date_local'] >= '2023-10-11' and a['first_person']=='是' and a['body_character_count'] >= 800)
sources = json.loads((E/'candidates.json').read_text())['sources']
for s in sources:
    raw = json.loads((E/s['source_file']).read_text())
    check('candidate_status:'+s['id'], s['qualifies'] == (raw['judgment']=='合格'))
    for c in s['claims']:
        for q in c['quotes']:
            check('quote:'+s['id']+':'+q, len(q)<=30 and q in raw['body'])
check('request_caps', ledger['counts']['baidu_search']<=15 and ledger['counts']['zhihu_page_open']<=25)
check('same_site_intervals_observed', all(e.get('seconds_since_previous_same_site_navigation', 5)>=5 for e in ledger['entries']), 'First Baidu navigation exact timestamp unavailable; this check covers recorded intervals only.')
check('reading_dwell_all', all(e.get('read_seconds',999)>=e.get('required_read_seconds',0) for e in ledger['entries']), 'First CRA page is short by 10.317 seconds; intentionally fail.')
result = {'validated_at':dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(),'result':'CONTENT_PASS_PROTOCOL_NEEDS_CHANGES','independent_review':False,'checks':checks,'body_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f,_ in answers},'qualified_n':len(qualified),'half_n':len(half),'answers_n':len(answers),'known_unmet':['First CRA dwell below requirement','First Baidu exact navigation timestamp missing','Claude independent acceptance pending']}
(E/'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
unexpected = [c for c in checks if not c['pass'] and c['check']!='reading_dwell_all']
print(json.dumps({'result':result['result'],'answers':len(answers),'qualified':len(qualified),'half':len(half),'unexpected_failures':unexpected,'minutes':round(minutes,2)},ensure_ascii=False))
if unexpected:
    raise SystemExit(1)
