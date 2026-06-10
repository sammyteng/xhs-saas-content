"""
fetch_favorites.py — 抓取当前登录用户的小红书收藏夹笔记列表
输出: JSON，字段包含 id / xsecToken / title / user / likedCount / cover
用法: uv run python scripts/fetch_favorites.py [--max N]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time

from xhs.bridge import BridgePage

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("fetch-favorites")

_WAIT_INITIAL_STATE_JS = "window.__INITIAL_STATE__ !== undefined"

# 收藏 tab 在 [笔记, 收藏, 点赞] 中的索引
COLLECT_TAB_INDEX = 1

_EXTRACT_MY_USER_ID_JS = """
(() => {
    const s = window.__INITIAL_STATE__;
    if (!s) return "";
    const me = s.user && s.user.userInfo;
    if (!me) return "";
    const info = me.value !== undefined ? me.value : (me._value !== undefined ? me._value : me);
    return info ? JSON.stringify(info) : "";
})()
"""

_EXTRACT_COLLECT_NOTES_JS = f"""
(() => {{
    const s = window.__INITIAL_STATE__;
    if (!s || !s.user || !s.user.notes) return "";
    // notes 是一个按 tab 索引分组的二维数组
    const notesRaw = s.user.notes;
    const notes = notesRaw.value !== undefined ? notesRaw.value : (notesRaw._value !== undefined ? notesRaw._value : notesRaw);
    if (!Array.isArray(notes)) return "";
    // 收藏 tab 数据在 index={COLLECT_TAB_INDEX}
    const collectNotes = notes[{COLLECT_TAB_INDEX}];
    return JSON.stringify(collectNotes || []);
}})()
"""


def wait_state(page: BridgePage, timeout: float = 12.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if page.evaluate(_WAIT_INITIAL_STATE_JS):
            return
        time.sleep(0.5)
    logger.warning("等待 __INITIAL_STATE__ 超时")


def get_my_user_id(page: BridgePage) -> str | None:
    page.navigate("https://www.xiaohongshu.com")
    page.wait_for_load()
    page.wait_dom_stable()
    wait_state(page)
    raw = page.evaluate(_EXTRACT_MY_USER_ID_JS)
    if not raw:
        return None
    info = json.loads(raw)
    return info.get("userId") or info.get("user_id")


def get_collect_feeds(page: BridgePage, user_id: str) -> list[dict]:
    url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
    logger.info("导航到用户主页: %s", url)
    page.navigate(url)
    page.wait_for_load()
    page.wait_dom_stable()
    wait_state(page)
    time.sleep(2)

    # 点击「收藏」tab
    logger.info("点击收藏 tab...")
    click_tab_js = f"""
    (() => {{
        // 找到所有顶部 tab 按钮
        const tabs = document.querySelectorAll('.user-page-tabs .tab-item, [class*="tabs"] span');
        const allTabs = [...document.querySelectorAll('span')].filter(
            el => ['笔记','收藏','点赞'].includes(el.innerText?.trim())
        );
        if (allTabs.length >= 2) {{
            allTabs[{COLLECT_TAB_INDEX}].click();
            return "clicked: " + allTabs[{COLLECT_TAB_INDEX}].innerText;
        }}
        return "not found, tabs=" + allTabs.map(t => t.innerText).join(',');
    }})()
    """
    result = page.evaluate(click_tab_js)
    logger.info("Tab click result: %s", result)
    time.sleep(3)  # 等待数据加载

    # 读收藏数据
    raw = page.evaluate(_EXTRACT_COLLECT_NOTES_JS)
    if not raw:
        logger.warning("收藏数据为空")
        return []

    feeds_raw = json.loads(raw)
    return [_normalize_feed(f) for f in feeds_raw if isinstance(f, dict)]


def _normalize_feed(f: dict) -> dict:
    note_card = f.get("noteCard") or f
    interact = note_card.get("interactInfo") or {}
    user = note_card.get("user") or f.get("user") or {}
    cover_info = note_card.get("cover") or {}
    cover_url = (
        cover_info.get("urlDefault")
        or cover_info.get("url")
        or cover_info.get("urlPre")
        or ""
    )
    return {
        "id": f.get("id") or note_card.get("noteId") or "",
        "xsecToken": f.get("xsecToken") or "",
        "title": note_card.get("title") or note_card.get("displayTitle") or "",
        "desc": note_card.get("desc") or "",
        "type": note_card.get("type") or f.get("type") or "",
        "user": {
            "userId": user.get("userId") or user.get("user_id") or "",
            "nickname": user.get("nickname") or user.get("nickName") or "",
        },
        "likedCount": interact.get("likedCount") or "",
        "collectedCount": interact.get("collectedCount") or "",
        "commentCount": interact.get("commentCount") or "",
        "cover": cover_url,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="抓取小红书收藏夹")
    parser.add_argument("--max", type=int, default=200, help="最多抓多少条（默认200）")
    parser.add_argument("--bridge-url", default="ws://localhost:9333")
    args = parser.parse_args()

    logger.info("连接 Bridge: %s", args.bridge_url)
    page = BridgePage(args.bridge_url)

    user_id = get_my_user_id(page)
    if not user_id:
        logger.error("无法获取当前用户 ID，请确保已登录")
        sys.exit(1)
    logger.info("当前用户 ID: %s", user_id)

    feeds = get_collect_feeds(page, user_id)
    feeds = feeds[: args.max]
    logger.info("共抓到 %d 条收藏", len(feeds))

    result = {"user_id": user_id, "total": len(feeds), "feeds": feeds}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
