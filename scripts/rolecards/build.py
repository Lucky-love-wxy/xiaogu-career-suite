#!/usr/bin/env python3
"""岗位证据卡片：离线快照、生成、核验。Python 3 标准库，无模型/网络调用。

python3 scripts/rolecards/build.py snapshot  # 从现有库保存脱敏输入，不覆盖已有快照
python3 scripts/rolecards/build.py build     # 只从 evidence 快照重建 cards/摘要/报告
python3 scripts/rolecards/build.py validate  # 引用、逐字片段、计数、文件集合核验，失败退出1
snapshot 为一次性冻结；输入更新请另开批次，不自动吞并先前改动。
"""
import argparse, csv, hashlib, json, re, sys
from collections import Counter, defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EV = ROOT / 'evidence/role-cards-2026-10'
OUT = ROOT / 'data/careerdb/role_cards'
REPORT = ROOT / 'docs/research/role-cards-2026-10.md'
PILOT = ['临床协调员', '医学事务/医学信息', '药物警戒', '医学理赔/核保', '医学AI/生物医学大模型']
FIELDS = ['name', 'aliases', 'plain_language', 'daily_work', 'deliverables', 'collaborators',
          'work_setting', 'entry_for_fresh', 'metrics', 'growth', 'risks', 'misconceptions', 'questions', 'search_keywords']
VERBS = re.compile(r'负责|协助|参与|完成|开展|进行|撰写|审核|维护|收集|整理|跟进|处理|执行|指导|组织|建立|制定|配合|接待|观察|推广|拜访|评估|监测|分析|设计|研发|编辑|校对|筛选|随访|培训|沟通|开发|管理|优化|构建')
NOISE = re.compile(r'薪资|福利|工资|待遇|万元|元/|\d+\s*[kK]/|联系方式|简历|投递|招聘人数|需求专业|学历要求|公司介绍|工作城市|发布|具备|具有|熟悉|熟练|优先|学习能力|精神|有限公司|能力|实战经验|专业知识培训|技能课程|成长|培养|全职|岗位要求|丰富多彩|行业前沿')
END = re.compile(r'任职要求|任职资格|任职条件|岗位要求|职位要求|招聘要求|资格要求|投递说明|公司介绍|公司简介|公司名称|薪资福利|工作经验|学历与专业|职位福利|任职资格要求|任职资质')
START = re.compile(r'岗位职责|工作职责|工作内容|主要职责|你将负责')
ACTION = re.compile(r'^(?:[^：:，,。]{1,24}[：:]\s*)?(?:负责|协助|参与|完成|开展|进行|撰写|审核|维护|收集|整理|跟进|处理|执行|指导|组织|建立|制定|配合|接待|观察|推广|拜访|评估|监测|分析|设计|研发|编辑|校对|筛选|随访|培训|沟通|开发|管理|优化|构建|支持|牵头|独立完成|利用|运用|确保|对接|针对|基于|根据)')
GENERIC = re.compile(r'上级|领导交办|领导安排|部门安排|其他(?:工作|任务|事务|事件)|方向）|岗位职责')
PII = re.compile(r'联系|邮箱|电话|手机|地址|@|https?://|\b1[3-9]\d{9}\b')
def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def rid(node): return 'role_'+hashlib.sha256(node.encode()).hexdigest()[:12]
def clean(text):
    # 不保存个人联系方式；按行剔除，避免输出片段含电话/邮件。
    return '\n'.join(x for x in text.splitlines() if not PII.search(x))
def tasks(desc):
    lines = desc.splitlines(); start = next((i for i,x in enumerate(lines) if START.search(x)), None)
    if start is not None: lines = lines[start:]
    out = []
    for x in lines:
        if END.search(x.strip()): break
        for s in re.split(r'[；;。\n]',x):
            s = re.sub(r'^[\s\"“（(\d一二三四五六七八九十①②③④⑤⑥、.．)）-]+','',s).strip(' ：:')
            if 8 <= len(s) <= 120 and VERBS.search(s) and ACTION.search(s) and not NOISE.search(s) and not GENERIC.search(s): out.append(s)
    return list(dict.fromkeys(out))
