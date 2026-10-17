#!/usr/bin/env python3
"""补取已发现的协议/关于页和限定单条公告。输入固定官方/官网发现URL；沿用collect快照与限速停站。
python3 supplement.py。无登录，不执行JS，不调API，不翻页。新主机先robots。
"""
from pathlib import Path
import json,urllib.parse,re,urllib.robotparser
s=(Path(__file__).parent/'collect.py').read_text().split('mode=sys.argv[1]')[0]
exec(compile(s,str(Path(__file__).parent/'collect.py'),'exec'))
items=[('https://www.iguopin.com/doc/info?channel_alias=User_Service','terms'),('https://www.ncss.cn/intro','about'),('https://www.gaoxiaojob.com/zhaopin/aboutUs/index.html','about'),('https://www.jobmd.cn/about','about'),('https://www.jobmd.cn/privacy?version=v5.0','terms'),('https://sso.ciiczhaopin.com/serviceagreement','terms'),('https://agreement.gaoxiaojob.com/docs/service-agreement/','terms')]
results=[]
for u,k in items:
 h=urllib.parse.urlsplit(u);m=fetch(f'{h.scheme}://{h.netloc}/robots.txt','robots');raw=(ROOT/m['path']/'raw.txt').read_text() if 'path' in m and (ROOT/m['path']/'raw.txt').exists() else ''
 if re.search(r'^User-agent:',raw,re.M|re.I):
  rp=urllib.robotparser.RobotFileParser();rp.parse(raw.splitlines())
  if not rp.can_fetch(UA,u):results.append({'url':u,'status':'robots_disallowed'});continue
 if m.get('status') in (403,429,412,'site_stopped') or m.get('blocked'):results.append({'url':u,'status':'site_stopped'});continue
 results.append(fetch(u,k))
# exactly one recruitment detail per chosen host, from already fetched inventory hrefs
for host,pattern in [('www.puh3.net.cn','非在编|超声医助|信息管理与大数据'),('www.gaoxiaojob.com','announcement/detail'),('www.crec.cn','人才招聘')]:
 ims=[json.loads(p.read_text()) for p in (OUT/'snapshots'/host).glob('*/meta.json') if json.loads(p.read_text()).get('kind')=='inventory']
 if not ims:continue
 links=json.loads((ROOT/ims[0]['path']/'links.json').read_text())
 targets=[x for x in links if re.search(pattern,x['label']+' '+x['url']) and urllib.parse.urlsplit(x['url']).netloc==host]
 if host=='www.crec.cn':continue # link is another list, defer to avoid extra list
 if targets:results.append(fetch(targets[0]['url'],'detail'))
(OUT/'supplement-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
