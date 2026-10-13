"""Build research CSVs from frozen official list transcription JSON, with source hashes.
Run: python3 tasks/industry-clusters-20261011/build_tables.py (repo root or any cwd).
Stdlib only; deterministic overwrite of this brief's tables; no network or runtime changes.
"""
import pathlib,json,csv,hashlib,collections,re
root=pathlib.Path(__file__).resolve().parents[2];ev=root/'evidence/industry-clusters-2026-10';out=root/'data/careerdb'
def writecsv(path,rows,fields):
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
batches=[]
for group in ('national','alternatives','regional'):
 p=ev/group/'lists.json'
 if not p.exists():raise RuntimeError('Missing '+str(p))
 x=json.loads(p.read_text())
 for b in x['lists']:
  b=dict(b);b['group']=group
  assert b['total']==len(b['entries']),(b['name'],b['batch'])
  assert len({str(e['no']) for e in b['entries']})==b['total']
  source=ev/group/b['source_file'];assert source.is_file(),source
  b['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
  batches.append(b)
geo=json.loads((root/'tasks/industry-clusters-20261011/geography.json').read_text())
province_by_city={c+'市':p for p,cs in geo['prefecture_provinces'].items() for c in cs.split()}
for b in batches:
 for e in b['entries']:
  original=e.get('city','');parts=[];notes=[]
  for c in original.split('、') if original else []:
   v=geo['county_to_prefecture'].get(c,c if c.endswith('市') else c+'市')
   parts.append(v)
   if v!=c:notes.append(c+'→'+v)
   if c in geo['county_to_prefecture'] and not e.get('district'):e['district']=c
  e['city']='、'.join(dict.fromkeys(parts))
  if not e.get('province') and parts:
   ps={province_by_city.get(c,c if c in ('北京市','天津市','上海市','重庆市') else '') for c in parts}
   if '' not in ps:e['province']='、'.join(sorted(ps));notes.append('按地级市补省字段')
  p=e.get('province','')
  if p and not p.endswith(('省','市','自治区')):e['province']=p+'市' if p in ('北京','天津','上海','重庆') else p+'省'
  e['note']='；'.join(filter(None,[e.get('note',''),e.get('geography_note',''),'行政字段规范化（非原文）：'+'；'.join(notes) if notes else '', '原文地理范围未解析为地级市；保留名称，不猜城市' if not original else '']))
rows=[];index={}
for k,b in enumerate(batches,1):
 bid=f'L{k:02}'
 b['id']=bid
 for e in b['entries']:
  eid=bid+':'+str(e['no']);index[eid]=(b,e)
  rows.append(dict(名单名称=b['name'],批次=b['batch'],集群或园区名称=e['name'],所在省=e.get('province',''),所在城市=e.get('city',''),所在区县=e.get('district',''),行业=e.get('industry',''),行业归类=e.get('category','其他'),来源文件=str((ev/b['group']/b['source_file']).relative_to(root)),页码或条目号=f"{eid}; "+str(e.get('page','')),来源URL=b['source_url'],SHA256=b['source_sha256'],地理处理说明=e.get('note',''),证据状态=b.get('nature',b.get('evidence_status','官方原文件已归档'))))
fields=['名单名称','批次','集群或园区名称','所在省','所在城市','所在区县','行业','行业归类','来源文件','页码或条目号','来源URL','SHA256','地理处理说明','证据状态']
writecsv(out/'industry_clusters.csv',rows,fields)
roles=[r for r in csv.DictReader((out/'research_queue.csv').open()) if r['tier']=='P1']
config=json.loads((root/'tasks/industry-clusters-20261011/role_industries.json').read_text());categories={r:cat for cat,names in config.items() for r in names}
assert len(categories)==50 and {r['name'] for r in roles}==set(categories)
links=[]
# Only sector language in original supports a link; role->employer is always a hypothesis.
patterns={'生物医药':r'生物医药|生物药|生物制药|医药|制药|生物产业|化学原料药', '医疗器械':r'医疗器械|医疗设备|诊断试剂|体外诊断', '人工智能与软件':r'人工智能|软件|信息技术服务', '临床研究服务':r'CRO|临床研究|临床试验|医药研发服务|合同研究', '医疗健康服务':r'医疗服务|健康服务|康复服务|医疗健康服务'}
for r in roles:
 cat=categories[r['name']];found=[]
 for eid,(b,e) in index.items():
  if cat in patterns and re.search(patterns[cat],e.get('industry','')):
   if not e.get('city'):continue
   found.append((eid,b,e))
 for eid,b,e in found:
  conditional='仅限软件/AI企业产品岗位，跨行业产品经理不适用。' if r['name']=='产品经理' else ''
  links.append(dict(岗位=r['name'],主要雇主行业=cat,对应集群或园区=e['name'],城市=e['city'],对应依据=eid+('; p'+str(e['page']) if e.get('page') else '')+'；原文行业='+e['industry'],置信度='低' if r['name'] in ('产品经理','科研岗（博士后/研究助理）','生物学研究人员','医学写作','临床数据管理/生物统计') else '中',备注='推测：该岗位可能受雇于'+cat+'相关企业；名单只证明行业载体，未证明该岗位在此招聘或主要集中于此。'+conditional+e.get('note',''),岗位节点=r['node']))
 if not found:
  links.append(dict(岗位=r['name'],主要雇主行业=cat,对应集群或园区='',城市='',对应依据='',置信度='低',备注='未找到：已收录完整批次无可定位的该细分行业条目（或条目城市未载）。推测：岗位雇主行业仅作分类；服务外包城市/综合高新区不能直接证明此岗位分布。',岗位节点=r['node']))
writecsv(out/'role_cluster_links.csv',links,['岗位','主要雇主行业','对应集群或园区','城市','对应依据','置信度','备注','岗位节点'])
(ev/'integrated-lists.json').write_text(json.dumps(dict(lists=batches),ensure_ascii=False,indent=2))
print('batches',len(batches),'entries',len(rows),'roles',len(roles),'links',len(links),'unmapped',sum(not x['对应依据'] for x in links))
