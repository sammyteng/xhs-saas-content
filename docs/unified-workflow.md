# 封面 + 内容图 统一视觉工作流

> 先用内置 `cover/` 生成封面（有人物照时），再生成内容图，
> 通过 `design-token.json` 自动保持全套图视觉统一。

## 快速开始

```bash
# ① 生成封面（输出: cover.png + design-token.json）
node cover/scripts/generate.mjs \
  --image ./me.jpg \
  --style hand-drawn-border \
  --title "三步搞定 AI 工作流" \
  --output-dir ./xhs-output

# ② 生成内容图（自动读取封面色彩）
# —— LLM 文生图（风格 1/2）
python3 scripts/gen_image.py \
  --prompt "一个干净的办公桌上放着笔记本和咖啡" \
  --design-token ./xhs-output/design-token.json \
  --aspect 4:5

# —— HTML 卡片截图（风格 3）
python3 scripts/shot.py \
  --html card.html \
  --out ./xhs-output/img_quote.png \
  --design-token ./xhs-output/design-token.json
```

## 工作原理

```
cover/（内置封面生成器）              内容图生成
│                                     │
│  选风格（如 hand-drawn-border）    │
│  ↓                                 │
│  生成封面.png                     │
│  ↓                                 │
│  导出 design-token.json  ----→  读取 design-token.json
│    ├─ primaryColor               │  ↓
│    ├─ accentColor                │  cover-bridge.json 映射
│    ├─ bgTone                     │  ↓
│    ├─ fontVibe                   │  注入提示词色彩 + HTML 配色
│    ├─ mood                       │  ↓
│    └─ negativePromptHints        │  输出视觉统一的内容图
```

## design-token.json 示例

```json
{
  "source": "xhs-cover-skill",
  "coverStyleId": "hand-drawn-border",
  "coverStyleName": "手绘边框",
  "generatedAt": "2025-01-15T10:30:00.000Z",
  "designToken": {
    "primaryColor": "#FFD93D",
    "accentColor": "#1A1A1A",
    "bgTone": "light",
    "fontVibe": "playful",
    "mood": "活力/综艺/有趣",
    "negativePromptHints": "no corporate feel, no dark moody style, no tech elements"
  }
}
```

## bgTone 映射规则

| 封面 bgTone | 内容图适配 | HTML 卡片底色 | 氛围 |
|---|---|---|---|
| `dark` | 暗调摆拍 + 暗色 HTML | `#1d1d1f` | 专业、深度 |
| `light` | 明亮简约 + 浅色 HTML | `#f5f3ee` | 干净、杂志 |
| `warm` | 暖光实拍 + 暖色 HTML | `#faf6ef` | 温馨、居家 |

## 可以不用封面联动吗？

完全可以。不传 `--design-token` 时，xhs-saas-content 完全独立工作，和之前一样。
封面联动是可选增强，不是强制依赖。
