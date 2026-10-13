#!/usr/bin/env python3
"""Company-check pilot collector (stdlib only).

Usage: python3 scripts/companycheck/collect.py search|fetch PLAN.json
       python3 scripts/companycheck/collect.py usage LABEL
Inputs: JSON list of {id, company, query, include_domains?} or {id, company, url, channel}.
Outputs: ignored evidence snapshots, SHA256 manifest and request ledger.
No cookies/login; keychain secret only in memory. Resume by immutable item id.
Robots failures are fail-closed; >=3s between requests to a host. HTTP
403/429, quota/risk/captcha stop that host for the local day, with no retries.
"""
import argparse, datetime, fcntl, hashlib, json, pathlib, subprocess, time, urllib.error, urllib.parse, urllib.request, urllib.robotparser

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'evidence/company-check-2026-10'
UA = 'CompanyCheckResearch/1.0'
TODAY = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).date().isoformat()
LEDGER = OUT / 'ledger.json'

def read(p, default):
    return json.loads(p.read_text()) if p.exists() else default

def save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2))
    tmp.replace(p)

state = read(LEDGER, {'api_calls': 0, 'search_calls': 0, 'last_request': {}, 'stopped': {}})

def site_key(host):
    # Explicit registry-domain allowlist for this pilot; do not guess with the
    # last two labels (which would incorrectly merge gov.cn/com.cn websites).
    for domain in ('qcc.com', 'tianyancha.com', 'hkexnews.hk', 'gsxt.gov.cn',
                   'mihoyo.com','baichuan-ai.com','bytedance.com','x-humanoid.com',
                   'volcengine.com','oceanengine.com','feishu.cn','caixin.com',
                   'bjnews.com.cn','yicai.com','cls.cn','lanjinger.com','wikipedia.org'):
        if host == domain or host.endswith('.'+domain): return domain
    return host

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # record 30x; a new URL requires its own robots check

def request(url, data=None, headers=None):
    host = urllib.parse.urlsplit(url).netloc
    site = site_key(host)
    if state['stopped'].get(site, {}).get('date') == TODAY:
        raise RuntimeError('site_stopped_today: ' + site)
    time.sleep(max(0, 3.1 - (time.time() - state['last_request'].get(site, 0))))
    state['last_request'][site] = time.time()
    save(LEDGER, state)
    if host == 'api.tavily.com':
        if state['api_calls'] >= 60:
            raise RuntimeError('60 API call cap reached')
        state['api_calls'] += 1
        if url.endswith('/search'): state['search_calls'] += 1
        save(LEDGER, state)  # count attempts before sending, never hide failed calls
    started = time.monotonic()
    req = urllib.request.Request(url, data=data, headers={'User-Agent': UA, **(headers or {})})
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=45) as r:
            raw, status, final = r.read(), r.status, r.url
            mime = r.headers.get('Content-Type', '')
    except urllib.error.HTTPError as e:
        raw, status, final, mime = e.read(), e.code, url, ''
    if status in (401, 403, 429, 432, 433, 521, 567) or (host == 'api.tavily.com' and status >= 400):
        state['stopped'][site] = {'date': TODAY, 'reason': f'HTTP {status}'}
        save(LEDGER, state)
    # Detect concrete challenge forms, not the word captcha inside ordinary articles.
    low = raw[:500000].decode('utf-8', errors='ignore').lower()
    signals = ('访问过于频繁', '访问频繁', '请完成验证', '请输入验证码', '验证后继续访问', 'verify you are human', 'cf-chl-', '访问验证', 'var arg1=', 'acw_sc__v2')
    if any(s in low for s in signals):
        state['stopped'][site] = {'date': TODAY, 'reason': 'captcha_or_risk_page'}
        save(LEDGER, state)
    if site == 'tianyancha.com' and '扫码登录' in low and '天眼查-商业查询平台' in low:
        state['stopped'][site] = {'date': TODAY, 'reason': 'login_required_generic_shell'}
        save(LEDGER, state)
    return raw, {'url': url, 'final_url': final, 'status': status, 'content_type': mime,
                 'elapsed_seconds': round(time.monotonic()-started, 3), 'access_date': TODAY,
                 'sha256': hashlib.sha256(raw).hexdigest(), 'blocked': state['stopped'].get(site)}

