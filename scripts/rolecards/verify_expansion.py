#!/usr/bin/env python3
"""验证增量作者资格、海外字段边界，以及JD字段未被从业者补证覆盖。
运行 python3 scripts/rolecards/verify_expansion.py；无网络、模型或第三方依赖。
"""
import copy,json
import build as b

def main():
    inputs=b.load_inputs();cards=[json.loads(p.read_text()) for p in b.OUT.glob('*.json')]
    result=b.verify(cards,inputs);assert result['status']=='PASS',result
    jd=b.assemble(inputs);b.apply_curation(jd);base={c['id']:c for c in jd}
    for c in cards:
        expected=base[c['id']]
        for field in b.FIELDS:
            retained=[x for x in c[field] if x['kind'] not in ('practitioner_self_report','onet_incumbent_rated','overseas_practitioner')]
            assert retained==expected[field],(c['id'],field,'JD change')
        assert [e for e in c['evidence'] if e['type'] in ('queue_metadata','recruitment_jd')]==expected['evidence'],(c['id'],'JD evidence change')
    crc=next(c for c in cards if c['node'].endswith(' › 临床协调员'))
    tests=[]
    for label,mutate in [('所有作者导流不能full',lambda e:e.update(promotional_motive=True)),
                         ('过期作者不能full',lambda e:e.update(date='2020-01-01')),
                         ('海外不计中国作者',lambda e:e.update(platform='overseas'))]:
        fake=copy.deepcopy(crc);finputs=copy.deepcopy(inputs)
        for e in fake['evidence']:
            if e['id'] in finputs['practitioners']['sources']:
                mutate(e);finputs['practitioners']['sources'][e['id']]=copy.deepcopy(e)
        fake.update(evidence_level='full',practitioner_author_n=2)
        reject=b.verify([fake],finputs);assert reject['errors'],label
        tests.append({'case':label,'result':'REJECTED'})
    fake=copy.deepcopy(crc);finputs=copy.deepcopy(inputs)
    e=next(e for e in fake['evidence'] if e['type']=='practitioner_self_report');e.update(platform='overseas');finputs['practitioners']['sources'][e['id']]=copy.deepcopy(e)
    q=e['text'][:20];fake['metrics'].append(b.claim('伪造海外支撑中国考核',[e['id']],[b.qref(e['id'],q)],kind='overseas_practitioner',scope='海外来源'))
    reject=b.verify([fake],finputs);assert any('overseas boundary' in str(x) for x in reject['errors'])
    tests.append({'case':'海外任务证据不得支撑中国指标','result':'REJECTED'})
    b.dump(b.ROOT/'evidence/practitioner-2026-10/contract-validation.json',{'status':'PASS','jd_fields_unchanged':True,'negative_cases':tests,'cards':len(cards)})
    print('PASS: 170卡JD字段未变；导流/过期/海外作者及字段限制4负例拒绝')
if __name__=='__main__':main()
