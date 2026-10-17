"""公开页面只读CDP取证。用法: python3 cdp_collect.py --out DIR --urls URL...
仅使用现有127.0.0.1:3456代理；不读取账号/凭证；每页保存DOM/HTML/截图。
证据原始文件不得入Git。失败退出，不切换网络路径。
"""
import argparse,json,time,urllib.request,urllib.parse,urllib.error,hashlib
from pathlib import Path
raise SystemExit('本脚本已停用：用户最新规则只允许单条执行绝对路径 node cdp.mjs，禁止Python直连代理。')
BASE='http://127.0.0.1:3456'
def api(path,body=None):
 req=urllib.request.Request(BASE+path,data=body.encode() if body else None)
 try:
  with urllib.request.urlopen(req,timeout=55) as r:return json.load(r)
 except urllib.error.HTTPError as exc:
  body=exc.read().decode('utf-8',errors='replace')
  print(json.dumps({'endpoint':path.split('?')[0],'status':exc.code,'error_body':body[:2000]},ensure_ascii=False),flush=True)
  raise
def collect(url,out):
 key=hashlib.sha256(url.encode()).hexdigest()[:12]
 dest=out/key;dest.mkdir(parents=True,exist_ok=True)
 tab=api('/new?'+urllib.parse.urlencode({'url':url}))['targetId']
 try:
  time.sleep(3)
  expr='JSON.stringify({url:location.href,title:document.title,text:document.body?.innerText,links:Array.from(document.querySelectorAll("a[href]")).map(a=>({text:a.innerText,url:a.href})),html:document.documentElement.outerHTML})'
  x=api('/eval?'+urllib.parse.urlencode({'target':tab}),expr)
  if 'value' not in x:raise RuntimeError(str(x))
  page=json.loads(x['value']);page['requested_url']=url;page['accessed_at']='2026-10-04';page['target_id']=tab
  (dest/'page.json').write_text(json.dumps(page,ensure_ascii=False,indent=2))
  (dest/'body.txt').write_text(page.get('text') or '')
  (dest/'page.html').write_text(page.pop('html') or '')
  shot=api('/screenshot?'+urllib.parse.urlencode({'target':tab,'file':str((dest/'screenshot.png').resolve())}))
  (dest/'screenshot-result.json').write_text(json.dumps(shot,ensure_ascii=False))
  print(json.dumps({'key':key,'url':page['url'],'title':page['title'],'text':page['text'][:16000],'evidence':str(dest)},ensure_ascii=False),flush=True)
 finally:api('/close?'+urllib.parse.urlencode({'target':tab}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--urls',nargs='+',required=True);a=p.parse_args()
 for url in a.urls:collect(url,a.out)
