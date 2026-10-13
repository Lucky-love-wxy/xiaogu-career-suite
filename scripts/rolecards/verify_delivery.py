#!/usr/bin/env python3
"""核验交付：原缓存文本绑定、四种篡改拒绝、纯证据隔离重建。

运行 python3 scripts/rolecards/verify_delivery.py；仅需Python标准库。
不联网、不调用模型；重复执行覆盖本批验收证据，不改卡片或运行时。
原HTML缓存若被移走，正文绑定步骤失败；build的证据离线重建仍可单独运行。
"""
import copy, hashlib, html, json, re, shutil, tempfile
from html.parser import HTMLParser
import build as b

class PageText(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]
    def handle_data(self,data): self.parts.append(data)
def norm(text): return re.sub(r'\s+','',html.unescape(text))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    cards=[json.loads(p.read_text()) for p in b.OUT.glob('*.json')]; inputs=b.load_inputs()
    baseline=b.verify(cards,inputs); assert baseline['status']=='PASS',baseline
    texts={}; checked=0; errors=[]
    for c in cards:
        for e in c['evidence']:
            if e['type']!='recruitment_jd': continue
            path=b.ROOT/e['cache_path'] if e['cache_path'] else None
            assert path and path.exists(),('缺原HTML缓存',e['id'])
            assert digest(path)==e['cache_sha256'],('缓存SHA变化',e['id'])
            if e['id'] not in texts:
                parser=PageText();parser.feed(path.read_text());texts[e['id']]=norm('\n'.join(parser.parts))
        for field in ['plain_language','daily_work','deliverables','collaborators','work_setting']:
            for claim in c[field]:
                for q in claim['quotes']:
                    if q['evidence_id'] not in texts:continue
                    checked+=1
                    if norm(q['text']) not in texts[q['evidence_id']]:errors.append(dict(card=c['id'],field=field,quote=q))
    b.dump(b.EV/'html-binding-check.json',dict(checked_n=checked,normalization='HTML实体解码、去空白；非原HTML字节逐字匹配',mismatch_n=len(errors),mismatches=errors))
    assert not errors,errors
    original=next(c for c in cards if c['name'][0]['text']=='临床协调员'); negatives=[]
    for label,change in [('正文和引用同时篡改',lambda x:(x['evidence'][1].update(text='伪造'),x['daily_work'][0]['quotes'][0].update(text='伪造'))),
                         ('数字文本篡改',lambda x:x['entry_for_fresh'][0].update(text='10000份都接受无经验')),
                         ('证据URL篡改',lambda x:x['evidence'][1].update(url='https://example.invalid/')),
                         ('伪造作者数/等级',lambda x:x.update(evidence_level='full',practitioner_author_n=99))]:
        test=copy.deepcopy(original); change(test); result=b.verify([test],inputs)
        assert result['errors'],label
        negatives.append(dict(case=label,result='REJECTED',errors=result['errors'][:2]))
    b.dump(b.EV/'negative-validation.json',negatives)
    real_ev,real_out,real_report=b.EV,b.OUT,b.REPORT
    names=['inputs.json','curation.json','quality-decisions.json','practitioner-annex.json']+[e['source_file'] for e in inputs['practitioners']['sources'].values()]
    if (real_ev/'../practitioner-2026-10/practitioner-annex.json').exists():names.append('../practitioner-2026-10/practitioner-annex.json')
    names=list(dict.fromkeys(names))
    expected={p.name:digest(p) for p in real_out.glob('*.json')}; expected['report']=digest(real_report)
    with tempfile.TemporaryDirectory(prefix='rolecards-offline-') as td:
        base=b.Path(td);b.EV=base/'evidence';b.OUT=base/'cards';b.REPORT=base/'report.md';b.EV.mkdir()
        for name in names:
            target=b.EV/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(real_ev/name,target)
        for _ in range(2):
            b.build(); actual={p.name:digest(p) for p in b.OUT.glob('*.json')};actual['report']=digest(b.REPORT)
            assert actual==expected,'隔离重建哈希不匹配'
        b.dump(real_ev/'reproduction.json',dict(status='PASS',output_n=len(expected),isolated_from_raw_database=True,
            input_files={n:digest(real_ev/n) for n in names},first_equals_final=True,second_equals_first=True,
            network_calls=0,model_calls=0,hashes=expected))
    b.EV,b.OUT,b.REPORT=real_ev,real_out,real_report
    print(f'PASS: {checked}缓存片段，4种篡改拒绝，{len(expected)}文件两次隔离重建一致')
if __name__=='__main__':main()
