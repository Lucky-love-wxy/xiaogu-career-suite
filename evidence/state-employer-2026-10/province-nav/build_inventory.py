"""Offline build of province entrance candidates from saved official navigation."""
import json,re
from pathlib import Path
ROOT=Path(__file__).parent
regions='北京 天津 河北 山西 内蒙古 辽宁 吉林 黑龙江 上海 江苏 浙江 安徽 福建 江西 山东 河南 湖北 湖南 广东 广西 海南 重庆 四川 贵州 云南 西藏 陕西 甘肃 青海 宁夏 新疆 兵团'.split()
def load(k): return json.loads((ROOT/(k+'-links.json')).read_text())
rows=[]
def add(region,category,name,url,proof,snapshot,observation,organizer=None):
 rows.append(dict(region=region,category=category,name=name,url=url,organizer=organizer or name,organizer_type='政府/事业单位（官方导航所指；具体主办待目标页核验）',coverage='省级' if region!='兵团' else '新疆生产建设兵团',official_evidence_url=proof,evidence_snapshot=str(snapshot),access_date='2026-10-11',existence_observation=observation,first_party='官方发布入口候选；具体招聘栏未核验',recruitment_column_url=None,content_type='未核验',robots_status='未进入本阶段',terms_status='未进入本阶段',identity_type='未分类',sample_source_match='由主任务统一匹配'))
for x in load('cpta'):
 if x['text'] in regions:
  add(x['text'],'省级公务员/人事考试入口',x['text']+'人事考试机构（中国人事考试网导航名称）',x['url'],'http://www.cpta.com.cn/',ROOT/'cpta.html','官方首页地方考试机构导航链接已取得；未访问目标正文，非公务员独立门户全覆盖')
hunan_urls={'湖南':'https://rst.hunan.gov.cn/','西藏':'https://hrss.xizang.gov.cn/','四川':'https://rst.sc.gov.cn/','山东':'https://hrss.shandong.gov.cn/','江西':'https://rst.jiangxi.gov.cn/','福建':'https://rst.fujian.gov.cn/','广西':'https://rst.gxzf.gov.cn/','北京':'https://rsj.beijing.gov.cn/','上海':'https://rsj.sh.gov.cn/','宁夏':'https://hrss.nx.gov.cn/','新疆':'https://rst.xinjiang.gov.cn/','甘肃':'https://rst.gansu.gov.cn/','青海':'https://rst.qinghai.gov.cn/','云南':'https://hrss.yn.gov.cn/','陕西':'https://rst.shaanxi.gov.cn/','贵州':'https://rst.guizhou.gov.cn/','广东':'https://hrss.gd.gov.cn/','海南':'https://hrss.hainan.gov.cn/','湖北':'https://rst.hubei.gov.cn/','河南':'https://hrss.henan.gov.cn/'}
nav={x['text']:x['url'] for x in load('shanghai_hrss') if '/tgssrsbm_' in x['url']}
for r in regions:
 name=r+'人力资源和社会保障部门'
 if r in hunan_urls:
  add(r,'省级人社入口',name,hunan_urls[r],'https://rst.hunan.gov.cn/rst/yqlj/sjrsw/index.html',ROOT/'hunan-web-extract.txt','湖南人社官方省级人社目录正文明确列出入口；未访问目标招聘栏目')
 else:
  url=nav[r]; f=ROOT/('hrss_'+r+'.html')
  if f.exists():
   m=re.search(r'location.href="([^"]+)"',f.read_text()); target=m.group(1) if m else url
   add(r,'省级人社入口',name,target,url,f,'上海人社官方导航跳转页已取得目标URL；未访问目标正文')
  else: add(r,'省级人社入口',name,url,'https://rsj.sh.gov.cn/',ROOT/'shanghai_hrss.html','上海人社官方导航包含该省名称；此URL为官方导航中间页，目标URL未展开')
for k in ['liaoning_health','liaoning_health_page2']:
 for x in load(k):
  for r in sorted(regions,key=lambda v: (v!='兵团',-len(v))):
   if (r in x['text']) and ('卫生健康委' in x['text']) and not any(y['region']==r and y['category']=='省级卫健入口' for y in rows):
    add(r,'省级卫健入口',x['text'],x['url'],'https://wsjk.ln.gov.cn/wsjk/xglj/gswsjkw/'+('index.shtml' if k=='liaoning_health' else 'ffece81f-2.shtml'),ROOT/(k+'.html'),'辽宁卫健官方各省卫健目录正文链接已取得；目标招聘栏目未核验')
    break
for x in load('sasac_directory'):
 if '国有资产监督管理委员会' in x['text']:
  r=next((r for r in sorted(regions,key=lambda v: (v!='兵团',-len(v))) if r in x['text']),None)
  if r: add(r,'省级国资入口',x['text'],x['url'],'http://wap.sasac.gov.cn/n4422011/n17627531/c17633273/content.html',ROOT/'sasac_directory.html','国务院国资委地方国资委官方目录链接已取得；具体招聘栏目未核验')
for r in ['四川','西藏']:
 add(r,'省级国资入口',r+'国资监管部门（官方目录未找到）',None,'http://wap.sasac.gov.cn/n4422011/n17627531/c17633273/content.html',ROOT/'sasac_directory.html','所读国务院国资委目录未列本地区；未猜测域名')
out={'scope':'31省区市+新疆生产建设兵团的官方入口候选存在性盘点；非招聘公告覆盖或规则结论','date':'2026-10-11','rows':rows,'blocked_hosts':[{'host':'gzw.nmg.gov.cn','url':'https://gzw.nmg.gov.cn/','error':'web open 403 Forbidden','action':'已停止该主机，后续不得请求'}],'gaps':['人社9条仍为上海官网导航中间页，未展开实际目标URL','人事考试32条有官方导航证据，但未逐页证明所有具公务员栏目','国资目录未列四川、西藏','全部省级入口具体招聘栏目、目标主办声明、robots与条款待主任务核验'],'counts':{c:sum(x['category']==c for x in rows) for c in set(x['category'] for x in rows)}}
Path(ROOT.parent/'province-inventory.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(out['counts'],len(rows))
