"""Generate the brief report and source registry from frozen evidence and CSVs.
Run python3 tasks/industry-clusters-20261011/write_report.py. Stdlib; local deterministic outputs only.
"""
import json,csv,pathlib,hashlib,re,html,collections
root=pathlib.Path(__file__).resolve().parents[2];ev=root/'evidence/industry-clusters-2026-10';doc=root/'docs/research';data=root/'data/careerdb';doc.mkdir(exist_ok=True)
batches=json.loads((ev/'integrated-lists.json').read_text())['lists'];clusters=list(csv.DictReader((data/'industry_clusters.csv').open(encoding='utf-8-sig')));links=list(csv.DictReader((data/'role_cluster_links.csv').open(encoding='utf-8-sig')));samples=json.loads((ev/'sample-cities.json').read_text())['roles']
source_rows={}
for b in batches:
 source_rows[b['source_url']]=dict(url=b['source_url'],标题=b['name']+' '+b['batch'],发布方=b['publisher'],文号或日期=b.get('document_number',b['date']),访问日期='2026-10-11',支撑哪条结论='完整收录单元 '+b['id']+' 共'+str(b['total'])+'条；名单存在、条目行业及地域',原始文件=str(pathlib.Path(b['source_file']).relative_to(root)) if pathlib.Path(b['source_file']).is_absolute() else str((ev/b['group']/b['source_file']).relative_to(root)),SHA256=b['source_sha256'],取证层='脚本静态下载原件')
# One official attachment may contain several complete sub-tables: preserve all lineage.
for u,r in source_rows.items():
 shared=[b for b in batches if b['source_url']==u]
 if len(shared)>1:
  r['标题']=shared[0]['name']+' / '+'、'.join(b['batch'] for b in shared)
  r['支撑哪条结论']='完整来源分表 '+ '+'.join(b['id'] for b in shared)+'；'+'+'.join(str(b['total']) for b in shared)+'='+str(sum(b['total'] for b in shared))+'条；行业及地域原文'
 if any(b.get('document_date') for b in shared):
  r['文号或日期']='正文'+shared[0]['document_date']+'；上网'+shared[0]['date']
for group in ('national','alternatives','regional'):
 for p in sorted((ev/group).glob('*manifest*.json')):
  m=json.loads(p.read_text());m=m if isinstance(m,list) else m.get('items',[])
  for item in m:
   u=item.get('url','');name=item.get('file','')
   f=ev/group/name
   if not u or not name or not f.is_file() or item.get('error') or 'robots' in name:continue
   if u in source_rows:continue
   title=name;date='未载/未核';publisher='官方发布方见原文'
   if f.suffix in ('.html','.htm'):
    text=f.read_text(errors='replace');t=re.search(r'<title[^>]*>(.*?)</title>',text,re.S|re.I)
    if t:title=html.unescape(re.sub('<.*?>','',t[1])).strip()
    d=re.search(r'(?i)<meta[^>]+name=["\x27](?:pubdate|pubdate_time|publishtime|publishdate)["\x27][^>]+content=["\x27]([^"\x27]+)',text)
    if d:date=d[1]
   source_rows[u]=dict(url=u,标题=title,发布方=publisher,文号或日期=date,访问日期='2026-10-11',支撑哪条结论=group+'/summary.md 对应存在性、政策、统计粒度、引用条件；不保证该页含完整名单',原始文件=str(f.relative_to(root)),SHA256=hashlib.sha256(f.read_bytes()).hexdigest(),取证层=item.get('layer','脚本静态下载'))
