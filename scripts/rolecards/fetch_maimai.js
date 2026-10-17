// CDP单页读取适配器：先在研究tab设置window.__rolecards_maimai_url为已观察的公开article/detail URL。
// 不批量循环、不在后台tab使用计时器；每次cua调用之间由操作者限速>=3秒。
// cdp.mjs eval --body-file 此文件；只读，无Cookie，无自动重试。
(async()=>{
 const url=window.__rolecards_maimai_url;
 if(!url||!url.startsWith('https://maimai.cn/article/detail?'))return JSON.stringify({error:'allowed public URL required'});
 const r=await fetch(url,{credentials:'omit'});if(!r.ok)return JSON.stringify({url,error:'HTTP '+r.status});
 const d=new DOMParser().parseFromString(await r.text(),'text/html');const h=d.querySelector('h1');
 if(!h)return JSON.stringify({url,error:'article heading missing'});
 const text=h.parentElement.parentElement.children[1]?.textContent.split('声明：本文内容')[0].split('相关推荐')[0];
 if(!text)return JSON.stringify({url,error:'article body missing'});
 return JSON.stringify({url,title:h.textContent,author_nickname:h.parentElement.querySelector('.truncate')?.textContent,
 date_raw:h.parentElement.textContent.match(/(?:\d{2}-)?\d{2}-\d{2}/)?.[0],
 text:text.replace(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/g,'[email-redacted]').replace(/(?<!\d)1[3-9]\d{9}(?!\d)/g,'[phone-redacted]'),
 accessed_at:new Date().toISOString(),credentials:'omit'});
})()
