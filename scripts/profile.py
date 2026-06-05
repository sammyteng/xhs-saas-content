#!/usr/bin/env python3
"""
风格偏好记忆：记住首次选定的 文章风格 / 图片风格 / 生图参数 / 作者信息，
二次运行自动复用，省去重复选择。想改时覆盖保存即可。

存储位置：默认 ~/.config/xhs-saas-content/profile.json
         可用环境变量 XHS_PROFILE 指定别的路径（便于跨设备/多账号各存一份）。

用法：
  python3 profile.py show
  python3 profile.py set --article-style A --image-style 1 \
      --provider gemini --model pro --aspect 9:16 --author "AI内容观察" --ip 上海
  python3 profile.py reset        # 清空偏好（重新进入首次选择）
  python3 profile.py path
"""
import os, sys, json, argparse, datetime

def profile_path():
    p = os.environ.get("XHS_PROFILE")
    if p:
        return os.path.abspath(os.path.expanduser(p))
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "xhs-saas-content", "profile.json")

def load():
    p = profile_path()
    if os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save(d):
    p = profile_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    return p

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show"); sub.add_parser("path"); sub.add_parser("reset")
    s = sub.add_parser("set")
    s.add_argument("--article-style"); s.add_argument("--image-style")
    s.add_argument("--provider"); s.add_argument("--model"); s.add_argument("--aspect")
    s.add_argument("--author"); s.add_argument("--ip")
    a = ap.parse_args()

    if a.cmd == "path":
        print(profile_path()); return
    if a.cmd == "show":
        d = load()
        if not d:
            print("（未配置：首次运行，选完风格后用  profile.py set  保存即可）")
        else:
            print(json.dumps(d, ensure_ascii=False, indent=2))
        return
    if a.cmd == "reset":
        p = save({}); print("已清空偏好：", p); return
    if a.cmd == "set":
        d = load(); gen = d.get("gen", {})
        for k, v in {"article_style": a.article_style, "image_style": a.image_style,
                     "author": a.author, "ip": a.ip}.items():
            if v is not None: d[k] = v
        for k, v in {"provider": a.provider, "model": a.model, "aspect": a.aspect}.items():
            if v is not None: gen[k] = v
        if gen: d["gen"] = gen
        d["saved_at"] = datetime.date.today().isoformat()
        p = save(d)
        print("已保存偏好：", p)
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return

if __name__ == "__main__":
    main()
