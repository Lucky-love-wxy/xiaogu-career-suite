#!/usr/bin/env python3
"""Offline acceptance: cards, source excerpts, hashes, revenue arithmetic and
collection safety guards. Run python3 scripts/companycheck/validate.py.
No network/keychain calls. Guard tests use mock responses and temporary files.
"""
import copy, hashlib, importlib.util, json, pathlib, re, tempfile, unittest
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parents[2]
E=ROOT/'evidence/company-check-2026-10'
IDS=('zhihu','kanzhun','mihoyo','bytedance','baichuan','humanoid')
spec=importlib.util.spec_from_file_location('company_collector',ROOT/'scripts/companycheck/collect.py')
collector=importlib.util.module_from_spec(spec);spec.loader.exec_module(collector)
buildspec=importlib.util.spec_from_file_location('company_builder',ROOT/'scripts/companycheck/build.py')
builder=importlib.util.module_from_spec(buildspec);buildspec.loader.exec_module(builder)

class Response:
    status=200; url='https://www.qcc.com/firm/test'
    headers={'Content-Type':'text/html'}
    def __init__(self,raw):self.raw=raw
    def read(self):return self.raw
    def __enter__(self):return self
    def __exit__(self,*args):return False

class Guards(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'tasks/company-check-20261012')
        self.old=(collector.OUT,collector.LEDGER,collector.state)
        collector.OUT=pathlib.Path(self.temp.name);collector.LEDGER=collector.OUT/'ledger.json'
        collector.state={'api_calls':0,'search_calls':0,'last_request':{},'stopped':{}}
    def tearDown(self):
        collector.OUT,collector.LEDGER,collector.state=self.old;self.temp.cleanup()
    def test_real_200_challenge_stops_other_subdomain(self):
        raw=(E/'kanzhun-qcc-direct.html').read_bytes()
        opener=unittest.mock.Mock();opener.open.return_value=Response(raw)
        with patch.object(collector.urllib.request,'build_opener',return_value=opener),patch.object(collector.time,'sleep'):
            _,m=collector.request('https://www.qcc.com/firm/test')
            self.assertIsNotNone(m['blocked'])
            with self.assertRaises(RuntimeError):collector.request('https://m.qcc.com/firm/second')
        self.assertEqual(opener.open.call_count,1)
    def test_60_call_cap_prevents_network(self):
        collector.state['api_calls']=60
        with patch.object(collector.urllib.request,'build_opener') as opener:
            with self.assertRaises(RuntimeError):collector.request('https://api.tavily.com/search',b'{}')
            opener.assert_not_called()
        self.assertEqual(collector.state['api_calls'],60)
    def test_roots_share_minimum_interval(self):
        collector.state['last_request']['qcc.com']=100
        opener=unittest.mock.Mock();opener.open.return_value=Response(b'<html>public text</html>')
        with patch.object(collector.urllib.request,'build_opener',return_value=opener),patch.object(collector.time,'time',return_value=101),patch.object(collector.time,'sleep') as sleep:
            collector.request('https://m.qcc.com/public')
        self.assertGreaterEqual(sleep.call_args.args[0],2.09)
    def test_all_pilot_subdomains_share_site_key(self):
        for domain in ('mihoyo.com','baichuan-ai.com','volcengine.com','feishu.cn','bjnews.com.cn'):
            self.assertEqual(collector.site_key('www.'+domain),collector.site_key('platform.'+domain))
        self.assertNotEqual(collector.site_key('www.a.gov.cn'),collector.site_key('www.b.gov.cn'))
    def test_real_login_shell_blocks_site(self):
        raw=(E/'zhihu-tianyancha-direct.html').read_bytes()
        opener=unittest.mock.Mock();opener.open.return_value=Response(raw)
        with patch.object(collector.urllib.request,'build_opener',return_value=opener),patch.object(collector.time,'sleep'):
            _,m=collector.request('https://www.tianyancha.com/company/first')
            self.assertEqual(m['blocked']['reason'],'login_required_generic_shell')
            with self.assertRaises(RuntimeError):collector.request('https://m.tianyancha.com/company/second')
        self.assertEqual(opener.open.call_count,1)
    def test_batch_exits_after_saving_trigger(self):
        plan=collector.OUT/'plan.json'
        plan.write_text(json.dumps([{'id':'first','url':'https://www.qcc.com/first'},{'id':'second','url':'https://www.qcc.com/second'}]))
        m={'status':200,'elapsed_seconds':0.1,'blocked':{'reason':'risk'}}
        with patch('sys.argv',['collect.py','fetch',str(plan)]),patch.object(collector,'robots_allowed',return_value=(True,'checked')),patch.object(collector,'request',return_value=(b'challenge',m)) as req:
            with self.assertRaises(SystemExit) as stopped:collector.main()
        self.assertEqual(stopped.exception.code,2)
        self.assertEqual(req.call_count,1)
        self.assertTrue((collector.OUT/'first.html').exists())
        self.assertFalse((collector.OUT/'second.meta.json').exists())
    def test_robots_disallow_prevents_target(self):
        (collector.OUT/'robots-example-com.txt').write_text('User-agent: *\nDisallow: /private\n')
        (collector.OUT/'robots-example-com.meta.json').write_text(json.dumps({'status':200}))
        with patch.object(collector,'request',side_effect=AssertionError('must not request target')):
            allowed,_=collector.robots_allowed('https://example.com/private/company')
        self.assertFalse(allowed)
    def test_unknown_robots_fail_closed(self):
        (collector.OUT/'robots-example-com.meta.json').write_text(json.dumps({'status':521,'blocked':{'reason':'HTTP521'}}))
        self.assertFalse(collector.robots_allowed('https://example.com/')[0])
    def test_redirect_not_followed(self):
        self.assertIsNone(collector.NoRedirect().redirect_request(None,None,302,'',{},'https://other.test/'))

