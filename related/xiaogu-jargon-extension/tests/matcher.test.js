// 匹配器单测：node --test tests/
const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const { compile, match } = require("../extension/matcher.js");

// 读 build.py 生成的 data.js，取出词条数组
const raw = fs.readFileSync(path.join(__dirname, "../extension/data.js"), "utf8");
const ENTRIES = JSON.parse(raw.slice(raw.indexOf("["), raw.lastIndexOf("]") + 1));
const P = compile(ENTRIES);
const terms = (text) => match(text, P).map((h) => ENTRIES[h.index].term);

test("长词优先：隔周双休不再单独命中双休", () => {
  assert.deepStrictEqual(terms("本岗位隔周双休"), ["隔周双休"]);
  assert.deepStrictEqual(terms("单双休，弹性工作"), ["隔周双休", "弹性工作"]);
});

test("否定跳过", () => {
  assert.deepStrictEqual(terms("非双休"), []);
  assert.deepStrictEqual(terms("没有团建"), []);
  // 小句边界外的否定不算
  assert.deepStrictEqual(terms("不出差，双休"), ["双休"]);
  // 词条自身含否定，照常命中
  assert.deepStrictEqual(terms("公司不打卡"), ["不打卡"]);
});

test("含否定字的常见复合词不算否定", () => {
  assert.deepStrictEqual(terms("提供非常有竞争力的薪酬"), ["有竞争力的薪酬"]);
  assert.deepStrictEqual(terms("需要不断拥抱变化"), ["拥抱变化"]);
  assert.deepStrictEqual(terms("不定期团建"), ["团建"]);
  assert.deepStrictEqual(terms("无责任底薪+提成"), ["底薪+高提成"]);
});

test("大小写与字符间空白", () => {
  assert.deepStrictEqual(terms("要有OWNER意识"), ["主人翁意识"]);
  assert.deepStrictEqual(terms("扁平 化管理"), ["扁平化管理"]);
});

test("位置互不重叠且升序", () => {
  const hits = match("14薪，五险一金按Base缴纳，带薪年假，扁平化管理", P);
  for (let i = 1; i < hits.length; i++) assert.ok(hits[i].start >= hits[i - 1].end);
  assert.ok(hits.length >= 3);
});
