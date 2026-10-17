// 工具栏图标：招聘站上切换开关；其他站点按需注入一次（activeTab 授权，不常驻全网）。
// content.js 自带防重入：已注入时再次执行只会切换开关。
chrome.action.onClicked.addListener(async (tab) => {
  if (!tab.id) return;
  try {
    await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ["data.js", "matcher.js", "content.js"] });
  } catch (err) {
    // chrome:// 页、应用商店等受限页面无法注入，忽略即可
    console.warn("小谷黑话：此页面不允许注入", err);
  }
});