def snapshot():
    dest = EV/'inputs.json'
    if dest.exists(): raise SystemExit('已有冻结快照；使用 build，不自动覆盖。')
    qpath=ROOT/'data/careerdb/research_queue.csv'; mpath=ROOT/'data/careerdb/postings_mapped.jsonl'; ppath=ROOT/'data/careerdb/postings.jsonl'
    queue=list(csv.DictReader(qpath.open())); raw={x['id']:x for x in map(json.loads,ppath.open())}
    nodes={x['node'] for x in queue}; rows=[]
    for m in map(json.loads,mpath.open()):
        if m.get('node') not in nodes: continue
        p=raw.get(m['id']); desc=clean((p or {}).get('description',''))
        role=m.get('role') or ''; reason=[]
        if not p: reason.append('人工补证未合并原始正文；且不将社招混入校招分母')
        if re.search(r'[|｜]|实习生[,，].*实习生',role): reason.append('多岗位标题，未作段落角色分离')
        if not desc: reason.append('缺可核职责正文')
        cache=ROOT/f"evidence/careerdb-2026-10-05/niuqi/job/{m['id']}.html"
        rows.append(dict(id=m['id'],url=m['url'],node=m['node'],company=m.get('company'),role=role,
            education=m.get('edu_level') or '未写',major_classes=m.get('major_classes') or [],
            description=desc,posted=m.get('posted'),archived=m.get('archived'),source=m.get('source'),
            manual=bool(m.get('manual')),excluded=reason,cache_path=str(cache.relative_to(ROOT)) if cache.exists() else None,
            cache_sha256=sha(cache) if cache.exists() else None))
    tree=ROOT/'data/careerdb/question_tree_medical.json'
    dump(dest,dict(schema_version=1,as_of='2026-10-06',queue=queue,postings=rows,
        question_tree=json.loads(tree.read_text()),sources={str(f.relative_to(ROOT)):sha(f) for f in [qpath,mpath,ppath,tree]},
        source_boundary='已有库冻结快照，未重新访问；脱敏正文不是本轮新抓网页；原HTML哈希可追溯。'))

def claim(text, ev, quotes=None, kind='jd_requirement', **extra):
    return dict(text=text,kind=kind,evidence_ids=ev,quotes=quotes or [],**extra)
def qref(eid,text): return dict(evidence_id=eid,text=text)
def load_inputs():
    inputs=json.loads((EV/'inputs.json').read_text())
    path=EV/'quality-decisions.json'
    if path.exists():
        decisions=json.loads(path.read_text())
        for p in inputs['postings']:
            if p['id'] in decisions: p['excluded']+=decisions[p['id']]
    annex=EV/'practitioner-annex.json'
    inputs['practitioners']=json.loads(annex.read_text()) if annex.exists() else {'sources':{},'roles':{}}
    supplemental=EV/'../practitioner-2026-10/practitioner-annex.json'
    if supplemental.exists():
        incoming=json.loads(supplemental.read_text())
        for eid,e in incoming['sources'].items():
            if eid in inputs['practitioners']['sources']:raise ValueError('duplicate supplemental evidence id: '+eid)
            inputs['practitioners']['sources'][eid]=e
        for name,entry in incoming['roles'].items():
            dest=inputs['practitioners']['roles'].setdefault(name,{'evidence':[],'claims':{},'full_scope':False})
            dest['evidence']+=entry['evidence']
            for field,claims in entry['claims'].items():dest['claims'].setdefault(field,[]).extend(claims)
            # 混合节点不能因新增相同子类的作者被升级整卡。
            dest['full_scope']=dest['full_scope'] or entry.get('full_scope',False)
    inputs['practitioner_as_of']=incoming.get('as_of','2026-10-07') if supplemental.exists() else '2026-10-06'
    for e in inputs['practitioners']['sources'].values():
        source=EV/e['source_file']
        raw=json.loads(source.read_text())
        text=raw.get('desc') or '\n'.join(raw.get('paragraphs',[]))
        if sha(source)!=e['source_sha256'] or text!=e['text'] or raw['url']!=e['url'] or raw['title']!=e['title']:raise ValueError('practitioner source binding: '+e['id'])
        author=raw.get('nickname') or raw.get('authorCandidates',[None])[0].strip()
        stamp=raw.get('time') or raw.get('timestamp')
        date=datetime.fromtimestamp(stamp,ZoneInfo('Asia/Shanghai')).date().isoformat() if stamp else raw['date'].strip()[:10]
        if e['author_nickname']!=author or e['date']!=date or e['accessed_at']!=raw['accessed_at']:raise ValueError('practitioner metadata binding: '+e['id'])
    return inputs

