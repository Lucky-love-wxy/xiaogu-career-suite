#!/usr/bin/env python3
"""身份分类少量定向取证。复用collect.py抓取与停站规则；每主机≤1招聘详情，Cookie禁用。"""
import pathlib,json,urllib.parse,urllib.robotparser,re
source=pathlib.Path(__file__).with_name('collect.py').read_text()
exec(source.split("mode=sys.argv[1]")[0])
original_out=OUT
identity=OUT/'identity';identity.mkdir(exist_ok=True)
pages=[
('grain','https://lswz.gov.cn/html/ywpd/rsrc/2025-03/24/content_287453.shtml','detail'),
('beijing','https://rsj.beijing.gov.cn/xxgk/gkzp/202512/t20251219_4350794.html','detail'),
('nanjing','https://njna.nanjing.gov.cn/xwzx/tzgg/202507/t20250718_5611229.html','detail'),
('civilnotice','https://www.12371.gov.cn/web/article/1438686605370654720/web/content_1438686605370654720.html','detail'),
('civillaw','https://www.samr.gov.cn/zw/zfxxgk/fdzdgknr/bgt/art/2023/art_6af2e9cf52224593b4dc15258bb34860.html','law'),
('publiclaw','https://www.mohrss.gov.cn/SYrlzyhshbzb/fwyd/SYkaoshizhaopin/zyhgjjgsydwgkzp/xgzc/201711/t20171110_281424.html','law'),
('sasaclaw','https://wap.sasac.gov.cn/n2588035/n2588320/n2588335/c20234181/content.html','policy'),
('soejob','https://wap.sasac.gov.cn/n2588035/n2588325/c35441351/content.html','detail'),
('publiclawgov','https://www.gov.cn/zhengce/2014-05/15/content_2680034.htm','law'),
('laborlaw','https://www.samr.gov.cn/zw/zfxxgk/fdzdgknr/bgt/art/2023/art_0abfdd261c03417b949df19d869add8d.html','law'),
('soeofficial','https://www.sasac.gov.cn/n2588035/n2588325/c35441351/content.html','detail'),
('soepolicy','https://www.sasac.gov.cn/n2588035/n2588320/n2588335/c20234181/content.html','policy'),
('huaibei','https://gzw.huaibei.gov.cn/zwzx/tzgg/57995144.html','detail'),
('baotoupolicy','https://baotou.gov.cn/zfxxgk/zc/zc_xzgfxwj/zfjqbm/sgyzcjdglwyh/202510/t20251004_663913.html','policy')]
results=[]
for ident,url,kind in pages:
 OUT=original_out
 host=urllib.parse.urlsplit(url);robot=fetch(f'{host.scheme}://{host.netloc}/robots.txt','robots')
 raw=pathlib.Path(ROOT/robot['path']/'raw.txt').read_text() if 'path' in robot and (ROOT/robot['path']/'raw.txt').exists() else ''
 valid=robot.get('status')==200 and bool(re.search(r'^\s*User-agent\s*:',raw,re.I|re.M))
 rp=urllib.robotparser.RobotFileParser();rp.parse(raw.splitlines());allowed=rp.can_fetch(UA,url) if valid else None
 OUT=identity
 page={'url':url,'status':'robots_disallowed'} if allowed is False else fetch(url,kind)
 results.append({'id':ident,'url':url,'kind':kind,'robot':robot,'robot_valid':valid,'allowed':allowed,'page':page})
(identity/'fetch-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
