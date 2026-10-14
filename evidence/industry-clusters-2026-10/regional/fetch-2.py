import json,time,urllib.request,urllib.error,urllib.parse,urllib.robotparser,hashlib
from pathlib import Path
p=Path(__file__).parent; last={}; blocked=set(); robots={}; out=[]
def fetch(url):
 host=urllib.parse.urlsplit(url).netloc
 time.sleep(max(0,5.1-(time.time()-last.get(host,0))))
 last[host]=time.time()
 req=urllib.request.Request(url,headers={"User-Agent":"ResearchEvidence/1.0"})
 with urllib.request.urlopen(req,timeout=40) as r:return r.read(),r.status,dict(r.headers)
for name,url in json.loads((p/'fetch-inputs-2.json').read_text()):
 host=urllib.parse.urlsplit(url).netloc; row={"file":name,"url":url,"access_date":"2026-10-11","layer":"script-static"}
 if host in blocked:row['error']='site stopped';out.append(row);continue
 try:
  if host not in robots:
   ru=urllib.parse.urlunsplit((urllib.parse.urlsplit(url).scheme,host,'/robots.txt','',''))
   try:
    b,st,h=fetch(ru);(p/(host+'-robots.txt')).write_bytes(b)
    rp=urllib.robotparser.RobotFileParser();rp.parse(b.decode('utf-8','replace').splitlines());robots[host]=rp
   except urllib.error.HTTPError as e:
    if e.code in (403,429):blocked.add(host);raise
    robots[host]=None
   except Exception:robots[host]=None
  if robots[host] and not robots[host].can_fetch('ResearchEvidence/1.0',url):raise RuntimeError('robots disallow')
  b,st,h=fetch(urllib.parse.quote(url,safe=':/?=&%'));(p/name).write_bytes(b);row.update(status=st,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),headers=h)
 except Exception as e:
  row['error']=repr(e)
  if isinstance(e,urllib.error.HTTPError) and e.code in (403,429):blocked.add(host)
 out.append(row);print(name,row.get('status',row.get('error')),flush=True)
 (p/'fetch-manifest-2.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
