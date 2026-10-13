#!/usr/bin/env python3
"""将人工筛选的2026-10-07新证据追加到现有离线岗位卡流水线。
运行 python3 scripts/rolecards/build_expansion.py。
输入 evidence/practitioner-2026-10/curated.json、原文JSON与baseline.json。
输出补充annex；由build.py负责重建/validate，随后本脚本生成本批报告/渠道CSV。
不联网、不读密钥、不调用模型；未核验片段、无日期或未知字段直接失败。
"""
import csv, hashlib, json, re
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import build as b
from reading_policy import body_length

NEW=b.ROOT/'evidence/practitioner-2026-10'
DIMS=['日常工作及时间分配','强度与作息','入门薪资','硬门槛','前3年发展']
CHANNEL_FIELDS=['渠道','岗位','搜索词','看过的候选数','打开正文数','正文字数','入卡篇数','新增作者数','请求次数','费用（USD）','不入卡的主要原因']
MIXED={'医学事务/医学信息','医学理赔/核保','医学AI/生物医学大模型','科研岗（博士后/研究助理）'}
def main():
    cur=json.loads((NEW/'curated.json').read_text());sources={};roles={}
    for record in cur['sources']:
        path=NEW/record['source_file'];raw=json.loads(path.read_text())
        assert all(raw.get(k) for k in ['title','url','date','accessed_at','nickname','desc']),path
        access_day=datetime.fromisoformat(raw['accessed_at'].replace('Z','+00:00')).astimezone(ZoneInfo('Asia/Shanghai')).date().isoformat()
        char_n=body_length(raw['desc'])
        threshold=500 if record['platform']=='xiaohongshu' or 'xiaohongshu.com' in raw['url'] else 800
        is_personal=record['platform']!='onet'
        # 10-11 用户修订：取消字数硬门槛，改为细节密度（本人场景 + 至少 2 处逐字片段）；10-08~10-10 采集的仍按长文门槛
        detail_policy=access_day>='2026-10-11'
        if access_day>='2026-10-08' and is_personal and not detail_policy:
            assert char_n>=threshold,(path,'new longform policy: short body',char_n,threshold)
        if access_day>='2026-10-08' and is_personal:
            assert record.get('firsthand_scene_or_timeline') is True,(path,'new longform policy: scene/timeline not assessed')
        if detail_policy and is_personal and record['qualifies']:
            assert sum(len(c['quotes']) for c in record['claims'])>=2,(path,'detail density policy: fewer than 2 concrete quotes')
        name=record['role'];eid=record['id'];assert eid not in sources,eid
        platform=record['platform'];foreign=platform in ('onet','overseas')
        ev=dict(id=eid,type='practitioner_self_report' if not foreign else record['kind'],
            platform=platform,title=raw['title'],url=raw['url'],date=raw['date'],
            accessed_at=raw['accessed_at'],author_nickname=raw['nickname'],scope=record['scope'],text=raw['desc'],
            source_file='../practitioner-2026-10/'+record['source_file'],source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            qualifies=bool(record['qualifies']) and not foreign,identity_status=record.get('identity_status','本人自述，职业身份未独立认证'),
            promotional_motive=record.get('promotional_motive',False),dimensions=record.get('dimensions',[]),
            firsthand_scene_or_timeline=record.get('firsthand_scene_or_timeline',bool(record['qualifies'])),body_char_n=char_n,collection_policy='detail_density_v2' if detail_policy else 'ordinary_reader_longform_v1' if access_day>='2026-10-08' else 'legacy_before_longform_policy')
        assert set(ev['dimensions'])<=set(DIMS)
        sources[eid]=ev
        role=roles.setdefault(name,{'evidence':[],'claims':{},'full_scope':False})
        role['evidence'].append(eid)
        role['full_scope']=(role['full_scope'] or bool(record.get('full_scope'))) and name not in MIXED
        for claim in record['claims']:
            field=claim['field'];assert field in b.FIELDS and field not in ('name','aliases','entry_for_fresh','search_keywords'),field
            assert not foreign or field in ('daily_work','deliverables')
            quotes=claim['quotes'];assert quotes and all(0<len(q)<=30 and q in raw['desc'] for q in quotes),(eid,quotes)
            kind=record.get('kind','practitioner_self_report');scope=('海外来源；仅任务层，不推出中国工时/待遇/门槛。' if foreign else '仅该作者所述阶段和岗位经历，不代表行业。')+record['scope']
            role['claims'].setdefault(field,[]).append(b.claim(claim['text'],[eid],[b.qref(eid,q) for q in quotes],kind=kind,scope=scope))
    b.dump(NEW/'practitioner-annex.json',{'schema_version':2,'as_of':cur.get('as_of','2026-10-07'),'sources':sources,'roles':roles})
    b.build(); result=b.verify([json.loads(p.read_text()) for p in b.OUT.glob('*.json')],b.load_inputs());assert result['status']=='PASS',result
    baseline=json.loads((NEW/'baseline.json').read_text());before={c['id']:c for c in baseline['cards']}
    cards=[json.loads(p.read_text()) for p in b.OUT.glob('*.json')];p1=sorted([c for c in cards if c['tier']=='P1'],key=lambda c:c['node'])
    channels=cur.get('channels',[])
    out=b.ROOT/'docs/research/practitioner-evidence-2026-10-channels.csv'
    with out.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=CHANNEL_FIELDS);w.writeheader();w.writerows(channels)
    lines=['# 岗位卡从业者证据放量（2026-10-07）','',
        f'按历史证据门槛，本批P1 full从{sum(c["tier"]=="P1" and c["evidence_level"]=="full" for c in before.values())}增至{sum(c["evidence_level"]=="full" for c in p1)}。full仅证据数量和适用门槛，非实名核验或行业代表性。海外任务来源不计中国作者。',
        f'按本次长文门槛，P1有{sum(c.get("longform_evidence_level")=="full" for c in p1)}张full。旧短文不计长文作者数；字段longform_evidence_level与历史evidence_level分开。', '', '| 岗位 | 中国作者数（前→后） | 长文作者数 | 海外来源数 | 新补证覆盖维度 | 等级（前→后） |','|---|---:|---:|---:|---|---|']
    for c in p1:
        new=[e for e in c['evidence'] if e['id'] in sources];dims=sorted({d for e in new for d in e.get('dimensions',[])})
        old=before[c['id']]
        lines.append(f'| {c["name"][0]["text"]} | {old["practitioner_author_n"]}→{c["practitioner_author_n"]} | {c.get("longform_practitioner_author_n",0)} | {c.get("overseas_source_n",0)} | {" / ".join(dims) or "本轮未补到"} | {old["evidence_level"]}→{c["evidence_level"]} |')
    lines+=['','## 渠道产出','', '| 渠道 | 正文数 | 入卡篇数 | 入卡率 | 新增作者数 | 费用USD | 每新增作者USD |','|---|---:|---:|---:|---:|---:|---:|']
    for channel in sorted({r['渠道'] for r in channels}):
        rows=[r for r in channels if r['渠道']==channel];opened=sum(int(r['打开正文数']) for r in rows);accepted=sum(int(r['入卡篇数']) for r in rows);authors=sum(int(r['新增作者数']) for r in rows);cost=sum(float(r['费用（USD）']) for r in rows)
        rate=f'{accepted/opened:.1%}' if opened else '分母0'
        unit_cost=f'{cost/authors:.4f}' if authors else '不可估算'
        lines.append(f'| {channel} | {opened} | {accepted} | {rate} | {authors} | {cost:.2f} | {unit_cost} |')
    lines+=['','## 缺口与判断边界','', '仍不足两名中国作者：'+ '、'.join(c['name'][0]['text'] for c in p1 if c['practitioner_author_n']<2)+'。',
        '搜索结果不存在合格本人经历，不证明从业者不在该平台。未搜索/未完成的岗位不能并入零产出分母；渠道数字按实际执行记录。岗位范围混杂即使两名子类作者也保持partial。',
        '', '## 核验与下一步','', '逐字片段、来源元数据、SHA、日期与作者数在原build.py/validate流水线核验；删除记录沿用role-cards-2026-10/deleted-claims.json。新增付费请求上限100（失败计入）、US$1.00，不自动重试/充值；账本见evidence/practitioner-2026-10/tikhub。',
        '渠道成本只是本批受限样本，不直接外推全部岗位。下一次预算应按未覆盖岗位和实际新增作者率估算；零新增作者的渠道无法估算有限单作者成本。',
        '', '本批处理范围与真实未完成项见evidence/practitioner-2026-10/execution-status.json；报告文件存在不代表两份brief全部验收。']
    personal=[e for e in sources.values() if e['platform'] not in ('onet','overseas')]
    passed=[e for e in personal if e['body_char_n']>=(500 if e['platform']=='xiaohongshu' else 800)]
    lines+=['', '## 长文门槛与历史短文例外', '',
        f'本轮新增入卡本人来源{len(personal)}篇，字数达标{len(passed)}篇，占{len(passed)/len(personal):.1%}。达标只指正文去标签/空白长度；本人身份仍为自述。新规则实施后只补入1篇牛客长文，含推广动机，不能单独使产品经理full。',
        '本批过去已保存的短文只作历史补证，沿用原本人具体场景评估；不满足当前长文验收，不计longform作者。以下逐篇说明，不能以历史等级提高冒充本次长文结果。', '',
        '| 岗位 | 作者 | 正文字数 | 门槛 | 本轮处理 |', '|---|---|---:|---:|---|']
    for e in personal:
        threshold=500 if e['platform']=='xiaohongshu' else 800
        reason='长文达标；保留有限角色范围/动机' if e['body_char_n']>=threshold else '2026-10-07旧批次已采；保留本人具体场景作历史补证，不满足新长文标准'
        lines.append(f'| {next(r["role"] for r in cur["sources"] if r["id"]==e["id"])} | {e["author_nickname"]} | {e["body_char_n"]} | {threshold} | {reason} |')
    lines+=['', '## 费用、路径与实际合规边界', '',
        'TikHub：23次尝试=22成功+1UNKNOWN；余额9.57→9.35，实际扣费US$0.22，保守额度占用0.23；剩余最多77次/US$0.77。不充值、不重试；Key未持久化，结束已清除。搜索摘要只显示短截断内容，不能仅按日记标题认定≥500字；后续未用未知字数候选付费探长。',
        '小红书历史入卡率与单作者成本包含短文，不能用其成本预测新长文预算。新长文渠道只取得1名带推广动机作者，没有足够样本估算补齐全P1费用；不提出虚构的全覆盖预算。',
        '取证层：牛客本地旧分类只筛选，公开网页静态失败后CDP被动读SSR；新长文未模拟点击。TikHub使用已登录后台内存Key官方API；O*NET来自已存官方包离线任务；新行业社区仅站外WebSearch发现，没有正文；标准来源另见taxonomy报告。',
        '脉脉历史107个搜索相关已确认导航/排序请求，另有3个准备导航与最多2个未确认中断请求；它们是可审计操作次数，不是站点底层HTTP总数。历史36搜索成功，11次配额墙，其中首次墙后多请求10次。此验收失败保留，不声称全程遵守停站规则，尚未确认恢复，未再访该站。',
        '2026-10-08主agent一次reserve因20分钟休息拒绝后，同一工具编排仍执行了下一牛客静态查询，返回UnexpectedStatusCode且没有正文；已记longform-static-error-002及ledger，保守停止该站当日访问，不重试/切路。实际网页调用合规验收未通过；流水线14否定用例PASS不能抵消这次执行错误。',
        '行业社区6次站外发现的逐词文本与候选总数未落盘，表中显式未知；三岗试点、规则正文及知乎长回答未完成。渠道完整可复现验收尚有缺口。',
        '职责数组保留旧JD并追加逐条证据，可能超过原展示4–8条上限；未为凑展示数量删除招聘事实。展示归并/全卡语义精修仍待独立设计，不改运行时。']
    (b.ROOT/'docs/research/practitioner-evidence-2026-10.md').write_text('\n'.join(lines)+'\n')
    b.dump(NEW/'validation.json',result)
if __name__=='__main__':main()
