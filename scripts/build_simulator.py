#!/usr/bin/env python3
"""
从 content.json + 图片列表生成「小红书发布模拟器」HTML（左右两屏：左图右文）。
无第三方依赖，纯标准库。

用法：
  python3 build_simulator.py --content content.json --out 小红书模拟器.html
  # 图片可写在 content.json 的 "images" 字段，也可用 --img 覆盖
  python3 build_simulator.py --content content.json --img cover.png --img img2.png

content.json 字段（均可选，缺省有默认值）：
{
  "author": "AI内容观察",
  "ip": "浙江",
  "title": "标题文字",
  "body": "正文，用 \\n 换行",
  "highlight": "正文中要加粗高亮的一句（可选）",
  "tags": ["标签1", "标签2"],
  "date": "06-03",
  "location": "浙江",
  "likes": "1.2万",
  "collects": "8675",
  "comments": 432,
  "images": ["cover.png", "img2.png", "img3.png"]
}
"""
import os, json, argparse, html

TEMPLATE = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>小红书发布模拟器</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased;}
  body{font-family:"PingFang SC","Noto Sans SC",sans-serif;
    background:radial-gradient(1200px 800px at 30% 0%,#2a2330,#15131a 60%,#0c0b10);
    min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:36px 16px 70px;color:#fff;}
  .head{text-align:center;margin-bottom:26px;}
  .head h1{font-size:25px;font-weight:800;letter-spacing:1px;}
  .head h1 .red{color:#ff2442;}
  .head p{color:#9a93a8;font-size:13.5px;margin-top:7px;}
  .note{width:1160px;max-width:96vw;height:760px;background:#fff;border-radius:18px;overflow:hidden;
    display:flex;box-shadow:0 30px 80px rgba(0,0,0,.5);}
  .media{width:600px;flex-shrink:0;background:#0a0a0a;position:relative;display:flex;flex-direction:column;}
  .stagebox{flex:1;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;}
  .stagebox img{max-width:100%;max-height:100%;object-fit:contain;display:block;}
  .cidx{position:absolute;top:14px;right:16px;background:rgba(0,0,0,.55);color:#fff;font-size:13px;padding:4px 12px;border-radius:14px;z-index:5;}
  .arrow{position:absolute;top:50%;transform:translateY(-50%);width:40px;height:40px;border-radius:50%;background:rgba(0,0,0,.45);color:#fff;border:none;font-size:20px;cursor:pointer;z-index:6;display:flex;align-items:center;justify-content:center;transition:.2s;}
  .arrow:hover{background:rgba(0,0,0,.75);}
  .arrow.l{left:12px;} .arrow.r{right:12px;}
  .rail{height:96px;flex-shrink:0;background:#111;display:flex;gap:8px;align-items:center;padding:0 12px;overflow-x:auto;}
  .rail::-webkit-scrollbar{height:0;}
  .thumb{height:74px;width:auto;border-radius:8px;border:2px solid transparent;cursor:pointer;opacity:.5;transition:.2s;flex-shrink:0;}
  .thumb.on{border-color:#ff2442;opacity:1;}
  .panel{flex:1;display:flex;flex-direction:column;min-width:0;}
  .author{display:flex;align-items:center;gap:11px;padding:20px 26px;border-bottom:1px solid #f3f3f3;flex-shrink:0;}
  .av{width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,#36a3ff,#00e0b8);display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:800;color:#fff;flex-shrink:0;}
  .nm{font-size:15.5px;font-weight:600;color:#222;}
  .sub{font-size:12px;color:#999;margin-top:2px;}
  .fl{margin-left:auto;background:#ff2442;color:#fff;font-size:14px;font-weight:600;padding:7px 22px;border-radius:20px;}
  .body{flex:1;overflow-y:auto;padding:22px 28px;}
  .body::-webkit-scrollbar{width:6px;} .body::-webkit-scrollbar-thumb{background:#e3e3e3;border-radius:3px;}
  .ntitle{font-size:21px;font-weight:700;color:#1a1a1a;line-height:1.42;margin-bottom:14px;}
  .ntext{font-size:15px;color:#2b2b2b;line-height:1.85;white-space:pre-wrap;}
  .ntext .b{font-weight:600;color:#111;}
  .tags{margin-top:14px;color:#1a4b8c;font-size:14.5px;line-height:1.95;}
  .meta{margin-top:16px;color:#b5b5b5;font-size:12.5px;}
  .botbar{height:62px;border-top:1px solid #f3f3f3;display:flex;align-items:center;gap:16px;padding:0 24px;flex-shrink:0;}
  .ipt{flex:1;background:#f5f5f5;border-radius:20px;color:#9a9a9a;font-size:13.5px;padding:10px 20px;}
  .ic{display:flex;align-items:center;gap:6px;color:#444;font-size:15px;}
  .ic .e{font-size:21px;}
</style>
</head>
<body>
  <div class="head">
    <h1><span class="red">小红书</span> 发布模拟器</h1>
    <p>左屏看图（← →切换）· 右屏看完整文案 · <span style="opacity:.8">全部内容 AI 生成</span></p>
  </div>
  <div class="note">
    <div class="media">
      <div class="stagebox">
        <span class="cidx" id="cidx">1 / {TOTAL}</span>
        <button class="arrow l" onclick="go(-1)">&lsaquo;</button>
        <button class="arrow r" onclick="go(1)">&rsaquo;</button>
        <img id="bigimg" src="./{FIRST_IMG}">
      </div>
      <div class="rail" id="rail"></div>
    </div>
    <div class="panel">
      <div class="author">
        <div class="av">{AVATAR}</div>
        <div><div class="nm">{AUTHOR}</div><div class="sub">IP属地：{IP}</div></div>
        <div class="fl">关注</div>
      </div>
      <div class="body">
        <div class="ntitle">{TITLE}</div>
        <div class="ntext">{BODY}</div>
        <div class="tags">{TAGS}</div>
        <div class="meta">编辑于 {DATE} · {LOCATION}　共 {COMMENTS} 条评论　·　<span style="opacity:.8">本内容由 AI 生成</span></div>
      </div>
      <div class="botbar">
        <span class="ipt">说点什么...</span>
        <span class="ic"><span class="e">&hearts;</span> {LIKES}</span>
        <span class="ic"><span class="e">&starf;</span> {COLLECTS}</span>
        <span class="ic"><span class="e">&#128172;</span> {COMMENTS}</span>
      </div>
    </div>
  </div>
<script>
  const imgs={IMGS_JSON};
  const total=imgs.length;let cur=0;
  const big=document.getElementById('bigimg'),cidx=document.getElementById('cidx'),rail=document.getElementById('rail');
  imgs.forEach((s,i)=>{const t=document.createElement('img');t.src="./"+s;t.className="thumb";t.onclick=()=>set(i);rail.appendChild(t);});
  function set(i){cur=(i+total)%total;big.src="./"+imgs[cur];cidx.textContent=`${cur+1} / ${total}`;
    [...rail.children].forEach((t,k)=>t.classList.toggle('on',k===cur));
    rail.children[cur].scrollIntoView({inline:'center',behavior:'smooth'});}
  function go(d){set(cur+d);}
  set(0);
  document.addEventListener('keydown',e=>{if(e.key==='ArrowRight')go(1);if(e.key==='ArrowLeft')go(-1);});
</script>
</body>
</html>
"""

def esc(s):
    return html.escape(str(s), quote=False)

def build_body(body, highlight):
    body = esc(body)
    if highlight:
        h = esc(highlight)
        if h in body:
            body = body.replace(h, f'<span class="b">{h}</span>')
    return body

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", required=True, help="content.json 路径")
    ap.add_argument("--out", default="小红书模拟器.html")
    ap.add_argument("--img", action="append", default=[], help="图片文件名，可多次（覆盖 json 中的 images）")
    args = ap.parse_args()

    with open(args.content, encoding="utf-8") as f:
        c = json.load(f)

    imgs = args.img or c.get("images") or []
    if not imgs:
        raise SystemExit("ERROR: 没有图片，请在 content.json 写 images 或用 --img 指定")

    author = c.get("author", "AI内容观察")
    avatar = c.get("avatar") or (author[:2] if author else "AI")
    tags = c.get("tags", [])
    tags_str = " ".join("#" + esc(t) for t in tags)

    htmlout = TEMPLATE
    repl = {
        "{TOTAL}": str(len(imgs)),
        "{FIRST_IMG}": esc(imgs[0]),
        "{AVATAR}": esc(avatar),
        "{AUTHOR}": esc(author),
        "{IP}": esc(c.get("ip", "未知")),
        "{TITLE}": esc(c.get("title", "")),
        "{BODY}": build_body(c.get("body", ""), c.get("highlight")),
        "{TAGS}": tags_str,
        "{DATE}": esc(c.get("date", "")),
        "{LOCATION}": esc(c.get("location", c.get("ip", ""))),
        "{COMMENTS}": esc(c.get("comments", 0)),
        "{LIKES}": esc(c.get("likes", "0")),
        "{COLLECTS}": esc(c.get("collects", "0")),
        "{IMGS_JSON}": json.dumps(imgs, ensure_ascii=False),
    }
    for k, v in repl.items():
        htmlout = htmlout.replace(k, v)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(htmlout)
    print(args.out)

if __name__ == "__main__":
    main()
