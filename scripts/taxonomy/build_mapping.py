#!/usr/bin/env python3
"""离线召回195节点的标准候选。python3 scripts/taxonomy/build_mapping.py。
先用人工双语功能词与标准定义召回，再应用明确的混杂/错配判断。
候选未通过逐样本语义审阅时保持provisional；不能按相似度定exact。
"""
import pathlib,json,csv,re,collections
R=pathlib.Path(__file__).resolve().parents[2];E=R/'evidence/taxonomy-2026-10';S=E/'raw/esco120';csv.field_size_limit(2000000)
def read(name):return list(csv.DictReader((S/name).open(encoding='utf-8-sig')))
groups={r['code']:r for r in read('ISCOGroups_en.csv')};esco=read('occupations_en.csv');seeds=json.loads((R/'scripts/taxonomy/mapping_seeds.json').read_text());nodes=json.loads((E/'node-review-inputs.json').read_text());pcs=json.loads((R/'scripts/taxonomy/pilot_config.json').read_text());pins={n:e for n,c,e in pcs['pilots']};oncodes={n:c for n,c,e in pcs['pilots']}
on=list(csv.DictReader((E/'raw/onet31/db_31_0_csv/occupation_data.csv').open()));onby={r['O*NET-SOC Code']:r for r in on}
seed={n:c for c,names in seeds['groups'].items() for n in names.split('|')}
# 召回词用于任务定义；不是入职资格或exact判定。
lex={'诊断':'diagnos','治疗':'treat','护理':'nurs','接待':'reception','试验':'trial','研究':'research','注册':'regulat','药品':'pharmaceut','药物':'drug','生物':'biolog','分析':'analys','实验':'laborator','检测':'test','质量':'quality','销售':'sales','客户':'customer','会计':'account','财务':'financ','投资':'invest','文献':'scientific','稿件':'text','编辑':'edit','翻译':'translat','口译':'interpret','编程':'program','软件':'software','数据':'data','数据库':'database','算法':'comput','网络':'network','安全':'safety','电气':'electrical','电子':'electronic','机械':'mechanical','工艺':'process','化学':'chemical','合成':'chemical','材料':'material','环保':'environment','设计':'design','教师':'teach','教学':'teach','课':'education','采购':'purchas','运输':'transport','物流':'logistic','理赔':'claim','受试者':'patient','沟通':'communicat','管理':'manag','记录':'record','评估':'evaluat','维护':'maintain','统计':'statistic','报表':'report','营销':'market','市场':'market','社区':'social','景观':'landscape','施工':'construction','建筑':'building','测量':'survey','招募':'recruit','人力':'human resource','合同':'contract','规划':'plan','排版':'publish','舞蹈':'dance','花卉':'flower','旅游':'travel','航空':'flight','车辆':'vehicle','设备':'equipment'}
rows=[];recall=[]
for x in nodes:
 name=x['name'];code=seed.get(name,'');issue=seeds['issues'].get(name,'');none=seeds['none'].get(name)
 if name in ['作者/撰稿人','环境采样/检测员','经理助理']:none=issue
 if code and code not in groups:raise ValueError('未知ISCO码 '+code)
 text=' '.join(x['titles']+x['duties']);terms={en for zh,en in lex.items() if zh in text};candidates=[]
 for o in esco:
  if code and o['iscoGroup']!=code:continue
  if not code:continue
  d=(o['preferredLabel']+' '+o['description']).lower();score=sum(1 for en in terms if en in d)
  if score:candidates.append((score,o))
 candidates.sort(key=lambda v:(-v[0],v[1]['code']))
 selected=[]
 if name in pins:selected=[next(o for o in esco if o['preferredLabel']==pins[name])]
 # 其他召回第一名保留在mapping-candidates，不写正式URI，防止相似度冒充已审职业。
 # 未对跨职业的混合公告选择一个细类。只保留待拆问题，不以第一名硬定职业。
 multi=any('|' in t or len(re.findall(r'[,，]',t))>=2 for t in x['titles'])
 needs_split=bool(none or multi or issue)
 mtype='none' if none else 'narrower' if needs_split else 'broader'
 if name=='临床医生（科室未细分）':mtype='narrower'
 # 单条样本缺职责不构成定义匹配；节点数保留，但标准字段是候选，不作为认可码。
 if not x['duties'] and not none:mtype='none';none='原始职责为空，仅名称不能确定主要工作任务'
 reason=none or issue or ('原始岗位有多岗公告；须分离后逐项映射' if multi else '职责词项召回到标准定义，现有节点是标准组的行业/职能子集；仍待逐条语义审阅')
 quote=(selected[0]['description'] if selected else groups.get(code,{}).get('description',''))[:30]
 if quote:reason+='；定义短摘录：'+quote
 rows.append({'node':x['node'],'name':name,'sample_n':x['sample_n'],'isco_code':code if not none else '', 'isco_title':groups[code]['preferredLabel'] if code and not none else '', 'esco_uri':'|'.join(o['conceptUri'] for o in selected) if not none else '', 'esco_title':'|'.join(o['preferredLabel'] for o in selected) if not none else '', 'dadian_code':'','dadian_title':'','onet_soc':oncodes.get(name,''),'onet_title':onby[oncodes[name]]['Title'] if name in oncodes else '', 'match_type':mtype,'confidence':'low' if needs_split or not x['duties'] else 'medium','reason':reason,'issue':'节点混杂' if needs_split else '其他' if none else '粒度不一致','review_status':'provisional：标准候选已召回，非195条最终映射验收','standard_basis':'ESCO1.2.0内嵌ISCO-08定义；大典编码未取得'})
 recall.append({'node':x['node'],'title_n':len(x['titles']),'duty_terms':sorted(terms),'candidate_isco_code':code,'candidates':[{'score':s,'uri':o['conceptUri'],'label':o['preferredLabel'],'definition':o['description'],'code':o['code']} for s,o in candidates[:5]],'selected_subtype':pins.get(name),'raw_titles':x['titles']})
assert len(rows)==195 and len({r['node'] for r in rows})==195
with (R/'data/careerdb/node_mapping_standards.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(E/'mapping-candidates.json').write_text(json.dumps(recall,ensure_ascii=False,indent=2)+'\n');counts=collections.Counter(r['match_type'] for r in rows);(E/'mapping-statistics.json').write_text(json.dumps({'row_n':195,'candidate_match_type':dict(counts),'final_accepted_mapping_n':0,'status':'候选层，缺逐节点语义审阅与大典编码；不能当可映射率'},ensure_ascii=False,indent=2)+'\n');print(dict(counts))
