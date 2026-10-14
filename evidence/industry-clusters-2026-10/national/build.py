"""Extract full PDF tables to lists.json, validate contiguous row count. python3 build.py"""
import pathlib,re,json,hashlib
r=pathlib.Path(__file__).parent
spec=[('advanced-2022','国家先进制造业集群','2022年累计名单',45,'https://www.gov.cn/xinwen/2022-11/30/5729722/files/4f50411cc5a144669fea2c3f47afd94e.pdf','2022-11-30','经小组赛、综合赛评审并向社会公示','https://www.miit.gov.cn/zwgk/zcwj/wjfb/tz/art/2024/art_52ac73d422f440e2ac36da0259eb30f8.html'),('advanced-2024','国家先进制造业集群','2024年新增名单',35,'https://www.gov.cn/zhengce/zhengceku/202412/P020241216828680409717.pdf','2024-12-16','经小组赛、综合赛评审并向社会公示','https://www.miit.gov.cn/zwgk/zcwj/wjfb/tz/art/2024/art_52ac73d422f440e2ac36da0259eb30f8.html'),('sme-2023','中小企业特色产业集群','2023年度（第二批）',100,'https://www.chinasme.org.cn/upload/1/cms/content/editor/1697786887617.pdf','2023-10-18','定位在县级区划范围内','https://www.miit.gov.cn/zwgk/zcwj/wjfb/tz/art/2022/art_2e39162e00e346ebb7611da191f5e36e.html'),('sme-2025','中小企业特色产业集群','2025年度（第四批）',100,'https://gyxxh.tj.gov.cn/ZWGK4147/ZCWJ6355/gjjwj/202511/W020251106409440997860.pdf','2025-10-31','定位在县级区划范围内','https://www.miit.gov.cn/zwgk/zcwj/wjfb/tz/art/2022/art_2e39162e00e346ebb7611da191f5e36e.html')]
provinces='北京市 天津市 上海市 重庆市 河北省 山西省 辽宁省 吉林省 黑龙江省 江苏省 浙江省 安徽省 福建省 江西省 山东省 河南省 湖北省 湖南省 广东省 海南省 四川省 贵州省 云南省 陕西省 甘肃省 青海省 内蒙古自治区 广西壮族自治区 宁夏回族自治区 西藏自治区 新疆维吾尔自治区'.split()
def geo(name):
 province=next((p for p in provinces if name.startswith(p)),'');t=name[len(province):]
 city=province if province in ['北京市','天津市','上海市','重庆市'] else ''
 if city=='':
  # Only names explicitly containing a city suffix; do not guess county's prefecture.
  m=re.match(r'(.+?市)',t)
  if m:
   city=m[1];t=t[m.end():]
   while t.startswith('、'):
    more=re.match(r'、(.+?市)',t)
    if not more:break
    city+='、'+more[1];t=t[more.end():]
 district='';m=re.match(r'(.+?[区县])',t) if (province or city) else None
 if m:district=m[1];t=t[m.end():]
 industry=t.removesuffix('产业集群').removesuffix('集群')
 return province,city,district,industry
lists=[]
for stem,name,batch,total,url,date,standard,surl in spec:
 entries=[];current=None
 pages=(r/(stem+'.txt')).read_text().split('\f')
 for page,body in enumerate(pages,1):
  for line in body.splitlines():
   m=re.match(r'^\s*(\d+)\s+(.+?)\s*$',line)
   if m and '名单' not in line:
    current={'no':int(m[1]),'name':re.sub(r'\s+','',m[2]),'page':page};entries.append(current)
   elif current and line.strip() and '序号' not in line and '附件' not in line and not line.strip().isdigit() and '名单' not in line:
    current['name']+=re.sub(r'\s+','',line)
 assert [x['no'] for x in entries]==list(range(1,total+1)),(stem,len(entries))
 for x in entries:
  p,c,d,i=geo(x['name']);x.update(province=p,city=c,district=d,industry=i,category='其他')
  if '医疗器械' in i:x['category']='医疗器械'
  elif '生物医药外包服务' in i:x['category']='生物医药';x['note']='名单未细分临床研究；不自动等同CRO临床服务'
  elif any(k in i for k in ['生物医药','生物药','原料药','中药','基因','生命健康','生物技术药']):x['category']='生物医药'
  elif any(k in i for k in ['人工智能','软件','计算系统','工业互联网服务','工业互联网平台','智慧城市智能系统']):x['category']='人工智能与软件'
 if stem=='advanced-2024':
  e=entries[18];e.update(province='北京市',city='北京市',district='海淀区',industry='人工智能',geography_note='北京海淀原文字面名称规范化')
 lists.append(dict(name=name,batch=batch,total=total,source_url=url,source_file=str(r/(stem+'.pdf')),publisher='工业和信息化部',date=date,standard_quote=standard,standard_source_url=surl,sha256=hashlib.sha256((r/(stem+'.pdf')).read_bytes()).hexdigest(),latest_note='已收录全批；最新性边界见summary.md',entries=entries))
(r/'lists.json').write_text(json.dumps({'lists':lists,'geography_note':'省市区仅按名称明确文字拆分；县级市不擅自归地级市，跨区域简称未扩写；industry是原名称摘取，category为研究归类。'},ensure_ascii=False,indent=2))
print([(x['batch'],len(x['entries'])) for x in lists]);print('total',sum(x['total'] for x in lists))
for x in lists:
 for e in x['entries']:
  if e['category']!='其他':print(x['batch'],e)
