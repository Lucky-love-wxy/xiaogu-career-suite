"""Rebuild offline research CSV/candidates/validation from saved bodies.
Run: python3 scripts/zhihu_batch/build_outputs.py
Input: evidence/zhihu-batch-2026-10/answer-*.json and annotations.json.
Output: docs/research/zhihu-batch-2026-10-answers.csv; evidence candidates,
summary, verification. No network, card writes, commits, or publishing.
"""
import csv
import datetime as dt
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT/'evidence/zhihu-batch-2026-10'
D = ROOT/'docs/research'
anno = json.loads((E/'annotations.json').read_text())
scope = json.loads((ROOT/'scripts/zhihu_batch/scope.json').read_text())
roles = [a['role'] for a in scope['roles']]
tz = dt.timezone(dt.timedelta(hours=8))
def count(body):
    body = re.sub(r'#[^#\n]+\[话题\]#', '', body)
    return len(re.sub(r'\s', '', body))
def dates(raw):
    dd = {d['type']: d['value'] for d in raw['dates']}
    modified = dd.get('dateModified') or dd['dateCreated']
    day = dt.datetime.fromisoformat(modified.replace('Z','+00:00')).astimezone(tz).date().isoformat()
    return day, ('编辑' if dd.get('dateModified') != dd.get('dateCreated') else '发布')
ledger=json.loads((E/'access-ledger.json').read_text())
stop_sequence=min((e['sequence'] for e in ledger.get('stop_events',[]) if e['site']=='zhihu'),default=10**9)
rows, sources, checks, audit_sources = [], [], [], []
searches = [json.loads(f.read_text()) for f in sorted(E.glob('search-*.json'))]
def discovery_query(raw):
    qid = re.search(r'/question/(\d+)', raw['page_url']).group(1)
    for search in searches:
        if search['role'] != raw['discovery_role']:
            continue
        if any(re.search(r'/question/'+qid+r'(?:/|$)', item.get('mu','')) for item in search.get('results', [])):
            return search['query']
    return '已保存外部检索链接；具体问法未匹配，不补造'
baseline_names = {json.loads(f.read_text())['author'].strip('\u200b\n ') for f in (ROOT/'evidence/zhihu-pilot-2026-10').glob('answer-*.json')}
prior_text = (D/'practitioner-originals-2026-10.md').read_text()
baseline_names |= set(re.findall(r'作者：([^\n]+?)\s*日期：', prior_text))
for path in sorted(E.glob('answer-*.json')):
    raw = json.loads(path.read_text())
    a = anno[path.name]
    assert raw.get('body', '').strip(), 'Do not count an unavailable body: '+path.name
    day, dtype = dates(raw)
    n = count(raw['body'])
    author = raw['author'].strip('\u200b\n ')
    qualified = a['judgment']=='合格'
    old = day < '2023-10-11'
    dims = sorted(set(c['dimension'] for c in a['claims']))
    examples = a.get('detail_examples', [])
    assert all(len(x)<=30 for x in examples), 'Long detail example: '+path.name
    for c in a['claims']:
        assert c['dimension'] in ['日常工作及时间分配','强度与作息','入门薪资','硬门槛','前3年发展']
        assert all(len(q)<=30 and q in raw['body'] for q in c['quotes']), 'Quote mismatch/too long: '+path.name
        assert not old or (c['dimension']=='日常工作及时间分配' and c['historical']), 'Old sensitive dimension: '+path.name
    if qualified:
        assert a['personal']=='是' and len(examples)>=2 and a['claims'], 'Insufficient personal details: '+path.name
        assert not a['template'] and not a['promotional_motive'], 'Template/promotional answer admitted: '+path.name
        source = {'id': 'zhihu-'+raw['answer_url'].split('/')[-1], 'role':a['role'],
          'source_file':path.name,'platform':'zhihu','qualifies':True,
          'full_scope':not all(c['historical'] for c in a['claims']),
          'promotional_motive':False,'dimensions':dims,'scope':a['scope'],
          'author_nickname':author,'identity':'本人自述，未独立认证',
          'date':day,'date_type':dtype,'character_count':n,'claims':a['claims']}
        source['protocol_eligible']=raw['request_sequence'] < stop_sequence
        (sources if source['protocol_eligible'] else audit_sources).append(source)
    rows.append({'岗位':a['role'],'检索岗位':raw['discovery_role'],
      '搜索词': discovery_query(raw),
      '问题标题':raw['question_title'].removesuffix(' - 知乎'),
      '问题链接':re.match(r'https://[^/]+/question/\d+',raw['page_url']).group(),
      '回答链接':raw['answer_url'],'作者昵称':author,'发布或编辑日期':day,'日期类型':dtype,
      '正文字数':n,'本人讲述':a['personal'],'具体内容示例':' / '.join(examples),
      '覆盖维度':' / '.join(dims),'是否当时的情况':('是' if qualified and all(c['historical'] for c in a['claims']) else ('部分' if any(c['historical'] for c in a['claims']) else '否')),
      '推广动机':'有，详见排除理由' if a['promotional_motive'] else '未发现明确商业或外平台导流',
      '疑似模板文':'是（未证实AI生成）' if a['template'] else '否',
      '采集协议状态':'停止点后，仅审计' if raw['request_sequence'] >= stop_sequence else '停止点前（时间记录仍有缺口）',
      '判定':a['judgment'],'不合格原因':a.get('rejection_reason',''),
      '请求序号':raw['request_sequence'],'原文文件':'evidence/zhihu-batch-2026-10/'+path.name,
      '适用边界':a.get('scope','')})
