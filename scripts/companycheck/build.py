#!/usr/bin/env python3
"""Build six evidence-bound company cards and channel measurements.

Run: python3 scripts/companycheck/build.py
Requires system pdftotext for source PDF text; otherwise stdlib only.
Input: fixed pilot evidence directory. Output: six JSON cards, sources.json,
channels.json/csv and SHA256 manifest. Does not access network or runtime code.
Curated claims below are editorial input; unsupported claims fail validation.
"""
import csv, hashlib, json, pathlib, re, subprocess
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[2]
E = ROOT / 'evidence/company-check-2026-10'
OUT = ROOT / 'data/companies'
DATE = '2026-10-12'
L1, L2, L4, L5 = '交易所/监管披露', '公司官网', '主流财经媒体原创报道', '百科'
SOURCES = {}

def write(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n')

class Text(HTMLParser):
    def __init__(self): super().__init__(); self.skip=0; self.parts=[]
    def handle_starttag(self,t,a):
        if t in ('script','style'): self.skip+=1
        if t=='meta':
            attrs=dict(a)
            if attrs.get('name') in ('description','title') and attrs.get('content'):
                self.parts.append(attrs['content'])
    def handle_endtag(self,t):
        if t in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self,d):
        if not self.skip and d.strip(): self.parts.append(d.strip())

def body(snapshot):
    p=ROOT/snapshot
    if p.suffix=='.pdf':
        subprocess.run(['pdftotext','-layout',str(p),str(p.with_suffix('.txt'))],check=True,capture_output=True)
        return p.with_suffix('.txt').read_text()
    if p.suffix=='.html':
        t=Text();t.feed(p.read_text(errors='replace'))
        p.with_suffix('.txt').write_text('\n'.join(t.parts))
        return '\n'.join(t.parts)
    if p.suffix=='.json': return json.loads(p.read_text())['text']
    return p.read_text()

def source(sid, evidence, level, title, quote, locator='', published=None):
    m=json.loads((E/(evidence+'.meta.json')).read_text())
    assert m.get('status')==200 and not m.get('blocked'), evidence
    assert 0<len(quote)<=30, (sid,quote)
    snapshot=m['snapshot']
    text=body(snapshot)
    assert re.sub(r'\s+','',quote) in re.sub(r'\s+','',text), (sid,'quote not in body',quote)
    SOURCES[sid]={'title':title,'url':m['url'],'level':level,'access_date':DATE,
                  'published_date':published,'excerpt':quote,'locator':locator,
                  'snapshot':snapshot,'sha256':hashlib.sha256((ROOT/snapshot).read_bytes()).hexdigest(),
                  'retrieval_layer':m.get('layer','script:urllib'),'evidence_id':evidence}
    return sid

def f(value,*ids,status='verified',note=None):
    obj={'value':value,'status':status,'source_ids':list(ids)}
    if note: obj['note']=note
    return obj

def missing(reason): return f('未找到',status='not_found',note=reason)

