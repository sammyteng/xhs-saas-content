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

**🚫 人物/解剖破绽（人物图最大翻车点，凡出现人物/手部必查）**
- 畸形的手 / 多指 / 缺指 / 手指粘连融合、多出来的肢体
- 扭曲错乱的人体结构、蜡感/塑料感皮肤、过度磨皮喷枪感皮肤
- 死板/不对称的眼睛、错乱崩坏的牙齿

**✅ 改用这些（更像真人发的）**
- **真实摄影/编辑风**：桌面实拍、手持产品、办公室/居家场景、自然光、有生活痕迹
- **干净 UI 截图 / 产品界面 mockup**：直接展示软件长啥样（最有说服力，用风格3 更可控）
- **极简平面 / 杂志排版**：白底或莫兰迪低饱和色、大字海报、留白、胶片颗粒质感
- **手绘/插画/便签贴纸风**：小红书很吃这套，亲切不端着
- **真实截图 + 手动标注**（箭头、圈重点）
- ⚠️ **场景/道具/配色按产品真实品类本地化**——美妆=梳妆台、财税=报表、教育=书桌，勿默认套办公/科技语境。

> 通用负面提示词（拼到每条 prompt 末尾）：
> `no neon glow, no cyberpunk, no holographic HUD, no floating circuit chips, no glowing 3D text, no lens flare, no generic AI robot/brain icons, not over-saturated, photorealistic and natural, looks like a real photo a person took, malformed hands, extra fingers, missing/fused fingers, extra limbs, distorted anatomy, waxy/plastic skin, over-smoothed airbrushed skin, dead/asymmetric eyes, mangled teeth, no garbled or gibberish text, no fake/nonsensical letters or characters anywhere in the scene, no random watermark text, no watermark, no logo, no signature`
>
> ⚠️ `no watermark / no logo / no signature` 对**平台后叠加的 badge** 收效有限，主防线仍是出图后的人工四角检查（见底部自检环节）。

## 生图模型可选（gen_image.py --provider）

`scripts/gen_image.py` 支持多家文生图模型，用 `--provider` 切换，key 各自从环境变量读取：

| provider | 模型 | 环境变量 | 安装 | 备注 |
|---|---|---|---|---|
| `openai`（**默认 = image-2**） | `gpt-image-2`（即 image-2，默认）/ `gpt-image-1.5` | `OPENAI_API_KEY` | `pip install openai` | 默认模型；可用环境变量 `OPENAI_IMAGE_MODEL` 覆盖，加 `--base-url` 接兼容聚合站 |
| `gemini` | Nano Banana Pro `gemini-3-pro-image`（别名 `pro`）/ `flash` | `GEMINI_API_KEY` / `GOOGLE_AI_API_KEY` | `pip install google-genai` | **中文字渲染最准**，支持参考图 `--ref`；中文老出错时切这家 |
| `ark`（豆包·即梦/Seedream） | `doubao-seedream-4-0-250828` | `ARK_API_KEY` | `pip install 'volcengine-python-sdk[ark]'` | 别名 `jimeng`/`doubao` |
| `dashscope`（通义万相） | `wan2.2-t2i-plus`（默认） | `DASHSCOPE_API_KEY` | `pip install dashscope` | 别名 `wanx`；wan2.5+ 走新接口，本脚本选 2.2 系列 |

比例 `--aspect`（9:16 / 4:5 / 1:1 / 16:9）会自动映射成各家支持的 size。
**风格3（HTML 渲染）不需要任何 key**，没有 API key 时全程可用它出图，中文零错字。

---

## 🔗 封面联动模式（自动适配）

当提供了 `--design-token`（来自 xhs-cover-skill 的输出）时，配图自动适配封面的视觉语言：

- **色彩**：风格 1/2 的提示词自动注入封面的主色调和氛围描述词
- **HTML 卡片**：风格 3 的 HTML 模板自动使用封面的配色方案（背景色、文字色、强调色）
- **负面提示词**：自动追加封面风格的 `negativePromptHints`，避免风格冲突
- **字体**：HTML 卡片的字体 family 和 weight 按封面的 `fontVibe` 自动适配

映射规则详见 `styles/cover-bridge.json`。

> 没有 design token 时，一切照旧——本 skill 完全独立可用。

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
{若需中文大字}: add the Chinese text "{标题}" as clean flat typography overlaid in a corner (not glowing). Aside from this title, keep all other surfaces (signs, screens, keyboards, labels) free of any text.
no neon glow, no cyberpunk, no holographic HUD, no floating circuit chips, no glowing 3D text,
no lens flare, no generic AI robot/brain icons, not over-saturated, malformed hands, extra fingers,
missing/fused fingers, extra limbs, distorted anatomy, waxy/plastic skin, over-smoothed airbrushed skin,
dead/asymmetric eyes, mangled teeth, no garbled or gibberish text, no fake/nonsensical letters or
characters anywhere in the scene, no random watermark text, no watermark, no logo, no signature. Aspect 9:16.
```

> ⚠️ LLM 渲染的中文易出错字/缺笔画，出图后需逐字核对；文字密集或含敏感/极限词时优先改用风格3（HTML 零错字）。

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
Render all Chinese text accurately. no neon, no glow, no 3D, no tech-HUD, flat and minimal,
no garbled or gibberish text, no fake/nonsensical letters or characters anywhere in the scene,
no random watermark text, no watermark, no logo, no signature.
```

