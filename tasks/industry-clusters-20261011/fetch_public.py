"""Archive public official files from a JSON manifest. python3 fetch_public.py manifest.json
Stdlib only. Resumes existing successful downloads, waits >=5s per host, checks robots,
stops a host on 403/429, retries transient failures at most once; no login or side effects remotely.
"""
import json,sys,time,urllib.request,urllib.error,urllib.parse,urllib.robotparser,hashlib,pathlib
# manifest 不当可信输入：输出只许落在本任务证据目录内（防路径穿越/任意读写），URL 只许 http/https（防 file:// 读本地、ftp 等）
base=(pathlib.Path(__file__).resolve().parents[2]/'evidence/industry-clusters-2026-10').resolve()
class SafeRedirect(urllib.request.HTTPRedirectHandler):
 # 默认重定向会跟到 ftp:// 等，绕过上面的 scheme 白名单，这里一并拦掉
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  if urllib.parse.urlparse(newurl).scheme not in ('http','https'):raise urllib.error.HTTPError(newurl,code,'redirect scheme not allowed',headers,fp)
  return super().redirect_request(req,fp,code,msg,headers,newurl)
opener=urllib.request.build_opener(SafeRedirect)
items=json.load(open(sys.argv[1])); last={}; denied=set(); robots={}; log=[]
agent='ResearchArchive/1.0'
for x in items:
 u=x['url'];pu=urllib.parse.urlparse(u);h=pu.netloc
 # 校验放在任何 mkdir/读写之前；拒绝也记日志，results.json 保持逐条完整
 if pu.scheme not in ('http','https') or not h:log.append(dict(x,status='rejected_url'));continue
 p=(base/x['path']).resolve()
 if p==base or not p.is_relative_to(base):log.append(dict(x,status='rejected_path'));continue
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists() and p.stat().st_size:log.append(dict(x,status='cached',sha256=hashlib.sha256(p.read_bytes()).hexdigest()));continue
 if h in denied:log.append(dict(x,status='host_stopped'));continue
 if h not in robots:
  ru=urllib.parse.urljoin(u,'/robots.txt')
  try:
   z=opener.open(urllib.request.Request(ru,headers={'User-Agent':agent}),timeout=25);raw=z.read();rp=urllib.robotparser.RobotFileParser();rp.parse(raw.decode(errors='replace').splitlines());robots[h]=rp
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
   resp=opener.open(urllib.request.Request(u,headers={'User-Agent':agent}),timeout=35);b=resp.read();p.write_bytes(b);log.append(dict(x,status='ok',final_url=resp.url,content_type=resp.headers.get('Content-Type'),sha256=hashlib.sha256(b).hexdigest()));last[h]=time.monotonic();break
  except Exception as e:
   last[h]=time.monotonic()
   if isinstance(e,urllib.error.HTTPError) and e.code in (403,429):denied.add(h)
   if h in denied or attempt==1:log.append(dict(x,status='error',error=str(e)));break
pathlib.Path(sys.argv[1]).with_suffix('.results.json').write_text(json.dumps(log,ensure_ascii=False,indent=2))
print(json.dumps(log,ensure_ascii=False,indent=2))
