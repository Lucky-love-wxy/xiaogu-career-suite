"""Parse complete locally archived government lists; no network or runtime changes."""
import json,re,hashlib
from pathlib import Path
p=Path(__file__).parent
manifest={r['file']:r for f in p.glob('fetch-manifest*.json') for r in json.loads(f.read_text())}
lists=[]
def add(name,batch,total,file,publisher,date,standard,entries,note='',nature='官方认定名单'):
 assert len(entries)==total,(name,len(entries),total)
 row=dict(name=name,batch=batch,total=total,source_url=manifest[file]['url'],source_file=str(p/file),publisher=publisher,date=date,standard_quote=standard,latest_note=note or '截至2026-10-11取得该版本；未证明已覆盖所有后续发布或动态退出。',entries=entries,nature=nature,sha256=manifest[file]['sha256'])
 lists.append(row)
def ent(no,name,province='',city='',district='',industry='',category='其他',page=''):
 return dict(no=str(no),name=name,province=province,city=city,district=district,industry=industry,category=category,page=page)
def infer_ind(name):
 # Industry phrases are extracted from the original cluster name, not employer knowledge.
 x=re.sub(r'产业集群$','',name)
 x=re.sub(r'^北京市','',x)
 x=re.sub(r'^.*?(?:区|县|市)','',x,count=1)
 return x
for year,count in [(2024,7),(2025,5),(2026,2)]:
 entries=[]
 for line in (p/f'beijing-{year}.txt').read_text().splitlines():
  m=re.match(r'^\s*(\d+)\s+(.+?)\s+(北京市\S+|\S+区)\s*$',line)
  if not m:continue
  no,name,district=m.groups();name=re.sub(r'\s+',' ',name).strip();industry=infer_ind(name)
  cat='医疗器械' if '诊断试剂和器械' in industry else '人工智能与软件' if any(x in industry for x in ['AI ','人工智能','AIGC']) else '其他'
  entries.append(ent(no,name,'北京','北京',district,industry,cat,1))
 add('北京市中小企业特色产业集群',str(year),count,f'beijing-{year}.pdf','北京市经济和信息化局',f'{year}-'+{2024:'07-10',2025:'07-14',2026:'06-22'}[year],'经综合评估',entries,'已取得2026年最新可得年度原始通知和完整2条附件；2024/2025为历史批次。')
# Zhejiang HTML: tables 18 + 57 (32 five-star,25 four-star) + 40.
tables=json.loads((p/'zhejiang-tables.json').read_text())
def expand(tb):
 active={};out=[]
 for raw in tb:
  row={};col=0
  for cell in raw:
   while col in active:row[col]=active[col][0];col+=1
   row[col]=cell['text'];rs=int(cell['attrs'].get('rowspan','1'))
   if rs>1:active[col]=(cell['text'],rs)
   col+=1
  for k,v in active.items():row.setdefault(k,v[0])
  active={k:(v[0],v[1]-1) for k,v in active.items() if v[1]>1}
  out.append([row.get(i,'') for i in range(max(row)+1)])
 return out
for ti,(batch,total) in enumerate([('2025-专精特新产业园',18),('2025-高星级小微企业园',57),('2025-小微企业园',40)]):
 entries=[];section=''
 for r in expand(tables[ti]):
  if not r or not r[0].isdigit():
   if r and ('五星级' in ''.join(r) or '四星级' in ''.join(r)):section=''.join(r)
   continue
  no,city,district,name,typ=r[:5]
  entries.append(ent((section+'-'+no) if ti==1 else no,name,'浙江',city,district,typ,'其他'))
 add('浙江省级特色产业园',batch,total,'zhejiang-2025-parks.html','浙江省经济和信息化厅','2026-03-05','经园区自主申报、地方审核推荐、省厅组织评审',entries,'2025年度名单于2026-03-05发布，完整115条分18/57/40；原行业栏仅生产制造/生产性服务，不据名称扩充医药/AI行业。')
# Sichuan official HTML contains the complete 35-row attachment twice (desktop/mobile).
t=(p/'sichuan-2025.txt').read_text();part=t[t.index('序号\n市（州）\n集群名称'):];entries=[]
for m in re.finditer(r'\n(\d+)\n([^\n]+市)\n([^\n]+产业集群)',part):
 no,city,name=m.groups()
 if any(e['no']==no for e in entries):continue
 district=re.match(r'^(.+?(?:区|县|市))',name).group(1)
 ind=infer_ind(name);cat='医疗健康服务' if ind=='转化医学' else '其他'
 entries.append(ent(no,name,'四川',city,district,ind,cat))
