#!/usr/bin/env python3
"""
给图片右下角打 "AI生成" 小字水印（80% 不透明度）。
依赖：pip install pillow

用法：
  # 给目录下所有 png/jpg 打水印
  python3 watermark.py --dir /path/to/images
  # 或指定具体文件
  python3 watermark.py --file a.png --file b.png
  # 自定义水印文字
  python3 watermark.py --dir ./imgs --text "AI生成"

说明：
  - 首次处理会把原图备份到 <dir>/orig/，之后每次都从干净原图重新打，避免叠加。
  - 字体自动探测常见 CJK 字体；可用 --font 指定。
"""
import os, glob, argparse
from PIL import Image, ImageDraw, ImageFont

# 常见 CJK 字体候选（macOS / Linux / Windows）
FONT_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
]

def find_font():
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    return None

def stamp(path, text, font_path, orig_dir):
    os.makedirs(orig_dir, exist_ok=True)
    name = os.path.basename(path)
    bak = os.path.join(orig_dir, name)
    if not os.path.exists(bak):
        Image.open(path).save(bak)

    im = Image.open(bak).convert("RGBA")  # 始终从干净原图开始
    W, H = im.size
    fs = max(20, int(W / 46))
    try:
        font = ImageFont.truetype(font_path, fs) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = int(W / 55)
    x = W - tw - pad * 2
    y = H - th - pad * 2
    # 浅色深底胶囊，提升可读性
    d.rounded_rectangle(
        [x - pad * 0.7, y - pad * 0.6, x + tw + pad * 0.7, y + th + pad * 0.9],
        radius=int(fs * 0.5), fill=(0, 0, 0, 90),
    )
    # 80% 不透明度白字
    d.text((x, y - bbox[1]), text, font=font, fill=(255, 255, 255, 204))
    out = Image.alpha_composite(im, overlay).convert("RGB")
    out.save(path)
    print("stamped", name, im.size, "fs", fs)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", help="图片目录（处理其中所有 png/jpg/jpeg）")
    ap.add_argument("--file", action="append", default=[], help="指定单个文件，可多次")
    ap.add_argument("--text", default="AI生成")
    ap.add_argument("--font", default=None, help="字体文件路径，留空自动探测")
    args = ap.parse_args()

    font_path = args.font or find_font()
    if not font_path:
        print("WARN: 未找到 CJK 字体，将用默认字体（可能不显示中文）")

    files = list(args.file)
    if args.dir:
        for ext in ("png", "jpg", "jpeg", "PNG", "JPG"):
            files += glob.glob(os.path.join(args.dir, f"*.{ext}"))
    files = sorted(set(os.path.abspath(f) for f in files))
    if not files:
        print("ERROR: 没有要处理的图片，请用 --dir 或 --file 指定", )
        return

    # orig 备份目录放在第一张图所在目录下
    base_dir = os.path.dirname(files[0])
    orig_dir = os.path.join(base_dir, "orig")
    for f in files:
        if os.path.basename(os.path.dirname(f)) == "orig":
            continue  # 跳过备份目录自身
        stamp(f, args.text, font_path, orig_dir)
    print("done")

if __name__ == "__main__":
    main()