sw=ev/'software/notice-web-extract.txt';u='https://www.miit.gov.cn/zwgk/wjgs/art/2024/art_588906fa60254833b9de827e8aa97c30.html'
source_rows[u]=dict(url=u,标题='2023年中国软件名城评估结果公布',发布方='工业和信息化部信息技术发展司',文号或日期='工信部信发函〔2023〕383号；2023-12-29；网页2024-01-09',访问日期='2026-10-11',支撑哪条结论='通知存在；附件全表未取得，不纳入主表',原始文件=str(sw.relative_to(root)),SHA256=hashlib.sha256(sw.read_bytes()).hexdigest(),取证层='web-access静态正文提取；非HTML原件/非附件')
overrides=json.loads((root/'tasks/industry-clusters-20261011/source_overrides.json').read_text())
for r in source_rows.values():
 name=pathlib.Path(r['原始文件']).name
 if name in overrides:r.update(overrides[name])
# Background attachments not used for a conclusion do not belong in the citation registry.
source_rows={u:r for u,r in source_rows.items() if '不作报告结论依据' not in r['支撑哪条结论']}
toy=ev/'examples/toy-shantou-web-result.txt'
if toy.exists():
 source_rows['https://www.shantou.gov.cn/stsgxj/gkmlpt/content/2/2357/post_2357762.html']=dict(url='https://www.shantou.gov.cn/stsgxj/gkmlpt/content/2/2357/post_2357762.html',标题='汕头两产业集群入选省级榜单',发布方='汕头市工业和信息化局',文号或日期='索引114405005555974461/2024-00282；成文2024-07-21；发布2024-07-31',访问日期='2026-10-11',支撑哪条结论='官方消息正文明确澄海玩具创意入选2024广东省名单；原附件及条号未取得',原始文件=str(toy.relative_to(root)),SHA256=hashlib.sha256(toy.read_bytes()).hexdigest(),取证层='web-access静态正文open提取；非原HTML/非认定附件')
