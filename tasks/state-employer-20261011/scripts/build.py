#!/usr/bin/env python3
"""离线生成本轮研究清单、来源表、30份文本试分类。python3 build.py。
只读careerdb输入；写研究报告/证据。规则档按已读原文人工设定，未知不自动放行。
"""
from pathlib import Path
import json,csv,re,hashlib,urllib.parse,collections
ROOT=Path(__file__).resolve().parents[3];E=ROOT/'evidence/state-employer-2026-10';D=ROOT/'docs/research';D.mkdir(exist_ok=True)
rows=json.loads((E/'inventory-frozen.json').read_text());rules=json.loads((E/'rules-results.json').read_text());irm=json.loads((E/'inventory-results.json').read_text());byid={i:r for r in rules for i in r['ids']};im={i:r['page'] for r in irm for i in r['ids']};metas=[json.loads(p.read_text()) for p in (E/'snapshots').rglob('meta.json')]
byhost=collections.defaultdict(list)
for m in metas:byhost[urllib.parse.urlsplit(m['url']).netloc].append(m)
def body(m):
 p=ROOT/m.get('path','')/'body.txt';return p.read_text() if p.exists() else ''
def gethost(h,kind):return next((m for m in byhost[h] if m.get('kind')==kind),None)
def pickquote(h,q):
 for m in byhost[h]:
  if q in body(m):return q,m['url'],m['path']+'/body.txt'
 raise ValueError((h,q))
Q={
 'rsj.beijing.gov.cn':('需征得北京市人力资源和社会保障局','有条件','公共免费新闻/资料引用需保留来源；商业/链接/镜像需书面许可，生产自动化未批准'),
 'www.bjsjs.gov.cn':('需征得北京市石景山区政府办公室','有条件','公共免费引用及来源条件；商业内容使用/链接需许可，生产未批准'),
 'rst.sc.gov.cn':('如需转载，请注明来源','有条件','来源注明；未找到商业用途或自动化许可，不据此启动生产抓取'),
 'www.sinopharmgroup.com.cn':('应注明“来源：【国药控股】”','有条件','仅原声明对应作品按其来源要求；第三方内容另核；未确认自动化/商业数据库许可'),
 'wjw.nmg.gov.cn':('不能用于赢利目的','有条件','限新闻性/资料性公共信息及来源例外，商业用途不在已知条件内'),
 'gzw.guizhou.gov.cn':('以新闻性或资料性公共免费信息为使用目的','有条件','公共免费善意引用；不得歪曲，自动化/商业许可未找到'),
 'www.boc.cn':('您可在非商业用途的情况下浏览、下载本网站的内容','有条件','非商业个人浏览；商业拷贝/下载/存储/电子抓取须书面许可'),
 'www.jobmd.cn':('未经Jobmd.cn同意，不得 擅自复制、使用或转载','不可用','当前未获许可，不作为小谷复制/汇总数据来源'),
 'www.crec.cn':('未经我方或其他方事先书面许可','不可用','内容复制/传播/存入检索系统等需事先书面许可'),
 'wsjkw.hlj.gov.cn':('未经本网协议授权不得转载、链接、转贴','不可用','当前无协议授权，不作内容接入'),
 'wjw.fujian.gov.cn':('未经本网协议授权不得转载、链接、转贴','不可用','当前无协议授权，不作内容接入'),
 'wsjkw.shandong.gov.cn':('不得利用本网站发布的内容进行商业性的原版原式地转载','不可用','原版原式商业转载被限制，第三方另需授权；当前用途未证可用'),
 'gzw.gd.gov.cn':('不得利用本网站发布的内容进行商业性的原版原式地转载','不可用','原版原式商业转载被限制，第三方须合法授权'),
 'hc.jiangxi.gov.cn':('不得利用本网站发布的内容进行商业性的原版原式地转载','不可用','原版原式商业转载被限制，第三方须合法授权'),
}
quotes={h:pickquote(h,q) for h,(q,k,c) in Q.items()}
# full service agreement supersedes terse disclaimer for Gaoxiaojob
q='复制、转载、使用、修改、链接、汇编、发表、抓取'
quotes['www.gaoxiaojob.com']=pickquote('agreement.gaoxiaojob.com',q);Q['www.gaoxiaojob.com']=(q,'不可用','2024-07-01协议明确书面同意前不得抓取/汇编/使用；已停止后续内容采集')
ciic=(E/'static-fallback/ciic-terms.txt').read_text();q='任何人不得复制或部分复制、转载或使用'
assert q in ciic;quotes['www.ciiczhaopin.com']=(q,'https://sso.ciiczhaopin.com/serviceagreement','evidence/state-employer-2026-10/static-fallback/ciic-terms.txt');Q['www.ciiczhaopin.com']=(q,'不可用','无Cookie Jina取得协议；商业使用/复制需书面许可，原始HTML仅占位')
# existing rows retained; supplemental URLs recorded as amendments, not erased missing-item history
am=json.loads((E/'inventory-amendments.json').read_text()) if (E/'inventory-amendments.json').exists() else []
for x in am:
 for r in rows:
  if r.get('region')==('四川' if '四川' in x['name'] else '西藏') and r['category']=='国央企综合平台':
   r.update(url=x['url'],publisher=x['name'].split('入口')[0],inventory_status='官方页增量补证；西藏独立门户/招聘栏仍未找到' if '西藏' in x['name'] else '官方联系页补证',official_evidence_url=x['url']);im[r['id']]=x['page'];byid[r['id']]={'robots':x['robots'],'robots_valid':False,'terms':[],'paths':[]}