add('四川省中小企业特色产业集群','2025',35,'sichuan-2025.html','四川省经济和信息化厅','2025-07-04','省级组织专家评审和网上公示',entries,'最新可得2025完整35条，认定有效2025—2027；不等于确认2026未有后续发布。')
# Shanghai handbook is complete, publicly issued by economic commission. It is kept as a handbook inventory,
# rather than silently changing PDF page references into the separate image catalogue's ordinal numbers.
groups=[('集成电路','集成电路设计产业园|临港新片区东方芯港|智能传感器产业园|浦江创芯之城'),('生物医药','张江创新药产业基地|临港新片区生命蓝湾|东方美谷·医药|湾区生物医药港|北上海生物医药产业园|青浦生命科学园|G60生物医药产业基地'),('人工智能','张江人工智能岛|西岸智慧谷|马桥AI试验区|临港新片区信息飞鱼'),('先进材料','超能新材料科创园|碳谷绿湾产业园|奉贤化工新材料产业园|上海电子化学品专区|Innogreen创新绿洲'),('电子信息','G60电子信息国际创新产业园|新型显示产业园|临港松江科技城|金桥5G产业生态园|G60松江信创产业园'),('汽车','临港南桥智行生态谷|汽车新能港'),('高端装备','临港新片区大飞机园|北斗西虹桥基地|华东无人机基地|机器人产业园|外高桥智能制造服务产业园|闵行开发区智能制造产业基地|张江机器人谷|长兴海洋装备产业园|临港新片区海洋创新园|中以（上海）创新园|动力之源|虹桥数字物流装备港'),('在线新经济','张江在线|长阳秀带|市北数智生态园|“虹桥之源”在线新经济生态园'),('时尚消费品','东方美谷·美妆|新食尚都市产业园|江南智造国际设计港'),('新兴领域','嘉定氢能港|国际氢能谷|宝武（上海）碳中和产业园|数智南大|漕河泾元创未来|张江数链|上海金谷智能终端制造基地')]
entries=[];pg=3
text=(p/'shanghai-2022.txt').read_text();compact=re.sub(r'\s+','',text)
for industry,names in groups:
 for name in names.split('|'):
  assert name in compact,name
  cat={'生物医药':'生物医药','人工智能':'人工智能与软件'}.get(industry,'其他')
  entries.append(ent('印刷页'+str(pg),name,'上海','上海','',industry,cat,pg));pg+=2
add('上海市特色产业园区投资手册','2022展示全量',53,'shanghai-2022.pdf','上海市经济和信息化委员会','2022-06','聚焦特定产业方向、特优园区主体、特强产业生态',entries,'53项官方招商手册展示全量；原认定公告目录2022原图另存，条目号使用手册印刷页码，不能当公告图序号。未证明2026仍53个。','官方园区招商手册（另有原始认定目录）')
for batch,file,people in [('2021第二批','ai-pilot-2021.html',[('北京','北京','北京',''),('天津（滨海新区）','天津','天津','滨海新区'),('杭州','浙江','杭州',''),('广州','广东','广州',''),('成都','四川','成都','')]),('2022新增批','ai-pilot-2022.html',[('南京','江苏','南京',''),('武汉','湖北','武汉',''),('长沙','湖南','长沙','')])]:
 es=[ent('正文列举'+str(i),n+'国家人工智能创新应用先导区',pr,c,d,'人工智能','人工智能与软件') for i,(n,pr,c,d) in enumerate(people,1)]
 add('国家人工智能创新应用先导区',batch,len(es),file,'工业和信息化部（北京国际科技创新中心政府门户转载）','2021-02-20' if '2021' in batch else '2022-09-30','先导区建设坚持应用牵引',es,'原部门已因403/攻击IP封禁停站；该政府门户明确注明工信部来源。完整新增批次5/3，非现行累计全国全表。','官方门户转载工信部新增名单')
for city,pr,file,doc in [('郑州','河南','ai-trial-zhengzhou.html','国科函规〔2021〕258号'),('沈阳','辽宁','ai-trial-shenyang.html','国科函规〔2021〕256号'),('哈尔滨','黑龙江','ai-trial-harbin.html','国科函规〔2021〕257号')]:
 add('国家新一代人工智能创新发展试验区',doc,1,file,'科技部','2021-11-13','开展人工智能政策试验',[ent('一',city+'国家新一代人工智能创新发展试验区',pr,city,'','人工智能','人工智能与软件')],'完整单项批复各1城市；未收集全国18城市原始函全集，不当累计全表。')
(p/'lists.json').write_text(json.dumps({'lists':lists},ensure_ascii=False,indent=2))
print([(x['name'],x['batch'],x['total']) for x in lists]);print('total',sum(x['total'] for x in lists))
