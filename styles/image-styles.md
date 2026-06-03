# 图片风格库 · 3 种可选 + 提示词模板

> 选定文章 + 风格后，根据内容**自动推荐 3 条生图提示词**给用户确认，再批量出图。
> 一篇小红书配 **6-9 张图**：1 张封面 + 1-2 张数据/信息图 + 若干概念/能力/场景图 + 1 张金句收尾。

## 生图模型可选（gen_image.py --provider）

`scripts/gen_image.py` 支持多家文生图模型，用 `--provider` 切换，key 各自从环境变量读取：

| provider | 模型 | 环境变量 | 安装 | 备注 |
|---|---|---|---|---|
| `gemini`（默认） | Nano Banana Pro `gemini-3-pro-image`（别名 `pro`，默认）/ `flash` | `GEMINI_API_KEY` 或 `GOOGLE_AI_API_KEY` | `pip install google-genai` | 中文字渲染最准，支持参考图 `--ref` |
| `openai` | `gpt-image-1.5`（默认）/ `gpt-image-2` / `gpt-image-1-mini` | `OPENAI_API_KEY` | `pip install openai` | 加 `--base-url` 可接 OpenAI 兼容聚合站 |
| `ark`（豆包·即梦/Seedream） | `doubao-seedream-4-0-250828`（Seedream 4.0，支持 4K/多图参考） | `ARK_API_KEY` | `pip install 'volcengine-python-sdk[ark]'` | 别名 `jimeng`/`doubao`；新版 5.0 出来后换 `--model` 即可 |
| `dashscope`（通义万相） | `wan2.2-t2i-plus`（默认）/ `wan2.2-t2i-flash` | `DASHSCOPE_API_KEY` | `pip install dashscope` | 别名 `wanx`；wan2.5+ image 走新接口，用本脚本请选 2.2 系列 |

比例 `--aspect`（9:16 / 4:5 / 1:1 / 16:9）会自动映射成各家支持的 size。
**风格3（HTML 渲染）不需要任何 key**，没有 API key 时全程可用它出图，中文零错字。

示例：
```bash
python3 scripts/gen_image.py --provider openai    --prompt "..." --out cover.png --aspect 9:16
python3 scripts/gen_image.py --provider ark       --prompt "..." --out img2.png  --aspect 4:5
python3 scripts/gen_image.py --provider dashscope --prompt "..." --out img3.png  --aspect 9:16
```

---

## 风格 1 · 深色科技氛围大图（LLM 文生图）

- **适用**：封面、概念图、场景图
- **观感**：深蓝/暗紫底 + 青色/品红辉光，未来感、留白、有质感
- **工具**：`scripts/gen_image.py`（Gemini，flash 快 / pro 字准）
- **比例**：封面 9:16，内页 4:5 或 1:1

**提示词模板**：
```
A modern dark-tech editorial illustration for a Xiaohongshu cover.
Theme: {主题一句话}.
Style: deep navy-to-purple gradient background, cyan and magenta neon glow,
soft volumetric light, minimal, high-end, lots of negative space, 3D-ish abstract shapes.
{若需中文大字}: render the Chinese text "{标题文字}" large, bold, centered, crisp and accurate.
No watermark, no extra logos. Aspect 9:16.
```

## 风格 2 · 信息图 / 数据冲击图（LLM 文生图，带中文）

- **适用**：罗列数据、对比、能力盘点（用 Nano Banana **pro** 模型，中文字渲染更准）
- **观感**：信息图排版，数字醒目，图标化，配色与封面统一
- **工具**：`scripts/gen_image.py --model pro`

**提示词模板**：
```
A clean infographic poster, vertical 4:5, dark-tech theme matching a navy+cyan palette.
Title in Chinese: "{信息图标题}".
Show {N} key data points as bold large numbers with short Chinese labels:
{逐条：数字 + 标签}.
Use simple line icons, clear hierarchy, generous spacing, no clutter.
Render all Chinese text accurately and legibly. No watermark.
```

## 风格 3 · HTML 卡片 / 金句大字板（HTML 渲染）

- **适用**：金句收尾、步骤流程、清单卡（文字 100% 可控、零错字）
- **观感**：PPT 极简风——超大字、强对比、单色强调、克制留白
- **工具**：写一个 HTML 文件 → `scripts/shot.py` 截图成 PNG
- **优势**：中文绝不出错，排版精准，可放表格/列表

**HTML 骨架**（存成 .html 后用 shot.py 截图，尺寸 1080x1350）：
```html
<div id="card" style="width:1080px;height:1350px;display:flex;flex-direction:column;
  justify-content:center;padding:90px;box-sizing:border-box;
  background:linear-gradient(160deg,#10131f,#1b2440);color:#fff;
  font-family:'PingFang SC','Noto Sans SC',sans-serif;">
  <div style="font-size:34px;color:#3fd0ff;letter-spacing:4px;">{小标签}</div>
  <div style="font-size:88px;font-weight:800;line-height:1.2;margin-top:24px;">{金句主文案}</div>
  <div style="font-size:30px;color:#9aa6c4;margin-top:40px;line-height:1.6;">{补充说明}</div>
</div>
```
截图命令：`python3 scripts/shot.py --html card.html --out img_quote.png --selector "#card" --w 1080 --h 1350`

---

## 配图清单建议（6-9 张）

| 序号 | 角色 | 推荐风格 |
|---|---|---|
| 1 | 封面（标题大字） | 风格1 或 风格3 |
| 2 | 核心数据/对比 | 风格2（信息图） |
| 3 | 概念图 | 风格1 |
| 4 | 能力/功能盘点 | 风格2 或 风格3 |
| 5 | 场景/案例 | 风格1 |
| 6 | 金句收尾 | 风格3（HTML 金句板） |
| 7-9 | 按需补充 | 任意，保持配色统一 |

> ⚠️ 全套图保持**同一配色与构图语言**，让 6-9 张像一组。出图后必须跑 `scripts/watermark.py` 打「AI生成」水印。
