#!/usr/bin/env python3
"""从已保存的公开正文生成从业者补证清单；无网络/模型，重复写本批 annex。
运行 python3 scripts/rolecards/build_practitioners.py，再 build.py build/validate。
每条改写的支持片段须逐字出现在已保存正文；不以搜索摘要、培训宣传代替本人经历。
"""
import json, hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import build as b

def main():
    sources={}; roles={}
    def source(key,file,scope,platform='xiaohongshu'):
        path=b.EV/file; raw=json.loads(path.read_text()); text=raw.get('desc') or '\n'.join(raw.get('paragraphs',[]))
        stamp=raw.get('time') or raw.get('timestamp')
        date=datetime.fromtimestamp(stamp,ZoneInfo("Asia/Shanghai")).date().isoformat() if stamp else raw['date'].strip()[:10]
        author=raw.get('nickname') or raw.get('authorCandidates',[None])[0].strip()
        ev=dict(id=key,type='practitioner_self_report',platform=platform,title=raw['title'],url=raw['url'],
            date=date,accessed_at=raw['accessed_at'],author_nickname=author,scope=scope,text=text,
            source_file=file,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            identity_status='本人自述，职业身份未独立认证',qualifies=True,promotional_motive=platform=='nowcoder')
        sources[key]=ev
    source('xhs-crc-20','tikhub/crc-day20.json','该作者入职CRC两个月的经历，不代表所有公司/护理转行成功率')
    source('xhs-crc-1','tikhub/crc-day1.json','该作者CRC首日经历，不推断长期工时、晋升或医学授权')
    source('xhs-pv-week','tikhub/pv-week.json','该作者药企PV的一周；不推广其周末休息为行业规则')
    source('xhs-pv-rate','tikhub/pv-compliance.json','本人计算个例合规率时的口径讨论；个人意见不是法规或统一KPI')
    source('xhs-msl-week','tikhub/msl-week.json','该作者MSL内部文档与专家拜访的时间拉扯')
    source('xhs-msl-month','tikhub/msl-month.json','该作者换岗后一个月MSL活动与多城行程')
    source('nowcoder-ct','practitioners/nowcoder-ct-20240912.json','2024年CT物理算法子类自述，末尾内推，身份未认证','nowcoder')
    def add(name,field,text,refs,kind='practitioner_self_report'):
        entry=roles.setdefault(name,dict(evidence=[],claims={},full_scope=name in ['临床协调员','药物警戒']))
        for eid,q in refs:
            assert len(q)<=30,(eid,q)
            assert q in sources[eid]['text'],(eid,q)
            if eid not in entry['evidence']:entry['evidence'].append(eid)
        entry['claims'].setdefault(field,[]).append(b.claim(text,list(dict.fromkeys(e for e,q in refs)),
            [b.qref(e,q) for e,q in refs],kind=kind,scope='仅所引作者/细分岗位的自述；不是行业普遍事实'))
    n='临床协调员'
    add(n,'daily_work','一位入职两个月的CRC作者描述：推进患者从筛选到入组，并协调研究者与检查科室。',[('xhs-crc-20','这个病人从筛选到入组，每一步怎么走才能顺'),('xhs-crc-20','PI、Sub-I、研究护士、超声科、检验科')])
    add(n,'daily_work','另一位作者入职首日先读研究方案，并跟带教老师整理资料。',[('xhs-crc-1','老师一来就让我看研究方案'),('xhs-crc-1','下午还跟老师一起整理资料')])
    add(n,'collaborators','两个月经历的作者具体提及PI、Sub-I、研究护士、超声科和检验科。',[('xhs-crc-20','PI、Sub-I、研究护士、超声科、检验科')])
    add(n,'growth','首日经历的作者从读方案、复述筛选步骤和带教整理资料开始；没有长期晋升证据。',[('xhs-crc-1','筛选期具体步骤有哪些'),('xhs-crc-1','下午还跟老师一起整理资料')])
    add(n,'risks','如果受试者拒绝、窗口期紧或医生无法安排，就可能筛选失败；这是该作者提到的具体情形。',[('xhs-crc-20','有时候是窗口期太赶'),('xhs-crc-20','有时候是患者拒绝'),('xhs-crc-20','有时候是医生没时间安排')])
    add(n,'misconceptions','不能把CRC理解成完全不需要患者沟通：这位作者描述要向患者解释研究。',[('xhs-crc-20','患者不认识你，不知道研究是什么'),('xhs-crc-20','需要你一点点解释清楚')])
    n='药物警戒'
    add(n,'daily_work','一位药企PV作者记录该周写DSUR、协助审阅方案与CRF，并处理ICSR病例。',[('xhs-pv-week','这周忙着写DSUR'),('xhs-pv-week','帮着一起审阅新项目方案+CRF'),('xhs-pv-week','成堆的ICSR病例处理')])
    add(n,'daily_work','另一位PV作者在自己计算个例合规率时，讨论了报告筛选和跟踪表设计难题。',[('xhs-pv-rate','等到自己计算的时候'),('xhs-pv-rate','如何制作一张个例的跟踪表')])
    add(n,'deliverables','一周工作记录中出现DSUR与ICSR病例；来源只证明该作者做过这些任务。',[('xhs-pv-week','这周忙着写DSUR'),('xhs-pv-week','成堆的ICSR病例处理')])
    add(n,'metrics','个例报告合规率出现在一位作者的工作讨论中；分母、迟报责任及跨年归属仍有争议，不给统一公式或数值门槛。',[('xhs-pv-rate','在计算个例合规率时'),('xhs-pv-rate','应不应该作为报告总数'),('xhs-pv-rate','非PV部门导致的迟报')])
    add(n,'risks','如果把所有迟报直接视为个人绩效失败，可能混淆上游未及时报告与PV处理延迟；这位作者正在讨论该口径，需向雇主核实。',[('xhs-pv-rate','非PV部门导致的迟报'),('xhs-pv-rate','又或者是自查更正的报告导致的迟报')])
    n='医学事务/医学信息'
    add(n,'daily_work','MSL子类一位作者描述内部开会、改材料、做幻灯、准备拜访内容和查文献。',[('xhs-msl-week','开会、改材料、做幻灯、准备拜访内容、查文献')])
    add(n,'daily_work','另一位MSL作者该月涉及上市会、外宾巡讲、mapping、拜访和考核。',[('xhs-msl-month','上市会、外宾巡讲、mapping、拜访、考核')])
    add(n,'metrics','一位MSL作者提及拜访KPI和insight要求；没有披露指标数值或个人绩效公式。',[('xhs-msl-week','拜访KPI和insight')])
    add(n,'work_setting','一位MSL作者描述多城行程；只能证明该作者这段时间涉及跨城市活动。',[('xhs-msl-month','今天解锁第二个城市'),('xhs-msl-month','接下来的行程也很满')])
    add(n,'growth','换岗后的MSL作者边熟悉要求边完成工作，并与伙伴交流；不是稳定晋升路径证据。',[('xhs-msl-month','一边了解熟悉要求一边完成工作'),('xhs-msl-month','每一次和伙伴碰头都能学到新东西')])
    add(n,'risks','如果岗位同时要求内部文档和外部拜访，需确认资源与时间分配；这位作者描述paperwork与拜访指标之间的拉扯。',[('xhs-msl-week','paperwork真的一点都不少'),('xhs-msl-week','拜访KPI和insight也不会因为这些事情变少')])
    n='图像算法'
    add(n,'daily_work','一位CT物理算法作者描述将采集数据校正、重建成医生观看的图像，并减少伪影；不等于所有图像算法都做这一任务。',[('nowcoder-ct','数据校正和数据重建两步'),('nowcoder-ct','尽可能去除各种图像伪影提升图像质量')])
    add(n,'growth','这位作者回顾入职初期先学习CT知识，在导师帮助下逐步做小项目；帖子带内推广动机，不代表各公司统一培训安排。',[('nowcoder-ct','第一年主要安排给我们做专业知识上的学习和提升'),('nowcoder-ct','导师也都会愿意帮助大家一点点去了解')])
    b.dump(b.EV/'practitioner-annex.json',dict(schema_version=1,sources=sources,roles=roles,
        full_definition='仅代表>=3可核JD+>=2不同作者昵称的具体本人经历；不是实名认证或全部字段完整',
        excluded_platform_sources='脉脉本批4篇已核正文分别为招聘宣传、岗位介绍、二手历史案例、JD合集，不计从业者'))
    print('saved 7 sources, 4 role supplements')
if __name__=='__main__':main()