def assemble(inputs):
    groups=defaultdict(list)
    for p in inputs['postings']: groups[p['node']].append(p)
    cards=[]
    for row in inputs['queue']:
        node=row['node']; allrows=groups[node]; usable=[x for x in allrows if not x['excluded']]
        # 同一 URL 只计一份；库上游已作company/title去重，保持可核实的URL口径。
        usable=list({x['url']:x for x in usable}.values())
        evidence=[dict(id='Q',type='queue_metadata',title='research_queue.csv 冻结节点',url=None,date=inputs['as_of'],
            scope='标准名称和分类元数据；不是岗位工作事实',text=node,source_file='inputs.json')]
        for p in usable:
            evidence.append(dict(id=p['id'],type='recruitment_jd',title=p['role'],company=p['company'],url=p['url'],date=p['posted'],
                accessed_at=None,snapshot_at=inputs['as_of'],scope='仅该雇主该招聘说明；校招平台样本不等于允许零经验',
                text=p['description'],source_file='inputs.json',archived=p['archived'],cache_path=p['cache_path'],cache_sha256=p['cache_sha256']))
        c=dict(schema_version='role-cards-research-v1',id=rid(node),node=node,family=node.split(' › ')[0],
            parent_id=node.rsplit(' › ',1)[0],tier=row['tier'],pilot=row['name'] in PILOT,evidence_level='partial',
            completion_stage='jd_only_draft',sample_n=len(usable),upstream_sample_n=int(row['sample_n']),
            practitioner_author_n=0,evidence=evidence,missing=['从业者一手分享：未找到可入卡的已核正文，缺2名不同作者',
            '日常体验、考核指标、发展路径与条件化风险：缺从业者证据，不用招聘宣传补齐'],
            excluded_samples=[dict(id=x['id'],url=x['url'],role=x['role'],reasons=x['excluded']) for x in allrows if x['excluded']])
        c.update({f:[] for f in FIELDS})
        c['name']=[claim(row['name'],['Q'],[qref('Q',row['name'])],kind='metadata')]
        titles=defaultdict(list)
        for p in usable: titles[p['role']].append(p['id'])
        for title,ids in sorted(titles.items(),key=lambda x:(-len(x[1]),x[0])):
            cl=claim(title,ids,kind='sample_title',count=len(ids))
            c['aliases'].append(cl); c['search_keywords'].append(dict(cl,kind='suggested_keyword'))
        pairs=[]
        for p in usable:
            pairs.extend((s,p['id']) for s in tasks(p['description']))
        counts=Counter(s for s,e in pairs); chosen=sorted(counts,key=lambda s:(-counts[s],len(s),s))[:8]
        for s in chosen:
            ids=list(dict.fromkeys(e for t,e in pairs if t==s))
            c['daily_work'].append(claim(s,ids,[qref(e,s) for e in ids],count=len(ids),scope='样本雇主写的职责，非从业者体验'))
        # 通用卡人话解释只复述可核职责；多来源综合只在curation文件中显式加入。
        if c['daily_work']:
            first=c['daily_work'][0]
            c['plain_language']=[claim('样本雇主列出的工作包括：'+first['text'].rstrip('，'),
                first['evidence_ids'],first['quotes'],kind='jd_summary',scope='招聘职责摘要，实际体验待核实')]
        else: c['missing'].append('未抽出职责句，plain_language与daily_work留空')
        for field,pat in [('deliverables',r'报告|报表|资料|文档|文件|记录|数据库|代码|方案|材料|模型|数据集|清单'),
                          ('collaborators',r'医生|研究者|受试者|患者|客户|团队|部门|CRA|护士|申办|监管|供应商|合作'),
                          ('work_setting',r'研究中心|医院|出差|驻|现场|实验室|车间|外勤|门店|跟台')]:
            for s,e in pairs:
                if re.search(pat,s) and s not in [x['text'] for x in c[field]]:
                    c[field].append(claim(s,[e],[qref(e,s)],scope='原句包含该字段线索；不补未写的工作地点/频次'))
                if len(c[field])>=4: break
        ids=[p['id'] for p in usable]; edu=Counter(x['education'] for x in usable); majors=Counter(m for p in usable for m in set(p['major_classes']))
        for label, counter, stat in [('学历字段',edu,'education'),('专业类字段',majors,'major_classes')]:
            for value,n in sorted(counter.items()):
                match=[p['id'] for p in usable if (p['education']==value if stat=='education' else value in p['major_classes'])]
                c['entry_for_fresh'].append(claim(f'{len(usable)}份保留的校招平台样本中，{n}份{label}为“{value}”',
                    ids,kind='sample_count',stat=dict(field=stat,value=value,n=n,denominator=len(usable),matched_ids=match)))
        c['entry_for_fresh_note']='专业为上游专业类归类；学历为上游结构字段归一值，非正文统一门槛；校招渠道不证明无经验可入职。'
        for label,pat in [('明确出现应届/实习字样',r'应届|毕业生|实习'),('明确出现经验不限/无经验字样',r'经验不限|无需.*经验|无经验|无工作经验')]:
            matched=[p for p in usable if re.search(pat,p['description']+'\n'+p['role'])]
            if matched:
                c['entry_for_fresh'].append(claim(f'{len(usable)}份保留样本中，{len(matched)}份{label}',ids,
                    kind='sample_count',stat=dict(field='regex',value=pat,n=len(matched),denominator=len(usable),matched_ids=[p['id'] for p in matched])))
        if ids:
            for text in ['这个岗位实际每天做哪些事，各占多少时间？','工作地点、服务对象和协作分工是什么，是否涉及驻点或出差？','是否接受本届无全职经验的应届生，必需学历、专业、证书和培训安排是什么？']:
                c['questions'].append(claim(text,ids,kind='suggested_question',rationale='招聘职责/校招渠道不足以确定实际体验与入职门槛'))
        if len(usable)<3:c['missing'].append(f'招聘正文样本不足3：当前{len(usable)}份；联网补抓未执行')
        if len(c['daily_work'])<4:c['missing'].append('可核职责少于4条，不凑数')
        cards.append(c)
    return cards

