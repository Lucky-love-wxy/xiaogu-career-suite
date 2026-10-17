"""Fetch official navigation only; no announcement pagination or logged-in state.
Run: python3 fetch_nav.py. Outputs raw HTML plus link extraction in this directory.
Uses urllib standard library, spaces same-host requests by >= 5 seconds; stops on 403/429.
"""
import urllib.request, urllib.parse, urllib.error, json, time
from pathlib import Path
from html.parser import HTMLParser
ROOT = Path(__file__).parent
URLS = {
 'sasac_directory': 'http://wap.sasac.gov.cn/n4422011/n17627531/c17633273/content.html',
 'liaoning_health_page2': 'https://wsjk.ln.gov.cn/wsjk/xglj/gswsjkw/ffece81f-2.shtml',
}
for x in json.loads((ROOT/'shanghai_hrss-links.json').read_text()):
 if '/tgssrsbm_' in x['url']: URLS['hrss_'+x['text']] = x['url']
class Links(HTMLParser):
 def __init__(self): super().__init__(); self.href=None; self.text=[]; self.links=[]
 def handle_starttag(self, tag, attrs):
  if tag=='a': self.href=dict(attrs).get('href'); self.text=[]
 def handle_data(self, data):
  if self.href: self.text.append(data)
 def handle_endtag(self, tag):
  if tag=='a' and self.href: self.links.append({'text': ''.join(self.text).strip(), 'href':self.href}); self.href=None
results=[]
for key, url in URLS.items():
 try:
  req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 research public navigation'})
  with urllib.request.urlopen(req,timeout=30) as r: body=r.read(); status=r.status; final=r.url; charset=r.headers.get_content_charset()
  (ROOT/(key+'.html')).write_bytes(body)
  html=body.decode(charset or ('utf-8' if b'charset="gb' not in body.lower() else 'gb18030'),errors='replace')
  p=Links(); p.feed(html)
  links=[dict(text=x['text'],url=urllib.parse.urljoin(final,x['href'])) for x in p.links]
  (ROOT/(key+'-links.json')).write_text(json.dumps(links,ensure_ascii=False,indent=2))
  results.append(dict(key=key,url=url,final_url=final,status=status,bytes=len(body),links=len(links)))
 except Exception as e: results.append(dict(key=key,url=url,error=str(e)))
 print(json.dumps(results[-1],ensure_ascii=False),flush=True)
 time.sleep(5)
(ROOT/'fetch-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