def snapshot(item_id, raw, meta, suffix):
    path = OUT / (item_id + suffix)
    path.write_bytes(raw)
    meta['snapshot'] = str(path.relative_to(ROOT))
    save(OUT / (item_id + '.meta.json'), meta)

def key():
    p = subprocess.run(['security', 'find-generic-password', '-s', 'xiaogu-tavily', '-w'], capture_output=True, text=True)
    if p.returncode: raise RuntimeError('Keychain read failed; secret was not printed')
    return p.stdout.strip()

def robots_allowed(url):
    parts = urllib.parse.urlsplit(url)
    base = parts.scheme + '://' + parts.netloc
    rid = 'robots-' + parts.netloc.replace('.', '-')
    meta_path = OUT / (rid + '.meta.json')
    if not meta_path.exists():
        raw, meta = request(base + '/robots.txt')
        snapshot(rid, raw, meta, '.txt')
    meta = read(meta_path, {})
    if meta.get('blocked'): return False, 'robots_site_blocked'
    if meta['status'] in (404, 410): return True, 'robots_absent'
    if meta['status'] != 200: return False, 'robots_unknown_http_' + str(meta['status'])
    rp = urllib.robotparser.RobotFileParser()
    rp.parse((OUT / (rid+'.txt')).read_text(errors='replace').splitlines())
    return rp.can_fetch(UA, url), 'robots_checked'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['search', 'fetch', 'usage'])
    ap.add_argument('input')
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.mode == 'usage':
        if (OUT/('usage-'+args.input+'.meta.json')).exists():
            print('usage snapshot cached; use a new label for a new observation')
            return
        raw, meta = request('https://api.tavily.com/usage', headers={'Authorization': 'Bearer '+key()})
        snapshot('usage-'+args.input, raw, meta, '.json')
        print(raw.decode() if meta['status'] == 200 else json.dumps(meta))
        return
    secret = key() if args.mode == 'search' else None
    for item in read(pathlib.Path(args.input), []):
        if (OUT/(item['id']+'.meta.json')).exists():
            print(item['id'], 'cached', flush=True); continue
        try:
            if args.mode == 'search':
                payload = {'query':item['query'], 'search_depth':'basic', 'max_results':6,
                           'include_raw_content':True, 'include_answer':False, 'include_usage':True}
                if 'include_domains' in item: payload['include_domains'] = item['include_domains']
                raw, meta = request('https://api.tavily.com/search', json.dumps(payload).encode(),
                                    {'Authorization':'Bearer '+secret, 'Content-Type':'application/json'})
                meta.update({**item, 'layer':'script:Tavily', 'channel':'tavily'})
                snapshot(item['id'], raw, meta, '.json')
            else:
                ok, reason = robots_allowed(item['url'])
                if not ok:
                    save(OUT/(item['id']+'.meta.json'), {**item, 'access_date':TODAY, 'status':'not_fetched', 'reason':reason})
                    print(item['id'], reason, flush=True)
                    if reason=='robots_site_blocked': raise SystemExit(2)
                    continue
                raw, meta = request(item['url'])
                meta.update({**item, 'layer':'script:urllib', 'robots':reason})
                snapshot(item['id'], raw, meta, '.pdf' if raw.startswith(b'%PDF') else '.html')
            print(item['id'], meta['status'], meta['elapsed_seconds'], flush=True)
            if meta.get('blocked'):
                print('site guard triggered: raw response saved; exiting batch',flush=True)
                raise SystemExit(2)
        except Exception as e:
            # Never print an exception that may contain credentials or HTTP request bodies.
            save(OUT/(item['id']+'.meta.json'), {**item, 'access_date':TODAY, 'status':'error', 'error_type':type(e).__name__, 'reason':str(e) if isinstance(e,RuntimeError) else 'transport_error'})
            print(item['id'], type(e).__name__, flush=True)
            if isinstance(e,RuntimeError) and str(e).startswith('site_stopped_today:'):
                raise SystemExit(2)

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT/'collector.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = read(LEDGER, {'api_calls':0,'search_calls':0,'last_request':{},'stopped':{}})
        main()