def build_sources():
    rows=[
      ('z-id','zhihu-direct-4',L1,'知乎2025年报','Zhihu Inc.','封面/公司信息'),
      ('z-official','zhihu-ir',L2,'知乎IR公司介绍','在线内容问答社区','公司介绍；财务以披露文件为准'),
      ('z-list','zhihu-direct-4',L1,'知乎2025年报','NYSE: ZH','印刷第4页及封面'),
      ('z-business','zhihu-direct-4',L1,'知乎2025年报','Marketing services','印刷第15页、115-118页'),
      ('z-member','zhihu-direct-4',L1,'知乎2025年报','membership fee','印刷第115页'),
      ('z-marketing','zhihu-direct-4',L1,'知乎2025年报','advertising contracts','印刷第116页'),
      ('z-revenue','zhihu-direct-4',L1,'知乎2025年报','1,538,942','印刷第15页，金额千元人民币'),
      ('z-new','zhihu-direct-2',L1,'知乎2026Q2及半年结果','Paid content and IP operations','PDF第8页及脚注，2026-08-26'),
      ('z-refine','zhihu-direct-2',L1,'知乎2026Q2及半年结果','strategic refinement','PDF第4页，职业培训业务调整'),
      ('k-id','kanzhun-direct-0',L1,'看准2025年度业绩公告','KANZHUN LIMITED','PDF第1页'),
      ('k-list','kanzhun-direct-0',L1,'看准2025年度业绩公告','Nasdaq Stock Ticker: BZ','PDF第1页，港股2076'),
      ('k-business','kanzhun-direct-0',L1,'看准2025年度业绩公告','paid enterprise customers','PDF第9页'),
      ('k-product','kanzhun-direct-0',L1,'看准2025年度业绩公告','direct recruitment model','PDF第4-5页'),
      ('k-revenue','kanzhun-direct-0',L1,'看准2025年度业绩公告','8,192,714','PDF第8页，金额千元人民币'),
      ('k-optimize','kanzhun-direct-0',L1,'看准2025年度业绩公告','optimization','PDF第9页，求职者增值工具优化'),
      ('m-id','mihoyo-supp-direct-2',L4,'新京报：米哈游回应股权托管登记','上海米哈游网络科技股份有限公司','记者韦英姿，2026-09-24'),
      ('m-unlisted','mihoyo-supp-direct-3',L4,'财联社：米哈游回应股权托管登记','公司目前没有上市融资计划','2026-09-23回应'),
      ('m-business','mihoyo-cdp',L2,'米哈游官网','并围绕原创IP打造了动画、音乐及周边等多元产品','关于米哈游'),
      ('m-products','mihoyo-cdp',L2,'米哈游官网','《原神》、《崩坏：星穹铁道》、《绝区零》','关于米哈游'),
      ('m-pay','mihoyo-supp-direct-1',L2,'米哈游游戏使用许可及服务协议','购买相关虚拟物品使用权','四：资费政策；2023版协议'),
      ('m-operator','mihoyo-supp-direct-1',L2,'米哈游游戏使用许可及服务协议','上海米哈游影铁科技有限公司','重要须知'),
      ('b-id','bytedance-supp-direct-6',L5,'ByteDance百科','ByteDance Ltd.','信息框'),
      ('b-unlisted','bytedance-supp-direct-6',L5,'ByteDance百科','Private','信息框，非证券监管负面证明'),
      ('b-products','bytedance-direct-2',L2,'ByteDance产品页','Douyin','官网产品目录'),
      ('b-lark','bytedance-direct-2',L2,'ByteDance产品页','Lark','官网产品目录'),
      ('b-jv','bytedance-supp-direct-0',L2,'TikTok美国合资公司成立公告','ByteDance retains 19.9%','2026-01-23'),
      ('a-id','baichuan-cdp',L2,'百川智能官网','百川智能科技有限公司','当前页脚'),
      ('a-old-id','baichuan-direct-2',L2,'百川平台医疗文档','北京百川智能科技有限公司','文档页脚，和主站名称不一致'),
      ('a-founded','baichuan-cdp',L2,'百川智能官网','百川智能成立于2023年3月24日','关于我们'),
      ('a-product','baichuan-cdp',L2,'百川智能官网','百小医 你的 AI家庭医生','首页'),
      ('a-free','baichuan-cdp',L2,'百川智能官网','永久免费调用 Baichuan-M3 Plus API','海纳百川计划，需准入审核'),
      ('a-funding','baichuan-funding-direct',L4,'第一财经：百川智能完成50亿元A轮融资','总融资金额达50亿元人民币','记者刘晓洁，2024-07-25'),
      ('a-plan','baichuan-final-direct-4',L4,'蓝鲸：王小川谈百川上市计划','2027','2026-01-14采访报道，意向并非完成上市'),
      ('h-id','humanoid-final-direct-3',L2,'北京人形公司介绍','北京人形机器人创新中心有限公司','官网公司简介'),
      ('h-founded','humanoid-final-direct-3',L2,'北京人形公司介绍','2023年11月','官网公司简介'),
      ('h-business','humanoid-final-direct-3',L2,'北京人形公司介绍','聚焦于具身智能机器人核心技术','官网公司简介'),
      ('h-products','humanoid-direct-0',L2,'北京人形渠道招募公告','天轶 2.0','2026-09-10；天工3.0/Omni、天轶2.0'),
      ('h-customers','humanoid-direct-0',L2,'北京人形渠道招募公告','系统集成商 / 自动化工程商','招募对象与应用场景，非已成交清单'),
      ('h-funding','humanoid-funding-direct',L2,'北京人形首轮融资公告','亿元市场化融资','2026-02-03；金额超7亿元'),
      ('h-funding-media','humanoid-supp-direct-5',L4,'财新：北京人形首轮融资','首轮超7亿元融资','2026-02-03正文'),
    ]
    for row in rows: source(*row)
    # Publication dates where material to the 12-month window.
    for sid,d in [('z-new','2026-08-26'),('z-refine','2026-08-26'),('k-optimize','2026-03-18'),('m-id','2026-09-24'),('m-unlisted','2026-09-23'),('b-jv','2026-01-23'),('a-funding','2024-07-25'),('a-plan','2026-01-14'),('h-funding','2026-02-03'),('h-funding-media','2026-02-03'),('h-products','2026-09-10')]: SOURCES[sid]['published_date']=d

