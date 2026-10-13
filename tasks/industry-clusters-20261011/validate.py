"""Validate frozen official source counts, CSV lineage, all P1 roles and 10 original-text spots.
Run python3 tasks/industry-clusters-20261011/validate.py; writes validation.json; exits nonzero on failure.
No network. Stdlib. PDF spots use archived pdftotext transcription and source SHA.
"""
import json,csv,pathlib,hashlib,re,collections
root=pathlib.Path(__file__).resolve().parents[2];ev=root/'evidence/industry-clusters-2026-10';data=root/'data/careerdb';batches=json.loads((ev/'integrated-lists.json').read_text())['lists'];checks=[]
def check(name,ok,detail=''):
 checks.append(dict(check=name,pass_=bool(ok),detail=detail))
def compact(s):return re.sub(r'\s+','',s)
clusters=list(csv.DictReader((data/'industry_clusters.csv').open(encoding='utf-8-sig')));links=list(csv.DictReader((data/'role_cluster_links.csv').open(encoding='utf-8-sig')))
for b in batches:
 source=pathlib.Path(b['source_file']);source=source if source.is_absolute() else ev/b['group']/source
 check(b['id']+' source hash',hashlib.sha256(source.read_bytes()).hexdigest()==b['source_sha256'])
 rows=[r for r in clusters if r['名单名称']==b['name'] and r['批次']==b['batch']]
 check(b['id']+' complete source unit',len(rows)==len(b['entries'])==b['total'],b['total'])
 check(b['id']+' unique no',len({str(e['no']) for e in b['entries']})==b['total'])
 check(b['id']+' quote length',len(b.get('standard_quote',''))<=30)
check('source unit count and total',len(batches)==20 and len(clusters)==545)
roles=[r for r in csv.DictReader((data/'research_queue.csv').open()) if r['tier']=='P1']
check('all 50 roles',len(roles)==50 and {r['node'] for r in roles}=={r['岗位节点'] for r in links})
index={r['页码或条目号'].split(';')[0]:r for r in clusters}
for l in links:
 if l['对应依据']:
  eid=l['对应依据'].split(';')[0].split('；')[0];r=index.get(eid)
  check('link lineage '+eid+' '+l['岗位'],bool(r) and l['对应集群或园区']==r['集群或园区名称'] and l['城市']==r['所在城市'] and '原文行业='+r['行业'] in l['对应依据'])
  check('role inference marked '+l['岗位'],'推测' in l['备注'] and l['置信度']!='高')
 else:check('unmapped reason '+l['岗位'],'未找到' in l['备注'])
spots=[('L01',5),('L01',37),('L01',38),('L01',39),('L01',40),('L02',19),('L02',30),('L03',2),('L03',7),('L04',75)]
spotresults=[]
for bid,no in spots:
 b=next(x for x in batches if x['id']==bid);e=next(x for x in b['entries'] if str(x['no'])==str(no));f=pathlib.Path(b['source_file']).with_suffix('.txt');t=f.read_text();pages=t.split('\f');page=e['page'];page_text=pages[page-1]
 ok=compact(e['name']) in compact(page_text) and str(no) in page_text
 check('original spot '+bid+':'+str(no),ok,e['name'])
 spotresults.append(dict(source_unit=bid,no=no,page=page,name=e['name'],source_file=b['source_file'],sha256=b['source_sha256'],match=ok))
source_rows=list(csv.DictReader((root/'docs/research/industry-clusters-2026-10-sources.csv').open(encoding='utf-8-sig')))
for r in source_rows:
 p=root/r['原始文件'];check('registry source hash '+r['原始文件'],p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA256'])
sample=json.loads((ev/'sample-cities.json').read_text());check('sample all 50',len(sample['roles'])==50);check('sample grain',sum(r['sample_n'] for r in sample['roles'])==623 and sum(len(r['missing_ids']) for r in sample['roles'])==28)
for f,h in sample['input_sha256'].items():check('sample input frozen '+f,hashlib.sha256((data/f).read_bytes()).hexdigest()==h)
report=(root/'docs/research/industry-clusters-2026-10.md').read_text();check('report required sections',all('## '+str(i)+'.' in report for i in range(1,8)))
result=dict(status='PASS' if all(c['pass_'] for c in checks) else 'NEEDS_CHANGES',source_units=len(batches),entries=len(clusters),p1_roles=50,successful_links=sum(bool(l['对应依据']) for l in links),unmapped_roles=sum(not l['对应依据'] for l in links),spot_checks=spotresults,checks=checks)
(root/'tasks/industry-clusters-20261011/validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ('spot_checks','checks')},ensure_ascii=False));print('failed',[c for c in checks if not c['pass_']]);raise SystemExit(0 if result['status']=='PASS' else 1)
