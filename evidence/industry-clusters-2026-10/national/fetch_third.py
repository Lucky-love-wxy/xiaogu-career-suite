import requests,pathlib,json,hashlib,time
root=pathlib.Path(__file__).parent
items=[('advanced-2022.pdf','https://www.gov.cn/xinwen/2022-11/30/5729722/files/4f50411cc5a144669fea2c3f47afd94e.pdf'),('sme-2023.pdf','https://www.hunan.gov.cn/zqt/zcsd/202310/31702618/files/85f217cd9cde4f6c9943163999d853b0.pdf'),('innovation-2022-hlj.html','https://www.hlj.gov.cn/hlj/c107856/202302/c00_31549926.shtml'),('innovation-2022-list.jpg','https://www.hlj.gov.cn/hlj/c107856/202302/31549926/images/2.jpg')]
records=[]
for name,url in items:
 try:
  r=requests.get(url,timeout=40);r.raise_for_status();(root/name).write_bytes(r.content);records.append({'file':name,'url':url,'sha256':hashlib.sha256(r.content).hexdigest(),'bytes':len(r.content),'layer':'Python requests static','access_date':'2026-10-11'}); print(name,len(r.content),flush=True)
 except Exception as e: records.append({'file':name,'url':url,'error':str(e)});print(name,str(e),flush=True)
 (root/'manifest-third.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
 time.sleep(5.2)
