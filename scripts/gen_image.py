#!/usr/bin/env python3
"""
自包含·多模型文生图脚本。支持 Gemini / OpenAI(GPT) / 豆包·即梦(Seedream) / 通义万相，
以及任意 OpenAI 兼容的第三方聚合端点。

用法（按 provider 选模型）：
  # Gemini（Nano Banana，默认，中文字渲染准）
  python3 gen_image.py --provider gemini --model pro --prompt "..." --out cover.png --aspect 9:16

  # OpenAI / GPT（gpt-image-1，默认）
  python3 gen_image.py --provider openai --prompt "..." --out cover.png --aspect 9:16

  # 豆包·即梦 / Seedream（火山引擎 ARK）
  python3 gen_image.py --provider ark --model doubao-seedream-3-0-t2i-250415 --prompt "..." --out cover.png --aspect 9:16

  # 通义万相（阿里 DashScope）
  python3 gen_image.py --provider dashscope --model wanx2.1-t2i-turbo --prompt "..." --out cover.png --aspect 9:16

  # 任意 OpenAI 兼容端点（如各类聚合站），用 --base-url + OPENAI_API_KEY
  python3 gen_image.py --provider openai --base-url https://your-proxy/v1 --model gpt-image-1 --prompt "..." --out cover.png

环境变量（按需，从环境读取，绝不写死）：
  gemini    -> GEMINI_API_KEY 或 GOOGLE_AI_API_KEY
  openai    -> OPENAI_API_KEY
  ark       -> ARK_API_KEY
  dashscope -> DASHSCOPE_API_KEY

依赖（按需安装对应一个即可）：
  gemini:    pip install google-genai
  openai:    pip install openai
  ark:       pip install 'volcengine-python-sdk[ark]'
  dashscope: pip install dashscope

各 provider 的模型别名见下方 MODELS。
"""
import os, sys, argparse, base64, urllib.request

# ---- 模型别名（截至 2026-06，API 可用的最新版）----
GEMINI_MODELS = {
    "flash": "gemini-2.5-flash-image",   # 快、便宜
    "pro": "gemini-3-pro-image",         # Nano Banana Pro，质量最高、中文最准（默认）
    "preview": "gemini-3-pro-image-preview",
}
OPENAI_DEFAULT = "gpt-image-1.5"         # 当前默认；可换 gpt-image-2 / gpt-image-1-mini
ARK_DEFAULT = "doubao-seedream-4-0-250828"   # Seedream 4.0（支持 4K、多图参考）
DASHSCOPE_DEFAULT = "wan2.2-t2i-plus"    # 通义万相 2.2（ImageSynthesis 同步/异步均支持）

# ---- aspect -> 各家支持的 size 字符串 ----
def aspect_to_size(provider, aspect):
    # 归一
    a = aspect.replace("：", ":").strip()
    if provider == "openai":  # gpt-image-1 仅支持这三种
        return {"9:16": "1024x1536", "4:5": "1024x1536", "3:4": "1024x1536",
                "1:1": "1024x1024", "16:9": "1536x1024", "4:3": "1536x1024"}.get(a, "1024x1536")
    if provider == "ark":
        return {"9:16": "864x1536", "4:5": "1024x1280", "3:4": "1024x1280",
                "1:1": "1024x1024", "16:9": "1536x864", "4:3": "1280x1024"}.get(a, "864x1536")
    if provider == "dashscope":
        return {"9:16": "720*1280", "4:5": "1024*1280", "3:4": "1024*1280",
                "1:1": "1024*1024", "16:9": "1280*720", "4:3": "1280*1024"}.get(a, "720*1280")
    return a  # gemini 直接用 aspect_ratio

def save_bytes(out, data):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "wb") as f:
        f.write(data)

def save_url(out, url):
    save_bytes(out, urllib.request.urlopen(url).read())

# ---------------- Gemini ----------------
def gen_gemini(args):
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_AI_API_KEY")
    if not key:
        sys.exit("ERROR: 缺少 GEMINI_API_KEY / GOOGLE_AI_API_KEY")
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        sys.exit("ERROR: 缺依赖，请 `pip install google-genai`")
    client = genai.Client(api_key=key)
    model_id = GEMINI_MODELS.get(args.model, args.model or GEMINI_MODELS["pro"])

    parts = [args.prompt]
    for rp in args.ref:
        with open(rp, "rb") as f:
            data = f.read()
        ext = os.path.splitext(rp)[1].lstrip(".").lower()
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
        parts.append(types.Part.from_bytes(data=data, mime_type=mime))

    img_cfg = types.ImageConfig(aspect_ratio=args.aspect)
    try:
        img_cfg.image_size = args.size
    except Exception:
        pass

    def call(cfg):
        return client.models.generate_content(
            model=model_id, contents=parts,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"], image_config=cfg),
        )
    try:
        resp = call(img_cfg)
    except Exception:
        resp = call(types.ImageConfig(aspect_ratio=args.aspect))

    for part in resp.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            save_bytes(args.out, part.inline_data.data)
            return True
    return False

