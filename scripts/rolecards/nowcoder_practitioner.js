/* Read-only, canonical source adapter for an already-opened public detail.
 * Uses observed SSR contentData, never user IDs, avatars, or profile fields.
 */
(()=>{let c=window.__INITIAL_STATE__?.prefetchData?.[2]?.ssrCommonData?.contentData;
if(!c)return JSON.stringify({url:location.href,status:'missing_ssr_body'});
let el=document.createElement('div');el.innerHTML=c.content||c.richText||'';
return JSON.stringify({url:location.href,title:c.title||'',nickname:c.userBrief?.nickname||'',date:new Date(c.createTime||c.createdAt||c.showTime).toLocaleDateString('en-CA',{timeZone:'Asia/Shanghai'}),accessed_at:new Date().toISOString(),desc:(el.innerText||el.textContent||'').replace(/(?<!\d)1[3-9]\d{9}(?!\d)|[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}/g,'[已移除联系方式]'),status:'full_body',method:'web-access Chrome CDP public detail SSR'});})();