def apply_curation(cards):
    path=EV/'curation.json'
    if not path.exists(): return
    cur=json.loads(path.read_text())
    for c in cards:
        for field,claims in cur.get(c['name'][0]['text'],{}).items():
            if field not in FIELDS: raise ValueError(field)
            c[field]=claims

def eligible_chinese_author(e, as_of):
    if e.get('platform') in ('onet','overseas') or not e.get('qualifies'):return False
    try:
        cutoff=datetime.fromisoformat(as_of).date().replace(year=int(as_of[:4])-3)
        return cutoff<=datetime.fromisoformat(e['date'][:10]).date()<=datetime.fromisoformat(as_of).date()
    except (ValueError,KeyError):return False

def practitioner_status(evidence,sample_n,full_scope,as_of):
    eligible=[e for e in evidence if eligible_chinese_author(e,as_of)]
    authors={(e['platform'],e['author_nickname']) for e in eligible}
    unpromoted={(e['platform'],e['author_nickname']) for e in eligible if not e.get('promotional_motive',False)}
    full=sample_n>=3 and len(authors)>=2 and bool(unpromoted) and full_scope
    return len(authors),'full' if full else 'partial'

def longform_status(evidence,sample_n,full_scope,as_of):
    from reading_policy import body_length
    eligible=[e for e in evidence if eligible_chinese_author(e,as_of) and body_length(e['text'])>=(500 if e['platform']=='xiaohongshu' else 800) and e.get('firsthand_scene_or_timeline', e.get('qualifies',False))]
    return practitioner_status(eligible,sample_n,full_scope,as_of)

def apply_practitioners(cards, inputs):
    catalog=inputs['practitioners']
    for c in cards:
        extra=catalog['roles'].get(c['name'][0]['text'])
        if not extra:continue
        ev=[catalog['sources'][eid] for eid in extra['evidence']]
        c['evidence']+=ev
        for field,claims in extra['claims'].items():c[field]+=claims
        c['practitioner_author_n'],c['evidence_level']=practitioner_status(ev,c['sample_n'],extra['full_scope'],inputs['practitioner_as_of'])
        c['longform_practitioner_author_n'],c['longform_evidence_level']=longform_status(ev,c['sample_n'],extra['full_scope'],inputs['practitioner_as_of'])
        c['evidence_level_basis']='历史证据门槛；本次长文门槛另见longform_evidence_level'
        c['overseas_source_n']=sum(e.get('platform') in ('onet','overseas') for e in ev)
        c['completion_stage']='jd_plus_scoped_practitioners'
        c['practitioner_scope_note']='不同作者昵称的本人自述，身份未实名核验；full只表示本批证据数量及角色适用门槛，不表示全部字段完整或行业代表性。'
        c['missing']=[x for x in c['missing'] if not x.startswith('从业者一手分享') and not x.startswith('日常体验、考核指标')]
        if c['practitioner_author_n']<2:c['missing'].append('从业者本人经历仍少于2不同作者')
        if not extra['full_scope']:c['missing'].append('本人分享仅覆盖细分子类：医学事务为MSL，图像算法为CT物理算法；不提升整个混合节点为full')
        for f in ['metrics','growth','risks']:
            if not c[f]:c['missing'].append(f+'未找到可入卡本人经历证据，留空')

