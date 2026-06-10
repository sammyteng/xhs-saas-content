"""
debug_favorites.py — 找出收藏 tab 的 index 和数据路径
"""
import json
import sys
import time
sys.path.insert(0, "scripts")
from xhs.bridge import BridgePage

USER_ID = "68bef27a0000000019021712"

page = BridgePage()

# 先看首页 tab 结构
url = f"https://www.xiaohongshu.com/user/profile/{USER_ID}"
print(f"导航到主页: {url}")
page.navigate(url)
page.wait_for_load()
page.wait_dom_stable()
time.sleep(3)

# 获取 tab 列表
tabs_js = """
(() => {
    const s = window.__INITIAL_STATE__;
    if (!s || !s.user) return "no state";
    // 找 tabs 列表
    const pageData = s.user.userPageData;
    const pd = pageData && (pageData.value !== undefined ? pageData.value : pageData._value);
    if (pd && pd.tabList) return JSON.stringify(pd.tabList);
    // 备用: 从 DOM 找 tab 按钮
    return "no tabList in pageData";
})()
"""
tabs = page.evaluate(tabs_js)
print("tabList:", tabs)

# 获取 DOM 里的 tab 按钮文本
dom_tabs_js = """
(() => {
    const tabs = document.querySelectorAll('.tab-item, [class*="tab"] span, .user-tab');
    return JSON.stringify([...tabs].map(t => ({text: t.innerText?.trim(), class: t.className})).filter(t => t.text));
})()
"""
dom_tabs = page.evaluate(dom_tabs_js)
print("DOM tabs:", dom_tabs[:500] if dom_tabs else "none")

# 查 noteQueries 有多少 tab
nq_js = """
(() => {
    const s = window.__INITIAL_STATE__;
    const nq = s && s.user && s.user.noteQueries;
    const raw = nq && (nq.value !== undefined ? nq.value : nq._value || nq);
    return JSON.stringify(raw);
})()
"""
nq = page.evaluate(nq_js)
print("noteQueries:", nq[:300] if nq else "none")
