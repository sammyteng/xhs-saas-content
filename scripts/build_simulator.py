#!/usr/bin/env python3
"""
从 content.json 生成「小红书发布模拟器」HTML。两种产物：

  # 编辑版（配合 serve.py：可改文案 / 单图重生成 / 换图 / 确认保存）
  python3 build_simulator.py --content content.json --out 小红书模拟器.html

  # 分享版（图片 base64 内嵌成单文件，发给别人不丢图，只读预览）
  python3 build_simulator.py --content content.json --out 小红书模拟器_分享版.html --embed

content.json 字段（均可选，缺省有默认值）：
{
  "author","ip","avatar",
  "titles": ["标题1","标题2","标题3"],        // 3 个候选，小红书标题≤20字符；也兼容旧的 "title":"..."
  "body": "正文，用 \\n 换行",
  "highlight": "正文中要加粗的一句（可选）",
  "tags": ["标签1","标签2"],
  "date","location","likes","collects","comments",
  "images": ["cover.png","img2.png"],         // 1-9 张，按内容定，不限固定数量
  "image_prompts": ["图1提示词","图2提示词"],  // 与 images 一一对应，用于单图重生成
  "gen": {"provider":"gemini","model":"pro","aspect":"9:16"}
}
"""
import os, json, argparse, base64, mimetypes

def norm(content):
    c = dict(content)
    if not c.get("titles"):
        t = c.get("title")
        c["titles"] = [t] if t else ["（未填标题）"]
    c["titles"] = [str(t) for t in c["titles"]][:3]
    c.setdefault("author", "AI内容观察")
    c.setdefault("avatar", (c["author"][:2] if c.get("author") else "AI"))
    c.setdefault("ip", "未知")
    c.setdefault("location", c.get("ip", ""))
    c.setdefault("body", "")
    c.setdefault("highlight", "")
    c.setdefault("tags", [])
    c.setdefault("date", "")
    c.setdefault("likes", "0")
    c.setdefault("collects", "0")
    c.setdefault("comments", 0)
    c.setdefault("images", [])
    c.setdefault("image_prompts", [])
    c.setdefault("gen", {"provider": "gemini", "model": "pro", "aspect": "9:16"})
    # prompts 补齐到与 images 等长
    while len(c["image_prompts"]) < len(c["images"]):
        c["image_prompts"].append("")
    return c

