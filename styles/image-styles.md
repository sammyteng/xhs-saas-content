# 图片风格库 · 3 种可选 + 提示词模板

> 选定文章 + 风格后，根据内容**自动推荐若干条生图提示词**给用户确认，再批量出图。
> 一篇小红书按内容配 **1-9 张图**（不固定数量）：封面 + 数据/信息图 + 概念/能力/场景图 + 金句收尾，按需取舍。

## ⚠️ 头号铁律：别做"一眼 AI"的图

小红书用户对廉价 AI 图极其敏感，**一眼假就划走**。下面这些是重灾区，**默认全部避免**：

**🚫 禁用元素（负面清单）**
- 霓虹辉光、赛博朋克、深蓝+青色/品红的「科技感」渐变
- 悬浮的发光芯片 / 电路板 / 全息 HUD / 数据流线条 / 能量漩涡
- 发光的 3D 立体字、镜头光晕（lens flare）、粒子特效
- 通用机器人头 / 发光大脑 / 蓝色小人 / 握手齿轮等套路图标
- 过度对称、塑料感渲染、糊成一团的"未来感"背景

**✅ 改用这些（更像真人发的）**
- **真实摄影/编辑风**：桌面实拍、手持产品、办公室/居家场景、自然光、有生活痕迹
- **干净 UI 截图 / 产品界面 mockup**：直接展示软件长啥样（最有说服力，用风格3 更可控）
- **极简平面 / 杂志排版**：白底或莫兰迪低饱和色、大字海报、留白、胶片颗粒质感
- **手绘/插画/便签贴纸风**：小红书很吃这套，亲切不端着
- **真实截图 + 手动标注**（箭头、圈重点）

> 通用负面提示词（拼到每条 prompt 末尾）：
> `no neon glow, no cyberpunk, no holographic HUD, no floating circuit chips, no glowing 3D text, no lens flare, no generic AI robot/brain icons, not over-saturated, photorealistic and natural, looks like a real photo a person took`

## 生图模型可选（gen_image.py --provider）

`scripts/gen_image.py` 支持多家文生图模型，用 `--provider` 切换，key 各自从环境变量读取：

| provider | 模型 | 环境变量 | 安装 | 备注 |
|---|---|---|---|---|
| `gemini`（默认） | Nano Banana Pro `gemini-3-pro-image`（别名 `pro`）/ `flash` | `GEMINI_API_KEY` / `GOOGLE_AI_API_KEY` | `pip install google-genai` | 中文字渲染最准，支持参考图 `--ref` |
| `openai` | `gpt-image-1.5`（默认）/ `gpt-image-2` | `OPENAI_API_KEY` | `pip install openai` | 加 `--base-url` 可接兼容聚合站 |
| `ark`（豆包·即梦/Seedream） | `doubao-seedream-4-0-250828` | `ARK_API_KEY` | `pip install 'volcengine-python-sdk[ark]'` | 别名 `jimeng`/`doubao` |
| `dashscope`（通义万相） | `wan2.2-t2i-plus`（默认） | `DASHSCOPE_API_KEY` | `pip install dashscope` | 别名 `wanx`；wan2.5+ 走新接口，本脚本选 2.2 系列 |

比例 `--aspect`（9:16 / 4:5 / 1:1 / 16:9）会自动映射成各家支持的 size。
**风格3（HTML 渲染）不需要任何 key**，没有 API key 时全程可用它出图，中文零错字。

---

## 风格 1 · 真实质感大图（写实摄影 / 编辑风，LLM 文生图）

- **适用**：封面、场景图、产品在真实环境里的样子
- **观感**：像真人随手拍——自然光、真实材质、有生活气，**不是**塑料科技渲染
- **比例**：封面 9:16，内页 4:5 或 1:1

**提示词模板**：
```
A natural, editorial-style photo for a Xiaohongshu cover about {主题}.
Scene: {具体真实场景，如「a laptop on a wooden desk in a sunny home office, a coffee mug beside it, a notebook with handwriting」}.
Style: realistic photography, soft natural daylight, shallow depth of field, warm and lived-in,
muted natural colors, candid feel.
{若需中文大字}: add the Chinese text "{标题}" as clean flat typography overlaid in a corner (not glowing).
no neon glow, no cyberpunk, no holographic HUD, no floating circuit chips, no glowing 3D text,
no lens flare, no generic AI robot/brain icons, not over-saturated. Aspect 9:16.
```

## 风格 2 · 信息图 / 数据图（扁平设计，LLM 文生图，带中文）

- **适用**：罗列数据、对比、能力盘点
- **观感**：**扁平极简平面设计**，白底或低饱和底色，像杂志/咨询报告里的图，**不要**科技霓虹
- **工具**：`scripts/gen_image.py --model pro`（中文更准）

**提示词模板**：
```
A clean flat-design infographic poster, vertical 4:5, on a white or soft off-white background.
Editorial magazine style, muted modern palette (1-2 accent colors max), generous whitespace.
Title in Chinese: "{标题}".
Show {N} data points as bold numbers with short Chinese labels: {逐条：数字 + 标签}.
Simple flat line icons, clear hierarchy, no clutter.
Render all Chinese text accurately. no neon, no glow, no 3D, no tech-HUD, flat and minimal.
```

## 风格 3 · HTML 卡片 / 金句大字板（HTML 渲染，最可控）

- **适用**：金句收尾、步骤流程、清单卡、UI mockup（文字 100% 可控、零错字、零 AI 味）
- **观感**：杂志/PPT 极简风——大字、强对比、留白；**推荐白底浅色系**，干净不廉价
- **工具**：写一个 HTML 文件 → `scripts/shot.py` 截图成 PNG
- **优势**：中文绝不出错，排版精准，天然不"AI"，可放表格/列表/仿真界面

**HTML 骨架**（浅色极简版，存成 .html 后截图，尺寸 1080x1350）：
```html
<div id="card" style="width:1080px;height:1350px;display:flex;flex-direction:column;
  justify-content:center;padding:96px;box-sizing:border-box;
  background:#f5f3ee;color:#1d1d1f;
  font-family:'PingFang SC','Noto Sans SC',sans-serif;">
  <div style="font-size:32px;color:#c0392b;letter-spacing:3px;font-weight:700;">{小标签}</div>
  <div style="font-size:84px;font-weight:800;line-height:1.25;margin-top:24px;">{金句主文案}</div>
  <div style="font-size:30px;color:#6b6b6b;margin-top:40px;line-height:1.7;">{补充说明}</div>
</div>
```
截图命令：`python3 scripts/shot.py --html card.html --out img_quote.png --selector "#card" --w 1080 --h 1350`

> 拿不准就优先用风格3（HTML）——可控、零错字、最不像 AI 图。

---

## 配图清单建议（1-9 张，按内容定）

| 角色 | 推荐风格 |
|---|---|
| 封面 | 风格1（真实质感）或 风格3（大字海报） |
| 核心数据/对比 | 风格2（扁平信息图）或 风格3 |
| 概念/场景 | 风格1（真实场景）|
| 能力/功能盘点 | 风格2 或 风格3 |
| 产品界面展示 | 风格3（UI mockup，最有说服力）|
| 金句收尾 | 风格3（HTML 金句板）|

> ⚠️ 全套图保持**同一视觉语言**（统一底色/字体/留白），让多张像一组。**不再打「AI生成」水印**。
> 出图后逐张自检一遍上面的「负面清单」，命中任何一条就改提示词重出。