with (D/'zhihu-batch-2026-10-answers.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w = csv.DictWriter(f,fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
(E/'candidates.json').write_text(json.dumps({'sources':sources,'audit_only_sources':audit_sources,'status':'PARTIAL_NOT_ACCEPTED','note':'sources仅停止点前；audit_only_sources不能入卡；全批仍有两次时间缺口，待正式验收'},ensure_ascii=False,indent=2))
answer_urls = [r['回答链接'] for r in rows]
pilot_urls = json.loads((E/'exclude-pilot-answers.json').read_text())['answer_urls']
assert len(answer_urls)==len(set(answer_urls)), 'Duplicate answer captured'
assert not set(answer_urls).intersection(pilot_urls), 'Pilot answer reread'
role_stats = []
for role in roles:
    rr=[r for r in rows if r['岗位']==role]; ss=[s for s in sources if s['role']==role]
    ns={s['author_nickname'] for s in ss}
    searched=[json.loads(f.read_text()) for f in E.glob('search-*.json') if json.loads(f.read_text())['role']==role]
    role_stats.append({'role':role,'answers':len(rr),'qualified':len(ss),'qualified_authors':len(ns),
      'new_authors_against_supplied_baselines':len(ns-baseline_names),
      'content_qualified_including_audit':len(ss)+sum(s['role']==role for s in audit_sources),
      'dedicated_registration_new_authors':0 if role=='医疗器械注册' else None,
      'adjacent_RC_RA_audit_authors':1 if role=='医疗器械注册' else None,
      'question_pages':len({r['问题链接'] for r in rr}),'searches':len(searched),
      'date_range':[min(s['date'] for s in ss),max(s['date'] for s in ss)] if ss else None,
      'reasons':dict(Counter(r['不合格原因'] for r in rr if r['判定']=='不合格'))})
old_reject = []
for s in sources+audit_sources:
    if s['character_count']<800 or s['date']<'2023-10-11':
        old_reject.append({'id':s['id'],'short':s['character_count']<800,'old':s['date']<'2023-10-11'})
ledger=json.loads((E/'access-ledger.json').read_text())
assert ledger['counts']['baidu_search']<=40 and ledger['counts']['zhihu_body_page_open']<=55
timed=[e for e in ledger['entries'] if e.get('opened_at')]
for site in ['baidu','zhihu']:
    ee=[e for e in timed if e['site']==site]
    for previous,e in zip(ee,ee[1:]):
        delta=(dt.datetime.fromisoformat(e['opened_at'])-dt.datetime.fromisoformat(previous['opened_at'])).total_seconds()
        assert delta>=5, 'Known same-site request gap below 5 seconds'
    if site=='baidu':
        for e in ee:
            end=dt.datetime.fromisoformat(e['opened_at'])
            assert sum(0<=(end-dt.datetime.fromisoformat(x['opened_at'])).total_seconds()<3600 for x in ee)<=15
eligible_rows=[r for r in rows if r['请求序号']<stop_sequence]
summary={'answers':len(rows),'protocol_pre_stop_answers':len(eligible_rows),'audit_only_answers':len(rows)-len(eligible_rows),
  'qualified':len(sources),'content_qualified_including_audit':len(sources)+len(audit_sources),
  'per_10':round(10*len(sources)/len(eligible_rows),3),
  'all_content_per_10_audit_only':round(10*(len(sources)+len(audit_sources))/len(rows),3),
  'qualified_unique_nicknames':len({s['author_nickname'] for s in sources}),
  'new_unique_nicknames_against_supplied_baselines':len({s['author_nickname'] for s in sources}-baseline_names),
  'baseline_boundary':'只对照所给试点17篇与practitioner-originals19篇昵称；不宣称全项目或跨平台实名去重',
  'role_stats':role_stats,'old_standard_rejected':old_reject,
  'judgments':dict(Counter(r['判定'] for r in rows))}
(E/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
def target_lengths(page):
    targets=[a for a in page['answers'] if not (a.get('excluded_previous_pilot') or a.get('excluded_previous_capture'))]
    def length(a):
        if 'body_length' in a: return a['body_length']
        if 'body' in a: return len(a['body'].strip())
        return a.get('unicode_without_whitespace')
    return [length(a) for a in targets]
page_lengths={f.name:target_lengths(json.loads(f.read_text())) for f in E.glob('page-*.json')}
verification={'validated_at':dt.datetime.now(tz).isoformat(),'result':'PROTOCOL_FAIL_PARTIAL_NOT_ACCEPTED',
  'checks':['Row/body counts match','Unique answers; no pilot URL repeated','Exact quotes <=30 chars',
    '>=2 concrete details per qualified answer','No old sensitive-dimension claims',
    'No template or promotional answer admitted','Batch/daily caps and known gaps pass','Rolling-hour search cap passes'],
  'independent_review_pending':False,'independent_review':'PASS:修复与审计交付；历史采集协议仍FAIL',
  'stop_sequence':stop_sequence,'requests_after_stop':[e['sequence'] for e in ledger['entries'] if e['site']=='zhihu' and e['sequence']>stop_sequence],
  'unknown_requests':[e['sequence'] for e in ledger['entries'] if e['state']=='UNKNOWN_IN_FLIGHT'],
  'empty_target_pages':[name for name,lengths in page_lengths.items() if lengths and all(n==0 for n in lengths)],
  'unknown_target_pages':[name for name,lengths in page_lengths.items() if any(n is None for n in lengths)],
  'body_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in E.glob('answer-*.json')}}
(E/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2))
print(json.dumps({'answers':len(rows),'qualified':len(sources),'authors':summary['qualified_unique_nicknames'],'old_standard_rejected':len(old_reject)},ensure_ascii=False))
