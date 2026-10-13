#!/usr/bin/env python3
"""验收证据检查：输入未改、source覆盖、固定30样本复算、引用逐字、元数据限速与详情上限。
python3 validate.py；输出evidence/validation.json；不替代主办方、条款语义与人工独立审阅。
"""
from pathlib import Path
import json,csv,hashlib,collections,urllib.parse
ROOT=Path(__file__).resolve().parents[3];E=ROOT/'evidence/state-employer-2026-10';rows=json.loads((E/'final-inventory.json').read_text());pil=json.loads((E/'pilot-results.json').read_text());expected=json.loads((E/'input-hashes.json').read_text());checks={};errors=[]
checks['inputs_unchanged']=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in expected.items())
mapped=[json.loads(l) for l in (ROOT/'data/careerdb/postings_mapped.jsonl').read_text().splitlines()];raw={x['id']:x for x in map(json.loads,(ROOT/'data/careerdb/postings.jsonl').read_text().splitlines())}
checks['all_source_labels_preserved']={r['source'] for r in mapped}.issubset({r['name'] for r in rows});checks['pilot_n_each']=dict(collections.Counter(x['group'] for x in pil));checks['pilot_ids_unique']=len({x['id'] for x in pil})==30
checks['pilot_join_and_quote']=all(x['id'] in raw and x['quote'] in raw[x['id']]['description'] and x['description_sha256']==hashlib.sha256(raw[x['id']]['description'].encode()).hexdigest() for x in pil)
checks['quotes_exact']=all(r['terms_quote'] in (ROOT/r['terms_snapshot']).read_text() for r in rows if r['terms_quote']!='未找到');checks['quote_limit']=all(len(r['terms_quote'])<=30 for r in rows if r['terms_quote']!='未找到')
checks['conditional_evidence']=all((ROOT/r['terms_snapshot']).exists() and (ROOT/r['robots_snapshot']).exists() for r in rows if r['rule_conclusion']=='有条件')
ids=json.loads((E/'identity-rules.json').read_text());cs=ids['reliable_signals']+ids['misleading_signals']+ids['institutional_bases'];checks['identity_quotes']=all(x['quote'] in (ROOT/x['body_snapshot']).read_text() and len(x['quote'])<=30 for x in cs)
metas=list({(m.get('url'),m.get('started_epoch')):m for p in E.rglob('meta.json') if (m:=json.loads(p.read_text())) and 'started_epoch' in m}.values());b=collections.defaultdict(list)
checks['all_request_meta_n']=len(metas)
checks['identity_file_hashes']=all(x['body_sha256']==hashlib.sha256((ROOT/x['body_snapshot']).read_bytes()).hexdigest() for x in cs)
for m in metas:b[urllib.parse.urlsplit(m['url']).netloc].append(m)
checks['no_scope_excluded_hosts']=not any('zhipin.com' in h or 'maimai.cn' in h for h in b);checks['no_cookies_in_direct_requests']=all(m.get('cookies_sent') is False for m in metas)
checks['detail_max_per_host']=dict(collections.Counter(urllib.parse.urlsplit(m['url']).netloc for m in metas if m.get('kind')=='detail'))
checks['recorded_host_spacing_min_seconds']=min((v-u for a in b.values() for u,v in zip(sorted(m['started_epoch'] for m in a),sorted(m['started_epoch'] for m in a)[1:])),default=None)
# All metadata in the evidence tree is merged and deduplicated by URL plus request start time.
checks['csv_rows']=len(list(csv.DictReader((ROOT/'docs/research/state-employer-platforms-2026-10.csv').open())));checks['source_csv_rows']=len(list(csv.DictReader((ROOT/'docs/research/state-employer-platforms-2026-10-sources.csv').open())))
for k in ['inputs_unchanged','all_source_labels_preserved','pilot_ids_unique','pilot_join_and_quote','quotes_exact','quote_limit','conditional_evidence','identity_quotes','identity_file_hashes','no_scope_excluded_hosts','no_cookies_in_direct_requests']:
 if not checks[k]:errors.append(k)
if any(v!=10 for v in checks['pilot_n_each'].values()):errors.append('pilot_n_each')
if any(v>1 for v in checks['detail_max_per_host'].values()):errors.append('detail_max_per_host')
if checks['recorded_host_spacing_min_seconds'] is not None and checks['recorded_host_spacing_min_seconds']<5:errors.append('spacing')
result={'status':'PASS' if not errors else 'NEEDS_CHANGES','checks':checks,'errors':errors,'boundary':'机械完整性通过不代表主办/许可/全量覆盖全部核验；自动合并所有带时间戳请求meta；旧省级导航原始HTML无完整时标，按fetch脚本与日志独立核','manual_quote_sample':[r['id'] for r in rows if r['rule_conclusion']=='有条件'][:5]};(E/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(bool(errors))