def verify(cards, inputs):
    errors=[]; rows={p['id']:p for p in inputs['postings']}; checked=0
    for c in cards:
        es={e['id']:e for e in c['evidence']}; ids={e['id'] for e in c['evidence'] if e['type']=='recruitment_jd'}
        if not ids<=set(rows):
            errors.append((c['id'],'unknown evidence'));continue
        sample=[rows[e] for e in ids]
        catalog=inputs['practitioners']; extra=catalog['roles'].get(c['node'].rsplit(' › ',1)[-1],{'evidence':[],'full_scope':False})
        observed=[e for e in c['evidence'] if e['id'] in catalog['sources']]
        if {e['id'] for e in observed}!=set(extra['evidence']):errors.append((c['id'],'practitioner evidence set'))
        for e in observed:
            from reading_policy import body_length
            if 'body_char_n' in e and e['body_char_n']!=body_length(e['text']):errors.append((c['id'],'body length binding',e['id']))
            if e.get('collection_policy')=='ordinary_reader_longform_v1' and e.get('platform') not in ('onet','overseas') and (body_length(e['text'])<(500 if e['platform']=='xiaohongshu' else 800) or e.get('firsthand_scene_or_timeline') is not True):errors.append((c['id'],'longform policy',e['id']))
            if e!=catalog['sources'].get(e['id']):errors.append((c['id'],'practitioner source binding',e['id']))
        long_n,long_level=longform_status(observed,len(sample),extra['full_scope'],inputs['practitioner_as_of'])
        if observed and (c.get('longform_practitioner_author_n')!=long_n or c.get('longform_evidence_level')!=long_level):errors.append((c['id'],'longform status'))
        author_n,expected_level=practitioner_status(observed,len(sample),extra['full_scope'],inputs['practitioner_as_of'])
        if c['id']!=rid(c['node']) or c['evidence_level']!=expected_level or c['practitioner_author_n']!=author_n:errors.append((c['id'],'identity/status'))
        for e in sample:
            source=es[e['id']]
            if e['excluded'] or e['node']!=c['node'] or source['text']!=e['description'] or source['url']!=e['url'] or source['date']!=e['posted'] or source['title']!=e['role'] or source['company']!=e['company'] or source['cache_path']!=e['cache_path'] or source['cache_sha256']!=e['cache_sha256']:errors.append((c['id'],'source binding',e['id']))
        if es.get('Q',{}).get('text')!=c['node']:errors.append((c['id'],'queue binding'))
        expected_ids={p['id'] for p in inputs['postings'] if p['node']==c['node'] and not p['excluded']}
        if ids!=expected_ids or len(sample)!=c['sample_n']:errors.append((c['id'],'sample_n/input set'))
        for field in FIELDS:
            for x in c[field]:
                checked+=1
                if not x['evidence_ids'] or not set(x['evidence_ids'])<=set(es):errors.append((c['id'],field,'reference'))
                for q in x['quotes']:
                    if q['evidence_id'] not in es or q['text'] not in es[q['evidence_id']]['text']:errors.append((c['id'],field,'quote',q))
                if x['kind'] in ('jd_requirement','jd_summary','research_inference','practitioner_self_report') and not x['quotes']:errors.append((c['id'],field,'no supporting quote'))
                overseas=[es[e] for e in x['evidence_ids'] if es[e].get('platform') in ('onet','overseas')]
                if overseas and (field not in ('daily_work','deliverables') or '海外来源' not in x.get('scope','')):errors.append((c['id'],field,'overseas boundary'))
                if x['kind'] in ('practitioner_self_report','onet_incumbent_rated','overseas_practitioner') and (not x['quotes'] or any(len(q['text'])>30 for q in x['quotes'])):errors.append((c['id'],field,'practitioner quote limit'))
                if x['kind'] in ('sample_title','suggested_keyword'):
                    actual=[p['id'] for p in sample if p['role']==x['text']]
                    if set(actual)!=set(x['evidence_ids']) or len(actual)!=x['count']:errors.append((c['id'],field,'title_count'))
                if x['kind']=='jd_requirement' and 'count' in x:
                    actual=[p['id'] for p in sample if x['text'] in tasks(p['description'])]
                    if set(actual)!=set(x['evidence_ids']) or len(actual)!=x['count']:errors.append((c['id'],field,'duty_count'))
                if x['kind']=='sample_count':
                    s=x['stat']; value=s['value']
                    matched=[p['id'] for p in sample if (p['education']==value if s['field']=='education' else value in p['major_classes'] if s['field']=='major_classes' else bool(re.search(value,p['description']+'\n'+p['role'])))]
                    expected_text=(f'{len(sample)}份保留的校招平台样本中，{len(matched)}份'+('学历字段' if s['field']=='education' else '专业类字段')+f'为“{value}”') if s['field']!='regex' else f'{len(sample)}份保留样本中，{len(matched)}份'+('明确出现应届/实习字样' if value==r'应届|毕业生|实习' else '明确出现经验不限/无经验字样')
                    if x['text']!=expected_text:errors.append((c['id'],field,'count text'))
                    if len(matched)!=s['n'] or set(matched)!=set(s['matched_ids']) or len(sample)!=s['denominator'] or set(x['evidence_ids'])!=ids:errors.append((c['id'],field,'count'))
    return dict(status='PASS' if not errors else 'FAIL',card_n=len(cards),claim_n=checked,errors=errors,
        limitation='引用/片段/计数及补证源绑定；不自动证明改写语义。full仅数量及岗位范围门槛，非实名认证/行业代表性。')

