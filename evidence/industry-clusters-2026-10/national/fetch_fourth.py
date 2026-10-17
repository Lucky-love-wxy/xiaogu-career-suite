import requests,pathlib,json,hashlib,time,urllib.parse
root=pathlib.Path(__file__).parent
items=[('sme-2023.pdf','https://www.chinasme.org.cn/upload/1/cms/content/editor/1697786887617.pdf'),('sme-2025.pdf','https://gyxxh.tj.gov.cn/ZWGK4147/ZCWJ6355/gjjwj/202511/W020251106409440997860.pdf'),('innovation-management-2026.html','https://www.beinet.net.cn/zcfg/zcfb/gj_10995/202610/t14470519.html'),('guangdong-sme-2024-yingde.html','https://www.yingde.gov.cn/zljs/zszx/zsdt/content/post_1891618.html')]
records=[];blocked=set();last={}
for name,url in items:
 host=urllib.parse.urlparse(url).netloc
 if host in blocked: continue
 time.sleep(max(0,5.2-(time.monotonic()-last.get(host,0))))
 try:
  r=requests.get(url,timeout=40);last[host]=time.monotonic()
  if r.status_code in (403,429):blocked.add(host)
  r.raise_for_status();(root/name).write_bytes(r.content);records.append({'file':name,'url':url,'sha256':hashlib.sha256(r.content).hexdigest(),'bytes':len(r.content),'layer':'Python requests static','access_date':'2026-10-11'}); print(name,len(r.content),flush=True)
 except Exception as e: records.append({'file':name,'url':url,'error':str(e)});print(name,str(e),flush=True)
 (root/'manifest-fourth.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