def check_artifacts():
    errors=[];source_n=0;fact_n=0
    for cid in IDS:
        card=json.loads((ROOT/'data/companies'/f'{cid}.json').read_text())
        for k in ('legal_name','brand_names','listing','main_business','revenue_mix','products_customers','recent_events','source_levels','as_of'):
            if k not in card:errors.append(f'{cid}: missing {k}')
        if card['as_of']!='2026-10-12':errors.append(f'{cid}: invalid as_of')
        for sid,s in card['sources'].items():
            source_n+=1;p=ROOT/s['snapshot']
            if hashlib.sha256(p.read_bytes()).hexdigest()!=s['sha256']:errors.append(f'{cid}/{sid}: snapshot hash mismatch')
            if not(0<len(s['excerpt'])<=30):errors.append(f'{cid}/{sid}: excerpt length')
            text=builder.body(s['snapshot'])
            if re.sub(r'\s+','',s['excerpt']) not in re.sub(r'\s+','',text):errors.append(f'{cid}/{sid}: excerpt missing')
        def walk(x):
            nonlocal fact_n
            if isinstance(x,dict):
                if 'source_ids' in x:
                    fact_n+=1
                    if x.get('status') not in ('not_found',) and not x['source_ids']:errors.append(f'{cid}: unsourced field')
                    if x.get('status')=='not_found' and (x['value']!='未找到' or not x.get('note')):errors.append(f'{cid}: unexplained missing field')
                    for sid in x['source_ids']:
                        if sid not in card['sources']:errors.append(f'{cid}: invalid source reference {sid}')
                for v in x.values():walk(v)
            elif isinstance(x,list):
                for v in x:walk(v)
        walk(card)
        if isinstance(card['revenue_mix'],list):
            for r in card['revenue_mix']:
                d=r['value']
                if sum(p['amount'] for p in d['parts'])!=d['total']:errors.append(f'{cid}: revenue parts mismatch')
                for p in d['parts']:
                    if abs(round(p['amount']/d['total']*100,2)-p['percent'])>.0001:errors.append(f'{cid}: percent mismatch')
        for event in card['recent_events']:
            d=event.get('event_date')
            if d and not '2025-10-12'<=d<='2026-10-12':errors.append(f'{cid}: event outside window')
    manifests=json.loads((E/'manifest.json').read_text())
    for m in manifests:
        if hashlib.sha256((ROOT/m['path']).read_bytes()).hexdigest()!=m['sha256']:errors.append('manifest mismatch: '+m['path'])
    # Detect common credential formats without ever returning matching content.
    paths=[ROOT/'docs/research/company-check-pilot-2026-10.md']+list((ROOT/'scripts/companycheck').glob('*'))+list((ROOT/'data/companies').glob('*.json'))
    for p in paths:
        if p.is_file() and re.search(r'tvly-[A-Za-z0-9_-]{15,}|sk-[A-Za-z0-9_-]{20,}',p.read_text(errors='replace')):errors.append('possible secret pattern: '+str(p.relative_to(ROOT)))
    ledger=json.loads((E/'ledger.json').read_text())
    if ledger['api_calls']>60:errors.append('API cap exceeded')
    if len(json.loads((E/'channels.json').read_text()))!=42:errors.append('company-channel row count')
    print(json.dumps({'cards':6,'source_references':source_n,'facts':fact_n,'manifest_files':len(manifests),'api_calls':ledger['api_calls'],'errors':errors},ensure_ascii=False))
    return errors

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Guards))
    errors=check_artifacts()
    summary={'status':'PASS' if result.wasSuccessful() and not errors else 'NEEDS_CHANGES','guard_tests':result.testsRun,'guard_failures':len(result.failures)+len(result.errors),'artifact_errors':errors,'scope':'local artifact/guards verification; not full live-network protocol acceptance'}
    (E/'validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    raise SystemExit(0 if summary['status']=='PASS' else 1)