def revenues(period,total,parts,sid,audited,note=''):
    return f({'period':period,'currency':'CNY','unit':'thousand','total':total,'audited':audited,
              'parts':[{'business':n,'amount':a,'percent':round(a/total*100,2),'percent_basis':'按官方金额计算'} for n,a in parts]},sid,note=note)

def cards():
    C={}
    C['zhihu']={
      'type':'listed', 'display_name':'知乎',
      'legal_name':f('Zhihu Inc.','z-id',note='上市母公司，不等于JD上的境内签约主体'),
      'brand_names':f(['知乎','Zhihu'],'z-id'),
      'listing':f({'status':'上市','venues':[{'exchange':'HKEX','ticker':'2390'},{'exchange':'NYSE','ticker':'ZH'}]},'z-id','z-list'),
      'main_business':[f('经营在线内容社区，通过向个人提供付费内容、向商业客户提供广告和内容营销服务获取收入。','z-official','z-member','z-marketing'),f('2026年披露增加“付费内容及IP运营”口径，并持续调整职业培训业务。','z-new','z-refine')],
      'revenue_mix':[revenues('2025-01-01/2025-12-31',2749004,[('营销服务',843933),('付费会员',1538942),('其他（包含职业培训等）',366129)],'z-revenue',True,'年报原表占比30.7%、56.0%、13.3%；卡片计算保留两位小数。'),revenues('2026-01-01/2026-06-30',1341687,[('营销服务',390404),('付费内容及IP运营',828260),('其他',123023)],'z-new',False,'2026重分类，不能将新旧收入名称直接拼接为同口径时间序列。')],
      'products_customers':{'products':f(['知乎社区','付费内容/会员','广告及内容商业化解决方案'],'z-member','z-marketing'), 'users':f('内容读者、创作者及社区使用者；免费用户不等于付费客户。','z-member','z-marketing',status='interpretation'), 'paying_customers':f('购买内容会员的个人，以及在社区投放广告、购买内容营销服务的商业客户。','z-member','z-marketing')},
      'recent_events':[{'event_date':None,'disclosed_on':'2026-08-26','event_period':'2026Q2','claim':f('Q2公告披露职业培训业务继续调整，其他收入由上年同期85,957千元降至65,192千元；这是收入/业务变化，不是裁员人数。','z-refine')}],
      'event_search_boundary':'窗口2025-10-12至2026-10-12；未找到可纳入的裁员/融资/新上市原创报道；并非确认不存在。'}
    C['kanzhun']={
      'type':'listed','display_name':'BOSS直聘（看准）','legal_name':f('KANZHUN LIMITED（看準科技有限公司）','k-id'), 'brand_names':f(['BOSS直聘','看准','Kanzhun'],'k-id','k-product'),
      'listing':f({'status':'上市','venues':[{'exchange':'HKEX','ticker':'2076'},{'exchange':'Nasdaq','ticker':'BZ'}]},'k-list'),
      'main_business':[f('经营BOSS直聘等在线招聘服务，让求职者与企业直接沟通，并主要向企业出售招聘服务与增值工具。','k-product','k-business')],
      'revenue_mix':[revenues('2025-01-01/2025-12-31',8267518,[('企业客户在线招聘服务',8192714),('其他（主要为求职者付费增值服务）',74804)],'k-revenue',False,'本公告为未经审计年度结果，已获审计委员会审阅；占比为计算值。2026中期定向搜索未命中目标，不能称本卡为最新财务全覆盖。')],
      'products_customers':{'products':f(['BOSS直聘','企业招聘/增值工具','求职者增值工具'],'k-product','k-business'),'users':f('招聘方和求职者，基础沟通有免费服务。','k-product'),'paying_customers':f('企业客户是主要付费方；少量收入来自求职者购买增值工具。','k-business','k-revenue')},
      'recent_events':[],
      'recent_disclosures':[{'event_date':None,'disclosed_on':'2026-03-18','event_period':'2025年度','claim':f('年度公告披露优化部分求职者增值功能，相关其他收入由85,651千元降至74,804千元。公告发布时间在窗口内，未给出优化动作的具体发生日，不能列为已确认窗口内事件。','k-optimize')}],
      'event_search_boundary':'窗口2025-10-12至2026-10-12；动作发生日未精确披露，该项属于窗口内发布的业务调整披露，不证明动作发生在窗口内；未找到合格裁员/融资/新上市事件。'}
    C['mihoyo']={
      'type':'private_large','display_name':'米哈游','legal_name':f('上海米哈游网络科技股份有限公司','m-id',note='集团代表主体；官网/游戏协议运营主体为上海米哈游影铁科技有限公司。具体JD签约主体须另核。'),'brand_names':f(['米哈游','miHoYo'],'m-business'),
      'listing':f({'status':'未上市','venues':[]},'m-unlisted',note='公司经记者确认的非上市股份公司回应；股权托管代码T00307不是证券交易所股票代码。'),
      'main_business':[f('研发和运营《原神》《崩坏：星穹铁道》《绝区零》等游戏，并围绕原创IP推出动画、音乐和周边。','m-business','m-products'),f('游戏协议允许通过收费游戏、虚拟物品使用权与增值服务收取费用；无法据此判断各项收入占比。','m-pay')],
      'revenue_mix':missing('未找到当期官方集团收入构成；不使用百科/媒体/游戏流水估计代替财务披露。'),
      'products_customers':{'products':f(['原神','崩坏：星穹铁道','绝区零','原创IP衍生内容/周边'],'m-products','m-business'),'users':f('游戏玩家及IP内容受众。','m-products','m-business',status='interpretation'),'paying_customers':f('购买游戏虚拟物品使用权或增值服务的玩家；衍生品收入占比未找到。','m-pay')},
      'recent_events':[{'event_date':'2026-09-23','claim':f('办理股权托管登记；9月23-24日公司向媒体回应是非上市股份公司治理常规安排，目前没有上市融资计划。','m-id','m-unlisted')}],
      'related_entities':f(['上海米哈游影铁科技有限公司（官网及游戏服务协议主体）'],'m-operator'),
      'event_search_boundary':'未找到合格的近12月裁员/业务收缩事件；不把其他游戏公司裁员新闻算入米哈游。'}
    C['bytedance']={
      'type':'private_large','display_name':'字节跳动','legal_name':f('ByteDance Ltd.（字节跳动有限公司）','b-id',status='provisional',note='本轮法定集团名只得到百科，未取得工商/官方注册文件；境内多个抖音/字跳主体不等于集团。'),'brand_names':f(['字节跳动','ByteDance'],'b-id'),
      'listing':f({'status':'未上市','venues':[]},'b-unlisted',status='provisional',note='百科Private及本轮未找到集团上市披露；不是监管的负面证明。TikTok美国合资重组不是集团IPO。'),
      'main_business':[f('向个人提供抖音、今日头条、TikTok等内容平台，另有Lark等企业协作产品；这是业务线目录，不代表收入排名。','b-products','b-lark'),f('商业化路径包括广告营销和企业软件/云服务收费，必须按JD所属业务线解释，不能套用集团统一收入比例。','b-ads','b-saas','b-cloud')],
      'revenue_mix':missing('未找到公开官方集团分业务收入构成；不将匿名媒体财务数据或业务规模当官方占比。'),
      'products_customers':{'products':f(['抖音','今日头条','TikTok','Lark/飞书','巨量引擎','火山引擎'],'b-products','b-lark','b-ads','b-saas','b-cloud'),'users':f('内容消费者/创作者和企业员工等各产品使用者。','b-products','b-lark',status='interpretation'),'paying_customers':f('广告主，以及购买企业软件或云/模型服务的组织；飞书有免费和付费版本，不能把员工都当购买方。','b-ads','b-saas','b-cloud')},
      'recent_events':[{'event_date':'2026-01-23','claim':f('TikTok公告美国USDS合资公司成立，ByteDance持有19.9%；只用于解释美国业务结构，不能推出集团上市或全球TikTok所有权全部转让。','b-jv')}],
      'event_search_boundary':'未找到可核验的集团近12月裁员/融资原创正文；不纳入匿名估值推算。'}
    C['baichuan']={
      'type':'startup','display_name':'百川智能','legal_name':f(['百川智能科技有限公司（主站页脚）','北京百川智能科技有限公司（平台文档页脚）'],'a-id','a-old-id',status='conflict',note='两处官方页面名称不一致；工商正文未取得，不替用户判断更名或关联主体。招聘样本使用前者。'),'brand_names':f(['百川智能','Baichuan'],'a-id','a-founded'),
      'listing':f({'status':'未上市','venues':[]},'a-plan',status='provisional',note='2026年1月采访称可能2027年启动上市；截至本轮未找到完成上市披露。意向不等于已申报。'),
      'main_business':[f('研发大语言模型，并提供面向个人/家庭健康信息服务的百小医、医疗模型和API。官网产品自述不能当独立疗效验证。','a-product','a-free'),f('海纳百川计划为符合准入要求、服务医务工作者的机构免费提供医疗API；使用该API不代表付费。','a-free')],
      'revenue_mix':missing('未找到官方收入金额或分业务占比；融资金额不是收入。'),
      'products_customers':{'products':f(['百小医','Baichuan医疗模型','海纳百川M3 Plus API'],'a-product','a-free'),'users':f('个人及家庭健康信息用户，及为医务工作者提供服务的机构。','a-product','a-free'),'paying_customers':missing('未找到当前产品已付费客户名单或实际收入主体；官网仍有通用模型价格，但不足以证明医疗API/百小医已实现付费。')},
      'recent_events':[{'event_date':'2026-01-13','disclosed_on':'2026-01-14','claim':f('媒体交流中创始人披露医疗AI方向及可能2027年启动上市的计划；是意向，非融资完成或已上市。','a-plan')}],
      'selection':{'posting_ids':['vyk5CtnNL'],'founded':f('2023-03-24','a-founded'),'public_funding':f('2024-07-25第一财经向公司求证A轮总融资50亿元；早于近12月窗口，仅作初创筛选证据。','a-funding')},
      'event_search_boundary':'2026-01-10报道回顾2025年初裁员，事件超出12月窗口，未纳入recent_events；数字来自匿名前员工，不能当已核实当前人数。'}
    C['humanoid']={
      'type':'startup','display_name':'北京人形机器人创新中心','legal_name':f('北京人形机器人创新中心有限公司','h-id'),'brand_names':f(['北京人形','北京人形机器人创新中心'],'h-id','h-funding'),
      'listing':f({'status':'未上市（本轮未找到上市披露）','venues':[]},'h-funding',status='provisional',note='官网披露首轮市场化融资，未找到该主体证券代码；不能将股东优必选等上市状态转移到该公司。未取得官方负面证明。'),
      'main_business':[f('研发具身智能机器人本体、控制/智能平台及应用方案，围绕“具身天工”和“慧思开物”开展产品研发与落地。','h-business'),f('通过渠道伙伴拓展工业、物流、能源、商业服务和教育科研等场景；官网方案和招募对象不等于已成交客户或规模收入。','h-customers')],
      'revenue_mix':missing('未找到官方收入构成；融资和机器人竞赛成绩不能代替收入。'),
      'products_customers':{'products':f(['具身天工/天工3.0/Omni','天轶2.0','慧思开物平台'],'h-products','h-business'),'users':f('集成商、科研教育团队与各行业机器人使用/开发团队。','h-customers',status='interpretation'),'paying_customers':missing('官网可见采购/合作入口、渠道类型与场景，但未找到可确认的已付费终端客户名单或合同。')},
      'recent_events':[{'event_date':'2026-02-03','claim':f('官网宣布完成首轮超7亿元市场化融资，财新同期报道；不是销售收入。','h-funding','h-funding-media')},{'event_date':'2026-09-10','claim':f('官网招募渠道伙伴并展示天工3.0、天轶2.0等产品，显示在推进商业化渠道建设，尚不能证明成交规模。','h-products','h-customers')}],
      'selection':{'posting_ids':['vYl5azaaL','vlY5azazZ'],'founded':f('2023-11','h-founded'),'public_funding':f('2026-02-03首轮超7亿元市场化融资。','h-funding','h-funding-media')},
      'event_search_boundary':'未找到合格近12月裁员/业务收缩消息；国资/产业方共建背景，不代表典型纯民营医疗AI初创。'}
    return C