def build():
    inputs=load_inputs(); cards=assemble(inputs); apply_curation(cards); apply_practitioners(cards,inputs)
    # 不合格条目删除，完整写审计；计数/引用不降格改写。
    deleted=[]
    for c in cards:
        for field in FIELDS:
            good=[]
            for x in c[field]:
                one=dict(c); one.update({f:([x] if f==field else []) for f in FIELDS})
                result=verify([one],inputs)
                if result['errors']:deleted.append(dict(card=c['id'],field=field,claim=x,errors=result['errors']))
                else:good.append(x)
            c[field]=good
    OUT.mkdir(parents=True,exist_ok=True)
    for c in cards:dump(OUT/(c['id']+'.json'),c)
    dump(EV/'deleted-claims.json',deleted)
    dump(EV/'validation.json',verify(cards,inputs))
    summaries={c['id']:dict(name=c['name'],sample_n=c['sample_n'],excluded=c['excluded_samples'],daily_work=c['daily_work'],entry_counts=c['entry_for_fresh'],titles=c['aliases']) for c in cards}
    for key,v in summaries.items():dump(EV/'sample-summaries'/f'{key}.json',v)
    dump(EV/'coverage.json',[dict(id=c['id'],name=c['name'][0]['text'],tier=c['tier'],sample_n=c['sample_n'],evidence_level=c['evidence_level'],practitioner_author_n=c['practitioner_author_n'],daily_work_n=len(c['daily_work']),missing=c['missing']) for c in cards])
    report(cards,inputs,len(deleted))
    print(json.dumps(verify(cards,inputs),ensure_ascii=False))

