import urllib.request,time,json,pathlib
p=pathlib.Path('/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/evidence/state-employer-2026-10/static-fallback');p.mkdir(exist_ok=True)
for key,u in [('guopin-terms','https://www.iguopin.com/doc/info?channel_alias=User_Service'),('ciic-terms','https://sso.ciiczhaopin.com/serviceagreement')]:
 try:
  r=urllib.request.urlopen(urllib.request.Request('https://r.jina.ai/'+u,headers={'User-Agent':'XiaoguResearch/1.0'}),timeout=45);b=r.read();(p/(key+'.txt')).write_bytes(b);m={'source_url':u,'layer':'web-access static Jina extraction; no user session','status':r.status,'accessed':'2026-10-11','bytes':len(b)}
 except Exception as e:m={'source_url':u,'error':str(e),'accessed':'2026-10-11'}
 (p/(key+'.json')).write_text(json.dumps(m,ensure_ascii=False,indent=2));print(m,flush=True);time.sleep(5.2)
