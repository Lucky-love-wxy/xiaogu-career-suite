"""Join archived postings by id; count city mentions, never current vacancies.
Run from repo root: python3 tasks/industry-clusters-20261011/sample_cities.py
Input: research_queue.csv, postings_mapped.jsonl, postings.jsonl. Output: evidence JSON + CSV.
Stdlib only, deterministic overwrite; no network; originals untouched.
"""
import csv,json,re,collections,pathlib,hashlib
root=pathlib.Path(__file__).resolve().parents[2];data=root/'data/careerdb';out=root/'evidence/industry-clusters-2026-10'
roles=[r for r in csv.DictReader((data/'research_queue.csv').open()) if r['tier']=='P1']
raw=[json.loads(s) for s in (data/'postings.jsonl').open()];mapped=[json.loads(s) for s in (data/'postings_mapped.jsonl').open()]
assert len({r['id'] for r in raw})==len(raw)
byid={r['id']:r for r in raw}
provinces='北京市 天津市 上海市 重庆市 河北省 山西省 内蒙古自治区 辽宁省 吉林省 黑龙江省 江苏省 浙江省 安徽省 福建省 江西省 山东省 河南省 湖北省 湖南省 广东省 广西壮族自治区 海南省 四川省 贵州省 云南省 西藏自治区 陕西省 甘肃省 青海省 宁夏回族自治区 新疆维吾尔自治区'.split()
def normalize(s):
 s=s.strip()
 if s in ('全国','其它','其他','不限','中国',''):return None
 for c in ('北京','天津','上海','重庆'):
  if s.startswith(c):return c+'市'
 for p in provinces[4:]:
  if s.startswith(p):s=s[len(p):];break
 for alias in ('内蒙古','广西','宁夏','新疆','西藏'):
  if s.startswith(alias):s=s[len(alias):];break
 m=re.match(r'^([^市]+市)',s)
 if m:return m[1]
 if any(x in s for x in ('区','县','省','自治州','盟','全国','海外','其他','其它')):return None
 if re.fullmatch(r'[\u4e00-\u9fff]{2,5}',s):return s+'市'
 return None
result=[];csvrows=[]
for role in roles:
 records={r['id']:r for r in mapped if r['node']==role['node']};cities=collections.Counter();original=collections.Counter();unparsed=collections.Counter();missing=[];empty=[]
 for i in records:
  x=byid.get(i)
  if x is None:missing.append(i);continue
  value=x.get('city','');original[value]+=1
  if not value:empty.append(i)
  cs=set()
  for token in re.split('[,，、;/；]',value):
   city=normalize(token)
   if city:cs.add(city)
   else:unparsed[token]+=1
  cities.update(cs)
 item=dict(node=role['node'],role=role['name'],sample_n=len(records),matched_n=len(records)-len(missing),missing_ids=missing,empty_city_ids=empty,cities=dict(cities.most_common()),raw_city_fields=dict(original),unparsed_tokens=dict(unparsed))
 result.append(item)
 for city,n in cities.most_common():csvrows.append(dict(岗位=role['name'],岗位节点=role['node'],城市=city,样本提及数=n,岗位样本数=len(records)))
(out/'sample-cities.json').write_text(json.dumps(dict(method='按ID关联本地原始city字段；一条多城市分别计一次；不解析省级/区县/全国/其它；医学高校校招存档样本，非在招数量。裸城市名追加市作为展示标准化，未进行行政区划补查。',input_sha256={f:hashlib.sha256((data/f).read_bytes()).hexdigest() for f in ('research_queue.csv','postings_mapped.jsonl','postings.jsonl')},roles=result),ensure_ascii=False,indent=2))
with (out/'sample-cities.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['岗位','岗位节点','城市','样本提及数','岗位样本数']);w.writeheader();w.writerows(csvrows)
print('roles',len(result),'P1 samples',sum(r['sample_n'] for r in result),'missing',sum(len(r['missing_ids']) for r in result),'rows',len(csvrows))
