import requests,pathlib,json,hashlib,time
root=pathlib.Path(__file__).parent
items=[('advanced-2022-gov.html','https://www.gov.cn/xinwen/2022-11/30/content_5729722.htm'),('innovation-2021-cumulative.pdf','https://kjt.hubei.gov.cn/kjdt/tzgg/202103/P020210311662149536169.pdf'),('innovation-confirm-2022.html','https://www.most.gov.cn/dfkj/hub/zxdt/202303/t20230316_185131.html'),('sme-2025-hebei.html','https://gxt.hebei.gov.cn/main/policy/zxzcdetail?id=a64da019-3a6a-4cf7-9d61-ca2b12ebb78b')]
records=[]
for name,url in items:
 try:
  r=requests.get(url,timeout=35);r.raise_for_status();(root/name).write_bytes(r.content);records.append({'file':name,'url':url,'sha256':hashlib.sha256(r.content).hexdigest(),'bytes':len(r.content),'layer':'Python requests static','access_date':'2026-10-11'}); print(name,len(r.content),flush=True)
 except Exception as e: records.append({'file':name,'url':url,'error':str(e)});print(name,str(e),flush=True)
 (root/'manifest-second.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
 time.sleep(5.2)
