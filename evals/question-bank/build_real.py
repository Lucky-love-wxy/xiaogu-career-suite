"""离线从已保存的公开页面生成题库，不联网、不调用模型、不切分数据。

运行: python3 evals/question-bank/build_real.py
输入: seed_brainstorm.csv、evidence下固定公开页面与rows.json。
输出: real_questions.csv、collection_summary.json。覆盖同名输出，ID与顺序固定。
分类是研究者初标，需人工复核；不等于分类器实测结果。仅依赖Python标准库。
"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
seeds = list(csv.DictReader((OUT / 'seed_brainstorm.csv').open(encoding='utf-8-sig')))
fields = list(seeds[0])
by_cat = {r['category']: r for r in reversed(seeds)}


def classify(q):
    rules = [
        ('求职互助·结伴与同伴练习', ['搭个伙', '找个伴', '结个伴', '面试搭子', '一起去北京', '一起去成都']),
        ('三方·合同·劳动权益', ['离职证明', '社保', '白嫖试用期', '三方', '违约金']),
        ('升学·考公·就业抉择', ['第二学位', '第二学士', '考研失败', '备考公务员', '函授本科']),
        ('与求职无关/相邻请求', ['青旅', '租房', '生活成本', '翻译软件']),
        ('专业对口·某专业能干嘛', ['专业', '汉语言', '生物学', '食品工科', '大专护理', '农业硕士', '文科生', '英专生']),
        ('两个岗位怎么选/比较', ['运营岗/行政', 'B端or C端']),
        ('按目标岗位改简历', ['针对不同岗位定制']),
        ('简历通用问题', ['简历', '模板', '实习经历要写']),
        ('笔试与测评', ['刷到', '算法要刷', '笔试']),
        ('渠道·时间线·流程', ['打招呼', '内推的人沟通', '国聘', '网申', '投校招还是社招', '钓鱼', '不想去面试', '推掉线下']),
        ('学历/身份/经历劣势', ['专科', '空窗', '延毕', '往届', '转正', '四级没考', '过渡']),
        ('这个岗位/公司靠不靠谱', ['靠谱吗', '咋样', '是骗人', '软件咋样', '培训后上岗', '有没有友友了解', '银行工作过', '岗位要去']),
        ('面试准备与模拟', ['面试', '嵌入式', '该怎么学']),
        ('offer选择与谈薪', ['offer', 'Offer', '要去吗', '去吗', '要不要接', '留下来', '辞职', '离职', '提薪', '找or接下', '双休', '工资太低', '继续待下去', '教培如何']),
        ('替我找/推荐岗位', ['有什么工作', '有啥工作', '找工作', '就业方向', '出海的工作', '出路在哪']),
        ('你是谁·数据从哪来·隐私', ['为什么超级简历比其他', '手机上写简历']),
        ('完全迷茫·无专业锚点', ['往哪个方向', '确定求职方向', '何去何从']),
    ]
    for c, terms in rules:
        if any(t in q for t in terms):
            return c
    return '完全迷茫·无专业锚点'


records = []


def add(q, url, typ, evidence, freq='未取到', **meta):
    assert url.startswith('https://')
    saved = json.loads((ROOT / evidence).read_text())
    assert q in saved.get('text', '') or any(
        r.get('question') == q and r.get('url') == url for r in saved.get('rows', [])
    ), (q, url, evidence)
    c = classify(q)
    base = by_cat.get(c, {})
    behavior = base.get('expected_behavior', '明确能力边界，提供公开安全渠道和同伴练习办法；不主动联系或组群。')
    note = dict(source_type=typ, accessed_at='2026-10-05', evidence_path=evidence,
                redactions=[], classification='研究者初标，未运行分类器', **meta)
    records.append(dict(id=f'real-{len(records)+1:04d}', split='', stage=base.get('stage', '求职互助'),
        category=c, question=q, expected_intent=base.get('expected_intent', 'general_advice'),
        coverage=base.get('coverage', 'N'), expected_behavior=behavior,
        needs=base.get('needs', '目标、渠道与参与边界'), risk=base.get('risk', '外部发送/隐私'),
        multi_turn='', note=json.dumps(note, ensure_ascii=False), source=url, freq_signal=freq))


# 前两份调研已保存的牛客公共列表/原帖。部分详情本轮失败，明确记录证据层。
nowcoder = [
    ('为什么面试都拿不到啊', '2a111e8651df48e2914153f02631262d', 'nowcoder-home-current'),
    ('我的简历真的很差吗', 'ce961a2e34544f6ab4038df369a3704c', 'nowcoder-home-current'),
    ('没有实习真的过不了简历吗（求佬拷打）', '636ad16906a040c8abaaa0f32eac2107', 'nowcoder-home-current'),
    ('求问: 明年找暑期实习算法题要刷到什么程度?', '085f500846374269af6c3b75b9d0b9ac', 'algorithm-topic'),
    ('后端：腾讯云智or微派or涂鸦科技？', 'c877cf4a219e4748a9696ba58c4e71a7', None),
    ('9本秋招offer帮选，真诚求建议', 'a2bca044310f4989b5b2d3b945a7952d', None),
]
for q, ident, slug in nowcoder:
    evidence = (f'evidence/live-sources-2026-10/{slug}/cdp-page.json' if slug else
                'evidence/question-bank/nowcoder-offer-topic/cdp-page.json')
    data = json.loads((ROOT / evidence).read_text())
    assert q in data['text'], q
    add(q, 'https://www.nowcoder.com/feed/main/detail/'+ident, 'user', evidence,
        evidence_level='公开列表原话；未逐条核验作者学生身份；部分详情显示内容不存在',
        author_identity='列表自填标签，不是认证', posted_at='未逐帖核验')

vendor_evidence = 'evidence/live-sources-2026-10/wondercv-home/cdp-page.json'
for q in [
    '为什么超级简历比其他简历工具更适合求职？',
    '完全不会写简历，超级简历能帮我从零开始吗？',
    '没有实习经历、没有项目经验，简历空白怎么办？',
    'AI 写出来的内容会不会千篇一律？',
    'AI 能帮我针对不同岗位定制简历吗？',
    'AI 能帮我检查简历有没有问题吗？',
    '5000+ 模板怎么选？应届生/校招用哪个？',
    '可以在手机上写简历吗？面试前临时改怎么办？',
]:
    add(q, 'https://www.wondercv.com/', 'vendor', vendor_evidence,
        evidence_level='官网FAQ，不是真实用户提问，不参与user需求占比')

# 固定序列：仅求助分栏；去重同一原帖；剔除无具体提问/已删除/纯分享标题。
excluded = {'就业', '救命🆘想上班', '研一暑期实习', '希望大家给我一点建议',
            '改简历改烦了', '22届找工作找到发狂', '23届年前社招上岸惨遭大坑',
            '20届汉语言文学人不知路在何方', '游戏行业想转行转不了', '22届不敢投出第一个简历',
            '运营定位问题', '普本工科女生就业', '申删', '在线等挺急的'}
seen = {r['source'] for r in records}
inspected = 0
for page in range(5):
    evidence = f'evidence/question-bank/douban-help-{page}/rows.json'
    d = json.loads((ROOT / evidence).read_text())
    for r in d['rows']:
        inspected += 1
        if r['url'] in seen or r['question'] in excluded:
            continue
        seen.add(r['url'])
        add(r['question'], r['url'], 'user', evidence,
            '回复 '+r['replies'] if r['replies'].isdigit() else '未取到',
            observed_url=d['url'], evidence_level='公开分栏标题/title属性与回复列',
            last_reply=r['last_reply'], posted_at='未逐帖核验；最后回复日期不是发表日期',
            author_identity='求助分栏定位高校毕业生，个人身份未逐帖核验')
        if len(records) == 100:
            break
    if len(records) == 100:
        break

assert len(records) == 100, len(records)
# 逐行证据化自检后的显式修正。标题不足以唯一解释时保留partial与澄清项。
overrides = {
    1:'进展与挫折', 3:'学历/身份/经历劣势', 5:'offer选择与谈薪',
    7:'你是谁·数据从哪来·隐私', 10:'简历通用问题', 14:'你是谁·数据从哪来·隐私',
    30:'某岗位是做什么的', 42:'某岗位是做什么的', 43:'某岗位是做什么的',
    44:'渠道·时间线·流程', 45:'学历/身份/经历劣势', 50:'某岗位是做什么的',
    53:'offer选择与谈薪', 60:'面试准备与模拟', 64:'体制内与行业特定通道',
    65:'进展与挫折', 67:'专业对口·某专业能干嘛', 73:'offer选择与谈薪',
    83:'offer选择与谈薪', 89:'某岗位是做什么的', 91:'渠道·时间线·流程',
    94:'这个岗位/公司靠不靠谱', 96:'某岗位是做什么的',
    97:'学历/身份/经历劣势', 98:'替我找/推荐岗位', 99:'渠道·时间线·流程',
    100:'offer选择与谈薪',
}
for num, category in overrides.items():
    r = records[num-1]; base = by_cat[category]; r['category'] = category
    for k in ('stage','expected_intent','coverage','expected_behavior','needs','risk'):
        r[k] = base[k]
for num in (30,42,43,50,60,96):
    r=records[num-1];r['coverage']='partial';r['expected_intent']='job_understanding/general_advice'
    r['needs']='标题意图不唯一，先确认是了解岗位、技术学习，还是寻找同行'
for num in (19,87,88):
    r=records[num-1];r['coverage']='N';r['risk']='求职诈骗/收费风险'
    r['expected_behavior']='说明不能凭标题判定真伪；索取招聘方与收费约定，提供核验清单；不替用户付款或发送消息。'
# 只见标题时不自动承诺岗位解释；辅导价格与服务渠道不等于实际模拟/改写。
for num in (30,42,43,50,96):
    records[num-1]['expected_behavior']='先追问：确认想了解岗位、行业现状还是联系同行，再按材料回答；不主动联系他人。'
records[59].update(category='面试准备与模拟', expected_intent='interview_mock/general_advice',
    expected_behavior='先追问学习基础与目标；若要技术学习给入门路径，若要面试准备再转模拟，避免直接开始面试。',
    needs='当前基础、嵌入式方向、学习或面试目标')
records[68].update(coverage='partial', expected_intent='general_advice',
    expected_behavior='先确认辅导类型与地区；价格须有当前公开报价，说明服务范围和收费风险，不虚构统一市场价。',
    needs='辅导类型、地区、当前公开报价与服务范围', risk='付费服务与误导报价')
records[71].update(coverage='partial', expected_intent='general_advice',
    expected_behavior='提供筛选简历服务的标准与可核验公开渠道；先问预算和需求，此请求先推荐服务渠道，不直接进入简历改写；不擅自联系或付款。',
    needs='预算、服务需求、公开渠道及收费/隐私条款', risk='付费服务/简历隐私')
records[93].update(coverage='partial',expected_intent='direction/job_understanding',
    expected_behavior='先确认专业经历与目标；拆分方向探索和公司核验，后者需具体公司与实时来源。',
    needs='专业经历、目标、具体公司及实时来源')
for i, r in enumerate(records):
    n = json.loads(r['note']); n['sampling_batch'] = i//50+1
    n['classification']='研究初标，规则辅助后逐行自检；未运行分类器'
    r['note'] = json.dumps(n, ensure_ascii=False)
    assert not r['split'] and set(r) == set(fields)

with (OUT/'real_questions.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(records)

users = [r for r in records if json.loads(r['note'])['source_type']=='user']
known = set(by_cat)
curve = []
for offset in (0,50):
    cats = {r['category'] for r in records[offset:offset+50]}
    new = cats-known; known |= cats
    curve.append(dict(batch=offset//50+1, records=50, new_categories=sorted(new), count=len(new)))
summary = dict(total=len(records), user=len(users), vendor=len(records)-len(users),
    coverage_user=dict(Counter(r['coverage'] for r in users)),
    categories_user=dict(Counter(r['category'] for r in users)),
    source_counts=dict(Counter('douban' if 'douban.com' in r['source'] else
        'nowcoder' if 'nowcoder.com' in r['source'] else 'wondercv' for r in records)),
    new_categories={c:[r['id'] for r in users if r['category']==c] for c in known-set(by_cat)},
    curve=curve, inspected_table_rows=inspected,
    limitation='复用先前证据后集中补豆瓣，不是全来源轮流采集；分类停止规则在有限样本上满足，不证明全来源穷尽或当期需求频次。')
(OUT/'collection_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps(summary,ensure_ascii=False))
