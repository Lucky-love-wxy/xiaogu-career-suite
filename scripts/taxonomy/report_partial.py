#!/usr/bin/env python3
"""离线汇总已验证标准试点及明确缺口；不将候选映射当最终映射。
运行 python3 scripts/taxonomy/report_partial.py；标准库，无网络/密钥/模型。
"""
import csv,json,hashlib,collections
from pathlib import Path
R=Path(__file__).resolve().parents[2];E=R/'evidence/taxonomy-2026-10';D=R/'docs/research'
def load(p):return json.loads((E/p).read_text())
def table(p):return list(csv.DictReader((R/p).open(encoding='utf-8-sig')))
rows=table('data/careerdb/node_mapping_standards.csv');tasks=table('data/careerdb/onet_transfer_check.csv');skills=table('data/careerdb/esco_skill_pilot.csv');stats=load('pilot-statistics.json')
sources=[
('https://isco.ilo.org/en/isco-08/','ISCO-08 structure and definitions','ILO','ISCO-08','2026-10-08','四层与官方Excel/CSV入口；本地实际计数来自ESCO内嵌表，原ILO下载未成功'),
('https://esco.ec.europa.eu/en/about-esco/faq?page=1','Frequently Asked Questions','European Commission','访问时版本','2026-10-07','分类数据2011/833/EU复用条件；API软件许可不能替代分类许可'),
('https://esco.ec.europa.eu/en/use-esco','Use ESCO：语言与当前版本','European Commission','28语言/1.2.1，2025-12-10','2026-10-08','官方语言清单不含中文，页脚当前版本；本地raw/esco-languages与official-body-readback'),
('https://esco.ec.europa.eu/en/use-esco/download','Download ESCO','European Commission','实际分析1.2.0；网站最新1.2.1','2026-10-07','公开CSV包、URI、职业技能关系；实际包保存在raw'),
('https://www.onetcenter.org/database.html','O*NET Database','USDOL/ETA','31.0 2026-08','2026-10-07','数据下载与版本；本地包及用户Excel已核验'),
('https://www.onetcenter.org/license_db.html','O*NET Database Content License','USDOL/ETA','31.0 CC BY4.0','2026-10-07','数据许可、署名、修改声明'),
('local:evidence/taxonomy-2026-10/raw/onet-2024-method.pdf','O*NET 2024 方法报告','O*NET Resource Center','2024','2026-10-07','数据来源方法，当前下载原URL未落盘；保留本地PDF，远端来源绑定待补'),
('https://www.onetcenter.org/crosswalks/esco/ESCO_to_ONET-SOC.xlsx','ESCO to O*NET-SOC Crosswalk','O*NET Resource Center','本次取得文件','2026-10-07','官方crosswalk；未计算双向覆盖率'),
('https://www.ndrc.gov.cn/fggz/jyysr/jysrsbxf/202210/t20221031_1340470_ext.html','新版职业分类大典净增158个新职业','国家发改委','2022-10-31','2026-10-08','正式版1639职业、97数字/134绿色/23交叉；非原包计数'),
('https://legal.lightcast.io/lightcast-legal/open-terms-of-use','Open Terms of Use','Lightcast','2026-10-01','2026-10-08','公开数据非商业使用与商业合同条件'),
('https://docs.lightcast.io/lightcast-api/docs/api-access','Access Options to Skills','Lightcast','访问时版本','2026-10-08','商业/生产需商业许可，公益免费须批准'),
('https://www.linkedin.com/blog/engineering/data/building-maintaining-the-skills-taxonomy-that-powers-linkedins-skills-graph','Building and maintaining the skills taxonomy','LinkedIn','历史官方工程文章','2026-10-08','可读结构设计，不等于公开可下载/可商用全量图')]
with (D/'occupation-skill-taxonomy-2026-10-sources.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['url','标题','发布方','版本/日期','访问日期','支撑哪条结论']);w.writerows(sources)
lines=['# 职业树与技能树试点（部分交付，2026-10-08）','',
'建议用 ISCO-08 的1位大类作为A、4位职业单元作为B，ESCO职业URI及中国细分扩展作为C；保留ISCO中间2/3位层级作元数据，行业和专业另建多对多维度。这是待验证设计建议。195节点已全部召回候选，但最终逐条认可数为0，不能报告可映射率。10岗位100条任务中54条在本地中国JD检出主动作或子任务，不能证明任务整体跨国相同；529条ESCO技能关系提供挂接样例。社招条款及真实两档样本未完成，不能认定可抓取或可用于产品。','',
'本报告保留已取得产物并列出未达验收项，不以文件存在代替研究完成。并行收集进程受会话使用额度中断；主进程已完成本地整理，未支付模型分类。','',
'## 标准对照与许可','',
'| 标准 | 版本、层级与实际计数 | 字段与技能关系 | 获取与语言 | 许可、来源方法和对照 |','|---|---|---|---|---|',
'| ISCO | ISCO-08；1/2/3/4位；ESCO1.2.0内嵌ISCO表实际10/43/130/436组，与[ILO官方结构](https://isco.ilo.org/en/isco-08/)一致 | 定义、主要任务、职业示例、技能等级与专门化；没有独立细技能多对多表 | ILO提供Excel/CSV/PDF入口；本次原ILO文件下载未成功，使用ESCO内嵌定义；官方中文数据包未取得 | 国际统计分类，专家与三方程序制定；商业数据复用许可未核清；与ESCO通过iscoGroup关联，不能套用ESCO许可覆盖ILO全部材料 |',
'| ESCO | 网站最新1.2.1，2025-12-10；实际分析包1.2.0，3039职业/13939技能/129004职业技能关系 | URI、preferred/alt labels、definition、ISCO组、skill type；职业与技能多对多，essential/optional | 实际公开CSV包无需登录/邮箱已取得；RDF/API入口有，但API默认/可选版本与网站最新不同；28种语言无官方中文，建议译名待审 | [FAQ](https://esco.ec.europa.eu/en/about-esco/faq?page=1)按2011/833/EU允许免费任何目的复用，需声明使用ESCO及改动；API软件EUPL不能作分类许可。专家维护与劳动力市场更新，不能当作中国从业者问卷 |',
'| O*NET | 31.0，2026-08；SOC扩展职业表1016行，Tasks18838、Task Ratings165780、Work Context305389、Job Zones923行 | 任务、重要度、评分N与时间/来源、情境、知识技能能力、Job Zones等；923有Zone不等于1016都完整 | 官方CSV/Excel包；用户下载Excel五表行数与已存CSV一致，只核行数/SHA，未逐字段等价校验；本次英语数据 | [CC BY4.0](https://www.onetcenter.org/license_db.html)，署名31.0、USDOL/ETA、许可链接和改动；Tasks评分由Incumbents/Occupational Experts，Skills/Abilities含分析员来源，不能全部说成在职者本人分享。官方ESCO→O*NET crosswalk已取得，未算覆盖率 |',
'| 大典 | 2022正式版；[官方发布](https://www.ndrc.gov.cn/fggz/jyysr/jysrsbxf/202210/t20221031_1340470_ext.html)8大类/1639职业、97数字/134绿色/23交叉；中小类数量未以正式原包核验 | 编码、定义、主要任务与数字/绿色标识；本次未取得正式全文，任务粒度未核 | 中文；未找到已核验的正式机器可读全包；深圳PDF静态和CDP均404，广元PDF静态405后CDP取回200/29MB，但PDF共78页，首为附件7《岗位类别编码表》，版本未证实，隔离；正式全文未取得 | 商业复用、全文版权及大典↔ISCO官方crosswalk未核清；公示稿1636及绿色133不能混入正式版1639/134。公开发布不自动证明开放商用 |','',
'本报告使用ESCO分类；建议译名及中国适用判断属于修改/补充。This publication uses the ESCO classification of the European Commission. O*NET®31.0数据由USDOL/ETA提供，以CC BY4.0使用；中国对照和译名由本项目添加，USDOL/ETA未批准、背书或测试这些修改。','',
'Lightcast 当前[开放条款](https://legal.lightcast.io/lightcast-legal/open-terms-of-use)排除商业用途，商业/生产使用需联系签约；不能沿用旧“免费Open Skills”印象。LinkedIn公开工程文章解释概念/别名/层级和内部图服务，本次未取得公开全量下载与商业授权，不能替代ESCO。BOSS/猎聘/智联技能标签尚未取得开放结构/许可证据，暂不作为公共技能标准。','',
'## 映射候选与原节点问题','',
'| 候选关系 | 数量 | 占195比例 |','|---|---:|---:|']
counts=collections.Counter(x['match_type'] for x in rows)
for k in ['exact','broader','narrower','none']:lines.append(f'| {k} | {counts[k]} | {counts[k]/195:.1%} |')
lines+=['','上述是候选分类，195行review_status均provisional，不是最终语义映射。大典编码0/195；未实现P1人工对齐。临床医生混合西医/中医/口腔/病理/兽医及经营任务，标narrower。作者/撰稿人实际样本含社工；分公司负责人出现财务管理；管培36跨职能公告，均须先拆原样本，不能改名称掩盖问题。','',
'候选none清单按issue分组（完整理由与原始标题见CSV、node-review-inputs及mapping-candidates）：']
for issue in sorted({r['issue'] for r in rows if r['match_type']=='none'}):lines.append('- '+issue+'：'+'、'.join(r['name'] for r in rows if r['match_type']=='none' and r['issue']==issue)+'。')
lines+=['','## O*NET任务与ESCO技能试点','',
'选取有可定位标准职业的医药、语言编辑与保险岗位，覆盖同一批10岗位；是便利样本，不代表全部P1。每岗按importance选前10条，含rating日期/N/source。中国比对限制在未隔离的职责原文，原JSONL损坏1838–1847行未静默修复。','',
'| 岗位 | 可用中国JD | 任务动作检出/10 | ESCO关系词项检出/总数 |','|---|---:|---:|---:|']
for s in stats:lines.append(f'| {s["name"]} | {s["valid_cn_jd_n"]} | {s["onet_found_n"]}/10 | {s["esco_found_n"]}/{s["esco_relation_n"]} |')
lines+=['','合计54/100是“JD同句主动作或明确子任务检出”，并非完整任务含全部示例的重合率。未检出只指这些JD没写；医药市场仅1份可用JD尤其不能外推。CRC任务中的生命体征/心电图等美国内容不可据此推出中国CRC的医疗操作权限。注册法规、医药代表制度等跨国差异须以中国现行制度另核，本轮未完成制度对照。','',
'Work Context原值保存于work-context-pilot.json，统一标中国侧无对应证据；O*NET情境、重要度、频率不是中国工时、薪资或晋升结论。可把Tasks、情境问项、Job Zones当访谈问题清单，再用中国本人长文/JD核验。','',
f'本试点529条关系包含{len(set(s["技能URI"] for s in skills))}个唯一技能URI，建议中文名已生成但未专业校审。最小中文化范围是这395个名称及定义/同义词，不必一次翻译13939个；395是本试点去重数，不能按10/195线性外推全库数量。可先校审检出词项，再补低检出项；本轮没有实测翻译工时或付费模型成本。','',
'共享技能样例（同URI仅说明标准关系共享，不证明能转岗或中国必需资格）：']
g=collections.defaultdict(dict)
for x in skills:g[x['岗位']][x['技能URI']]=x
for a,b in [('药物合成','药物分析'),('期刊/学术编辑','英语翻译'),('生物信息工程师','保险理赔')]:
 common=sorted(set(g[a])&set(g[b]));k=common[0];s=g[a][k];lines.append(f'- {a} ↔ {b}：[{s["技能英文名"]}]({k})，建议“{s["建议中文名"]}”。')
lines+=['','第三组提供医学相关训练向通用保险职能的可提问切入点，不能自动推荐职业适配；两侧中国JD是否需要同技能要再核。ESCO essential/optional只是该ESCO子类关系，不能写成中国强制准入。','',
'## 社招可行性与未完成验收','',
'四来源BOSS、猎聘、智联、前程无忧的robots/用户协议正文、经验筛选与未登录字段没有完整保存；不批准或推断批量抓取合规。5岗×两档真实样本未执行，未混入校招统计。旧BOSS NETWORK_ERROR仅说明一次浏览器连接失败，不能证明网站永久不可访问；连接是否恢复仍需按取证阶梯以实际正文核验。','',
'尚需：195节点逐条语义审阅、正式大典全文/P1编码及版权、ISCO材料复用许可、完整标准crosswalk覆盖率、ESCO最新1.2.1对比、中文技能专业校审与全库去重、反向“中国有而O*NET没有”完整任务清单、四社招来源规则与5岗两档样本。未完成项保留在execution-status.json与任务start，最终映射认可率未知。','',
'本地验证确认195行唯一节点、临床医生narrower、10岗×10任务、同10岗529技能关系、未出现字段明确标注、译名待审。证据化自检；最终标准报告尚未独立review。研究未改运行时、职业树、提示词或校招统计，无commit/push。']
(D/'occupation-skill-taxonomy-2026-10.md').write_text('\n'.join(lines)+'\n')
manifest=[]
for f in sorted((E/'raw').rglob('*')):
 if f.is_file() and not f.name.endswith('.b64'):manifest.append({'file':str(f.relative_to(R)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(E/'file-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
assert len(rows)==195 and len({r['node'] for r in rows})==195
assert next(r for r in rows if r['name']=='临床医生（科室未细分）')['match_type']=='narrower'
assert len(tasks)==100 and len(skills)==529
assert {r['岗位'] for r in skills}=={r['\ufeff岗位'] if '\ufeff岗位' in r else r['岗位'] for r in tasks}
(E/'validation.json').write_text(json.dumps({'status':'PASS','scope':'结构及已存数据自检；非完整简报验收','mapping_rows':195,'final_accepted_mapping_n':0,'tasks':100,'skills':529,'network_calls':0},ensure_ascii=False,indent=2)+'\n')
print('PASS partial report;195 candidate nodes;100 tasks;529 relations')
