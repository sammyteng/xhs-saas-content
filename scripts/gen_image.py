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
from __future__ import annotations

import os, sys, argparse, base64, time, urllib.request, urllib.error, json

# ---- 模型别名（截至 2026-06，API 可用的最新版）----
GEMINI_MODELS = {
    "flash": "gemini-2.5-flash-image",   # 快、便宜
    "pro": "gemini-3-pro-image",         # Nano Banana Pro，质量最高、中文最准（默认）
    "preview": "gemini-3-pro-image-preview",
}
OPENAI_DEFAULT = "gpt-image-1.5"         # 当前默认；可换 gpt-image-2 / gpt-image-1-mini
# OpenAI 默认模型支持环境变量覆盖（缺省回退到上面的默认值）
OPENAI_MODEL = os.environ.get("OPENAI_IMAGE_MODEL", OPENAI_DEFAULT)
ARK_DEFAULT = "doubao-seedream-4-0-250828"   # Seedream 4.0（支持 4K、多图参考）
DASHSCOPE_DEFAULT = "wan2.2-t2i-plus"    # 通义万相 2.2（ImageSynthesis 同步/异步均支持）

# ---- 网络超时（秒） ----
HTTP_DOWNLOAD_TIMEOUT = 60     # save_url 下载图片
OPENAI_CLIENT_TIMEOUT = 120    # OpenAI / ARK client
DASHSCOPE_TIMEOUT = 120        # DashScope ImageSynthesis 调用

# ---- 网络异常统一重试包装 ----
def _is_retryable_error(e: Exception) -> bool:
    """判定异常是否可重试：连接/读超时、5xx、429 可重试；4xx（含安全过滤）等不可重试。"""
    # 连接 / 读取超时类
    if isinstance(e, (TimeoutError, urllib.error.URLError)):
        # URLError 含 socket.timeout / 连接拒绝等，均视为可重试
        if isinstance(e, urllib.error.HTTPError):
            return e.code == 429 or 500 <= e.code < 600
        return True
    # HTTPError 直接命中
    if isinstance(e, urllib.error.HTTPError):
        return e.code == 429 or 500 <= e.code < 600
    # 第三方 SDK 异常：靠 status_code / 文本特征判断
    status = getattr(e, "status_code", None) or getattr(e, "status", None) or getattr(e, "code", None)
    if isinstance(status, int):
        return status == 429 or 500 <= status < 600
    text = str(e).lower()
    if any(s in text for s in ("timed out", "timeout", "connection", "temporarily", "503", "502", "504", "429")):
        return True
    # 安全过滤 / 4xx 等不可重试
    return False

def with_retries(fn, *, what: str, attempts: int = 3):
    """统一网络重试：最多 attempts 次，指数退避；不可重试错误立即抛出。

    attempts=3 即首次 + 2 次重试，退避 1s / 2s。
    """
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 — 由 _is_retryable_error 精细分流
            last = e
            if i == attempts - 1 or not _is_retryable_error(e):
                raise
            delay = 2 ** i
            print(f"[retry] {what} 第 {i + 1} 次失败（{e}），{delay}s 后重试", file=sys.stderr)
            time.sleep(delay)
    raise last  # 理论不可达

# ---- cover-bridge.json 路径（相对于本脚本） ----
BRIDGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "styles", "cover-bridge.json")

