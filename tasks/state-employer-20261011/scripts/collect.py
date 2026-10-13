#!/usr/bin/env python3
"""公开渠道存在性及规则快照。用法 python3 collect.py inventory|rules。
输入 evidence/.../inventory-frozen.json；输出每主机raw/meta/正文/links与请求日志。
仅标准库，无Cookie、登录、API调用或列表翻页；同站请求间隔≥5.2s；403/429/验证码停站。
断点按URL SHA256复用，不重试；robots拒绝不访问条款/详情。未找到规则保持未知。
"""
import urllib.request,urllib.error,urllib.parse,urllib.robotparser,json,pathlib,hashlib,time,threading,concurrent.futures,re,sys
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[3]; OUT=ROOT/'evidence/state-employer-2026-10'; OUT.mkdir(exist_ok=True)
UA='XiaoguResearch/1.0 (public-source audit; no login)';last={};locks={};guard=threading.Lock();stopped={'gzw.nmg.gov.cn'}
for _mf in (OUT/'snapshots').rglob('meta.json'):
 _m=json.loads(_mf.read_text())
 if _m.get('status') in (403,429,412) or _m.get('blocked'):stopped.add(urllib.parse.urlsplit(_m['url']).netloc)
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.text=[];self.links=[];self.skip=0;self.href=None;self.label=[]
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
  if t=='a':self.href=dict(a).get('href');self.label=[]
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
  if t=='a' and self.href:self.links.append((self.href,''.join(self.label).strip()));self.href=None
 def handle_data(self,d):
  if not self.skip:self.text.append(d.strip())
  if self.href:self.label.append(d)
def fetch(url,kind):
 h=urllib.parse.urlsplit(url).netloc.lower()
 if any(x in h for x in ['zhipin.com','maimai.cn']):return {'url':url,'status':'scope_excluded'}
 key=hashlib.sha256(url.encode()).hexdigest()[:20]; d=OUT/'snapshots'/h/key;d.mkdir(parents=True,exist_ok=True);mf=d/'meta.json'
 if mf.exists():return json.loads(mf.read_text())
 with guard:lock=locks.setdefault(h,threading.Lock())
 with lock:
  if h in stopped:return {'url':url,'status':'site_stopped'}
  time.sleep(max(0,5.2-(time.monotonic()-last.get(h,0))));last[h]=time.monotonic()
  m={'url':url,'kind':kind,'accessed':'2026-10-11 Asia/Shanghai','started_epoch':time.time(),'ua':UA,'cookies_sent':False,'path':str(d.relative_to(ROOT))}
  try:
   req=urllib.request.Request(url,headers={'User-Agent':UA});res=urllib.request.urlopen(req,timeout=22);b=res.read(3000000)
   m.update(status=res.status,final_url=res.url,headers=dict(res.headers),bytes=len(b))
   (d/'raw.bin').write_bytes(b)
   charset=res.headers.get_content_charset();txt=''
   for enc in [charset,'utf-8','gb18030']:
    if not enc:continue
    try:txt=b.decode(enc);break
    except (UnicodeDecodeError,LookupError):pass
   if not txt:txt=b.decode('utf-8','replace')
   (d/'raw.txt').write_text(txt)
   p=Parser();p.feed(txt);body='\n'.join(s for s in p.text if s);links=[{'url':urllib.parse.urljoin(res.url,u),'label':n} for u,n in p.links]
   (d/'body.txt').write_text(body);(d/'links.json').write_text(json.dumps(links,ensure_ascii=False,indent=2));m['body_chars']=len(body)
   title=re.search(r'<title[^>]*>(.*?)</title>',txt,re.S|re.I);m['title']=re.sub('<.*?>','',title.group(1)).strip() if title else ''
   if any(w in body[:1500] for w in ['安全验证','请输入验证码','访问过于频繁','人机验证','验证码校验']):m['blocked']='captcha';stopped.add(h)
  except urllib.error.HTTPError as e:
   m.update(status=e.code,error=str(e));(d/'error.txt').write_text(str(e))
   if e.code in (403,429,412):stopped.add(h)
  except Exception as e:m.update(status='error',error=str(e))
  m['finished_epoch']=time.time();mf.write_text(json.dumps(m,ensure_ascii=False,indent=2));print(kind,h,m['status'],flush=True);return m
mode=sys.argv[1]; rows=json.loads((OUT/('inventory-main.json' if mode=='inventory' else 'inventory-frozen.json')).read_text())
# one operation per host in pool; no home/list scraping beyond exact inventory target.
groups={}
for r in rows:
 if r.get('rule_sample'):groups.setdefault(urllib.parse.urlsplit(r['url']).netloc,[]).append(r)
def inventory(g):
 r=g[0];return {'ids':[x['id'] for x in g],'page':fetch(r['url'],'inventory')}
def rules(g):
 r=g[0];u=urllib.parse.urlsplit(r['url']);base=f'{u.scheme}://{u.netloc}';m=fetch(base+'/robots.txt','robots');z={'ids':[x['id'] for x in g],'robots':m,'terms':[]}
 if m.get('status') in (403,429,'site_stopped',412) or m.get('blocked'):z['outcome']='不可用：停站';return z
 d=ROOT/m['path'] if 'path' in m else None
 raw=(d/'raw.txt').read_text() if d and (d/'raw.txt').exists() else ''
 valid=m.get('status')==200 and bool(re.search(r'^\s*User-agent\s*:',raw,re.I|re.M))
 z['robots_valid']=valid;rp=urllib.robotparser.RobotFileParser();rp.parse(raw.splitlines())
 z['paths']=[{'url':x['url'],'allowed':rp.can_fetch(UA,x['url']) if valid else None} for x in g]
 if valid and all(not p['allowed'] for p in z['paths']):z['outcome']='不可用：robots禁止样例路径';return z
 im=fetch(r['url'],'inventory')
 if 'path' not in im or im.get('blocked') or im.get('status') in (403,429):z['outcome']='不可用：正文未取得/停站';return z
 ls=ROOT/im['path']/'links.json';links=json.loads(ls.read_text()) if ls.exists() else []
 terms=[x for x in links if re.search('网站声明|版权声明|法律声明|法律申明|免责声明|用户协议|服务协议|法律协议|使用条款',x['label'])]
 for t in terms[:2]:
  th=urllib.parse.urlsplit(t['url']).netloc
  if th!=u.netloc:continue # different-host rules not inherited
  if valid and not rp.can_fetch(UA,t['url']):z['terms'].append(dict(url=t['url'],status='robots_disallowed'));continue
  z['terms'].append(fetch(t['url'],'terms'))
 # footer quotations are statements too; never interpret bare copyright as automation license
 z['outcome']='规则缺口待人工判读';return z
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:results=list(ex.map(inventory if mode=='inventory' else rules,groups.values()))
(OUT/f'{mode}-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print('DONE',mode,len(results))
