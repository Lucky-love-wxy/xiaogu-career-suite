import json,pathlib,hashlib
root=pathlib.Path(__file__).parent;parts=root.parent/'parts'
vers={n:json.loads((root/f'oss-{n}-commit.txt').read_text())['sha'] for n in ['mem0','letta','lettacode','langgraph','graphiti']}
solutions=[]
def sol(name,v,answers):solutions.append({'name':name,'version':v,'questions':[{'q':i+1,'answer':a,'evidence_ids':e} for i,(a,e) in enumerate(answers)]})
sol('mem0 OSS Python SDK',vers['mem0'],[
('以 user_id/agent_id/run_id 隔离用户、agent、会话事实；主要是事实文本+向量+metadata（含角色、来源、时间、关联记忆），SQLite 保存历史及最近消息。源码单独处理 procedural_memory；不是强制把事实/事件/反思分成四个数据库，也没有求职旅程 schema。', ['oss-mem0-source-1','oss-mem0-source-2']),
('调用方决定何时调用 add；infer=True 默认由 LLM 选择值得记录的内容，infer=False 直接写非 system 消息。当前 V3 执行路径采用 ADD-only，查相近旧记忆、单次抽取、hash 去重、关联旧记忆；矛盾记录新增并链接而非自动覆写旧值。另有显式 update/delete 和 expiration_date。源码 add 的 docstring 仍描述自动增改删，与当前执行路径及 README 不一致，不能当现行默认。用户确认、纠错审批仍须应用另做。', ['oss-mem0-source-1','oss-mem0-extra-3','oss-mem0-readme']),
('search 相关检索，可设 top_k；当前默认 top_k=20；语义、BM25 与实体信号依赖后端及可选 NLP。调用方选择哪些结果进入 prompt，不要求每轮全量。token 减少是检索子集的机制推断；写入仍耗 LLM/embedding，不能把 README 托管平台 benchmark 当 OSS 本地效果或中文 token 承诺。', ['oss-mem0-source-1','oss-mem0-extra-2','oss-mem0-readme']),
('不能理解为仅 Python+SQLite：SQLite 是 history.db；默认 vector provider=qdrant，无远端参数时走 QdrantClient(path=...)，支持本地嵌入式向量存储而不必另起向量服务。默认 LLM/embedding 访问 OpenAI；官方 Ollama 配置可换本地模型，但还需要 Ollama 推理进程、模型文件和向量依赖。库、Docker 自托管服务、云平台是三种交付形态，不等价。遥测有外发路径，完全本地须另核验并关闭。', ['oss-mem0-source-2','oss-mem0-extra-1','oss-mem0-extra-2','oss-mem0-source-4','oss-mem0-readme','oss-mem0-extra-4']),
('Apache-2.0。未找到独立中文记忆准确率评测。实际中文/多语言问题有公开反馈：issue #4884（三级用户报告）称 BM25/实体信号退化，PR #6718 提出中文 pipeline 修复但取证时 open、merged=false；不能视作已发布修复。当前抽取 prompt 支持 use_input_language，但函数默认 False，执行调用未打开该选项；中文保持同语不能仅凭旧 prompt 推定。', ['oss-mem0-source-3','oss-mem0-issue-4884','oss-mem0-pr-6718','oss-mem0-extra-3','oss-mem0-source-1']),
('具体已知问题：#4884 报告非英文 BM25 无命中/实体 boost 丢失；当前代码固定英文 spaCy 可核验。源码对抽取 JSON 解析失败返回空记忆列表（与无事实相同表象），LLM 请求异常则抛 LLMError；Qdrant 旧 collection 无 BM25 sparse slot 时降为语义搜索并警告。ADD-only 会留下历史矛盾，需要检索/上层来源及时间策略判别；这是源码机制风险，不是已测出的错误率。未找到可直接适用于当前 commit 的“不该记的隐私内容”事故统计。', ['oss-mem0-issue-4884','oss-mem0-verify-1','oss-mem0-verify-2','oss-mem0-source-1','oss-mem0-extra-2'])])
sol('Letta 当前活跃源（Letta Code；原 MemGPT）',vers['lettacode'],[
('原 letta 仓库当前 main 明确 V1 Python API server 已 retired，历史源在 archive；现行活跃源为 letta-code。当前 MemFS：根 MEMORY.md 索引、根 Markdown core memory（常驻）、子目录 deferred memory（按需读）、skills（程序性记忆），Git 跟踪；本地对话/compaction 以 JSONL/JSON 存。不能把旧 core/recall/archival 文档冒充当前部署的默认。', ['oss-letta-readme','oss-letta-extra-4','oss-letta-extra-3','oss-letta-extra-6']),
('主 agent 可改 memory；可配置周期 dreaming/reflection，由后台 agent 看近期或多会话 transcript，筛掉临时、已记录信息，针对纠错/偏好/事实更新文件。反思 prompt 要求以最新证据替换陈旧事实，不并列保留矛盾；用户要求忘记、敏感或错误内容应删除。语义冲突依靠 agent 判断，不是确定性冲突规则；Git 合并冲突另有 repair worker、锁与 attempted 状态。不是每轮强制反思，需配置触发策略。', ['oss-lettacode-verify-1','oss-letta-extra-4','oss-letta-extra-5']),
('core 内容和索引/描述常驻 prompt，deferred/skill 正文按需读取；支持消息搜索。本地 transcript-search 明确不支持 vector/hybrid，只支持 fts（源码含 CJK substring 处理）。token 随 core 大小和选读变化；后台反思另耗模型调用。该机制不能推出固定节省比例。', ['oss-letta-extra-4','oss-letta-extra-6','oss-letta-extra-7']),
('当前活跃实现是 npm/Node 而非 Python 库；本地 MemFS Git + 磁盘 JSON/JSONL，无须向量服务的本地消息检索已经存在。因此不能直接在“仅 Python+SQLite”约束下即插即用。README 默认 Letta Cloud，提供 backend local；本地状态不代表本地推理，LLM provider 仍另配置。可自托管 App Server；未运行或验证其完全离线部署。历史 Python server 可复现但已退休，不建议把它算作现行支持。', ['oss-letta-readme','oss-lettacode-verify-1','oss-lettacode-verify-2','oss-letta-extra-3','oss-letta-extra-7']),
('Apache-2.0。未找到独立中文长期记忆效果评测；找到中文使用界面反馈 #2644：IME 候选窗错位（2026-06-01 举报，2026-07-03 closed），这是界面问题，不能推定当前中文记忆准确率低或故障仍在。当前检索源码有 CJK 子串匹配，说明适配机制，不等于效果评测。', ['oss-letta-extra-1','oss-letta-issue-2644','oss-letta-extra-7']),
('具体边界：本地 vector/hybrid 搜索抛不支持错误；MemFS 未提交/无可读 revision 会导致编译为空 core；不可读已提交文件被 best-effort 跳过。Git 冲突修复存在已尝试但无法解决状态；反思依赖模型选择与改写，未找到当前 commit 的语义错记率公开评测。README 明确原生 Windows 自动 dreaming 默认关闭，手动可用，这是平台限制不是记忆全失效。', ['oss-letta-extra-7','oss-letta-extra-6','oss-letta-extra-5','oss-lettacode-verify-1'])])
sol('LangGraph 长期记忆 Store（Python）',vers['langgraph'],[
('Store 是按 namespace tuple + key 存 JSON mapping 的通用跨会话数据层，Item 有 created_at/updated_at。用户事实、事件、批次反馈、复盘都可由应用定义 value schema；Store 本身不抽取、不规定四种记忆。InMemoryStore 是进程内字典，退出丢失。当前仓库已有官方 SqliteStore，和线程 checkpointer 是不同类。', ['oss-langgraph-source-1','oss-langgraph-source-2','oss-langgraph-source-4']),
('应用/图节点决定何时 put、get、delete。同 namespace+key 的 put 更新/替换值；SqliteStore 批次同键去重后 INSERT OR REPLACE，并支持 TTL/sweep。是否记忆、模型还是用户确认、版本冲突/事实矛盾的语义合并由应用实现。TTL 是技术过期机制，不能替代同意、最小化和删除流程。', ['oss-langgraph-source-1','oss-langgraph-source-4']),
('get 精确读；search 有 namespace、metadata filter、limit/offset，配置 index 后才有语义检索；InMemory 默认不启用 embedding。Store 不自动把结果塞进 prompt，图节点自行装配。token 由抽取节点、embedding、召回数量、注入字段决定；未找到可通用于任意 Store 图的节省比例。', ['oss-langgraph-source-1','oss-langgraph-source-2','oss-langgraph-source-4']),
('可以用 Python + SQLite 文件在单机跑当前官方 SqliteStore；有 sqlite_vec/orjson 等库依赖，无须额外向量数据库服务。不启用 index 时普通字段存取不需境外调用；语义检索可传自定义本地 embedding。官方示例出现 OpenAI embedding 只是示例，不是库强制默认。SqliteStore 同步类不支持 async，应另用 AsyncSqliteStore；本次只源码确认，不做安装/并发/耐久测试。', ['oss-langgraph-source-4','oss-langgraph-source-1','oss-langgraph-verify-1']),
('MIT（仓库主许可；各组件另核验）。未找到独立中文长期记忆效果评测；Store 的中文保存/语义效果取决于应用 schema、embedding 和 LLM。找到 #8514 中文 Windows GBK 环境 langgraph dev 启动失败的用户报告，但属 API/CLI 读取编码，不是 SQLite Store 中文检索评测或 Linux 服务器必然失败。', ['oss-langgraph-source-5','oss-langgraph-issue-8514']),
('可核验失败边界：InMemoryStore 进程退出数据丢失；无 index 时语义搜索不启用；SqliteStore 同步类 async 调用不支持。已公开 #8514 报告 CLI/API locale 编码失败，不能外推为核心 Store 缺陷。Store 不自动验证事实/敏感信息，若应用盲 put 则原样持久化；这是职责边界推断，不是 LangGraph 已确认隐私事件。', ['oss-langgraph-source-2','oss-langgraph-source-1','oss-langgraph-source-4','oss-langgraph-issue-8514'])])
sol('Graphiti OSS（与 Zep 托管服务区分）',vers['graphiti'],[
('记忆组成：entity 节点及摘要、fact/relationship 边、episode 原始事件及来源、开发者 ontology；边有有效时间范围，可追溯来源 episode。Graphiti 默认 store_raw_episode_content=True；不是自动提供求职用户表/线程管理的完整助手服务。Zep 是托管 context infrastructure，不能把其 user/thread、治理、性能承诺算作 OSS 功能。', ['oss-graphiti-readme','oss-graphiti-source-1']),
('调用方决定哪些 episode 入库；add_episode 做 LLM 实体/关系抽取、去重、embedding、边冲突解决。LLM 提示词区分 duplicate 与 contradicted facts；新信息使旧边失效，历史保留，不直接删掉旧事实。不是每轮自动运行，选择有价值/征求用户确认要应用决定；时间失效不等于用户删除个人信息。', ['oss-graphiti-source-1','oss-graphiti-extra-1']),
('search 是语义+关键词+图关系的混合召回，返回相关关系，可用 recipes/重排；调用方装配到 prompt。检索减少需注入的候选历史是机制推断，写入的实体抽取/去重/摘要和重排可能另耗模型 token；未找到对当前 OSS 中文求职场景通用 token 成本实证。', ['oss-graphiti-source-1','oss-graphiti-readme']),
('不能仅 Python+SQLite：默认 Neo4j；可选 FalkorDB、Neptune 等图后端，FalkorDB Lite 可嵌入但不是 SQLite；Kuzu 当前 deprecated。默认 OpenAI LLM/embedder/reranker；官方支持 OpenAI-compatible 本地 Ollama/vLLM 等，能避免默认境外推理调用但需图存储+本地模型服务。README 遥测 opt-out，完全本地还需关闭 GRAPHITI_TELEMETRY_ENABLED。Zep 托管与 Graphiti 本地自建的境外依赖需分开评估。', ['oss-graphiti-readme','oss-graphiti-source-1','oss-graphiti-source-2']),
('Apache-2.0。未找到独立中文长期记忆基准；找到三级用户反馈 #312（2025-03-31）：中文自建库效果不错，但总结/推断仍混英文。评论表示计划跟随 episode 语言，后续追问进展；issue closed 本身不能证明已修复。该反馈距本次逾一年，仅作历史故障线索，不能评定当前中文水平。', ['oss-graphiti-source-3','oss-graphiti-issue-312','oss-graphiti-comments-312']),
('官方 README 明确小/本地模型可能生成不合 schema 的 JSON 导致抽取失败；支持 json_schema/json_object 切换但无准确性保证。官方提醒 LLM provider 429 风险、需低并发；Kuzu 上游未维护而弃用。#312 是中英混杂历史反馈。LLM 判断关系矛盾/重复不是事实真值保证；未找到当前 OSS 的敏感信息误记事故统计。', ['oss-graphiti-readme','oss-graphiti-extra-1','oss-graphiti-issue-312'])])
quotes={
'oss-mem0-source-1':'# === V3 PHASED BATCH PIPELINE', 'oss-mem0-source-2':'Path to the history database', 'oss-mem0-source-3':'Apache License', 'oss-mem0-source-4':'Self-Hosted AI Companion',
'oss-mem0-readme':'ADD-only extraction','oss-mem0-extra-1':'default="qdrant"','oss-mem0-extra-2':'BM25 keyword scoring','oss-mem0-extra-3':'use_input_language=False','oss-mem0-extra-4':'MEM0_TELEMETRY','oss-mem0-issue-4884':'BM25 silently becomes a no-op.','oss-mem0-pr-6718':'Empty BM25 text','oss-mem0-verify-1':'en_core_web_sm','oss-mem0-verify-2':'token.lemma_',
'oss-letta-readme':'retired Letta V1 API server','oss-lettacode-verify-1':'Letta Cloud is the default.','oss-lettacode-verify-2':'"engines"','oss-letta-extra-1':'Apache License','oss-letta-extra-3':'appendFileSync','oss-letta-extra-4':'Core memory','oss-letta-extra-5':'could not resolve it','oss-letta-extra-6':'if (!revision)','oss-letta-extra-7':'Use "fts".','oss-letta-issue-2644':'IME candidate selection window',
'oss-langgraph-source-1':'JSON-serializable values','oss-langgraph-source-2':'Data is lost','oss-langgraph-source-4':'INSERT OR REPLACE INTO store','oss-langgraph-source-5':'MIT License','oss-langgraph-verify-1':'sqlite-vec','oss-langgraph-issue-8514':'UnicodeDecodeError',
'oss-graphiti-readme':'Kuzu is **deprecated**','oss-graphiti-source-1':'store_raw_episode_content','oss-graphiti-extra-1':'contradicted_facts','oss-graphiti-source-2':'base_url','oss-graphiti-source-3':'Apache License','oss-graphiti-issue-312':'mixed with English','oss-graphiti-comments-312':'Looking forward to it!'}
entries={}
for p in sorted(root.glob('oss-fetch-*.json')):
 for s in json.loads(p.read_text()):entries[s['id']]=s
