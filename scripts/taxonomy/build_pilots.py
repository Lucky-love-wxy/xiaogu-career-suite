#!/usr/bin/env python3
"""离线职业任务/技能试点。运行 python3 scripts/taxonomy/build_pilots.py。
输入冻结的官方CSV、pilot_config与校招岗位原文；输出两个试点CSV及来源/情境/审查证据。
无联网、无模型、无付费；不存在的URI/空正文不补齐。词项命中是保守召回，不证明技能达标。
"""
import csv,json,pathlib,re,hashlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[2]
EV=ROOT/'evidence/taxonomy-2026-10'; RAW=EV/'raw'; ON=RAW/'onet31/db_31_0_csv'; ES=RAW/'esco120'
csv.field_size_limit(2000000)
def csvrows(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def writejson(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def writecsv(p,rows,fields):
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def readjsonl(p):
 rows=[];bad=[]
 for n,l in enumerate(p.read_text().splitlines(),1):
  try:rows.append(json.loads(l))
  except json.JSONDecodeError:bad.append(n)
 return rows,bad
def norm(s):return re.sub(r'\s+',' ',s).strip()
def duty_section(s):
 # 只查招聘工作内容；职责与任职要求在原公告次序可能相反，优先独立提取职责段。
 markers=list(re.finditer(r'岗位职责[：:]?|工作职责[：:]?|主要职责[：:]?',s))
 if markers:s=s[markers[0].end():]
 elif '职位描述：' in s:s=s.split('职位描述：',1)[1]
 else:return ''
 for m in ['任职资格','任职要求','岗位要求','应聘条件','招聘条件','岗位待遇','薪资福利','联系方式','公司介绍','单位简介','投递说明','应聘方式']:
  if m in s:s=s.split(m,1)[0]
 return norm(s)
def match(rows,alternatives):
 for p in rows:
  # 词项同句、来自职责段；拒绝整份公告跨段拼接。
  for clause in re.split(r'[。；;\n]',p['duty_body']):
   if any(all(t.lower() in clause.lower() for t in terms) for terms in alternatives):
    return p,clause.strip()
 return None,''
suggestions=dict(line.split('\t',1) for line in (ROOT/'scripts/taxonomy/translation_suggestions.tsv').read_text().splitlines() if line.strip())
config=json.loads((ROOT/'scripts/taxonomy/pilot_config.json').read_text()); cards=json.loads((ROOT/'data/careerdb/cards.json').read_text())
post,bad=readjsonl(ROOT/'data/careerdb/postings.jsonl');mapped,_=readjsonl(ROOT/'data/careerdb/postings_mapped.jsonl');posts={r['id']:r for r in post}; tiers={r['node']:r['tier'] for r in csvrows(ROOT/'data/careerdb/research_queue.csv')}
tasks=csvrows(ON/'task_statements.csv'); rating={(r['O*NET-SOC Code'],r['Task ID']):r for r in csvrows(ON/'task_ratings.csv') if r['Scale ID']=='IM'}
occ={r['O*NET-SOC Code']:r for r in csvrows(ON/'occupation_data.csv')}; esco={r['preferredLabel']:r for r in csvrows(ES/'occupations_en.csv')};skills={r['conceptUri']:r for r in csvrows(ES/'skills_en.csv')};rels=csvrows(ES/'occupationSkillRelations_en.csv')
transfer=[];skillout=[];pilotstats=[];foreign=[];cn=[];contexts=[];excluded=[]
for name,code,esconame in config['pilots']:
 node=next(k for k,v in cards.items() if v['name']==name and v['sample_n']>0);assert tiers[node]=='P1'
 candidates=[]
 for m in mapped:
  if m.get('node')!=node:continue
  p=posts.get(m['id']);
  if not p:excluded.append({'node':node,'id':m['id'],'reason':'原始正文缺失或JSONL损坏'});continue
  if '|' in m['role'] or re.search(r'[,，].*[,，]',m['role']):excluded.append({'node':node,'id':m['id'],'reason':'多岗位公告不对当前节点整段计入'});continue
  # 已在岗位卡审核中发现的标签与正文冲突、不属于实际目标任务的两条。
  if m['id'] in ['v8s5ZCCNZ','vU85NCNZt']:excluded.append({'node':node,'id':m['id'],'reason':'上游错配/正文任务不属于当前职业'});continue
  body=duty_section(p.get('description',''))
  if not body:excluded.append({'node':node,'id':m['id'],'reason':'未提取到独立职责正文'});continue
  candidates.append({'id':m['id'],'url':p['url'],'role':m['role'],'duty_body':body,'source_date':p.get('posted','')})
 # 同单位同职责去重，不把重复发布扩大检出证据数。
 dedup={}
 for r in candidates:dedup.setdefault((r['role'],r['duty_body']),r)
 candidates=list(dedup.values());cn.extend(dict(r,node=node) for r in candidates)
 selected=[r for r in tasks if r['O*NET-SOC Code']==code]
 selected.sort(key=lambda r:(r['Task Type']!='Core',-float(rating.get((code,r['Task ID']),{}).get('Data Value',0)),int(r['Task ID'])))
 selected=selected[:10];assert len(selected)==10
 found=0
 for t in selected:
  p,clause=match(candidates,config['task_terms'].get(t['Task ID'],[]));found+=bool(p);rr=rating[(code,t['Task ID'])]
  row={'岗位':name,'node':node,'O*NET职业':occ[code]['Title'],'onet_soc':code,'task_id':t['Task ID'],'任务原文':t['Task'],'Task Type':t['Task Type'],'importance':rr['Data Value'],'rating_scale':'IM (1–5)','rating_n':rr['N'],'rating_date':rr['Date'],'rating_source':rr['Domain Source'],'中国样本状态':'中国样本中出现' if p else '未出现','中国样本证据URL':p['url'] if p else '未出现','中国职责短摘录':clause[:30] if p else '', 'match_basis':'职责同句出现主动作/明确子任务；不等同全部示例' if p else '所核有效职责正文未检出；不证明中国不存在','O*NET链接':f'https://www.onetonline.org/link/details/{code}','data_version':'31.0'}
  transfer.append(row)
  foreign.append({'node':node,'name':name,'type':'onet_incumbent_rated' if t['Domain Source']=='Incumbent' else 'onet_occupational_expert_rated','version':'31.0','onet_soc':code,'task_id':t['Task ID'],'text':t['Task'],'importance':rr['Data Value'],'rating_n':rr['N'],'date':rr['Date'],'domain_source':rr['Domain Source'],'url':row['O*NET链接'],'source_file':'evidence/taxonomy-2026-10/raw/onet31/db_31_0_csv/task_statements.csv','rating_file':'evidence/taxonomy-2026-10/raw/onet31/db_31_0_csv/task_ratings.csv','field_scope':['daily_work','deliverables'],'china_author_denominator':False})
 e=esco[esconame];relations=[r for r in rels if r['occupationUri']==e['conceptUri']];skillfound=0;translated=0
 for rel in relations:
  s=skills[rel['skillUri']];label=s['preferredLabel'].strip();rule=config['skill_terms'].get(label);p,clause=match(candidates,[rule[1]]) if rule else match(candidates,[[suggestions[label]]]) if label in suggestions else (None,'');skillfound+=bool(p);translated+=bool(rule or label in suggestions)
  skillout.append({'岗位':name,'node':node,'ESCO职业':esconame,'esco_uri':e['conceptUri'],'技能URI':s['conceptUri'],'技能英文名':label,'关系类型':rel['relationType'],'中国样本JD是否提到':'提到对应职责词项' if p else ('未检出' if rule else '未检出建议中文名逐字表述；未作语义复核'),'证据URL':p['url'] if p else '未出现' if rule else '未出现（逐字检索口径）','中国职责短摘录':clause[:30] if p else '', '建议中文名':rule[0] if rule else suggestions.get(label,'待译：'+label),'translation_status':'建议译名，待专业校审' if rule or label in suggestions else '未译','data_version':'1.2.0','scope_note':'ESCO职业仅为适用子类型；不能按essential改成中国必需门槛'})
 pilotstats.append({'name':name,'node':node,'valid_cn_jd_n':len(candidates),'onet_top_task_n':10,'onet_found_n':found,'esco_relation_n':len(relations),'esco_found_n':skillfound,'esco_translated_n':translated,'esco_uri':e['conceptUri']})
 for r in csvrows(ON/'work_context.csv'):
  if r['O*NET-SOC Code']!=code or r['Category'] or r['Element Name'] not in ['Duration of Typical Work Week','Time Pressure','Contact With Others','Deal With External Customers','Face-to-Face Discussions','Work Schedules']:continue
  contexts.append(dict(r,china_status='中国侧无同量表对应证据',node=node,name=name,version='31.0'))
writecsv(ROOT/'data/careerdb/onet_transfer_check.csv',transfer,list(transfer[0]));writecsv(ROOT/'data/careerdb/esco_skill_pilot.csv',skillout,list(skillout[0]))
writejson(EV/'pilot-statistics.json',pilotstats);writejson(EV/'onet-foreign-task-sources.json',foreign);writejson(EV/'china-pilot-duties.json',cn);writejson(EV/'work-context-pilot.json',contexts);writejson(EV/'pilot-exclusions.json',excluded);writejson(EV/'input-quality.json',{'invalid_jsonl_lines':bad,'note':'损坏行不静默修复，未混入中国比对正文'})
print(json.dumps({'pilots':len(pilotstats),'tasks':len(transfer),'skills':len(skillout),'stats':pilotstats},ensure_ascii=False))
