#!/usr/bin/env python3
"""
反同质化引擎：跨多篇内容轮换"创意维度"，并用历史账本查重，避免每篇撞车。
品牌层(作者/IP/语气) 由 profile.py 锁定保持账号一致；
创意层(角度/风格/结构/钩子/配图/标题) 由本脚本每篇轮换。

历史账本：默认 ~/.config/xhs-saas-content/history.json（可用 XHS_HISTORY 改路径，按账号各存一份）。

用法：
  python3 diversity.py pick                                   # 给本篇分配一组"不撞最近"的维度（读 profile 的 style_pool 限制）
  python3 diversity.py check --combo '{...}'                  # 检查某组合是否与最近撞车（≥3 维相同即撞）
  python3 diversity.py record --combo '{...}' --title "标题"  # 生成后记账，供下篇查重
  python3 diversity.py show [--n 8]                           # 看最近 N 篇的维度
  python3 diversity.py path
"""
import os, sys, json, argparse, random, datetime

DIMS = {
    "angle":         ["痛点", "数据实证", "横向对比", "真实故事", "反对观点", "教程拆解", "场景代入", "人群细分"],
    "article_style": ["A", "B", "C", "D", "E", "F", "G", "H"],
    "structure":     ["清单体", "故事体", "对比体", "QA体", "吐槽体", "总分体"],
    "hook_type":     ["场景切入", "数字冲击", "反常识断言", "直接提问", "自嘲自黑", "对话体", "悬念前置", "金句开场"],
    "image_style":   ["写实", "扁平", "HTML卡片", "截图标注", "手绘插画"],
    "title_pattern": ["情绪词+设问", "数字清单", "身份背书", "痛点+利益", "反差对比", "疑问句", "祈使句"],
}
CLASH_DIMS = 3   # 与某一篇历史 ≥3 维相同 = 撞车
WINDOW = 6       # 查重只看最近几篇

def hist_path():
    p = os.environ.get("XHS_HISTORY")
    if p:
        return os.path.abspath(os.path.expanduser(p))
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "xhs-saas-content", "history.json")

def load_hist():
    p = hist_path()
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            return []
    return []

def save_hist(h):
    p = hist_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(h, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return p

def load_profile():
    pp = os.environ.get("XHS_PROFILE")
    if not pp:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
        pp = os.path.join(base, "xhs-saas-content", "profile.json")
    if os.path.exists(pp):
        try:
            return json.load(open(pp, encoding="utf-8"))
        except Exception:
            return {}
    return {}

def profile_style_pool():
    sp = load_profile().get("style_pool")
    if isinstance(sp, str):
        sp = [x.strip() for x in sp.split(",") if x.strip()]
    return sp or None

def cfg_int(cli, env, key, default):
    """优先级：命令行参数 > 环境变量 > profile > 默认值"""
    if cli is not None:
        return int(cli)
    e = os.environ.get(env)
    if e:
        try: return int(e)
        except ValueError: pass
    pv = load_profile().get(key)
    if pv is not None:
        try: return int(pv)
        except (ValueError, TypeError): pass
    return default

def recent_values(hist, dim):
    vals = []
    for e in reversed(hist):
        v = e.get(dim)
        if v is not None:
            vals.append(v)
    return vals  # most-recent-first

def pick(hist):
    pool_styles = profile_style_pool()
    combo = {}
    for dim, options in DIMS.items():
        opts = list(options)
        if dim == "article_style" and pool_styles:
            filt = [o for o in opts if o in pool_styles]
            if filt:
                opts = filt
        used = recent_values(hist, dim)
        # 选"最久没用过/从没用过"的：never-used 视为最佳
        def lru(o):
            return used.index(o) if o in used else 10 ** 6
        best = max(lru(o) for o in opts)
        cands = [o for o in opts if lru(o) == best]
        combo[dim] = random.choice(cands)
    return combo

def check(hist, combo, clash_dims=CLASH_DIMS, window=WINDOW):
    clashes = []
    for e in hist[-window:]:
        same = [d for d in DIMS if e.get(d) and e.get(d) == combo.get(d)]
        if len(same) >= clash_dims:
            clashes.append({"title": e.get("title", ""), "date": e.get("date", ""), "same": same})
    return {"ok": len(clashes) == 0, "clashes": clashes}

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pick"); sub.add_parser("path")
    sp = sub.add_parser("show"); sp.add_argument("--n", type=int, default=8)
    ck = sub.add_parser("check"); ck.add_argument("--combo", required=True)
    ck.add_argument("--clash-dims"); ck.add_argument("--window")
    sub.add_parser("config")
    rc = sub.add_parser("record"); rc.add_argument("--combo", required=True); rc.add_argument("--title", default="")
    a = ap.parse_args()
    hist = load_hist()

    if a.cmd == "path":
        print(hist_path()); return
    if a.cmd == "pick":
        print(json.dumps(pick(hist), ensure_ascii=False)); return
    if a.cmd == "show":
        if not hist:
            print("（历史为空：还没记过账）"); return
        for e in hist[-a.n:]:
            print(json.dumps(e, ensure_ascii=False))
        return
    if a.cmd == "config":
        print(json.dumps({"clash_dims": cfg_int(None, "XHS_CLASH_DIMS", "clash_dims", CLASH_DIMS),
                          "window": cfg_int(None, "XHS_WINDOW", "window", WINDOW)}, ensure_ascii=False)); return
    if a.cmd == "check":
        cd = cfg_int(a.clash_dims, "XHS_CLASH_DIMS", "clash_dims", CLASH_DIMS)
        wn = cfg_int(a.window, "XHS_WINDOW", "window", WINDOW)
        print(json.dumps(check(hist, json.loads(a.combo), cd, wn), ensure_ascii=False)); return
    if a.cmd == "record":
        combo = json.loads(a.combo)
        combo["title"] = a.title
        combo["date"] = datetime.date.today().isoformat()
        hist.append(combo)
        p = save_hist(hist)
        print("已记账：", p)
        print(json.dumps(combo, ensure_ascii=False))
        return

if __name__ == "__main__":
    main()
