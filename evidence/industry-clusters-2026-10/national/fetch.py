"""Public official snapshots; 5s host spacing, bounded retry, resume, SHA256. Run: python3 fetch.py"""
import requests,time,pathlib,json,hashlib,urllib.parse
root=pathlib.Path(__file__).parent
items=[
('advanced-2022.html','https://www.miit.gov.cn/xwdt/gxdt/sjdt/art/2022/art_8d77dc1565ce423e980f597c9c17601c.html'),
('advanced-2022.pdf','https://www.miit.gov.cn/cms_files/filemanager/1226211233/attach/202210/a9fdce8756724b459a4fa2dcc3735082.pdf'),
('advanced-2024.html','https://www.miit.gov.cn/zwgk/zcwj/wjfb/tz/art/2024/art_52ac73d422f440e2ac36da0259eb30f8.html'),
('advanced-2024.pdf','https://www.gov.cn/zhengce/zhengceku/202412/P020241216828680409717.pdf'),
('sme-2023.html','https://www.miit.gov.cn/zwgk/zcwj/wjfb/tg/art/2023/art_0b55574b3f3943e68e815f5eb0854dee.html'),
('sme-2023.pdf','https://www.miit.gov.cn/cms_files/filemanager/1226211233/attach/20238/1390bc67ac7a4b88b0eeb6fb4cb1522b.pdf'),
('sme-2025.html','https://www.miit.gov.cn/zwgk/zcwj/wjfb/tg/art/2025/art_84aa1e893c174f64973537495109d6aa.html'),
('sme-2025.pdf','https://www.miit.gov.cn/cms_files/filemanager/1226211233/attach/202510/b38d359736bc48408f7977561e84bd02.pdf'),
('sme-2022-recheck-2025.pdf','https://www.miit.gov.cn/cms_files/filemanager/1226211233/attach/202510/f9f5b17a312242b489be012fb37359c5.pdf'),
('sme-standard-2022.html','https://www.miit.gov.cn/zwgk/zcwj/wjfb/tz/art/2022/art_2e39162e00e346ebb7611da191f5e36e.html'),
('sme-recommend-2026.html','https://wap.miit.gov.cn/jgsj/qyj/wjfb/art/2026/art_16bf1fe5ae504010ba309f90c2bc6e62.html'),
('guangdong-sme-2024.html','https://gxj.gz.gov.cn/fw/gzzxqyzhfwpt/zhxw/rdxw/content/post_9764435.html'),
('innovation-2022-official.html','https://www.chinatorch.gov.cn/kjb/tzgg/202302/d8f9752e9ef04cccb34b34f0d2c4693c.shtml'),
('innovation-2022-publicity.html','https://www.ncsti.gov.cn/kjdt/tzgg/202302/t20230209_108262.html'),
('sock-official-description.html','https://zjic.zj.gov.cn/zkfw/szhfn/202308/t20230802_20367704.shtml')]
last={};blocked=set();records=[]
for name,url in items:
 host=urllib.parse.urlparse(url).netloc; p=root/name
 if p.exists(): records.append({'file':name,'url':url,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'resumed':True});continue
 if host in blocked: records.append({'file':name,'url':url,'error':'host stopped after denial'});continue
 time.sleep(max(0,5.2-(time.monotonic()-last.get(host,0))))
 try:
  r=requests.get(url,timeout=40);last[host]=time.monotonic()
  if r.status_code in (403,429): blocked.add(host)
  r.raise_for_status()
  if name.endswith('.pdf') and not r.content.startswith(b'%PDF'):raise ValueError('not PDF')
  p.write_bytes(r.content);records.append({'file':name,'url':url,'status':r.status_code,'bytes':len(r.content),'sha256':hashlib.sha256(r.content).hexdigest(),'access_date':'2026-10-11','layer':'Python requests static'})
  print(name,len(r.content),flush=True)
 except Exception as e: records.append({'file':name,'url':url,'error':str(e)});print(name,str(e),flush=True)
 (root/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
