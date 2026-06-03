#!/usr/bin/env python3
"""
把 HTML 卡片渲染成高清 PNG（用于 HTML 风格的图片：信息图、金句卡、封面等）。
依赖：pip install playwright && playwright install chromium

用法：
  # 截取整页（按 viewport 尺寸）
  python3 shot.py --html card.html --out cover.png --w 1080 --h 1350
  # 只截取某个元素（CSS 选择器）
  python3 shot.py --html cards.html --out img2.png --selector "#card2" --w 1080 --h 1350

说明：
  - device_scale_factor=2，输出 2 倍高清。
  - 小红书竖图常用 1080x1350（4:5）或 1080x1920（9:16）。
"""
import argparse, os
from playwright.sync_api import sync_playwright

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True, help="本地 html 文件路径")
    ap.add_argument("--out", required=True)
    ap.add_argument("--selector", default=None, help="CSS 选择器，截取单个元素；留空截整页")
    ap.add_argument("--w", type=int, default=1080)
    ap.add_argument("--h", type=int, default=1350)
    ap.add_argument("--scale", type=int, default=2)
    args = ap.parse_args()

    url = "file://" + os.path.abspath(args.html)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": args.w, "height": args.h},
            device_scale_factor=args.scale,
        )
        page.goto(url)
        page.wait_for_timeout(400)  # 等字体/图片加载
        if args.selector:
            page.locator(args.selector).screenshot(path=args.out)
        else:
            page.screenshot(path=args.out)
        browser.close()
    print(args.out)

if __name__ == "__main__":
    main()
