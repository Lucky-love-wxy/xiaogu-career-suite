"""从已保存证据生成医学方向表；不联网、不读密钥、不调用模型。
运行 python3 scripts/build_major_directions.py
输入 evidence/major-destinations-2026-10/posting-annotations.json、每职位source.json、school-extracts.json(可选)。
输出 data/directions/三个UTF-8 CSV与collection-summary.json；覆盖同名输出，固定排序，校验失败退出。
作者初标不自动变成模型事实；未采集学校时major表只有表头并明确Q1未完成。
"""
import csv,json,hashlib,re
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; E=ROOT/'evidence/major-destinations-2026-10'; OUT=ROOT/'data/directions'
OUT.mkdir(parents=True,exist_ok=True)
MAJOR=['school','school_tier(A/B/C)','province','cohort(届别)','report_url','report_published','granularity(major/college/school)','major','metric(去向结构/单位性质/行业/职业类别/非医疗去向描述)','category(报告原文名称)','value(原文数值或文字)','unit(%/人)','page','accessed_at','evidence_path','note']
POST=['role_family','role_name','posting_title','company_type','city','education_req','major_req','experience_req','accepts_fresh(Y/N/未写)','certificate_req','posted_or_seen_at','url','platform','accessed_at','evidence_path']
SUMMARY=['role_family','role_name','occupation_code(大典编码或空)','postings_n','fresh_ok_n','master_plus_n','certificate_n','search_queries(平台:搜索词:返回条数)','verified(Y/未验证)','note']
def output(name,fields,rows):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
rows=[]; groups=defaultdict(list)
for a in json.loads((E/'posting-annotations.json').read_text())['items']:
    p=E/a['slug']/'source.json';d=json.loads(p.read_text());assert d['state']=='jd_found' and d['jd'][0]
    assert '/job_detail/' in d['url'] and '?' not in d['url']; raw=d['jd'][0]+d['requirements']
    for field in ['education_req','major_req']:
        assert a[field] in raw,(a['slug'],field)
    company=d['company'].splitlines(); company=[c for c in company if c.strip()]
    ctype=' / '.join(company[1:-1]);city=d['requirements'].split()[0]
    x=dict(role_family=a['role_family'],role_name=a['role_name'],posting_title=d['heading'],company_type=ctype,city=city,
        education_req=a['education_req'],major_req=a['major_req'],experience_req=a['experience_req'],certificate_req=a['certificate_req'],
        posted_or_seen_at='抓取2026-10-05；发布日期未显示',url=d['url'],platform='BOSS直聘',accessed_at='2026-10-05',evidence_path=str(p.relative_to(ROOT)))
    x['accepts_fresh(Y/N/未写)']=a['accepts_fresh'];rows.append(x);groups[(a['role_family'],a['role_name'])].append(x)
majorfile=E/'school-extracts.json'; majors=json.loads(majorfile.read_text()) if majorfile.exists() else []
schoolfile=E/'school-kangda/source.json'
if schoolfile.exists():
    d=json.loads(schoolfile.read_text()); tables={t['index']:t['rows'] for t in d['tables']}
    selected=['临床医学','护理学','药学','预防医学','中医学','医学影像学','医学检验技术','口腔医学']
    present=set(); schoolrows=[]
    def schoolrow(major,metric,category,value,unit,locator,note,granularity='major'):
        schoolrows.append(dict(zip(MAJOR,[
          '南京医科大学康达学院','C','江苏','2024届',d['url'],d['report_published'],granularity,major,
          metric,category,value,unit,locator,d['accessed_at'],str(schoolfile.relative_to(ROOT)),
          '官方HTML年报；PDF未取得，网页表号不是PDF页码。'+note])))
    for cells in tables[15][1:]:
        # 原网页有院系合并单元格，短行首列是专业，不是院系。
        major=cells[-6]
        if major not in selected:continue
        present.add(major)
        for category,value in zip(tables[15][0][-5:],cells[-5:]):
            schoolrow(major,'去向结构',category,value,'%', '网页表2-8',
              '分母为该专业2024届本科毕业生；就业系统年度数据截止2024-12-31。')
    for index,metric,locator in [(25,'行业','网页表3-8'),(27,'单位性质','网页表3-10'),(31,'职业类别','网页表3-14')]:
        for cells in tables[index][1:]:
            major=cells[-2]
            if major not in selected:continue
            matches=re.findall(r'([^，]+)（([\d.]+)%）',cells[-1]);assert matches,cells
            for category,value in matches:
                schoolrow(major,metric,category,value,'%',locator,
                  '报告列出的主要类别，可能不是穷尽；分母为该专业已就业毕业生，不能当全体毕业生比例。原表标就业管理系统，但职位类别分母人数未列，勿跨表反推人数。')
    for major in selected:
        metrics=['非医疗去向描述'] if major in present else ['去向结构','单位性质','行业','职业类别','非医疗去向描述']
        for metric in metrics:
            schoolrow(major,metric,'未列出','未列出','','网页已核表2-8/3-8/3-10/3-14',
              '未按该专业列出。医学影像技术不等同医学影像学。' if major not in present else
              '有企业/行业大类，未取得具体CRO、保险、媒体等岗位去向描述；不推断企业即非医疗行业。')
    # 同一学校只从一份固定原文生成，避免可选手工表重复计数。
    assert not any(x['school']=='南京医科大学康达学院' for x in majors)
    majors.extend(schoolrows)
for x in majors:
    assert x['page'] and x['report_url'] and x['granularity(major/college/school)'] in ['major','college','school']
    assert (ROOT/x['evidence_path']).is_file(),x['evidence_path']
summaries=[]
for (family,name),items in groups.items():
    companies={x['company_type'].split(' / ')[0] for x in items}
    summaries.append({'role_family':family,'role_name':name,'occupation_code(大典编码或空)':'','postings_n':len(items),
      'fresh_ok_n':sum(x['accepts_fresh(Y/N/未写)']=='Y' for x in items),
      'master_plus_n':sum('硕士' in x['education_req'] and '本科' not in x['education_req'] for x in items),
      'certificate_n':sum(x['certificate_req']!='未写' and '优先' not in x['certificate_req'] for x in items),
      'search_queries(平台:搜索词:返回条数)':'BOSS:'+('医学编辑 应届' if name=='医学编辑' else 'CRC 应届')+':未测（带查询参数路径robots禁止）；来自公开聚合页导航，不是搜索返回总数',
      'verified(Y/未验证)':'Y' if len(companies)>=3 else '未验证',
      'note':'仅岗位存在/3公司详细JD验证；搜索计数未验收，大典未取。fresh_ok包含经验不限/在校实习，不表示无实习可录用；certificate_n计必需证书含CET4，不计优先。CRC仍在医院现场，非临床诊疗不等于不去医院。'})
output('major_destinations.csv',MAJOR,majors);output('role_postings.csv',POST,rows);output('role_summary.csv',SUMMARY,summaries)
counts={'jd_n':len(rows),'companies_n':len({r['company_type'].split(' / ')[0] for r in rows}),'roles_n':len(summaries),'schools_n':len({r['school'] for r in majors}),'school_rows_n':len(majors),'q1':'未开始证据采集' if not majors else '部分：官方HTML1校；原PDF0；10校/三档/四省未通过','search_counts':'未测','occupation_codes':'未取得大典原文'}
(OUT/'collection-summary.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2))
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(E.rglob('*')) if p.is_file() and p.name!='manifest.json'}
(E/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(json.dumps(counts,ensure_ascii=False))