used={e for s in solutions for q in s['questions'] for e in q['evidence_ids']}
used|={f'oss-{n}-commit' for n in vers}
sources=[]
for id in sorted(used):
 s=entries[id];s['title']=id;s['quote']=quotes.get(id,'');s['level']=3 if ('issue-' in id or 'comments-' in id or '-pr-' in id) else 1
 s['status']='正文已读/源码静态核验' if s['status']==200 else str(s['status'])
 if s['quote']:
  body=pathlib.Path(s['snapshot']).read_text();assert s['quote'] in body,(id,s['quote'])
  assert len(s['quote'])<=30,(id,len(s['quote']))
 sources.append(s)
data={'solutions':solutions,'sources':sources,'limitations':['未安装、部署或运行收费 API；不声称本地运行通过。','版本为访问时 HEAD commit，不是稳定 release 推荐。','后续证据脚本每域请求间隔至少3.1秒；首次4仓库GitHub首页web批量侦察未先查robots且无法证明请求间隔，作为采集审计缺口披露，不用作结论证据。API/raw robots 返回404，无规则文件不当作许可证明。','原始证据是HTTP正文文本/JSON/源码，不是浏览器截图；引用源全部保存SHA256。首次web侦察返回未落盘，不进入结论证据集。','中文检索范围为官方源码/README与各仓库Chinese关键词issue/PR；未找到独立中文评测不等于不存在。','公网提供方与模型文件下载依赖、遥测、商用许可证须按实际选型进一步核验。']}
(parts/'opensource.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
lines=['## B. 开源长期记忆方案','', '访问日期：2026-10-14。四方案均锁定实际 commit；仅静态阅读公开官方源码、README 和公开反馈，未安装或付费调用。新版本已发生明显变更：mem0 默认 ADD-only、Letta 当前改为 Letta Code、LangGraph 当前源码已有官方 SQLite Store。','', '| 方案 | 取证版本 | 交付形态 |','|---|---|---|']
for s in solutions:lines.append(f"| {s['name']} | `{s['version']}` | {'Python 数据层' if 'LangGraph' in s['name'] else 'Node agent harness' if 'Letta' in s['name'] else 'Python 记忆库/另有服务' if 'mem0' in s['name'] else 'Python 时序图框架'} |")
labels=['记忆种类与存法','写入、更新、冲突','读取与 token','部署与境外依赖','许可与中文效果','公开失败与已知边界']
for s in solutions:
 lines += ['',f"### {s['name']}",'','| 问题 | 答案与证据 |','|---|---|']
 for q in s['questions']:lines.append(f"| {q['q']}. {labels[q['q']-1]} | {q['answer']} {' '.join('['+e+']' for e in q['evidence_ids'])} |")
lines+=['','### 对设计的影响（条件性判断，不替设计方定案）','','- 如严格维持 Python + SQLite 单机，LangGraph 当前 SqliteStore 可以直接作为存取层候选；它不代办事实抽取、确认、旅程状态机或用户纠错，不能把安装 Store 当完成记忆系统。[oss-langgraph-source-1][oss-langgraph-source-4]','- mem0 可以复用抽取/相关检索；默认 Qdrant + OpenAI，不能将 history.db 当完整 SQLite 方案。ADD-only 使来源、时间、当前有效状态和用户纠正记录尤其重要。[oss-mem0-source-1][oss-mem0-extra-1][oss-mem0-extra-3]','- Letta 分层 core/deferred 与后台反思可借鉴；当前 npm/Node harness、Git 和默认云模式不满足直接嵌入 Python+SQLite 的原始约束，历史 V1 退休事实应先沟通。[oss-letta-readme][oss-letta-extra-4][oss-lettacode-verify-1]','- Graphiti 的事件溯源及关系有效时间适合借机制；若只保存少量求职事实与轮次状态，额外图数据库/模型链不是必需条件，这是复杂度判断而非性能实测。用户删除须删除原 episode 与派生事实，不能只让旧关系“失效”。[oss-graphiti-source-1][oss-graphiti-readme]','- 各方案都不自带“用户事实—给过哪批—实际反馈—结果复盘”这一求职业务契约；应由应用保存带证据来源的显式状态，不能让模型摘要独占真值。[oss-langgraph-source-1][oss-mem0-extra-3][oss-graphiti-source-1]','','### 证据目录','','正文快照为 raw HTTP body（Markdown 源码、Python/TypeScript 源码或 GitHub API JSON），不是可视截图。一级：官方源码/仓库说明；三级：公开 issue/PR 作者的体验、故障或修复主张；官方仓库容器不提升用户举报为官方确认。API/raw robots.txt 是 404，无规则文件并不证明许可。','']
for s in sources:lines.append(f"- **{s['id']}**｜L{s['level']}｜[{s['title']}]({s['url']})｜2026-10-14｜短摘：{s['quote'] or 'commit sha见快照'}｜快照 `{s['snapshot']}`｜SHA256 `{s['sha256']}`")
lines += ['','采集审计：首次四仓库 GitHub 首页采用一次 web 批量侦察，未先核验 robots，且无法证明其请求间隔，未作为报告结论证据。后续全部引用源通过 Python 每域至少 3.1 秒限速与 robots 检查取得；该修复不抹去首次侦察缺口。Generative Agents 反思论文由主报告 C/方法节补充，不将 Letta 的反思 prompt 当该论文的实验证据。']
(parts/'opensource.md').write_text('\n'.join(lines)+'\n')
print('solutions',len(solutions),'answers',sum(len(s['questions']) for s in solutions),'sources',len(sources))
