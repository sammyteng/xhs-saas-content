#!/usr/bin/env python3
"""
小红书模拟器本地后端。启动后用浏览器打开，编辑版即可：
  - 单图重生成（调 gen_image.py）
  - 上传换图
  - （可选）「确认内容」→ 保存 content.confirmed.json + 自动生成分享版；自动化场景可跳过确认直接使用 content.json

用法：
  python3 scripts/serve.py <输出目录> [--port 8000]
  # 然后浏览器打开 http://127.0.0.1:8000/小红书模拟器.html

依赖：标准库即可；生图依赖见 gen_image.py。生图 key 从环境变量读取。
"""
import os, sys, json, time, base64, re, secrets, argparse, subprocess, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial

SCRIPTS = os.path.dirname(os.path.abspath(__file__))

# 合法 provider 白名单，对齐 gen_image.py 的 DISPATCH 键
VALID_PROVIDERS = {"gemini", "openai", "ark", "jimeng", "doubao", "dashscope", "wanx"}
# 上传 data URL 头校验（锚定，只允许常见图片类型）
DATA_URL_RE = re.compile(r"^data:image/(png|jpeg|jpg|webp);base64$")

def make_handler(outdir):
    class H(SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=outdir, **k)

        def _allowed_hosts(self):
            port = self.server.server_address[1]
            return {f"127.0.0.1:{port}", f"localhost:{port}"}

        def _check_origin(self):
            """防 CSRF / DNS-rebinding：校验 Origin 与 Host。合法返回 True，否则已写 403 返回 False。"""
            port = self.server.server_address[1]
            allowed_hosts = self._allowed_hosts()
            allowed_origins = {f"http://127.0.0.1:{port}", f"http://localhost:{port}"}
            origin = self.headers.get("Origin")
            # 现代浏览器非 GET 请求都带 Origin；缺失可放行，但若存在必须匹配
            if origin is not None and origin not in allowed_origins:
                self._json(403, {"ok": False, "error": "拒绝跨站请求：Origin 不在白名单内"})
                return False
            # 校验 Host 挡 DNS-rebinding
            host = self.headers.get("Host", "")
            if host not in allowed_hosts:
                self._json(403, {"ok": False, "error": "拒绝请求：Host 不在白名单内"})
                return False
            return True

        def _json(self, code, obj):
            body = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read(self):
            n = int(self.headers.get("Content-Length", 0))
            return json.loads(self.rfile.read(n) or b"{}")

        def do_POST(self):
            if not self._check_origin():
                return
            try:
                if self.path == "/api/regen":
                    return self.regen()
                if self.path == "/api/upload":
                    return self.upload()
                if self.path == "/api/save":
                    return self.save()
            except Exception as e:
                return self._json(500, {"ok": False, "error": str(e)})
            self._json(404, {"ok": False, "error": "unknown endpoint"})

        def regen(self):
            d = self._read()
            idx = int(d.get("index", 0))
            prompt = d.get("prompt", "").strip()
            if not prompt:
                return self._json(400, {"ok": False, "error": "提示词为空"})
            provider = d.get("provider", "gemini")
            if provider not in VALID_PROVIDERS:
                return self._json(400, {"ok": False,
                    "error": f"非法 provider '{provider}'，可选：{', '.join(sorted(VALID_PROVIDERS))}"})
            fname = f"img{idx}_v{int(time.time())}_{secrets.token_hex(2)}.png"
            out = os.path.join(outdir, fname)
            cmd = [sys.executable, os.path.join(SCRIPTS, "gen_image.py"),
                   "--provider", provider,
                   "--prompt", prompt, "--out", out, "--aspect", d.get("aspect", "9:16")]
            if d.get("model"):
                cmd += ["--model", d["model"]]
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            except subprocess.TimeoutExpired:
                return self._json(504, {"ok": False, "error": "生图超时（超过180秒），请重试或更换 provider"})
            if r.returncode != 0 or not os.path.exists(out):
                return self._json(500, {"ok": False, "error": (r.stderr or r.stdout or "生图失败").strip()[-300:]})
            self._json(200, {"ok": True, "file": fname})

        def upload(self):
            d = self._read()
            idx = int(d.get("index", 0))
            data_url = d.get("dataUrl", "")
            if "," not in data_url:
                return self._json(400, {"ok": False, "error": "无效图片"})
            head, b64 = data_url.split(",", 1)
            m = DATA_URL_RE.match(head)
            if not m:
                return self._json(400, {"ok": False,
                    "error": "无效图片类型：仅支持 png / jpeg / jpg / webp"})
            mime = m.group(1)
            ext = {"jpeg": "jpg", "jpg": "jpg", "png": "png", "webp": "webp"}[mime]
            fname = f"img{idx}_up{int(time.time())}_{secrets.token_hex(2)}.{ext}"
            with open(os.path.join(outdir, fname), "wb") as f:
                f.write(base64.b64decode(b64))
            self._json(200, {"ok": True, "file": fname})

        def save(self):
            payload = self._read()
            if not isinstance(payload, dict):
                return self._json(400, {"ok": False, "error": "无效内容：payload 必须是 JSON 对象"})
            conf = os.path.join(outdir, "content.confirmed.json")
            with open(conf, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            # 自动生成分享版（图片内嵌单文件）
            share_name = "小红书模拟器_分享版.html"
            share_out = os.path.join(outdir, share_name)
            try:
                r = subprocess.run(
                    [sys.executable, os.path.join(SCRIPTS, "build_simulator.py"),
                     "--content", conf, "--out", share_out, "--embed"],
                    capture_output=True, text=True, timeout=180)
            except subprocess.TimeoutExpired:
                return self._json(504, {"ok": False, "error": "生成分享版超时（超过180秒），请重试或更换 provider"})
            # 不谎报：分享版生成失败时如实回报，内容本体已保存
            if r.returncode != 0:
                err = (r.stderr or r.stdout or "生成分享版失败").strip()[-300:]
                return self._json(500, {"ok": False, "path": "content.confirmed.json",
                    "share": None, "error": f"内容已保存，但分享版生成失败：{err}"})
            self._json(200, {"ok": True, "path": "content.confirmed.json", "share": share_name})

        def log_message(self, *a):
            pass
    return H

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", nargs="?", default=".", help="输出目录（含 小红书模拟器.html 和图片）")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    outdir = os.path.abspath(args.dir)
    handler = make_handler(outdir)
    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    url = f"http://127.0.0.1:{args.port}/小红书模拟器.html"
    print(f"模拟器后端已启动：{url}")
    print("Ctrl+C 退出")
    if not args.no_open:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已退出")

if __name__ == "__main__":
    main()
