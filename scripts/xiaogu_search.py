#!/usr/bin/env python3
"""Deterministic lookup for Xiaogu jargon and occupation records."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JARGON=ROOT/'database/jargon.json'
OCC=ROOT/'database/occupations.json'

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def jargon(query):
    rows=[]
    for e in load(JARGON):
        terms=[e.get('term',''),*e.get('aliases',[])]
        hits=[t for t in terms if t and t.lower() in query.lower()]
        if hits:
            rows.append({'id':e.get('id',e['term']),'term':e['term'],'matched_text':max(hits,key=len),'entry':e,'source':'database/jargon.json','confidence':'exact_or_alias'})
    rows.sort(key=lambda x:(-len(x['matched_text']),x['term']))
    return {'query':query,'type':'jargon','status':'matched' if rows else 'index_miss','matches':rows}
def occupation(query,limit=5):
    q=query.lower(); out=[]
    for e in load(OCC):
        name=e['name']; aliases=e.get('aliases',[]); kws=e.get('keywords',[])
        nh=name.lower() in q; ah=[x for x in aliases if x.lower() in q]; kh=[x for x in kws if x.lower() in q]
        score=(30 if nh else 0)+len(ah)*18+len(kh)*4
        if nh or ah or len(kh)>=2:
            out.append({'id':e['id'],'name':name,'score':score,'confidence':'high' if nh or ah else 'medium','matched_terms':([name] if nh else [])+ah+kh,'occupation':e,'source':'database/occupations.json'})
    out.sort(key=lambda x:(-x['score'],x['name']))
    return {'query':query,'type':'occupation','status':'matched' if out else 'index_miss','matches':out[:max(0,limit)]}
def analyze(text):
    return {'query':text,'type':'analyze','jargon':jargon(text),'occupation':occupation(text)}
def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='kind',required=True)
    for name in ('jargon','occupation','analyze'):
        sp=sub.add_parser(name); sp.add_argument('--query',required=True); sp.add_argument('--limit',type=int,default=5)
    a=p.parse_args(); r=jargon(a.query) if a.kind=='jargon' else occupation(a.query,a.limit) if a.kind=='occupation' else analyze(a.query)
    print(json.dumps(r,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