# coherent robots path matcher supports * and $, handles longest allow rule for generic research UA
# empty/invalid rule text remains unknown; absence of a file never becomes a granted license.
def rp_allow(raw,url):
 groups=[];uas=[];direct=[]
 for l in raw.splitlines():
  l=l.split('#',1)[0].strip()
  if ':' not in l:continue
  k,v=[x.strip() for x in l.split(':',1)];k=k.lower()
  if k=='user-agent':
   if direct:groups.append((uas,direct));uas=[];direct=[]
   uas.append(v.lower())
  elif k in ['allow','disallow'] and uas:direct.append((k,v))
 if uas:groups.append((uas,direct))
 specific=[g for g in groups if any(a!='*' and a in 'xiaoguresearch/1.0' for a in g[0])];chosen=specific or [g for g in groups if '*' in g[0]]
 p=urllib.parse.urlsplit(url);target=p.path+('?' +p.query if p.query else '');matches=[]
 for _,ds in chosen:
  for k,v in ds:
   if not v:continue
   end=v.endswith('$');pat=re.escape(v[:-1] if end else v).replace(r'\*','.*')
   if re.match('^'+pat+('$' if end else ''),target):matches.append((len(v.replace('*','')),k=='allow'))
 return max(matches,default=(0,True))[1]