# ---------------- OpenAI / 兼容端点 ----------------
def gen_openai(args):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("ERROR: 缺少 OPENAI_API_KEY")
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("ERROR: 缺依赖，请 `pip install openai`")
    kwargs = {"api_key": key}
    if args.base_url:
        kwargs["base_url"] = args.base_url
    client = OpenAI(**kwargs)
    model_id = args.model or OPENAI_DEFAULT
    size = aspect_to_size("openai", args.aspect)
    resp = client.images.generate(model=model_id, prompt=args.prompt, size=size, n=1)
    d = resp.data[0]
    if getattr(d, "b64_json", None):
        save_bytes(args.out, base64.b64decode(d.b64_json))
        return True
    if getattr(d, "url", None):
        save_url(args.out, d.url)
        return True
    return False

# ---------------- 豆包·即梦 / Seedream (火山 ARK) ----------------
def gen_ark(args):
    key = os.environ.get("ARK_API_KEY")
    if not key:
        sys.exit("ERROR: 缺少 ARK_API_KEY")
    try:
        from volcenginesdkarkruntime import Ark
    except ImportError:
        sys.exit("ERROR: 缺依赖，请 `pip install 'volcengine-python-sdk[ark]'`")
    client = Ark(api_key=key)
    model_id = args.model or ARK_DEFAULT
    size = aspect_to_size("ark", args.aspect)
    resp = client.images.generate(model=model_id, prompt=args.prompt, size=size, response_format="url")
    d = resp.data[0]
    if getattr(d, "b64_json", None):
        save_bytes(args.out, base64.b64decode(d.b64_json))
        return True
    if getattr(d, "url", None):
        save_url(args.out, d.url)
        return True
    return False

# ---------------- 通义万相 (阿里 DashScope) ----------------
def gen_dashscope(args):
    key = os.environ.get("DASHSCOPE_API_KEY")
    if not key:
        sys.exit("ERROR: 缺少 DASHSCOPE_API_KEY")
    try:
        from dashscope import ImageSynthesis
    except ImportError:
        sys.exit("ERROR: 缺依赖，请 `pip install dashscope`")
    model_id = args.model or DASHSCOPE_DEFAULT
    size = aspect_to_size("dashscope", args.aspect)
    rsp = ImageSynthesis.call(api_key=key, model=model_id, prompt=args.prompt, n=1, size=size)
    if rsp.status_code != 200:
        sys.exit(f"ERROR: DashScope {rsp.status_code} {getattr(rsp,'message','')}")
    save_url(args.out, rsp.output.results[0].url)
    return True

DISPATCH = {
    "gemini": gen_gemini,
    "openai": gen_openai,
    "ark": gen_ark,          # 豆包/即梦/Seedream 同源
    "jimeng": gen_ark,       # 别名
    "doubao": gen_ark,       # 别名
    "dashscope": gen_dashscope,
    "wanx": gen_dashscope,   # 别名
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="gemini",
                    help="gemini | openai | ark(豆包/即梦) | dashscope(通义万相)")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=None, help="模型名/别名，留空用该 provider 默认")
    ap.add_argument("--aspect", default="9:16")
    ap.add_argument("--size", default="2K", help="仅 Gemini 部分模型支持")
    ap.add_argument("--base-url", default=None, help="OpenAI 兼容端点（聚合站/代理）")
    ap.add_argument("--ref", action="append", default=[], help="参考图（仅 Gemini），可多次")
    args = ap.parse_args()

    fn = DISPATCH.get(args.provider.lower())
    if not fn:
        sys.exit(f"ERROR: 未知 provider '{args.provider}'，可选：{', '.join(sorted(set(DISPATCH)))}")

    try:
        ok = fn(args)
    except SystemExit:
        raise
    except Exception as e:
        sys.exit(f"ERROR: 生图失败（{args.provider}）：{e}")

    if not ok:
        sys.exit("ERROR: 模型未返回图片（可能命中安全过滤，调整 prompt 重试）")
    print(args.out)

if __name__ == "__main__":
    main()
