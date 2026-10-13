"""Local request journal; no network. reserve/finish requests, rebuild counts.
Run: python3 scripts/zhihu_batch/journal.py reserve SITE KIND ROLE URL
     python3 scripts/zhihu_batch/journal.py finish EVIDENCE_FILE
An UNKNOWN request counts toward caps. Never reset prior counters on recovery.
"""
import datetime as dt
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
E = ROOT/'evidence/zhihu-batch-2026-10'
f = E/'access-ledger.json'
l = json.loads(f.read_text())
now = dt.datetime.now(dt.timezone.utc)
if sys.argv[1] == 'reserve':
    site, kind, role, url = sys.argv[2:]
    same = [e for e in l['entries'] if e['site']==site]
    if any(e.get('state') == 'UNKNOWN_IN_FLIGHT' for e in same):
        raise SystemExit('Refuse: unresolved same-site UNKNOWN; reconcile saved evidence first')
    if any(e.get('site') == site for e in l.get('stop_events', [])):
        raise SystemExit('Refuse: same-site STOP; no automatic clearance')
    timed = [e for e in same if e.get('opened_at')]
    if timed:
        gap = (now-dt.datetime.fromisoformat(timed[-1]['opened_at'])).total_seconds()
        if gap < 5: raise SystemExit('Refuse: same-site gap below 5 seconds')
    if site=='baidu':
        recent = [e for e in same if (now-dt.datetime.fromisoformat(e['opened_at'])).total_seconds()<3600]
        if len(recent)>=15 or len(same)>=40: raise SystemExit('Refuse: Baidu rolling-hour/batch cap')
    if site=='zhihu' and len(same)+5>=60: raise SystemExit('Refuse: Zhihu daily cap, including pilot')
    l['entries'].append({'sequence':len(l['entries'])+1,'site':site,'kind':kind,'role':role,'url':url,'opened_at':now.isoformat(),'state':'UNKNOWN_IN_FLIGHT'})
elif sys.argv[1] == 'finish':
    name = sys.argv[2]
    d = json.loads((E/name).read_text())
    entry = l['entries'][-1]
    entry.update({'checked_at':d.get('checked_at',now.isoformat()),'state':d['state'],'evidence_file':name,'observed_url':d.get('url')})
    if d.get('query'): entry['query']=d['query']
    if d['state'].startswith('STOP_'):
        l.setdefault('stop_events',[]).append({'site':entry['site'],'sequence':entry['sequence'],'state':d['state'],'evidence_file':name})
l['counts']['baidu_search'] = sum(e['site']=='baidu' for e in l['entries'])
l['counts']['zhihu_body_page_open'] = sum(e['site']=='zhihu' for e in l['entries'])
l['counts']['read_answers'] = len(list(E.glob('answer-*.json')))
l['updated_at'] = now.isoformat()
f.write_text(json.dumps(l,ensure_ascii=False,indent=2))
print(json.dumps({'sequence':len(l['entries']),'counts':l['counts']},ensure_ascii=False))
