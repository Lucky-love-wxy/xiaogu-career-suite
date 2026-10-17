import urllib.request,urllib.error,json,time,hashlib,pathlib,sys
from urllib.parse import urlsplit
root=pathlib.Path(__file__).parent
last={}; entries=[]
def get(id,url):
 h=urlsplit(url).netloc; time.sleep(max(0,3.1-(time.monotonic()-last.get(h,0))))
 req=urllib.request.Request(url,headers={'User-Agent':'CodexResearch/1.0','Accept':'application/vnd.github+json' if h=='api.github.com' else '*/*'})
 try:
  with urllib.request.urlopen(req,timeout=40) as r:data=r.read();status=r.status
 except urllib.error.HTTPError as e:
  data=e.read();status=e.code
  if status in [403,429]:raise RuntimeError('STOP '+h+' '+str(status))
 last[h]=time.monotonic();p=root/(id+'.txt');p.write_bytes(data)
 entries.append(dict(id=id,url=url,status=status,snapshot=str(p),snapshot_type='raw HTTP response body',sha256=hashlib.sha256(data).hexdigest(),accessed='2026-10-14',layer='script/static',level=1))
 print(id,status,len(data),flush=True)
 return data
for host in ['api.github.com','raw.githubusercontent.com']:
 get('oss-robots-'+host.split('.')[0],'https://'+host+'/robots.txt')
repos={'mem0':'mem0ai/mem0','letta':'letta-ai/letta','langgraph':'langchain-ai/langgraph','graphiti':'getzep/graphiti'}
if sys.argv[-1]=='scout':
 for name,repo in repos.items():
  c=json.loads(get('oss-'+name+'-commit','https://api.github.com/repos/'+repo+'/commits/HEAD'));sha=c['sha']
  get('oss-'+name+'-tree','https://api.github.com/repos/'+repo+'/git/trees/'+sha+'?recursive=1')
  get('oss-'+name+'-readme','https://raw.githubusercontent.com/'+repo+'/'+sha+'/README.md')
else:
 plan=json.loads((root/'oss-plan.json').read_text())
 for item in plan:get(item['id'],item['url'])
(root/('oss-fetch-'+sys.argv[-1]+'.json')).write_text(json.dumps(entries,ensure_ascii=False,indent=2))
