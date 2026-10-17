#!/usr/bin/env python3
"""离线汇总TikHub本批请求账本；不联网，失败/未知尝试保守占用预算。
运行 python3 scripts/rolecards/summarize_api.py；实际扣费仍以billing余额回读核对。
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EV=ROOT/'evidence/practitioner-2026-10/tikhub'
def main():
    rows=[]
    for p in sorted(EV.glob('request-*.json')):
        x=json.loads(p.read_text());n=x.get('call_n') or x.get('attempt_n')
        rows.append({'n':n,'file':str(p.relative_to(ROOT)),'role':x['role'],'endpoint':x['endpoint'],
            'state':'success' if x.get('http')==200 and x.get('code')==200 else x.get('result','failure'),
            'request_id':x.get('request_id')})
    assert len({x['n'] for x in rows})==len(rows),'duplicate attempt numbers'
    assert sorted(x['n'] for x in rows)==list(range(1,len(rows)+1)),'attempt gap'
    assert len(rows)<=100
    successful=sum(x['state']=='success' for x in rows)
    result={'attempts':rows,'total_attempt_n':len(rows),'successful_n':successful,'unknown_n':sum(x['state']=='UNKNOWN' for x in rows),
        'conservative_budget_consumed_usd':round(len(rows)*.01,2),'successful_request_price_sum_usd':round(successful*.01,2),
        'remaining_max_attempts':100-len(rows),'authorization':'2026-10-07 user approved additional US$1.00, max100 attempts including failures, no recharge/no retry',
        'actual_billing':'余额回读独立记录billing.json，不把保守预算占用冒充实际扣费。'}
    (EV/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print({k:v for k,v in result.items() if k not in ('attempts','authorization')})
if __name__=='__main__':main()