with (doc/'industry-clusters-2026-10-sources.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(next(iter(source_rows.values()))));w.writeheader();w.writerows(source_rows.values())
def rel(p):return str(p.relative_to(doc)) if p.is_relative_to(doc) else str(p)
def row(values):return '| '+' | '.join(str(v).replace('|','／').replace('\n',' ') for v in values)+' |'
parts=['# 官方产业集群名单与小谷 P1 岗位地域对应','\n访问日期：2026-10-11。对象：research_queue.csv 中50个P1岗位。状态：研究交付；不是当前岗位地域市场全景，未取得材料见第7节。', '''
## 1. 结论

官方名单可用于展示“已认定或公开展示的行业载体在哪里”。本次归档20个完整来源单元545条，包含国家先进制造、中小企业特色集群、地方园区、AI先导区/试验区和服务外包城市；不同年份/层级有重叠，545不是独立现行集群数。可明确落到上海、北京、苏州、泰州、连云港、无锡、深圳、广州、天津、长沙、海口等地的生物医药/医疗器械载体，以及北京、上海、南京、成都等地的软件/AI载体；这些证据不能证明岗位“主要集中”于上述城市。50岗均已处理，28岗有条件对应，22岗未找到直接对应；全部岗位→雇主行业对应均为推测，服务岗位与宽泛平台岗位需要招聘量或从业者证据补充。正式行政认定文件可按法律与文件性质引用，商业展示应保留原名、来源、日期和条号；官方网页公开不等于手册图片、年鉴编排等均已获得复制许可。逐条依据见下表、第3/5/6节与来源表。

## 2. 名单盘点

“未找到”指本次未取得对应原始完整名单，不等于名单不存在。最新可得版本与当前有效合集不同。标准短摘是认定程序/范围摘要，不代替完整准入指标。取证层主要为脚本静态下载；商务部2021通知另有Chrome CDP正文。每份收录来源的SHA256在主CSV和来源CSV中保存，全部原始附件或页面在evidence目录；下表以L编号定位来源单元。

| ID | 名称/批次 | 发布方 | 文件日期/上网日期 | 数量/附件 | 程序或范围原文短摘 | 原文件 |
|---|---|---|---|---|---|---|''']
for b in batches:
 parts.append(row([b['id'],b['name']+' / '+b['batch'],b['publisher'],b.get('document_date',b['date'])+(' / '+b['date'] if b.get('document_date') else ''),str(b['total'])+' / 已收齐',b.get('standard_quote','未找到'),f"[原文]({b['source_url']})"]))
parts.append('''
上海L15（以主表实际L编号为准）按官方招商手册展示全量收录，引用定位为印刷页；另存2022认定公告目录及原图。招商手册与认定文件性质分别保留。浙江115园分3表，各自独立序号；不能从园区名称猜其细分行业。AI三份城市函每份只有1项，完整的是单份批复，不是全国2021年总表。

| 起点体系 | 核实结论与原始文件边界 | 最新可得与覆盖行业 |
|---|---|---|
| 国家先进制造业集群 | 已核实，2022累计45、2024新增35完整原PDF | 最新取得正式批2024；2026遴选线索不能当已公布结果；新一代信息技术、高端装备、医药等见原条目 |
| 国家战略性新兴产业集群 | 存在已核实；原始66条认定全表未找到，未导入CSV | 发改委2021官方分析记2019首批66，涉及12领域；含生物医药17、AI4、信息技术服务7，但不能从领域计数推城市 |
| 中小企业特色产业集群 | 已核实，2023/2025各100原PDF | 最新取得2025第四批；2026国家正式全表未找到；2022复核97与2024批未收齐；历史条目不能当全部现行 |
| 创新型产业集群 | 存在已核实；2022年46条全量原附件未找到 | 科技部地方动态可证存在，不证明全国全表；现主管工信部，2026新管理办法未归档正文，当前准入指标未核，不沿用旧标准 |
| 国家高新技术产业开发区 | 存在已核实；178完整原名单未取得 | 国务院批准/工信部主管；2025政府转载178仅作存在性，前50排名不能充全表 |
| 国家生物产业基地、国家级医药园区 | 基地存在已核实；23条全表及统一本体“国家级医药相关产业园区”全表未找到 | 发改委2023会议称23，举6城市而非全表；高技术基地通用定义不是生物基地准入表 |
| AI创新应用先导区 | 官方政府门户转载工信部新增名单5+3收齐 | 2022材料累计11是历史时点，未核现行全表；同一先导区不等于所在城市所有企业 |
| 新一代AI创新发展试验区 | 科技部三份2021单城市批复原文收齐 | 郑州/沈阳/哈尔滨3函，不冒充全国全表；2023建20左右是指引目标 |
| 非官方园区排名 | 未纳入官方主表 | 本次不收集协会/机构排名；不存在与官方认定混表 |

各体系范围、标准来源、文号、版本与失败证据详见[国家子研究](../../evidence/industry-clusters-2026-10/national/summary.md)、[地方/AI子研究](../../evidence/industry-clusters-2026-10/regional/summary.md)、[替代来源子研究](../../evidence/industry-clusters-2026-10/alternatives/summary.md)。完整来源表为[industry-clusters-2026-10-sources.csv](industry-clusters-2026-10-sources.csv)。

| 省市 | 原始材料和结论 | 最新与缺口 |
|---|---|---|
| 北京 | 2024/2025/2026市级特色集群原PDF7/5/2；2026海淀AI软件，2024通州体外诊断器械 | 2026最新取得；非全部历年有效合集 |
| 上海 | 2022特色园区公告目录53与手册53 | 后续现行目录未核；手册行业栏目7生物医药、4AI |
| 江苏 | 2026-08-26生物医药行动计划原文苏工信医药〔2026〕242号，指向南京/无锡/常州/苏州/南通/连云港/泰州 | 行动计划不是园区认定；2025集群公示URL404，省级药械园区完整原表未找到 |
| 广东 | 粤府函〔2020〕82号20战略产业政策含生物医药与健康、软件服务 | 全省培育政策不是城市园区名录；省级药械园区完整原表未找到，深圳公示TLS失败 |
| 浙江 | 2025特色园区115原HTML，文件2026-02-24/上网2026-03-05；科技厅基地目录存在 | 行业仅生产制造/生产性服务，不能细分药械；科技厅分页未取齐不收录 |
| 四川 | 2025省特色集群35原HTML，第2武侯转化医学 | 转化医学不直接等于医疗服务；首批17先进集群提案答复不是17条原名单 |

玩具：汕头市工信局[2024-07-31官方消息](https://www.shantou.gov.cn/stsgxj/gkmlpt/content/2/2357/post_2357762.html)明确澄海区玩具创意产业集群入选2024广东省级名单；但该原名单41条附件及澄海条号未取得，方法验证保留为“入选旁证已核，原名单条号未找到”，不写国家级。另L04第75原PDF是东莞石排镇潮流玩具，不是澄海。袜子：已收录545条未找到诸暨大唐袜业单列认定条目；L04第36为诸暨智能刺绣机，L02第28环杭州湾现代纺织服装未点名大唐，均不能替代袜业证明。官方产业地理描述不是认定名单；袜业名单与条号未找到。

## 3. P1相关行业的载体城市

下表逐条按名单行业文字及名称展示，地理字段属于行政区划规范化；跨区域简称未展开，不能把成渝或京津冀缩成几个核心城市。按行业匹配的条件性岗位映射仅使用下表中原文含行业且城市可定位的条目。一个混合行业条目可同时相关药/械，行业归类单标签不会覆盖原文。

| 行业原文 | 城市/范围 | 集群或园区 | 定位/来源 |
|---|---|---|---|''')
for c in clusters:
 if c['行业']!='服务外包' and re.search('医药|医疗器械|医疗设备|诊断|人工智能|软件|生物药|化学原料药|外包|转化医学|生命健康',c['行业']):
  parts.append(row([c['行业'],c['所在城市'] or '原名范围：'+c['集群或园区名称'],c['集群或园区名称'],c['页码或条目号']+f" [原文]({c['来源URL']})"]))
parts.append('''
服务外包37城仅作替代线索，不属于上表的直接行业匹配；“服务外包”不足以证明当地有CRO或某种岗位。医疗健康服务未找到可直接用作岗位覆盖的原始专门名录。“天津滨海生物医药外包服务”是反面证据：不能泛称制造业集群名单完全没有研发服务；但也不能把所有外包都解读为临床研究。

## 4. 名单覆盖不到的岗位与替代来源

CRO/临床研究岗位没有取得明确“临床研究/临床试验/CRO”条目，天津医药外包服务只作相关载体线索。健康管理、理疗、心理咨询、医院运营、公共卫生、保险理赔、药店、出版、翻译等未找到直接对应，不能从人口规模、综合高新区或软件名城替它们补齐。产品经理、医学AI等跨行业岗位只在指定雇主行业下对应；例如产品经理仅对应软件/AI企业产品岗位。

服务外包城市37个由3份正式文件21+10+6重建，与访问当日商务部介绍的37总数一致；不是各城市CRO企业名单，也不证明2021后没有调整。中国软件名城2023评估通知存在已核，工信部信发函〔2023〕383号，原附件14条未取得；MIIT攻击提示后停止，不将新闻拼成全14城市表。具体官方替代材料与行业关联如下。

| 替代来源 | 已取得粒度 | P1用途与限制 |
|---|---|---|
| 服务外包城市 | 中国服务外包示范城市37；正式存量与新增文件 | 给CRO、翻译、软件服务雇主研究提供检索城市线索；岗位行业对应未证明 |
| 2023软件名城评估通知 | 通知正文，附件未取得 | 软件算法/产品可相关；不能从该通知输出全名单或当前招聘量 |
| 经济普查年鉴2023表1-7/1-8 | 31省级地区×行业大类法人单位数/从业人员原图 | 包括医药制造、软件服务、互联网、研发、卫生；不是市×岗位，法人单位不是企业数；只记录粒度不计算 |
| 第五次经济普查公报第7号 | 2023年末省级地区第二/三产业合计单位数、人数 | 没有省×具体行业交叉，不能冒充行业分布 |
| 地级市×CRO/CRA/医学事务/医药代表岗位官方就业全表 | 未找到 | 不用招聘网站填补，本次不补全市场数量 |

[原始统计表目录](https://www.stats.gov.cn/sj/pcsj/jjpc/5jp/zk/left.htm)、[表1-7](https://www.stats.gov.cn/sj/pcsj/jjpc/5jp/zk/html/A1-07.jpg)、[表1-8](https://www.stats.gov.cn/sj/pcsj/jjpc/5jp/zk/html/A1-08.jpg)、[公报第7号](https://www.stats.gov.cn/xxgk/sjfb/zxfb2020/202412/t20241226_1957890.html)均已归档。数据时点2023年末，不是2026当前招聘统计。

## 5. 岗位对应与样本旁证

[岗位-集群对应CSV](../../data/careerdb/role_cluster_links.csv)覆盖50/50岗位。置信度中/低评的是条件性行业对应，不是招聘集中度；没有岗位的直接地域事实时不设“高”。每条成功对应有L编号、原条号/印刷页及行业原文；未对应行的依据为空并说明原因，不能伪造条号。对应规则固定于任务目录role_industries.json和build_tables.py，所有“该岗位可能受雇于此行业”均标推测。药物生产等岗位对应外包服务时尤其要核具体雇主与业务，不可当已确认雇主清单。

postings_mapped.jsonl没有城市；本次仅按唯一ID关联本地postings.jsonl，50岗共623条存档映射，其中28条关联不到原记录，595条有原记录。每条多城市分别计一次，同条同城市去重；全国/其它/省级或未解析字段单列，不从公司名猜城市。城市后缀、自治区简称规范化规则已保存。表中城市提及数不是当前在招职位数；来源偏医学高校校招，2025发布或归档样本亦在内，角色匹配本身沿用既有node，不再宣称人工逐条验证。完整城市分布、缺失ID和原字段计数见sample-cities.json/csv，输入三文件SHA已保存。

| P1岗位 | 原映射样本数 / 原城市关联缺失 | 样本城市提及前5（非市场排名） | 名单条件对应城市/缺口 |
|---|---|---|---|''')
for s in samples:
 ls=[l for l in links if l['岗位']==s['role'] and l['对应依据']];cs=sorted(set(c for l in ls for c in l['城市'].split('、')))
 sample='、'.join(c+' '+str(n) for c,n in list(s['cities'].items())[:5]) or '无可解析城市'
 parts.append(row([s['role'],str(s['sample_n'])+' / '+str(len(s['missing_ids'])),sample,'、'.join(cs) if cs else '未找到直接细分行业条目']))
parts.append('''
不能把两列的重合看成独立验证：名单是行政载体，样本来自少数学校校招入口；两者单位、时间与抽样方法不同。样本数字只是字段计数，不作市场占比、岗位供给量或城市排序建议。

## 6. 引用合规

依据[国家版权局公开的2020修正著作权法](https://www.ncac.gov.cn/xxfb/flfg/flfg_532/202103/t20210309_50530.html)第五条，国家机关具有立法、行政、司法性质的文件及其官方正式译文等不适用该法。推断：本次国家/省市正式认定通知与行政附表可按其文件性质引用必要事实、名称、地域与条号；这不是所有网页及素材的商用许可。原文与本地哈希可复核，未取得许可声明的材料如实标记。

| 收录体系/材料 | 公开性质 | 具体引用条件及未取得部分 |
|---|---|---|
| 先进制造、国家/北京/四川中小企业特色集群、浙江园区正式通知 | 政府行政认定及附表公开 | 依第五条文件性质判断可引用；保留发文机关、文号/日期、原名/编号、链接；未取得逐站额外商用条款 |
| 服务外包3份正式文件 | 国务院/部门行政文件，财政部/商务部官网公开 | 同上；财政部页脚明确“如需转载，请注明来源”；归档文件不能改写成CRO认定 |
| AI先导区政府门户转载报道 | 官方转载，原部门正式公文未取得 | 名称等事实可带来源引用；转载文章全文/图片具体许可未找到，不能宣称取得全文再分发权 |
| AI三城市函 | 科技部行政文件，注明主动公开 | 同正式文件原则；许可不扩大至网站图像设计等 |
| 上海投资手册及目录图片 | 官方招商出版/公告展示，原材料公开 | 名称、行业事实可来源注明；整本手册、图像设计/地图/照片再发布许可未找到，不复制整册到产品 |
| 未收齐的战略集群、创新型、高新区、生物基地 | 存在性研究文章/消息与转载 | 只引用已经核实的存在性、时点与粒度；不能生成不存在的全名单或假称行政认定附件 |
| 年鉴表1-7/1-8及编排 | 政府在线公开，中国统计出版社版权 | [版权页](https://www.stats.gov.cn/sj/pcsj/jjpc/5jp/zk/notepyrightc.htm)明确未经许可不得翻印/拷贝/仿制/转载。内部核验归档不等于对外授权；产品不直接复刻年鉴图或全表，需按具体用途核许可 |

“政府认定集群所在地”不能包装成“政府认证小谷”或“该岗位全国主要分布”；保留原年份与动态管理风险。第五条适用判断与许可判断分开，本文没有作出所有材料可任意商用的结论。

## 7. 未解决问题与验收边界

1. 战略性新兴66、国家生物基地23、创新型全国名单、高新区178未取得原始完整表；每体系存在性来源与具体缺口已记录，未纳入不完整条目。
2. 国家SME历史批次及复核有效性未收齐；地方园区后续动态调整未核，不能称545条现行有效独立载体。江苏/广东专门药械园区原表未找到。
3. 玩具已核澄海入选的官方消息，但2024广东原全表及澄海条号未取得；袜业认定名单条号未找到。这两项不能声明全部完成直接名单验证。
4. 工信部403/IP攻击提示、发改委robots403、开平robots403等触发停站；完整失败记录保留。证书/SSL与404失败不通过关闭TLS或绕权限解决。不得用搜索摘要补原表。最新批次检索结论受来源可访问范围限制。
5. 50岗全部处理不等于50岗都有对应，更不等于岗位集中度成立。28岗条件对应、22岗未找到；实际招聘量由用户另行手工采集，本研究不访问BOSS/脉脉/知乎，也不抓取招聘网站。
6. 没有写运行时、职业树/岗位卡，没有commit/push。Claude验收及brief第9节保持由Claude处理；本次独立审阅结果见任务目录review.md。

| brief验收 | 本次证据/判定 |
|---|---|
| 起点逐体系存在+原文或未找到 | 已逐项区分，部分原始全表未找到；非官方榜单未混表 |
| 收录批次条数一致、抽查10条原条号 | 自动检查与10条原文核对见validation.json；只验收所收批次，不代表各体系历年全量 |
| 玩具袜子明确核实结论 | 玩具入选旁证已核但原条号未找到；袜业名单/条号未找到，保持边界 |
| 50 P1岗位覆盖、依据 | 50/50；成功对应可定位；无对应行明确未找到 |
| 样本偏差明确 | 623条、28缺原城市，医学校招偏差与非招聘量已注明 |
| Claude最终验收 | 尚未进行，本文与数据/证据可供其审阅 |

复现入口：tasks/industry-clusters-20261011/start.md；sample_cities.py → build_tables.py → write_report.py → validate.py。网络无需重跑即可复建本次静态研究产物。
''')
text='\n'.join(parts)
# refer to the real stable source id, not an assumed ordinal
sh=next(b for b in batches if '投资手册' in b['name'])
text=text.replace('上海L15（以主表实际L编号为准）', '上海'+sh['id'])
(doc/'industry-clusters-2026-10.md').write_text(text)
print('sources',len(source_rows),'report chars',len(text))