# ---- 设计 Token → 提示词注入 ----
def load_design_token(token_path):
    """读取 design-token.json，返回 designToken 字典（或 None）。"""
    if not token_path or not os.path.exists(token_path):
        return None
    with open(token_path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("designToken", data)  # 兼容顶层即 designToken 的情况

def load_bridge():
    """加载 cover-bridge.json 映射表。"""
    if not os.path.exists(BRIDGE_PATH):
        return None
    with open(BRIDGE_PATH, encoding="utf-8") as f:
        return json.load(f)

def apply_design_token_to_prompt(prompt, token, bridge):
    """根据 designToken + bridge 映射，给 prompt 追加色彩/风格提示词。

    返回 (new_prompt, extra_negative)：
      - new_prompt 只含【正向】增强（绝不把负向词拼进来）；
      - extra_negative 是独立的负向字符串，交由调用方按 provider 分流处理。
    """
    if not token or not bridge:
        return prompt, ""

    bg_tone = token.get("bgTone", "light")
    primary_color = token.get("primaryColor", "")
    mappings = bridge.get("bgTone_mappings", {})
    mapping = mappings.get(bg_tone)
    # 修4：未知 bgTone 不再静默丢弃 —— 打 WARN 并回退 light 档（.get 安全取，避免 KeyError）
    if mapping is None:
        print(
            f"[design-token] WARN: 未知 bgTone='{bg_tone}'，cover-bridge.json 无对应映射，已回退到 light 档",
            file=sys.stderr,
        )
        mapping = mappings.get("light")

    extra_positive = ""
    if mapping:
        color_hint = mapping.get("prompt_color_hint", "").replace("{primaryColor}", primary_color)
        style_hint = mapping.get("prompt_style_hint", "")
        extra_positive = f"{color_hint}, {style_hint}".strip(", ")

    extra_negative = ""
    neg_hints = token.get("negativePromptHints")
    if isinstance(neg_hints, list):
        extra_negative = ", ".join(neg_hints)
    elif isinstance(neg_hints, str) and neg_hints:
        extra_negative = neg_hints

    # 修1：仅拼接【正向】增强，负向词独立返回，不得混入正向 prompt
    if extra_positive:
        prompt = f"{prompt}\n{extra_positive}"

    return prompt, extra_negative

def merge_negative_into_prompt(prompt, negative):
    """给无原生负向能力的 provider（gemini/openai）用：把负向词以明确否定句式并入正向 prompt 末尾。

    不裸拼名词，而是用英文否定句式（avoid: ..., no ...）显式表达「不要什么」。
    """
    neg = (negative or "").strip().strip(",").strip()
    if not neg:
        return prompt
    return f"{prompt}\nAvoid the following: {neg}. No {neg}."

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
    # 修2：下载加超时 + 网络异常重试，避免无限挂起
    data = with_retries(
        lambda: urllib.request.urlopen(url, timeout=HTTP_DOWNLOAD_TIMEOUT).read(),
        what="下载生成图片",
    )
    save_bytes(out, data)

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

    # gemini 无原生 negative_prompt，将负向词以否定句式并入正向 prompt
    prompt_text = merge_negative_into_prompt(args.prompt, getattr(args, "negative", ""))
    parts = [prompt_text]
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
        resp = with_retries(lambda: call(img_cfg), what="Gemini 生图")
    except Exception:
        # 回退到无 size 的最小配置，同样带超时重试
        resp = with_retries(
            lambda: call(types.ImageConfig(aspect_ratio=args.aspect)),
            what="Gemini 生图(回退配置)",
        )

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
    kwargs = {"api_key": key, "timeout": OPENAI_CLIENT_TIMEOUT}
    if args.base_url:
        kwargs["base_url"] = args.base_url
    client = OpenAI(**kwargs)
    # 修3：默认模型支持 OPENAI_IMAGE_MODEL 覆盖，缺省回退到 OPENAI_DEFAULT
    model_id = args.model or OPENAI_MODEL
    # openai 无原生 negative_prompt，将负向词以否定句式并入正向 prompt
    prompt_text = merge_negative_into_prompt(args.prompt, getattr(args, "negative", ""))
    size = aspect_to_size("openai", args.aspect)
    try:
        resp = with_retries(
            lambda: client.images.generate(model=model_id, prompt=prompt_text, size=size, n=1),
            what="OpenAI 生图",
        )
    except Exception as e:
        # 修3：模型不可用 / 400 类错误给中文提示
        status = getattr(e, "status_code", None) or getattr(e, "status", None)
        text = str(e).lower()
        model_err = "model" in text and ("not" in text or "exist" in text or "invalid" in text)
        if status == 400 or model_err:
            sys.exit(
                f"ERROR: OpenAI 模型 '{model_id}' 不可用或不存在。"
                "建议用 --model 指定可用模型、改用其他 provider（gemini/ark/dashscope），"
                f"或退回 HTML 兜底（shot.py）。原始报错：{e}"
            )
        raise
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
    client = Ark(api_key=key, timeout=OPENAI_CLIENT_TIMEOUT)
    model_id = args.model or ARK_DEFAULT
    size = aspect_to_size("ark", args.aspect)
    negative = (getattr(args, "negative", "") or "").strip().strip(",").strip()

    def _call(with_negative: bool):
        gen_kwargs = {"model": model_id, "prompt": args.prompt, "size": size, "response_format": "url"}
        if with_negative and negative:
            gen_kwargs["negative_prompt"] = negative  # Seedream 若 SDK 支持则原生传入
        return client.images.generate(**gen_kwargs)

    try:
        resp = with_retries(lambda: _call(with_negative=True), what="ARK/Seedream 生图")
    except TypeError:
        # SDK 不接受 negative_prompt 参数，回退到无负向调用
        resp = with_retries(lambda: _call(with_negative=False), what="ARK/Seedream 生图(无负向)")
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
    negative = (getattr(args, "negative", "") or "").strip().strip(",").strip()

    call_kwargs = {"api_key": key, "model": model_id, "prompt": args.prompt, "n": 1, "size": size}
    if negative:
        call_kwargs["negative_prompt"] = negative  # DashScope 原生支持负向提示词
    # 修2：网络调用加超时 + 重试（部分 SDK 版本支持 read_timeout/connect_timeout）
    try:
        rsp = with_retries(
            lambda: ImageSynthesis.call(
                **call_kwargs, read_timeout=DASHSCOPE_TIMEOUT, connect_timeout=DASHSCOPE_TIMEOUT
            ),
            what="DashScope/通义万相 生图",
        )
    except TypeError:
        # 老版本 SDK 不接受 timeout 参数，回退到无显式超时调用（仍带重试）
        rsp = with_retries(
            lambda: ImageSynthesis.call(**call_kwargs),
            what="DashScope/通义万相 生图(无超时参数)",
        )
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
    ap.add_argument("--design-token", default=None,
                    help="封面 skill 导出的 design-token.json 路径（可选），提供时自动适配封面色彩风格")
    args = ap.parse_args()

    # ---- 若提供了 design token，注入色彩/风格提示词 ----
    args.negative = ""  # 负向提示词：默认空，由各 provider 按能力分流处理
    token = load_design_token(args.design_token)
    bridge = load_bridge() if token else None
    if token and bridge:
        # 修1：拿到独立的 negative，按 provider 分流（dashscope/ark 走原生 negative_prompt；
        #      gemini/openai 由各自函数以否定句式并入正向 prompt），不再丢弃
        args.prompt, args.negative = apply_design_token_to_prompt(args.prompt, token, bridge)
        msg = (
            f"[design-token] bgTone={token.get('bgTone')}, "
            f"primaryColor={token.get('primaryColor')} → 提示词已注入封面风格"
        )
        if args.negative:
            msg += f"；负向提示词={args.negative}"
        print(msg, file=sys.stderr)

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
