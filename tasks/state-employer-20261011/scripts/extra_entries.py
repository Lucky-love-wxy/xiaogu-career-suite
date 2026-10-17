from pathlib import Path
import json,urllib.parse,re
s=Path('/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/tasks/state-employer-20261011/scripts/collect.py').read_text().split('mode=sys.argv[1]')[0];exec(compile(s,'collect.py','exec'))
updates=[]
for name,u in [('四川省国资入口','https://gzw.sc.gov.cn/scsgzw/c100138/lxfs.shtml'),('西藏自治区国资入口（政府网公开报告替代，独立门户未找到）','https://www.xizang.gov.cn/zwgk/xxgk_424/xxgknb/2023nb/202401/t20240129_401305.html')]:
 h=urllib.parse.urlsplit(u);m=fetch(f'{h.scheme}://{h.netloc}/robots.txt','robots');raw=(ROOT/m['path']/'raw.txt').read_text() if 'path' in m and (ROOT/m['path']/'raw.txt').exists() else '';allowed=True
 if re.search('^User-agent:',raw,re.M|re.I):
  rp=urllib.robotparser.RobotFileParser();rp.parse(raw.splitlines());allowed=rp.can_fetch(UA,u)
 page=fetch(u,'official-entry') if allowed else {'url':u,'status':'robots_disallowed'}
 updates.append(dict(name=name,url=u,robots=m,page=page))
(OUT/'inventory-amendments.json').write_text(json.dumps(updates,ensure_ascii=False,indent=2))
