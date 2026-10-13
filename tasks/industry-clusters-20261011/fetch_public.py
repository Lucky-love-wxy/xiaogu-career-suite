"""Archive public official files from a JSON manifest. python3 fetch_public.py manifest.json
Stdlib only. Resumes existing successful downloads, waits >=5s per host, checks robots,
stops a host on 403/429, retries transient failures at most once; no login or side effects remotely.
"""
import json,sys,time,urllib.request,urllib.error,urllib.parse,urllib.robotparser,hashlib,pathlib
items=json.load(open(sys.argv[1])); last={}; denied=set(); robots={}; log=[]
agent='ResearchArchive/1.0'
for x in items:
 u=x['url'];h=urllib.parse.urlparse(u).netloc;p=pathlib.Path(x['path']); p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists() and p.stat().st_size:log.append(dict(x,status='cached',sha256=hashlib.sha256(p.read_bytes()).hexdigest()));continue
 if h in denied:log.append(dict(x,status='host_stopped'));continue
 if h not in robots:
  ru=urllib.parse.urljoin(u,'/robots.txt')
  try:
   z=urllib.request.urlopen(urllib.request.Request(ru,headers={'User-Agent':agent}),timeout=25);raw=z.read();rp=urllib.robotparser.RobotFileParser();rp.parse(raw.decode(errors='replace').splitlines());robots[h]=rp
   p.with_name(h+'.robots.txt').write_bytes(raw)
  except urllib.error.HTTPError as e:
   robots[h]=None
   if e.code in (403,429):denied.add(h);log.append(dict(x,status='robots_host_stopped',error=str(e)));continue
   log.append(dict(url=ru,status='robots_unavailable',error=str(e)))
  except Exception as e:robots[h]=None;log.append(dict(url=ru,status='robots_unknown',error=str(e)))
  last[h]=time.monotonic()
 if robots[h] and not robots[h].can_fetch(agent,u):log.append(dict(x,status='robots_disallow'));continue
 for attempt in range(2):
  time.sleep(max(0,5.2-(time.monotonic()-last.get(h,0))))
  try:
   resp=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':agent}),timeout=35);b=resp.read();p.write_bytes(b);log.append(dict(x,status='ok',final_url=resp.url,content_type=resp.headers.get('Content-Type'),sha256=hashlib.sha256(b).hexdigest()));last[h]=time.monotonic();break
  except Exception as e:
   last[h]=time.monotonic()
   if isinstance(e,urllib.error.HTTPError) and e.code in (403,429):denied.add(h)
   if h in denied or attempt==1:log.append(dict(x,status='error',error=str(e)));break
pathlib.Path(sys.argv[1]).with_suffix('.results.json').write_text(json.dumps(log,ensure_ascii=False,indent=2))
print(json.dumps(log,ensure_ascii=False,indent=2))