for r in rows:
 h=urllib.parse.urlsplit(r['url']).netloc;x=byid.get(r['id']) or next((z for z in rules if urllib.parse.urlsplit(z['robots']['url']).netloc==h),None);pg=im.get(r['id']) or gethost(h,'inventory');rb=x['robots'] if x else None
 r['actual_host']=h;r['access_date']='2026-10-11';r['list_path']=urllib.parse.urlsplit(r['url']).path or '/';dm=gethost(h,'detail');r['detail_url']=dm['url'] if dm else '未取样/未找到';r['detail_path']=urllib.parse.urlsplit(dm['url']).path if dm else '未取样/未找到'
 valid=x.get('robots_valid',False) if x else False
 if rb and rb.get('path'):
  p=ROOT/rb['path']/'raw.txt';raw=p.read_text() if p.exists() else ''
  valid=bool(re.search(r'^\s*User-agent\s*:',raw,re.M|re.I)) and rb['status']==200
 else:raw=''
 r['robots_url']=rb['url'] if rb else '未找到';r['robots_snapshot']=rb.get('path','')+('/raw.txt' if rb and rb.get('status')==200 else '/meta.json') if rb and rb.get('path') else '未找到（已停站/未核）';r['robots_status']='有效规则' if valid else f"未找到有效规则；{rb.get('status') if rb else '未核'}"
 r['list_robot_result']=('允许' if rp_allow(raw,r['url']) else '禁止') if valid else '未知'
 r['detail_robot_result']=('允许' if rp_allow(raw,dm['url']) else '禁止') if valid and dm else '未知/未取样'
 r['terms_url']='未找到';r['terms_quote']='未找到';r['terms_snapshot']='未找到';r['terms_version']='未找到';r['rule_conclusion']='不可用';r['condition']='未满足本轮接入证据门槛；并非已证明法律禁止'
 if h in Q:
  q,k,c=Q[h];r.update(rule_conclusion=k,condition=c,terms_quote=quotes[h][0],terms_url=quotes[h][1],terms_snapshot=quotes[h][2]);t=(ROOT/quotes[h][2]).read_text();d=re.search(r'(?:更新日期|生效日期|最后更新日期|发布日期|发布时间)[:：\s]*([0-9]{4}[^\n]{0,26})',t);r['terms_version']=d.group(1) if d else '未找到'
 if r['list_robot_result']=='禁止':r['rule_conclusion']='不可用';r['condition']='robots禁止本轮列表/入口路径；不绕过'
 if pg and (pg.get('blocked') or pg.get('status') in [403,429,412]):r['rule_conclusion']='不可用';r['condition']='出现拒绝/验证，停站'
 r['public_body']='取得公开原始HTML正文（不保证招聘内容完整）' if pg and pg.get('status')==200 and pg.get('body_chars',0)>500 else '未取得目标正文/静态占位/未核'
 r['login_requirement']='本轮所读正文无需登录；投递/其他列表未测' if r['public_body'].startswith('取得') else '未核；未登录/未注册/未使用用户会话'
 r['api_rss_download']='未找到官方数据API/RSS；仅入口页检查，不证明不存在'
 if pg:
  b=body(pg)
  if re.search(r'RSS|rss',b):r['api_rss_download']='页面出现RSS字样；未验证订阅端点或使用许可'
  if re.search(r'附件|下载',b):r['api_rss_download']+='；出现下载/附件字样，具体文件未取样'
 r['sample_source_present']='是' if r.get('sample_n',0)>0 else '否（精确source名；别名未合并）'
 if r['id'].startswith('S'):
  r['first_hand']='否：本次实际证据为牛企转载；标签所指原发布身份未核';
  if r['category']=='高校就业网':r['category']='高校/院系来源标签（人事/就业功能待核）';r['published_content_type']='现有样本转载；源站内容未核';r['recruitment_identity']='未明确（需原公告）';r['condition']+='；仅核实际转载主机，规则不转移给标签原站'
  # rules of aggregate actual host are retained, never presented as rules of unknown original site.
 else:
  r['first_hand']=r.get('first_hand') or ('招聘方可直接发布+转载混合，逐公告核一手性' if r['name'] in ['国聘','国家大学生就业服务平台','丁香人才','高校人才网','中智招聘','中科人才网'] else '否：商业转载/入口导航' if r['category']=='汇总转载站' else '官方主体入口候选；原发/转载逐公告判断')
  r['published_content_type']='门户/目录入口；具体招聘栏目未逐条取得'
  r['recruitment_identity']='未明确（来源类别不能替代公告岗位身份）'
  if r['name']=='北京大学人事部':r['recruitment_identity']='同一单位内混合（列表明确事业编制/劳动合同招聘）'
  if r['name']=='北京大学第三医院':r['recruitment_identity']='同一单位内混合（官网非在编样例+本地在编样本；在编原始官网未复核）'
  if r['name'] in ['国聘','国家大学生就业服务平台','高校人才网','丁香人才','中智招聘','中科人才网']:r['recruitment_identity']='综合混合（含事业单位/企业及其他；非专属编制/国企）'
  if r['category']=='公务员考录':r['published_content_type']='公务员/考试入口；考试网另含职业资格，不均属公务员';r['recruitment_identity']='公务员考录渠道；具体岗位/参公需公告与职位表'
  if r['category']=='央企/地方国企自有招聘官网':r['published_content_type']='本企业招聘入口候选';r['recruitment_identity']='国央企员工招聘候选；集团内研究机构、博士后、派遣仍按公告'
  if r['name']=='西部计划':r['recruitment_identity']='其他：基层志愿服务；不自动授编'
  if r['name']=='军队人才网':r['recruitment_identity']='其他：军队文职单列，非公务员/事业编的同一制度'
 r['repost_chain']='招聘主体原公告→官方主管/考试平台或招聘平台→高校就业网→牛企/汇总站（一般链路推测；具体样本未追全）'
 r['rule_fact']='已取得相关声明；见逐字短引与条件' if h in Q else '未找到完整规则依据（不能推出许可或禁止）';
 r['publisher_verified']='官方目录可证明入口名称；目标主办页未全面核' if r['id'].startswith('P') else '未找到独立官网主办证据' if r['id'].startswith('S') else '候选标注，参见官网正文/声明；未逐条核实法人'
 if pg and pg.get('status')==200:r['existence_snapshot']=pg['path']+'/body.txt';r['inventory_status']+='；本轮目标HTTP200不等于招聘正文完整'
 else:r['existence_snapshot']=r.get('evidence_snapshot','未找到')
 r['publisher_quote']='未找到';r['publisher_snapshot']='未找到'
 if pg and pg.get('status')==200:
  footer=body(pg)[-2500:]
  m=re.search(r'(?:主办单位|主办)\s*[:：]\s*([^\n]{3,90})',footer)
  if m:
   q=m.group(0).split('承办')[0].split('版权所有')[0].split('备案')[0].strip()
   if len(q)<=70:
    r['publisher_quote']=q;r['publisher_snapshot']=pg['path']+'/body.txt';r['publisher']=re.sub(r'^(?:主办单位|主办)\s*[:：]\s*','',q);r['publisher_verified']='官网页脚主办声明已核；未作法人登记穿透核验'