> ⚠️ LLM 渲染的中文易出错字/缺笔画，出图后需逐字核对；文字密集或含敏感/极限词时优先改用风格3（HTML 零错字）。

## 风格 3 · HTML 卡片 / 金句大字板（HTML 渲染，最可控）

- **适用**：金句收尾、步骤流程、清单卡、UI mockup（文字 100% 可控、零错字、零 AI 味）
- **观感**：杂志/PPT 极简风——大字、强对比、留白；**推荐白底浅色系**，干净不廉价
- **工具**：写一个 HTML 文件 → `scripts/shot.py` 截图成 PNG
- **优势**：中文绝不出错，排版精准，天然不"AI"，可放表格/列表/仿真界面

**HTML 骨架**（浅色极简版，存成 .html 后截图，尺寸 1080x1350）：
```html
<!-- 颜色占位：{bg} 与 {accent} 有 design token 时由 cover-bridge.json 注入；
     无 token 时按上方「按品类选调性」速查替换，默认暖红仅为示例、勿跨品类照抄。 -->
<div id="card" style="width:1080px;height:1350px;display:flex;flex-direction:column;
  justify-content:center;padding:96px;box-sizing:border-box;
  background:{bg};color:#1d1d1f;
  font-family:'PingFang SC','Noto Sans SC',sans-serif;">
  <div style="font-size:32px;color:{accent};letter-spacing:3px;font-weight:700;">{小标签}</div>
  <div style="font-size:84px;font-weight:800;line-height:1.25;margin-top:24px;">{金句主文案}</div>
  <div style="font-size:30px;color:#6b6b6b;margin-top:40px;line-height:1.7;">{补充说明}</div>
</div>
```
截图命令：`python3 scripts/shot.py --html card.html --out img_quote.png --selector "#card" --w 1080 --h 1350`

> 拿不准就优先用风格3（HTML）——可控、零错字、最不像 AI 图。

### HTML 卡片风格库（6 款预设 · 配色直接填进上方骨架的 `{bg}`/`{accent}`）

> 来源：本地 `huashu-design` 的「无生图也能还原」风格库蒸馏，每款标了纯 HTML/CSS 还原度。
> 用法：首轮选「图片风格 = HTML 卡片」时挑一款（或按产品品类自动选）；封面有 design token 时仍优先用 token 配色。**别三款都落在「米白+留白+一个点缀色」**——那是最常见的千篇一律。

| 预设 | 配色（bg / 文字 / accent） | 字体倾向 | 适合品类 | 还原 |
|---|---|---|---|---|
| **克制蓝 B2B**（默认稳妥） | `#f7f6f2` / `#1a1a1a` / `#2f6df6` | Inter / 思源黑 | SaaS·财税·B2B 工具 | 98% |
| **暖色出版** | `#faf6ef` / `#2b2b2b` / `#c0552d` | 衬线标题 + 无衬线正文 | 生活·美妆·居家·食品 | 97% |
| **Swiss 黑白** | `#ffffff` / `#0a0a0a` / `#0a0a0a` | Geist/Helvetica 锐利直角 | 高端·极简·设计工具 | 98% |
| **暗色双色** | `#14141a` / `#f0f0f0` / 单荧光 `#00e676` | 等宽字 + 1px 细线 | 科技·开发者·酷感 | 96% |
| **撞色粗野** | `#fde047` / `#111111` / `#ff2d55` | 粗黑无衬线 + 3-4px 实色描边 | 年轻·潮玩·吸睛·快讯 | 95% |
| **黑白大字报** | `#ffffff` 或 `#111111` / 反色 / 单色 | 巨号粗体占半屏 | 观点·金句·锐评 | 88% |

⚠️ **暗色双色**只用**单个** accent + 细线，**不堆霓虹/赛博/发光**（踩负面清单）；**撞色粗野**用实色粗描边卡片，不用阴影发光。
想「多卖点平铺」→ 用 **Bento 便当格**（模块网格，还原 95%）：把上方骨架的 flex 改成 `display:grid` 多格，每格一个卖点。

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

### 按品类选调性（速查）

| 品类 | 配色建议 |
|---|---|
| 美妆 | 柔粉 / 低饱和米杏 |
| 食品 | 暖橙 / 木质暖白 |
| 金融·B2B | 中性灰 + 克制蓝 |
| 母婴 | 明快柔和糖果色 |
| 医疗 | 冷白克制（⚠️ 注意 P0-9 医疗垂类红线，避免效果暗示）|
| 潮玩 | 高饱和撞色 |

> 此表为**默认调性**，最终优先服从封面 design token（`cover-bridge.json`）。

> ⚠️ 全套图保持**同一视觉语言**（统一底色/字体/留白），让多张像一组。**不再打「AI生成」水印**。

### 出图后逐张自检清单

- [ ] 对照上面的「负面清单」（含**人物/解剖破绽**），命中任何一条就改提示词重出
- [ ] 逐图检查**四角有无厂商角标/可见水印**（尤其 `ark`·即梦、`dashscope`·通义万相出图易残留），命中则重出后裁剪，或换 provider（如转**风格3 HTML 渲染，零厂商标记**）
- [ ] 嵌字**逐字核对**无错别字/缺笔画（LLM 渲染中文易出错；密集/敏感文字优先改风格3）
- [ ] 嵌字已纳入**合规扫描**（违禁词/极限词），参见同目录 [`content-compliance.md`](./content-compliance.md)
