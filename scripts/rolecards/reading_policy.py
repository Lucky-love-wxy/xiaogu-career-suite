#!/usr/bin/env python3
"""从业者公开网页采集的共享只读节奏规则（不发网络请求）。
CLI: python3 scripts/rolecards/reading_policy.py count <canonical_source.json>
网络操作者先reserve，之后complete；所有执行者共用同一ledger，限制页触发当日stop。
"""
import json,re,time,random,fcntl,sys
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEDGER=ROOT/'evidence/practitioner-2026-10/access-ledger.json'
TZ=ZoneInfo('Asia/Shanghai')
def body_length(text):
    # 标签属于元数据，不能靠话题标签填满长文门槛；不删正文Markdown标题。
    text=re.sub(r'#[^#\n]*\[话题\]#','',text)
    lines=[x for x in text.splitlines() if not re.fullmatch(r'(?:#[^\s#]+[ \t]*)+',x.strip())]
    return len(re.sub(r'\s+','','\n'.join(lines)))
def transact(update):
    LEDGER.parent.mkdir(parents=True,exist_ok=True)
    with LEDGER.with_suffix('.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        d=json.loads(LEDGER.read_text()) if LEDGER.exists() else {'events':[],'blocked_days':{}}
        result=update(d);LEDGER.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');return result

def reserve(site,kind,url,known_chars=None):
    if kind not in ('search','body','rules','recovery'):raise ValueError(kind)
    if kind=='body':
        threshold=500 if site=='xiaohongshu.com' else 800
        if known_chars is None or known_chars<threshold:raise ValueError('长度未知或不足，先用标题/本地长文筛选；不打开详情探长度')
    now=datetime.now(TZ);today=now.date().isoformat()
    def check(d):
        if any(e.get('state')=='reserved' for e in d['events']):raise RuntimeError('上一个请求尚未检查实际页面，不能发下一请求')
        if any(e.get('state')=='body_verified' and not e.get('read_end') for e in d['events']):raise RuntimeError('上一篇正文尚未完成真实阅读停留')
        blocked=d['blocked_days'].get(site)
        if blocked==today:raise RuntimeError('该站点当日已停，不再请求')
        if blocked and kind!='recovery':raise RuntimeError('限制尚未核验恢复，跨日不自动放行')
        if kind=='recovery':
            last_block=next((e for e in reversed(d['events']) if e['site']==site and (e.get('state') in ('captcha','too_frequent','http_429','http_403','empty_redirect') or e.get('stop_site_today'))),None)
            if not blocked or not last_block or not url or url!=last_block.get('url'):raise ValueError('恢复检查只适用于前日停站的同一已观察入口')
        es=[e for e in d['events'] if e['site']==site];hour=now-timedelta(hours=1)
        if kind=='search' and sum(e['kind']=='search' and datetime.fromisoformat(e['at'])>=hour for e in es)>=15:raise RuntimeError('该站点每小时搜索已达15')
        if kind=='body' and sum(e['kind']=='body' and e['at'][:10]==today for e in es)>=60:raise RuntimeError('该站点当日正文已达60')
        if es:
            gap=(now-datetime.fromisoformat(es[-1]['at'])).total_seconds()
            if gap<5:raise RuntimeError(f'同站尚需等待{5-gap:.1f}秒（执行时另加随机波动）')
        session=d.get('continuous_started_at')
        if session and (now-datetime.fromisoformat(session)).total_seconds()>=1200:
            raise RuntimeError('连续操作20分钟，先休息5分钟并记录rest，再请求；换站/agent不重置')
        if not session:d['continuous_started_at']=now.isoformat()
        key=f'{site}:{len(d["events"])+1}'
        d['events'].append({'id':key,'site':site,'kind':kind,'url':url,'known_body_char_n':known_chars,'at':now.isoformat(),'state':'reserved'})
        return key
    return transact(check)
def complete(key,state,body_char_n=None,evidence_file=None):
    if state not in ('body_verified','results_verified','rules_verified','captcha','too_frequent','http_429','http_403','empty_redirect','error'):raise ValueError(state)
    def update(d):
        e=next(x for x in d['events'] if x['id']==key)
        if e['state']!='reserved':raise ValueError('请求终态已记录，不能覆盖')
        if e['kind']=='recovery' and state=='results_verified' and not evidence_file:raise ValueError('恢复检查必须有实际页面证据')
        e.update(state=state,checked_at=datetime.now(TZ).isoformat(),body_char_n=body_char_n,evidence_file=evidence_file)
        if e['kind']=='recovery' and state=='results_verified':
            d['blocked_days'].pop(e['site'],None)
        if state in ('captcha','too_frequent','http_429','http_403','empty_redirect'):d['blocked_days'][e['site']]=datetime.now(TZ).date().isoformat()
    transact(update)
def record_reading(key,start,end,chars):
    required=chars*30/1000
    if chars<0 or end>datetime.now(TZ) or (end-start).total_seconds()<required:raise ValueError('未达到真实阅读停留时长')
    def update(d):
        e=next(x for x in d['events'] if x['id']==key)
        if e['kind']!='body' or e['state']!='body_verified' or not e.get('checked_at') or not e.get('body_char_n') or start<datetime.fromisoformat(e['checked_at']):raise ValueError('阅读须在该正文请求之后')
        if e.get('body_char_n') is not None and chars!=e['body_char_n']:raise ValueError('阅读字数须与已检查正文相同')
        e.update(read_start=start.isoformat(),read_end=end.isoformat(),body_char_n=chars,required_read_seconds=required)
    transact(update)

def record_rest(start,end):
    if end>datetime.now(TZ) or (end-start).total_seconds()<300:raise ValueError('休息不足真实5分钟')
    def update(d):
        if any(e.get('state')=='reserved' or (e.get('state')=='body_verified' and not e.get('read_end')) for e in d['events']):raise ValueError('请求检查及阅读未完成，不能计休息')
        last=max([datetime.fromisoformat(e.get('read_end') or e.get('checked_at') or e['at']) for e in d['events']]+[datetime.fromisoformat(r['end']) for r in d.get('rests',[])],default=start)
        if start<last:raise ValueError('休息须在最后活动之后且不复用')
        d.setdefault('rests',[]).append({'start':start.isoformat(),'end':end.isoformat()});d['continuous_started_at']=None
    transact(update)
if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='count':
        raw=json.loads(Path(sys.argv[2]).read_text());print(body_length(raw['desc']))
    else:raise SystemExit(__doc__)