def report(cards,inputs,deleted):
    lines=['# 岗位卡片调研（2026-10-06）','', '**部分验收：招聘证据草稿已补入一批真实公开本人分享，整体170岗位调研仍未完成。** 所有本人经历仅适用所引作者与细分岗位，不作为行业普遍体验。','',
        '## 完成边界','',
        '简报的5试点已形成带引用草稿与流水线。P1/P2/P3全部节点有JSON；这是岗位覆盖，不能冒充170岗位完整研究。用户已指定脉脉、牛客并授权CDP，追加TikHub小红书及现有余额上限US$0.10。本轮通过CDP公开取证与TikHub App V2获取详情；搜索摘要不入卡。','',
        '| 批次 | 有卡片 | full | full比例 | 3份以上可用JD | 日常职责达到4条 |','|---|---:|---:|---:|---:|---:|']
    for tier in ['P1','P2','P3']:
        subset=[c for c in cards if c['tier']==tier]; full_n=sum(c['evidence_level']=='full' for c in subset); lines.append(f'| {tier} | {len(subset)} | {full_n} | {full_n/len(subset):.1%} | {sum(c["sample_n"]>=3 for c in subset)} | {sum(len(c["daily_work"])>=4 for c in subset)} |')
    lines+=['',f'以上full列沿用历史证据门槛；按新长文门槛的full共{sum(c.get("longform_evidence_level")=="full" for c in cards)}张。各卡独立longform字段及新批报告说明门槛，不能把旧短文full当本次长文验收。','', '## 口径和证据限制','',
        '- 库内样本按冻结映射节点、唯一URL计数；名称含多岗位分隔符的页面隔离，不把PM/BD等职责计入CRC。人工补证只有索引记录时不合并为正文，也不把社招混入校招统计。',
        '- 学历统计来自上游归一字段；专业来自上游专业类归类，均不是独立复核后的录用门槛。结构字段与正文可能冲突，保留原文而不替雇主解决。',
        '- 校招页面、实习标签和“经验不限”是三种不同证据。只计出现次数，不从缺少经验要求推出接受无经验。证书未系统抽取，保持未知。',
        '- 除5试点人工精修外，其余165张为自动聚合草稿，未完成逐张语义精修。不可直接向产品用户展示为完整职业解释。',
        '- 原始库有存档职位及来源日期；本轮未重新访问这些JD。accessed_at为空，snapshot_at不是抓取日期。',
        '- 指标、发展、风险和误解缺从业者证据就留空；招聘中的培训/晋升宣传不当实际发展证据。',
        '- 字段采用{text, kind, evidence_ids, quotes}，保留来源性质；这是一份研究schema，不改运行时职业索引契约。',
        '- 正文输入只复制脱敏行；原HTML路径与SHA256用于追溯。新搜索结果为候选，不算已核原文，不用自动摘要填卡。','',
        '## 五张试点','', '| 岗位 | 文件 | 保留JD | 隔离样本 | 证据状态 |','|---|---|---:|---:|---|']
    for c in cards:
        if c['pilot']:lines.append(f'| {c["name"][0]["text"]} | [JSON](../../data/careerdb/role_cards/{c["id"]}.json) | {c["sample_n"]} | {len(c["excluded_samples"])} | {c["evidence_level"]}：{c["practitioner_author_n"]}名本人作者 |')
    lines+=['','## 验证与离线复现','',f'- 全量引用、逐字片段、计数由 validate 核验；删除条目 {deleted} 条。见 evidence/role-cards-2026-10/validation.json 与 deleted-claims.json。',
        '- scripts/rolecards/build.py build 仅读 evidence 输入，重建170张卡片、样本摘要及本报告，补证还需practitioner-annex.json及其引用的正文快照；10-07增量还需practitioner-2026-10/practitioner-annex.json及对应新正文。validate 对真实输出检查，不读取运行时或调用模型。',
        '- 已额外对原HTML缓存核对1401个支持片段，实体解码并去空白后全部匹配；见html-binding-check.json。这不冒充本轮新抓取或原HTML字节逐字匹配。',
        '- 幂等哈希与人工抽查记录见 evidence/role-cards-2026-10/reproduction.json、spot-check.md；独立只读审阅见 tasks/research-2026-10/review-role-cards-2026-10.md。',
        '','```bash','python3 scripts/rolecards/build.py build','python3 scripts/rolecards/build.py validate','```','',
        '## 尚未通过的验收','',
        f'不足3份JD的岗位{sum(c["sample_n"]<3 for c in cards)}个，可核职责少于4条的岗位{sum(len(c["daily_work"])<4 for c in cards)}个。尚有{sum(c["practitioner_author_n"]<2 for c in cards)}岗位缺2名本人作者；混合节点即使有2名MSL作者也保持partial。未覆盖的体验/metrics/growth/risks留空。部分节点不足3JD，未联网补抓；部分节点职责不足4条。P3只完成库内聚合草稿，未做外部研究。候选检索尚未覆盖全部岗位。没有宣布完整调研完成。','',
        '## 对设计的影响','',
        '以下设计建议主要由招聘原文推出；新增本人分享仅按对应细分范围补证，未补证岗位的实际体验仍待复核；不修改提问树或build.py。来源ID均可在对应JSON的evidence和inputs.json中定位。','',
        '1. CRC雇主在医院外不等于工作地点在医院外。现有样本明确研究中心与医生、受试者协作，入口应分别问“是否做诊疗”与“是否接受医院驻点”，不能合为一道问题。来源：[CRC卡](../../data/careerdb/role_cards/role_bd628efdd859.json)，v885nazzz / v8Y5MZLaa。',
        '2. “医学事务/医学信息”混有MSL、医学内容、技术轮岗与多岗位合集。先隔离合集，再按实质职责分卡；B1“围绕临床试验”不足以覆盖全部上市产品医学事务。来源：[医学事务卡](../../data/careerdb/role_cards/role_c0c760f18848.json)，v8U5ZCNnZ / vyYNL5LNL；合集v885NtCMN已隔离。',
        '3. “医学理赔/核保”当前可核正文主要为理赔。不能用理赔样本推断核保日常；设计应把投保前风险评估与出险后案件审核分开，核保仍待补证。来源：[理赔卡](../../data/careerdb/role_cards/role_9532388099aa.json)，v8s5nztnM / vYY5tMaCz；核保划分仅为待核设计建议。',
        '4. 医学AI节点至少包含AIDD、AI化学实验、模型应用开发、医学标注和推广工作，门槛不能混合计数后当统一要求。建议按交付物和任务分组，再讨论是否细分节点。来源：[医学AI卡](../../data/careerdb/role_cards/role_8f7c7258beb3.json)，v8kNLZMaZ / vYl5M55zN / vrm5aatLZ / vrk5ntMZa / vYm55aMCZ。',
        '5. 队列P1仍有“科研岗（博士后/研究助理）”，与brief背景“不调研学术路线”存在范围张力。本轮将该节点全部正文隔离，卡片仅保留元数据；企业研发助理需逐份分离后再纳入。来源：inputs.json中queue节点、question_tree的B7；quality-decisions.json。',
        '6. AIDD例的结构学历字段与正文博士要求存在冲突。这说明仅用结构化门槛做提问树排除存在风险，应保留冲突并要求招聘方确认，不能直接判本科/硕士可进。来源：医学AI卡 evidence v8kNLZMaZ正文“博士学历”与inputs同ID education=硕士；本轮未解决上游冲突。','']
    index=lines.index('## 尚未通过的验收')
    section=['## 2026-10-06原始从业者补证与费用','',
        '- CRC与PV各有2不同作者昵称的具体本人经历，达到3JD+2作者门槛；full不是实名认证、行业代表性或全部字段完整。MSL两名作者只覆盖医学事务节点的子类，因此整卡仍partial。',
        '- 6篇小红书图文详情加1篇牛客CT物理算法本人分享入卡；脉脉4篇已核正文分别是招募宣传、岗位介绍、历史二手案例和JD合集，未计本人数量。牛客帖子带内推，已保留动机说明。',
        '- 小红书仅采用文字正文，图片未审阅；不调用用户资料或评论接口，不保存作者ID/头像/联系方式。每岗位最多保留10候选；搜索候选不当详情正文。',
        '- TikHub成功请求10次：搜索4次、详情6次；[官方单价](https://tikhub.io/xiaohongshu-api)US$0.01，余额9.67→9.57美元，减少US$0.10，达到本次授权上限。免费额度0.05未变化；日统计回读仍8次/0.08，未作为追加请求依据。详见tikhub/manifest.json与billing.json。未充值，Key未持久化，任务窗口Key已清除。',
        '- CRC考证建议、作息、加班和PV个人合规率意见不变成统一录用门槛/考勤/公式。核保只有新发现的候选，详情未读；不能把保险销售分享当核保员经历。',
        '', '| 本人来源 | 适用范围 | 日期 |', '|---|---|---|']
    for e in inputs['practitioners']['sources'].values():
        if e['source_file'].startswith('../practitioner-2026-10/'):continue
        title=e["title"].replace("|", "\\|")
        section.append(f'| [{title}]({e["url"]}) | {e["scope"]} | {e["date"]} |')
    section+=['','本批补证独立只读审阅见 tasks/research-2026-10/review-role-practitioners-2026-10.md；历史招聘草稿PASS不替代本批审阅。','']
    if (EV/'../practitioner-2026-10/practitioner-annex.json').exists():
        section+=['2026-10-07增量作者、海外任务证据及独立预算见 [从业者放量报告](practitioner-evidence-2026-10.md)；以上7源与US$0.10均指10-06批次，不合并为本轮费用。','']
    lines[index:index]=section
    REPORT.parent.mkdir(parents=True,exist_ok=True); REPORT.write_text('\n'.join(lines))

def validate():
    inputs=load_inputs(); cards=[json.loads(p.read_text()) for p in sorted(OUT.glob('*.json'))]
    result=verify(cards,inputs)
    if {c['id'] for c in cards}!={rid(r['node']) for r in inputs['queue']}: result['errors'].append('文件集合不匹配队列')
    result['status']='FAIL' if result['errors'] else 'PASS';dump(EV/'validation.json',result);print(json.dumps(result,ensure_ascii=False));return bool(result['errors'])
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('command',choices=['snapshot','build','validate']);args=ap.parse_args()
    if args.command=='snapshot':snapshot()
    elif args.command=='build':build()
    else:sys.exit(validate())