def embed_map(images, base_dir):
    src = {}
    for name in images:
        p = name if os.path.isabs(name) else os.path.join(base_dir, name)
        if not os.path.exists(p):
            continue
        mime = mimetypes.guess_type(p)[0] or "image/png"
        with open(p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        src[name] = f"data:{mime};base64,{b64}"
    return src

HTML = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>小红书发布模拟器</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased;}
  body{font-family:"PingFang SC","Noto Sans SC",sans-serif;
    background:radial-gradient(1200px 800px at 30% 0%,#2a2330,#15131a 60%,#0c0b10);
    min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:30px 16px 70px;color:#fff;}
  .head{text-align:center;margin-bottom:18px;}
  .head h1{font-size:24px;font-weight:800;letter-spacing:1px;}
  .head h1 .red{color:#ff2442;}
  .head p{color:#9a93a8;font-size:13px;margin-top:6px;}
  .note{width:1180px;max-width:97vw;height:782px;background:#fff;border-radius:18px;overflow:hidden;
    display:flex;box-shadow:0 30px 80px rgba(0,0,0,.5);}
  /* LEFT */
  .media{width:600px;flex-shrink:0;background:#0a0a0a;position:relative;display:flex;flex-direction:column;}
  .stagebox{flex:1;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;min-height:0;}
  .stagebox img{max-width:100%;max-height:100%;object-fit:contain;display:block;}
  .cidx{position:absolute;top:14px;right:16px;background:rgba(0,0,0,.55);color:#fff;font-size:13px;padding:4px 12px;border-radius:14px;z-index:5;}
  .arrow{position:absolute;top:42%;transform:translateY(-50%);width:40px;height:40px;border-radius:50%;background:rgba(0,0,0,.45);color:#fff;border:none;font-size:20px;cursor:pointer;z-index:6;}
  .arrow:hover{background:rgba(0,0,0,.78);}
  .arrow.l{left:12px;} .arrow.r{right:12px;}
  .rail{height:84px;flex-shrink:0;background:#111;display:flex;gap:8px;align-items:center;padding:0 12px;overflow-x:auto;}
  .rail::-webkit-scrollbar{height:0;}
  .thumb{height:64px;width:auto;border-radius:8px;border:2px solid transparent;cursor:pointer;opacity:.5;flex-shrink:0;}
  .thumb.on{border-color:#ff2442;opacity:1;}
  /* per-image prompt panel */
  .imgtools{flex-shrink:0;background:#15151c;border-top:1px solid #222;padding:10px 12px;display:flex;flex-direction:column;gap:8px;}
  .imgtools textarea{width:100%;height:54px;resize:none;border-radius:8px;border:1px solid #333;background:#0e0e14;color:#e8e8ef;font-size:12.5px;padding:8px 10px;font-family:inherit;}
  .imgrow{display:flex;gap:8px;align-items:center;}
  .imgrow select{background:#0e0e14;color:#cfcfe0;border:1px solid #333;border-radius:7px;font-size:12px;padding:6px 8px;}
  .btn{border:none;border-radius:8px;font-size:12.5px;font-weight:600;padding:8px 12px;cursor:pointer;}
  .btn.p{background:#0071e3;color:#fff;} .btn.p:hover{background:#0063c7;}
  .btn.g{background:#2a2a33;color:#dcdce6;} .btn.g:hover{background:#35353f;}
  .btn:disabled{opacity:.5;cursor:not-allowed;}
  /* RIGHT */
  .panel{flex:1;display:flex;flex-direction:column;min-width:0;}
  .author{display:flex;align-items:center;gap:11px;padding:16px 24px;border-bottom:1px solid #f3f3f3;flex-shrink:0;}
  .av{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#36a3ff,#00e0b8);display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:800;color:#fff;flex-shrink:0;}
  .nm{font-size:15px;font-weight:600;color:#222;}
  .sub{font-size:12px;color:#999;margin-top:2px;}
  .fl{margin-left:auto;background:#ff2442;color:#fff;font-size:13.5px;font-weight:600;padding:6px 20px;border-radius:20px;}
  .body{flex:1;overflow-y:auto;padding:18px 26px;}
  .body::-webkit-scrollbar{width:6px;} .body::-webkit-scrollbar-thumb{background:#e3e3e3;border-radius:3px;}
  .titlebar{font-size:21px;font-weight:700;color:#1a1a1a;line-height:1.4;outline:none;}
  .titlebar.edit:hover,.titlebar.edit:focus{background:#fff7f8;border-radius:6px;}
  .cnt{font-size:12px;margin:6px 0 2px;color:#9a9a9a;}
  .cnt.over{color:#ff2442;font-weight:600;}
  .chips{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 14px;}
  .chip{font-size:12.5px;color:#444;background:#f3f4f6;border:1px solid #e6e6ea;border-radius:14px;padding:5px 12px;cursor:pointer;}
  .chip.on{background:#fff0f2;border-color:#ff2442;color:#ff2442;font-weight:600;}
  .ntext{font-size:15px;color:#2b2b2b;line-height:1.85;white-space:pre-wrap;outline:none;}
  .ntext.edit:hover,.ntext.edit:focus{background:#fafafa;border-radius:6px;}
  .ntext .b{font-weight:600;color:#111;}
  .tags{margin-top:14px;color:#1a4b8c;font-size:14.5px;line-height:1.95;}
  .meta{margin-top:14px;color:#b5b5b5;font-size:12.5px;}
  .botbar{min-height:60px;border-top:1px solid #f3f3f3;display:flex;align-items:center;gap:12px;padding:10px 22px;flex-shrink:0;flex-wrap:wrap;}
  .ipt{flex:1;background:#f5f5f5;border-radius:20px;color:#9a9a9a;font-size:13px;padding:9px 18px;min-width:120px;}
  .ic{display:flex;align-items:center;gap:5px;color:#444;font-size:14px;}
  .ic .e{font-size:19px;}
  .stat{width:100%;font-size:12.5px;color:#0071e3;}
  .hint{font-size:11.5px;color:#8a8a93;}
</style>
</head>
<body>
  <div class="head">
    <h1><span class="red">小红书</span> 发布模拟器</h1>
    <p id="modehint"></p>
  </div>
  <div class="note">
    <div class="media">
      <div class="stagebox">
        <span class="cidx" id="cidx">1 / 1</span>
        <button class="arrow l" onclick="go(-1)">&lsaquo;</button>
        <button class="arrow r" onclick="go(1)">&rsaquo;</button>
        <img id="bigimg">
      </div>
      <div class="rail" id="rail"></div>
      <div class="imgtools" id="imgtools">
        <textarea id="promptbox" placeholder="这张图的提示词…改完点「重新生成此图」"></textarea>
        <div class="imgrow">
          <select id="prov"><option value="gemini">Gemini</option><option value="openai">GPT</option><option value="ark">即梦/Seedream</option><option value="dashscope">通义万相</option></select>
          <select id="asp"><option>9:16</option><option>4:5</option><option>1:1</option><option>16:9</option></select>
          <button class="btn p" id="btnregen" onclick="regen()">重新生成此图</button>
          <button class="btn g" onclick="document.getElementById('fileup').click()">上传换图</button>
          <input type="file" id="fileup" accept="image/*" style="display:none" onchange="if(this.files[0])upload(this.files[0])">
        </div>
      </div>
    </div>
    <div class="panel">
      <div class="author">
        <div class="av" id="av">AI</div>
        <div><div class="nm" id="nm"></div><div class="sub" id="sub"></div></div>
        <div class="fl">关注</div>
      </div>
      <div class="body">
        <div class="titlebar" id="titlebar"></div>
        <div class="cnt" id="cnt"></div>
        <div class="chips" id="chips"></div>
        <div class="ntext" id="ntext"></div>
        <div class="tags" id="tags"></div>
        <div class="meta" id="meta"></div>
      </div>
      <div class="botbar">
        <span class="ipt">说点什么...</span>
        <span class="ic"><span class="e">&hearts;</span> <span id="likes"></span></span>
        <span class="ic"><span class="e">&starf;</span> <span id="collects"></span></span>
        <button class="btn p" id="btnconfirm" onclick="confirmContent()">✓ 确认内容</button>
        <div class="stat" id="stat"></div>
      </div>
    </div>
  </div>
<script>
const DATA = __DATA__;
const SRC  = __SRC__;        // 文件名 -> dataURI（分享版内嵌，编辑版为空）
const SHARE = __SHARE__;     // 分享版只读
const SERVED = location.protocol.indexOf('http') === 0;  // 是否经 serve.py 后端
const TITLE_MAX = 20;

const $ = id => document.getElementById(id);
let cur = 0, titleIdx = 0;

function srcOf(n){ return SRC[n] || ('./'+n); }
function bust(n){ return SRC[n] ? srcOf(n) : srcOf(n)+'?t='+Date.now(); }

function renderHead(){
  $('modehint').innerHTML = SHARE
    ? '只读分享版 · 图片已内嵌单文件 · 左屏翻图（← →）· 右屏看完整内容'
    : '左屏：单图可改提示词重生成/换图 · 右屏：点标题切换、点正文直接改 · 改完点「确认内容」保存';
  $('av').textContent = DATA.avatar || 'AI';
  $('nm').textContent = DATA.author || '';
  $('sub').textContent = 'IP属地：' + (DATA.ip || '');
  $('likes').textContent = DATA.likes || '0';
  $('collects').textContent = DATA.collects || '0';
  $('tags').textContent = (DATA.tags || []).map(t=>'#'+t).join(' ');
  $('meta').textContent = '编辑于 ' + (DATA.date||'') + ' · ' + (DATA.location||DATA.ip||'') + '　共 ' + (DATA.comments||0) + ' 条评论';
  $('prov').value = (DATA.gen&&DATA.gen.provider) || 'gemini';
  $('asp').value  = (DATA.gen&&DATA.gen.aspect) || '9:16';
}

/* ---- 标题（3 候选 + 20 字符限制） ---- */
function renderTitles(){
  const chips = $('chips'); chips.innerHTML='';
  (DATA.titles||[]).forEach((t,i)=>{
    const c=document.createElement('span'); c.className='chip'+(i===titleIdx?' on':''); c.textContent=t;
    c.onclick=()=>setTitle(i); chips.appendChild(c);
  });
  if(SHARE) chips.style.display = (DATA.titles||[]).length>1 ? 'flex':'none';
}
function setTitle(i){
  titleIdx=i; const t=(DATA.titles||[])[i]||'';
  $('titlebar').textContent=t; updateCnt();
  [...$('chips').children].forEach((c,k)=>c.classList.toggle('on',k===i));
}
function updateCnt(){
  const len=[...($('titlebar').textContent||'')].length;
  const e=$('cnt'); e.textContent='标题 '+len+' / '+TITLE_MAX+' 字符'+(len>TITLE_MAX?'（超出，小红书会截断）':'');
  e.classList.toggle('over', len>TITLE_MAX);
}

/* ---- 正文（高亮 + 可编辑） ---- */
function renderBody(){
  const el=$('ntext'); const body=DATA.body||''; const h=DATA.highlight;
  el.textContent=body;
  if(h && body.indexOf(h)>=0 && !SHARE===false){ /* keep plain for edit */ }
  if(h && body.indexOf(h)>=0){
    el.innerHTML = body.split(h).join('<span class="b">'+h.replace(/[&<>]/g,s=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[s]))+'</span>');
  }
}

/* ---- 图片轮播 ---- */
function renderRail(){
  const rail=$('rail'); rail.innerHTML='';
  (DATA.images||[]).forEach((s,i)=>{
    const t=document.createElement('img'); t.src=bust(s); t.className='thumb'; t.onclick=()=>set(i); rail.appendChild(t);
  });
}
function set(i){
  const n=(DATA.images||[]).length||1; cur=((i%n)+n)%n;
  const name=(DATA.images||[])[cur];
  if(name) $('bigimg').src=bust(name);
  $('cidx').textContent=(cur+1)+' / '+n;
  [...$('rail').children].forEach((t,k)=>t.classList.toggle('on',k===cur));
  if($('rail').children[cur]) $('rail').children[cur].scrollIntoView({inline:'center',behavior:'smooth'});
  $('promptbox').value=(DATA.image_prompts||[])[cur]||'';
}
function go(d){ set(cur+d); }

/* ---- 单图重生成 / 上传 ---- */
async function regen(){
  if(!SERVED){ alert('重新生成需要后端：\n在该目录执行  python3 scripts/serve.py  后用浏览器打开。'); return; }
  const b={index:cur, prompt:$('promptbox').value, provider:$('prov').value, model:(DATA.gen&&DATA.gen.model)||'', aspect:$('asp').value};
  const btn=$('btnregen'); btn.disabled=true; const old=btn.textContent; btn.textContent='生成中…';
  try{
    const r=await fetch('/api/regen',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});
    const j=await r.json();
    if(j.ok){ DATA.images[cur]=j.file; DATA.image_prompts[cur]=$('promptbox').value; renderRail(); set(cur); stat('已重新生成第 '+(cur+1)+' 张'); }
    else alert('生成失败：'+(j.error||'未知'));
  }catch(e){ alert('生成失败：'+e); }
  btn.disabled=false; btn.textContent=old;
}
function upload(file){
  const fr=new FileReader();
  fr.onload=async()=>{
    const dataUrl=fr.result;
    if(SERVED){
      try{
        const r=await fetch('/api/upload',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({index:cur,dataUrl})});
        const j=await r.json();
        if(j.ok){ DATA.images[cur]=j.file; renderRail(); set(cur); stat('已替换第 '+(cur+1)+' 张'); } else alert('上传失败：'+j.error);
      }catch(e){ alert('上传失败：'+e); }
    } else { SRC[DATA.images[cur]]=dataUrl; renderRail(); set(cur); stat('本地预览已替换（未连后端，不落盘）'); }
  };
  fr.readAsDataURL(file);
}

/* ---- 确认内容 → 保存 JSON + 生成分享版 ---- */
function collect(){
  return Object.assign({}, DATA, {
    titles: DATA.titles,
    title: $('titlebar').textContent.trim(),   // 最终选定/编辑后的标题
    titleIndex: titleIdx,
    body: $('ntext').innerText
  });
}
async function confirmContent(){
  const payload=collect();
  if([...(payload.title||'')].length>TITLE_MAX){ if(!confirm('标题超过 '+TITLE_MAX+' 字符，确定继续？')) return; }
  if(SERVED){
    try{
      const r=await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      const j=await r.json();
      if(j.ok) stat('✓ 已确认并保存：'+j.path+'　|　分享版：'+(j.share||'-')+'（发布流程待开发）');
      else alert('保存失败：'+j.error);
    }catch(e){ alert('保存失败：'+e); }
  } else {
    const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});
    const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='content.confirmed.json'; a.click();
    stat('✓ 已下载 content.confirmed.json（未连后端；分享版请用 build_simulator.py --embed 生成）');
  }
}
function stat(m){ $('stat').textContent=m; }

/* ---- init ---- */
function init(){
  renderHead(); renderTitles(); setTitle(0); renderBody(); renderRail(); set(0);
  if(SHARE){
    $('imgtools').style.display='none';
    $('btnconfirm').style.display='none';
    $('titlebar').classList.remove('edit');
    $('ntext').classList.remove('edit');
  } else {
    $('titlebar').classList.add('edit'); $('titlebar').contentEditable=true;
    $('titlebar').addEventListener('input',updateCnt);
    $('ntext').classList.add('edit'); $('ntext').contentEditable=true;
    if(!SERVED){ $('btnregen').title='需 serve.py 后端'; }
  }
  document.addEventListener('keydown',e=>{
    if(e.target.isContentEditable||e.target.tagName==='TEXTAREA') return;
    if(e.key==='ArrowRight')go(1); if(e.key==='ArrowLeft')go(-1);
  });
}
init();
</script>
</body>
</html>
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", required=True)
    ap.add_argument("--out", default="小红书模拟器.html")
    ap.add_argument("--embed", action="store_true", help="把图片 base64 内嵌成单文件（分享版）")
    args = ap.parse_args()

    with open(args.content, encoding="utf-8") as f:
        content = norm(json.load(f))

    base_dir = os.path.dirname(os.path.abspath(args.content))
    src = embed_map(content["images"], base_dir) if args.embed else {}

    html = (HTML
            .replace("__DATA__", json.dumps(content, ensure_ascii=False))
            .replace("__SRC__", json.dumps(src, ensure_ascii=False))
            .replace("__SHARE__", "true" if args.embed else "false"))

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)
    print(args.out)

if __name__ == "__main__":
    main()
