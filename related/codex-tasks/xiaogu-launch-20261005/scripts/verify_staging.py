#!/usr/bin/env python3
"""在服务器上验收localhost staging（模拟模型），只创建明确标记的虚拟测试账号。
运行：/opt/xiaogu/staging/.venv/bin/python verify_staging.py
不输出验证码、口令、cookie或用户内容；只输出检查结果。依赖应用及标准库。
"""
import http.cookiejar
import json
import re
import secrets
import sqlite3
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
sys.path.insert(0, '/opt/xiaogu/staging/web')
from store import Store
base = 'http://127.0.0.1:8102'
store = Store('/var/lib/xiaogu/staging/xiaogu.db', env='staging')
results = {}
def request(opener, path, data=None):
    req=urllib.request.Request(base+path, data=None if data is None else json.dumps(data).encode(),
                              headers={'Content-Type':'application/json'})
    try:
        with opener.open(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
plain=urllib.request.build_opener()
status, meta=request(plain,'/api/meta')
assert status==200 and meta['env']=='staging' and meta['provider']=='mock'
results['meta_staging_mock']='PASS'
assert request(plain,'/api/chat',{'message':'测试'})[0]==401
results['unauthenticated_chat']='PASS'
clients=[]
for i in range(2):
    contact=f'staging-check-{secrets.token_hex(5)}@example.invalid'
    invite=store.create_invites(1,500,max_uses=1,note='synthetic staging acceptance')[0]
    jar=http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    status, body=request(opener,'/api/auth/code',{'contact':contact})
    assert status==200 and 'dev_code' not in body
    log=subprocess.check_output(['journalctl','-u','xiaogu@staging','--since','5 minutes ago','--no-pager','-o','cat'],text=True)
    codes=re.findall(r'\[login-code\] '+re.escape(contact)+r' -> (\d{6})',log)
    assert codes,'登录验证码未送达服务日志'
    status, _=request(opener,'/api/auth/verify',{'contact':contact,'code':codes[-1], 'invite':invite,'consent':True})
    assert status==200
    assert list(jar) and all(cookie.secure for cookie in jar)
    results['secure_session_cookie']='PASS'
    # 这里只检查服务器本机HTTP链路，模拟TLS终止后的cookie传递；不修改服务配置。
    for cookie in jar:cookie.secure=False
    status, me=request(opener,'/api/me')
    assert status==200 and me['balance']==500
    clients.append(opener)
results['invitation_and_console_login']='PASS'
status, body=request(clients[0],'/api/chat',{'message':'扁平化管理是什么意思'})
assert status==200 and body.get('text') and body.get('session_id')
assert body['credits']['charged']==0
results['mock_chat_no_charge']='PASS'
status,_=request(clients[1],'/api/chat',{'message':'继续','session_id':body['session_id']})
assert status==404
results['cross_account_session_isolation']='PASS'
assert request(clients[0],'/api/auth/logout',{})[0]==200
assert request(clients[0],'/api/chat',{'message':'继续'})[0]==401
results['logout']='PASS'
with sqlite3.connect('/var/lib/xiaogu/staging/xiaogu.db') as conn:
    assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
results['sqlite_integrity']='PASS'
print(json.dumps(results,ensure_ascii=False))