fields=['id','category','name','url','publisher','publisher_type','publisher_verified','publisher_quote','publisher_snapshot','coverage','published_content_type','first_hand','sample_source_present','sample_n','actual_host','inventory_status','existence_snapshot','list_path','detail_url','detail_path','robots_url','robots_status','robots_snapshot','list_robot_result','detail_robot_result','terms_url','terms_version','terms_quote','terms_snapshot','login_requirement','api_rss_download','rule_fact','rule_conclusion','condition','recruitment_identity','repost_chain','access_date']
with (D/'state-employer-platforms-2026-10.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
(E/'final-inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
# deterministic first 10 in mapped-file order; exact ID join to original descriptions.
mapped=[json.loads(l) for l in (ROOT/'data/careerdb/postings_mapped.jsonl').read_text().splitlines()];raw={x['id']:x for x in map(json.loads,(ROOT/'data/careerdb/postings.jsonl').read_text().splitlines())};pil=[]
for g,s in [('国聘','国聘'),('国家大学生就业服务平台','国家大学生就业服务平台'),('医院人事处','北京大学第三医院')]:
 for r in [r for r in mapped if r['source']==s][:10]:
  txt=raw[r['id']]['description'];q='';c='未明确';reason='正文未明确岗位编制、签约关系及国有性质；不得凭单位名/source推断'
  if '按医院非在编员工薪酬标准发放' in txt:q='按医院非在编员工薪酬标准发放';c='非在编（待遇条款文本判断）';reason='岗位待遇明确非在编员工标准；保留转载证据级别，原公告身份需核'
  elif '在编2026年应届毕业生1名' in txt:q='在编2026年应届毕业生1名';c='在编（文本判断）';reason='招聘对象明示在编；官网原始同条公告未复核'
  elif '公司性质\n民营企业' in txt:q='公司性质\n民营企业';reason='转载平台自报民营；可作候选排除，尚非所有权核验；用工合同未明确'
  elif '公司性质\n外商独资/外企代表处' in txt:q='公司性质\n外商独资/外企代表处';reason='转载平台自报外资；不凭该标签认定国央企员工'
  elif '公司性质\n合资企业' in txt:q='公司性质\n合资企业';reason='合资可能含国资；不能自动排除或归国企；合同与持股关系未核'
  elif '机关/事业单位/非营利机构' in txt:q='机关/事业单位/非营利机构';reason='平台合并分类不证明事业编；岗位身份未写明'
  elif '博士后' in r['role']:reason='博士后培养岗位未写明编制，不推断出站后身份'
  pil.append(dict(group=g,source=s,id=r['id'],url=r['url'],company=r['company'],role=r['role'],class_result=c,determinate=c!='未明确',quote=q,reason=reason,posted=r['posted'],archived=r['archived'],description_sha256=hashlib.sha256(txt.encode()).hexdigest(),raw_input='data/careerdb/postings.jsonl',evidence_level='本地牛企转载正文；非原发布方全文复核',ownership='未核（平台自报标签不作国有证明）'))
(E/'pilot-inputs.json').write_text(json.dumps([{'group':x['group'],'id':x['id'],'input_sha256':x['description_sha256'],'raw_input':x['raw_input']} for x in pil],ensure_ascii=False,indent=2))
(E/'pilot-results.json').write_text(json.dumps(pil,ensure_ascii=False,indent=2))
with (E/'pilot-results.csv').open('w',newline='') as f:w=csv.DictWriter(f,list(pil[0]));w.writeheader();w.writerows(pil)
stat={g:{'n':len(xs),'determinate':sum(x['determinate'] for x in xs),'rate':sum(x['determinate'] for x in xs)/len(xs),'classes':dict(collections.Counter(x['class_result'] for x in xs))} for g in dict.fromkeys(x['group'] for x in pil) if (xs:=[x for x in pil if x['group']==g])}
(E/'pilot-statistics.json').write_text(json.dumps(stat,ensure_ascii=False,indent=2))
# All snapshot metadata remains visible, including failed/placeholder requests.
sources=[]
for m in sorted(metas,key=lambda m:(m['url'],m.get('kind',''))):
 h=urllib.parse.urlsplit(m['url']).netloc;rs=[r for r in rows if r['actual_host']==h];pub=rs[0]['publisher'] if rs else '未找到（按目标官网页面核）'
 sources.append(dict(url=m['url'],title=m.get('title') or m.get('kind',''),publisher=pub,version_date='未找到',access_date='2026-10-11',supports='该主机的公开存在性/规则核验；失败页不支持招聘或许可事实',snapshot=m.get('path','')+'/meta.json',layer='脚本公开HTTP，无Cookie',status=m['status']))
for h,(q,u,snap) in quotes.items():sources.append(dict(url=u,title=h+'声明摘录',publisher=next((r['publisher'] for r in rows if r['actual_host']==h),'未找到'),version_date=next((r['terms_version'] for r in rows if r['actual_host']==h),'未找到'),access_date='2026-10-11',supports=Q[h][2],snapshot=snap,layer='web-access静态Jina，无用户会话' if 'static-fallback' in snap else '脚本公开HTTP，无Cookie',status='正文已核'))
idrules=json.loads((E/'identity-rules.json').read_text())
for x in idrules['reliable_signals']+idrules['misleading_signals']+idrules['institutional_bases']:sources.append(dict(url=x['url'],title=x['source_id']+'官方公告/制度',publisher={'www.samr.gov.cn':'全国人大制定；市场监管总局官网转载','www.gov.cn':'国务院；中国政府网发布','lswz.gov.cn':'国家粮食和物资储备局','rsj.beijing.gov.cn':'北京市人社局；延庆区招聘主体见正文','www.12371.gov.cn':'中共中央组织部发布；重庆党建门户转载','njna.nanjing.gov.cn':'南京江北新区卫生健康和民政局','gzw.huaibei.gov.cn':'安徽相润投资控股集团；淮北市国资委转载','baotou.gov.cn':'包头市国资委；包头政府网发布'}.get(urllib.parse.urlsplit(x['url']).netloc,'官网署名见正文'),version_date='原网页日期见快照；不以访问日替代',access_date='2026-10-11',supports=x['interpretation']+'；'+x['boundary'],snapshot=x['body_snapshot'],layer=x['evidence_layer'],status='正文已核'))
for x in json.loads((E/'province-inventory.json').read_text())['rows']:sources.append(dict(url=x['official_evidence_url'],title='官方地方入口导航：'+x['name'],publisher='官方导航主办机构见原文',version_date='未找到',access_date='2026-10-11',supports='仅证明导航存在及指向；不证明当前域名、招聘正文或规则已核',snapshot=x['evidence_snapshot'],layer='脚本公开HTTP，无Cookie',status='导航已核'))
with (D/'state-employer-platforms-2026-10-sources.csv').open('w',newline='') as f:w=csv.DictWriter(f,list(sources[0]));w.writeheader();w.writerows(sources)
print(json.dumps({'inventory_rows':len(rows),'source_labels':len({r['source'] for r in mapped}),'rule_hosts':len(rules),'pilot':stat,'grades':dict(collections.Counter(r['rule_conclusion'] for r in rows))},ensure_ascii=False,indent=2))
