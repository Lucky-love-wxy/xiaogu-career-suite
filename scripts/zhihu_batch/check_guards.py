"""Offline regression checks for empty-body and STOP/UNKNOWN guards; no network.
Run: python3 scripts/zhihu_batch/check_guards.py (Python 3 and Node required).
"""
import json, subprocess, tempfile
from pathlib import Path
S=Path(__file__).resolve().parent
reader=(S/'read_loaded_answers.js').read_text()
excluded='https://www.zhihu.com/question/597894539/answer/126502285208'
for bodies, expected in [([(excluded,''),('new','')],'STOP_EMPTY_BODY_OR_LOGIN_REQUIRED'), ([(excluded,'')],'NO_NEW_ANSWERS'), ([('new','own task')],'LOADED_ANSWERS'), ([], 'STOP_EMPTY_BODY_OR_LOGIN_REQUIRED')]:
    mock="const window={}; const location={href:'offline'}; const data="+json.dumps(bodies)+"; const document={title:'offline',body:{innerText:''},querySelectorAll:()=>data.map(([url,body])=>({querySelectorAll:sel=>sel==='meta[itemprop=url]'?[{content:url.includes('/answer/')?url:'https://www.zhihu.com/question/1/answer/9'}]:[],querySelector:sel=>sel==='.RichContent-inner'?{innerText:body}:null}))};"
    result=subprocess.run(['node','-e',mock+'console.log('+reader+');'],capture_output=True,text=True,check=True)
    assert json.loads(result.stdout)['state']==expected,(expected,result.stdout)
search=(S/'search_current_role.js').read_text()
for state in ['UNKNOWN_IN_FLIGHT','STOP_VERIFICATION']:
    mock="const location={hostname:'www.baidu.com'}; const window={__xiaoguOfflineResearchSearchCheckpoint:[{state:"+json.dumps(state)+"}]};const fetch=()=>{throw Error('UNEXPECTED_NETWORK')};"
    result=subprocess.run(['node','-e',mock+'('+search+').then(()=>process.exit(2)).catch(e=>{if(!e.message.startsWith("Refuse:"))process.exit(3)});'],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
journal=(S/'journal.py').read_text()
with tempfile.TemporaryDirectory() as td:
    root=Path(td); e=root/'evidence/zhihu-batch-2026-10';e.mkdir(parents=True)
    journal=journal.replace('ROOT = Path(__file__).resolve().parents[2]', 'ROOT = Path('+repr(td)+')')
    p=root/'journal.py';p.write_text(journal)
    for site in ['baidu','zhihu']:
        for mode in ['unknown','stop']:
            l={'entries':[{'site':site,'state':'UNKNOWN_IN_FLIGHT'}] if mode=='unknown' else [],'stop_events':[{'site':site}] if mode=='stop' else [],'counts':{}}
            (e/'access-ledger.json').write_text(json.dumps(l))
            r=subprocess.run(['python3',str(p),'reserve',site,'search','offline','offline'],capture_output=True,text=True)
            assert r.returncode and 'Refuse:' in r.stderr,(site,mode,r.stdout,r.stderr)
print('PASS: 4 DOM states, 2 browser checkpoint states, 4 durable same-site guards; no network')
