#!/usr/bin/env python3
"""
小红书模拟器本地后端。启动后用浏览器打开，编辑版即可：
  - 单图重生成（调 gen_image.py）
  - 上传换图
  - （可选）「确认内容」→ 保存 content.confirmed.json + 自动生成分享版；自动化场景可跳过确认直接使用 content.json

用法：
  python3 scripts/serve.py <输出目录> [--content content.json] [--port 8000]
  # 然后浏览器打开 http://127.0.0.1:8000/小红书模拟器.html

依赖：标准库即可；生图依赖见 gen_image.py。生图 key 从环境变量读取。
"""
import os, sys, json, time, base64, argparse, subprocess, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial

SCRIPTS = os.path.dirname(os.path.abspath(__file__))

def make_handler(outdir, content_name):
    class H(SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=outdir, **k)

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
            fname = f"img{idx}_v{int(time.time())}.png"
            out = os.path.join(outdir, fname)
            cmd = [sys.executable, os.path.join(SCRIPTS, "gen_image.py"),
                   "--provider", d.get("provider", "gemini"),
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
            ext = "png"
            if "jpeg" in head or "jpg" in head:
                ext = "jpg"
            fname = f"img{idx}_up{int(time.time())}.{ext}"
            with open(os.path.join(outdir, fname), "wb") as f:
                f.write(base64.b64decode(b64))
            self._json(200, {"ok": True, "file": fname})

        def save(self):
            payload = self._read()
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
            share = share_name if r.returncode == 0 else None
            self._json(200, {"ok": True, "path": "content.confirmed.json", "share": share})

        def log_message(self, *a):
            pass
    return H

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", nargs="?", default=".", help="输出目录（含 小红书模拟器.html 和图片）")
    ap.add_argument("--content", default="content.json")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    outdir = os.path.abspath(args.dir)
    handler = make_handler(outdir, args.content)
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
