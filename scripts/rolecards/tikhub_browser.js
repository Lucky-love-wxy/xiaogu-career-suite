// 仅在本任务TikHub后台研究tab中加载：cdp.mjs eval --body-file 此文件。
// Key须由用户授权的现有后台复制按钮在内存获得；不读其他凭证，不持久化。
// 此文件只安装函数，不发API请求。调用需要覆盖具体费用的授权。
(()=>{
 window.__rolecards_api_cache=window.__rolecards_api_cache||{};
 window.__rolecardsApiCall=async job=>{
  const allowed=['search_notes','get_image_note_detail','get_video_note_detail'];
  if(!allowed.includes(job.endpoint))throw new Error('endpoint not allowed');
  if(!window.__rolecards_tikhub_key)throw new Error('key not available');
  const key=JSON.stringify([job.endpoint,Object.entries(job.params).sort()]);
  if(window.__rolecards_api_cache[key])return window.__rolecards_api_cache[key];
  if(window.__rolecards_api_stopped)throw new Error('prior API failure: no retry');
  if((window.__rolecards_api_n||0)>=10)throw new Error('US$0.10 conservative request cap reached');
  const u=new URL('https://api.tikhub.io/api/v1/xiaohongshu/app_v2/'+job.endpoint);
  for(const [k,v]of Object.entries(job.params))u.searchParams.set(k,String(v));
  window.__rolecards_api_n=(window.__rolecards_api_n||0)+1;
  try{
   const r=await fetch(u,{headers:{Authorization:'Bearer '+window.__rolecards_tikhub_key},credentials:'omit'});
   const j=await r.json();window.__rolecards_last=j;
   const out={endpoint:job.endpoint,params:job.params,http:r.status,code:j.code,request_id:j.request_id,call_n:window.__rolecards_api_n,accessed_at:new Date().toISOString()};
   if(!r.ok||j.code!==200){window.__rolecards_api_stopped=true;return {...out,error:'API rejected; no retry'};}
   if(job.endpoint==='search_notes')out.items=(j.data?.data?.items||[]).filter(x=>x.model_type!=='ads'&&x.note).map(x=>({id:x.note.id,title:x.note.title||x.note.name,desc:x.note.desc,nickname:x.note.user?.nickname,time:x.note.timestamp,type:x.note.type,likes:x.note.liked_count}));
   else{
    out.notes=[];
    function scan(o){if(!o||typeof o!=='object')return;if(typeof o.desc==='string')out.notes.push({id:o.id||o.note_id,title:o.title||o.name,desc:o.desc,nickname:o.user?.nickname,time:o.time,timestamp:o.timestamp,last_update_time:o.last_update_time,type:o.type});else for(const v of Object.values(o))scan(v);}
    scan(j.data);
   }
   window.__rolecards_api_cache[key]=out;return out;
  }catch(e){window.__rolecards_api_stopped=true;return {error:String(e),call_n:window.__rolecards_api_n};}
 };
 return JSON.stringify({installed:true,call_n:window.__rolecards_api_n||0,remaining_max_requests:10-(window.__rolecards_api_n||0)});
})()