def field_levels(obj):
    ids=set()
    def visit(x):
        if isinstance(x,dict):
            ids.update(x.get('source_ids',[]))
            for v in x.values():visit(v)
        elif isinstance(x,list):
            for v in x:visit(v)
    visit(obj)
    return sorted({SOURCES[x]['level'] for x in ids}) or ['未找到/本地记录']

def channel_rows(C):
    metas=[json.loads(p.read_text()) for p in E.glob('*.meta.json')]
    rows=[]
    for cid,c in C.items():
        for channel in ('tavily','exchange','official','gsxt','qcc','tianyancha','supplement'):
            chosen=[m for m in metas if m.get('company')==cid and (m.get('channel')==channel or (channel=='supplement' and m.get('channel') in ('media','encyclopedia')))]
            times=[m['elapsed_seconds'] for m in chosen if isinstance(m.get('elapsed_seconds'),(int,float))]
            usable=any(s['evidence_id'] in [m.get('id',pathlib.Path(m.get('snapshot','')).stem) for m in chosen] for s in SOURCES.values())
            if channel=='tavily':usable=any(m.get('status')==200 for m in chosen)
            if channel=='supplement':
                usable=any(m.get('status')==200 and m.get('snapshot') and len(body(m['snapshot']))>200 for m in chosen)
            if channel=='official' and cid in ('mihoyo','baichuan'):usable=True
            if channel=='gsxt':usable=False
            if channel in ('qcc','tianyancha'):usable=False
            applicable=not(channel=='exchange' and c['type']!='listed')
            fields={'tavily':'URL/主体候选及聚合正文；经复核后才能用', 'exchange':'主体/上市/主营/收入/业务调整', 'official':'产品/业务/使用方；部分收费规则与事件', 'gsxt':'未取得企业正文','qcc':'不计合规成功；风控/入口/非目标主体','tianyancha':'仅登录壳；未取得企业正文','supplement':'百科身份/媒体事件与融资，须看单条等级'}[channel]
            row={'company':cid,'type':c['type'],'channel':channel,'applicable':applicable,'usable_body':usable,'fields':fields,'request_count':len(times),'mean_response_seconds':round(sum(times)/len(times),3) if times else None,'timed_total_seconds':round(sum(times),3) if times else None,'login_or_payment': '登录壳可见；具体字段/付费墙未实测' if channel=='tianyancha' else '风控后停止；付费边界未实测' if channel=='qcc' else 'robots521停止；未进入查询' if channel=='gsxt' else '本轮使用不需登录/付费' if applicable else '不适用','observations':[{'url':m.get('url'),'status':m.get('status'),'reason':m.get('reason'),'elapsed_seconds':m.get('elapsed_seconds'),'snapshot':m.get('snapshot')} for m in chosen]}
            if channel=='gsxt':row['shared_preflight']='gsxt-entry.meta.json；一次共享预检，未逐公司请求'
            rows.append(row)
    write(E/'channels.json',rows)
    with (ROOT/'docs/research/company-check-pilot-2026-10-channels.csv').open('w') as file:
        fields=[k for k in rows[0] if k!='observations']
        w=csv.DictWriter(file,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    return rows

def main():
    build_sources()
    # Fee/monetization primary sources only; no AI-generated SEO articles.
    source('b-ads','bytedance-final-direct-0',L2,'巨量引擎营销资源','广告','官方帮助页；商业产品与广告主资源')
    source('b-saas','bytedance-final-direct-1',L2,'飞书定价版本介绍','商业版和企业版需要另外购买','未带Cookie的静态HTML meta description；公开文档摘要')
    source('b-cloud','bytedance-cloud-cdp',L2,'火山方舟模型服务计费','按 token 后付费','官方产品计费文档公开正文，页面显示登录/注册入口')
    C=cards()
    for cid,c in C.items():
        c.update({'id':cid,'schema_version':'company-check-pilot-v1','as_of':DATE,'status':'partial_evidence','scope':'公司公开信息；不等于具体岗位/签约主体核验'})
        c['source_levels']={k:field_levels(v) for k,v in c.items() if k not in ('source_levels','sources')}
        ids=set()
        def walk(x):
            if isinstance(x,dict):
                ids.update(x.get('source_ids',[]))
                for v in x.values():walk(v)
            elif isinstance(x,list):
                for v in x:walk(v)
        walk(c); c['sources']={sid:SOURCES[sid] for sid in sorted(ids)}
        write(OUT/(cid+'.json'),c)
    write(E/'sources.json',SOURCES)
    rows=channel_rows(C)
    manifest=[]
    for p in sorted(E.iterdir()):
        if p.is_file() and p.name not in ('manifest.json','ledger.json','validation.json'):
            manifest.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    write(E/'manifest.json',manifest)
    print(json.dumps({'cards':len(C),'sources':len(SOURCES),'channel_rows':len(rows),'evidence_files':len(manifest)},ensure_ascii=False))

if __name__=='__main__':main()
