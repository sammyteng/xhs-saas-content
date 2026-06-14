#!/usr/bin/env python3
"""
把 HTML 卡片渲染成高清 PNG（用于 HTML 风格的图片：信息图、金句卡、封面等）。
依赖：pip install playwright && playwright install chromium

用法：
  # 截取整页（按 viewport 尺寸）
  python3 shot.py --html card.html --out cover.png --w 1080 --h 1350
  # 只截取某个元素（CSS 选择器）
  python3 shot.py --html cards.html --out img2.png --selector "#card2" --w 1080 --h 1350
  # 使用封面 design token 自动适配配色
  python3 shot.py --html card.html --out img.png --design-token design-token.json

说明：
  - device_scale_factor=2，输出 2 倍高清。
  - 小红书竖图常用 1080x1350（4:5）或 1080x1920（9:16）。
  - 提供 --design-token 时，自动注入封面配色的 CSS 自定义属性到 HTML，
    HTML 模板中用 var(--card-bg) 等即可自动适配。
"""
import argparse, os, json, sys
from playwright.sync_api import sync_playwright

# ---- cover-bridge.json 路径（相对于本脚本） ----
BRIDGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "styles", "cover-bridge.json")

def load_design_token(token_path):
    """读取 design-token.json，返回 designToken 字典（或 None）。"""
    if not token_path or not os.path.exists(token_path):
        return None
    with open(token_path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("designToken", data)

def load_bridge():
    """加载 cover-bridge.json 映射表。"""
    if not os.path.exists(BRIDGE_PATH):
        return None
    with open(BRIDGE_PATH, encoding="utf-8") as f:
        return json.load(f)

def build_css_overrides(token, bridge):
    """根据 designToken + bridge 映射，生成 CSS 自定义属性 <style> 块。"""
    if not token or not bridge:
        return ""

    bg_tone = token.get("bgTone", "light")
    primary_color = token.get("primaryColor", "")
    accent_color = token.get("accentColor", primary_color)
    font_vibe = token.get("fontVibe", "")

    tone_map = bridge.get("bgTone_mappings", {}).get(bg_tone)
    font_vibe_mappings = bridge.get("fontVibe_mappings", {})
    font_map = font_vibe_mappings.get(font_vibe)
    # token 提供了 fontVibe，但 bridge 里没有对应档 → 回退 bold-sans 并告警
    if font_vibe and not font_map:
        print(
            f"[design-token] WARN: 未知 fontVibe='{font_vibe}'，"
            f"已回退到 bold-sans 档",
            file=sys.stderr,
        )
        font_map = font_vibe_mappings.get("bold-sans")

    props = []
    if tone_map:
        card = tone_map.get("html_card", {})
        props.append(f"  --card-bg: {card.get('background', '#f5f3ee')};")
        props.append(f"  --card-text: {card.get('text_color', '#1d1d1f')};")
        # accent_from / label_color_from 指向 token 中的字段名
        accent_field = card.get("accent_from", "primaryColor")
        label_field = card.get("label_color_from", "primaryColor")
        if accent_field in token:
            accent_value = token[accent_field]
        else:
            print(
                f"[design-token] WARN: 间接寻址字段 accent_from='{accent_field}' "
                f"不在 token 中，已回退到 primaryColor",
                file=sys.stderr,
            )
            accent_value = primary_color
        if label_field in token:
            label_value = token[label_field]
        else:
            print(
                f"[design-token] WARN: 间接寻址字段 label_color_from='{label_field}' "
                f"不在 token 中，已回退到 primaryColor",
                file=sys.stderr,
            )
            label_value = primary_color
        props.append(f"  --card-accent: {accent_value};")
        props.append(f"  --card-label: {label_value};")

    if font_map:
        props.append(f"  --card-font-family: {font_map.get('html_font_family', '')};")
        props.append(f"  --card-title-weight: {font_map.get('html_title_weight', 800)};")
        props.append(f"  --card-title-size: {font_map.get('html_title_size', '84px')};")

    if not props:
        return ""

    return "<style>:root {\n" + "\n".join(props) + "\n}</style>"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True, help="本地 html 文件路径")
    ap.add_argument("--out", required=True)
    ap.add_argument("--selector", default=None, help="CSS 选择器，截取单个元素；留空截整页")
    ap.add_argument("--w", type=int, default=1080)
    ap.add_argument("--h", type=int, default=1350)
    ap.add_argument("--scale", type=int, default=2)
    ap.add_argument("--design-token", default=None,
                    help="封面 skill 导出的 design-token.json 路径（可选），提供时自动注入封面配色")
    args = ap.parse_args()

    url = "file://" + os.path.abspath(args.html)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    # ---- 若提供了 design token，构建 CSS 覆盖 ----
    css_override = ""
    token = load_design_token(args.design_token)
    bridge = load_bridge() if token else None
    if token and bridge:
        css_override = build_css_overrides(token, bridge)
        if css_override:
            print(f"[design-token] bgTone={token.get('bgTone')}, fontVibe={token.get('fontVibe')} → CSS 自定义属性已注入", file=sys.stderr)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": args.w, "height": args.h},
            device_scale_factor=args.scale,
        )
        page.goto(url)
        # 注入 CSS 自定义属性（在 <head> 尾部追加 <style> 块）
        if css_override:
            page.evaluate(f"document.head.insertAdjacentHTML('beforeend', {json.dumps(css_override)})")
        page.wait_for_timeout(400)  # 等字体/图片加载
        if args.selector:
            page.locator(args.selector).screenshot(path=args.out)
        else:
            page.screenshot(path=args.out)
        browser.close()
    print(args.out)

if __name__ == "__main__":
    main()

