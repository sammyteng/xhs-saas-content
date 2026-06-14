# 内置封面生成器（cover/） — 人物照封面

> ⚠️ **本目录已并入 `xhs-saas-content`**，是它的「人物照封面生成器」。在本 skill 内的用法见主 `SKILL.md` 文末「附 · （可选）配图」。
> - 命令：`node cover/scripts/generate.mjs --image 人物照 --style 风格ID --title "大标题" ...`（`--image` **必填**；不带参数运行可列出 22 种风格）
> - 首次：`cd cover && npm install`（装 sharp）
> - **需自配你自己的 key**（chat-image 兼容接口）：`XHS_COVER_API_KEY` + `--base-url` + `--model`，或 `~/.config/xhs-cover/config.json`。**仓库不含任何 key**。
> - 纯设计封面（无人物照）请改用 `scripts/gen_image.py`（images-API，如 gpt-image-2）。
>
> 以下为原独立 skill 文档（其中的 clone / 安装路径仅对「单独使用本目录」有效；并入后无需 clone）。

直接生成或修改小红书封面。本工具为通用 Agent Skill，不绑定特定客户端。支持在 Claude Code、Codex 或终端直接运行，通过配置多模态大模型 API Key（如 Gemini 或 OpenAI 兼容接口）即可一键完成爆款排版与合成。

---

## 效果预览

支持 22 种预设风格，覆盖职场、居家、综艺、文艺等各类场景。每个风格的具体定义与一句话描述请参考下方「风格列表」。

---

## 前置要求

- Node.js 18+（macOS / Linux / Windows 均支持）
- 多模态生图 API 凭证（如 Google AI Studio API Key 或 OpenAI 兼容代理 Key）

---

## 安装

选择你使用的客户端平台克隆本仓库：

**Claude Code：**
```bash
git clone https://github.com/sammyteng/xhs-cover-skill ~/.claude/skills/xhs-cover
cd ~/.claude/skills/xhs-cover && npm install
```

**Codex：**
```bash
git clone https://github.com/sammyteng/xhs-cover-skill ~/.codex/skills/xhs-cover-skill
cd ~/.codex/skills/xhs-cover-skill && npm install
```

**OpenClaw：**
```bash
git clone https://github.com/sammyteng/xhs-cover-skill ~/.openclaw/skills/xhs-cover
cd ~/.openclaw/skills/xhs-cover && npm install
```

然后在 OpenClaw 配置文件中添加 API 环境变量：
```yaml
skills:
  entries:
    xhs-cover:
      env:
        XHS_COVER_API_KEY: "你的 API Key"
        XHS_COVER_BASE_URL: "https://generativelanguage.googleapis.com/v1beta/openai"
        XHS_COVER_MODEL: "gemini-3-pro-image"
```

**或者使用安装脚本（自动检测平台）：**

```bash
curl -fsSL https://raw.githubusercontent.com/sammyteng/xhs-cover-skill/main/install.sh | bash
```

---

## 使用方法

在客户端输入任意触发词即可开始对话引导：
- `生成封面` / `小红书封面` / `制作封面` / `xhs封面`
- `修改封面`（在上一张图的基础上进行调整）

如果是在 Claude Code / 终端直接运行，需要先配置大模型 API Key（见下方「API 配置」）。

---

## API 配置

可以直接通过对话引导中的 Onboarding 步骤进行配置，也可以在本地手动配置。

### 方案 A：Google AI Studio

1. 访问 [aistudio.google.com/apikey](https://aistudio.google.com/apikey) 创建 API Key
2. 在 Skill Onboarding 中选择「Google AI Studio」，粘贴 Key 即可

> **关于免费**：Google AI Studio 有免费层级（无需绑卡），但**图片生成**功能是否在免费额度内会随 Google 的策略调整，建议在 [ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing) 确认最新情况。需要科学上网。

> **关于模型名称**：Gemini 图片生成模型的 API 名称会随版本迭代变化，请在 [ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models) 确认当前支持图片输出的模型名。

### 方案 B：第三方 API 代理

支持任意兼容 OpenAI 格式的代理服务（无需科学上网，按量付费）。按需自行选择服务商，配置时提供 Base URL、API Key 和模型名称即可。

配置文件保存在 `~/.config/xhs-cover/config.json`：

```json
{
  "apiType": "third-party",
  "apiKey": "your-api-key",
  "baseUrl": "https://your-provider.com",
  "model": "gemini-3-pro-image-preview",
  "outputDir": "~/Desktop/XHS封面",
  "defaultAspectRatio": "3:4"
}
```

---

## 命令行直接使用

也可以绕过 Skill，直接调用脚本：

```bash
node ~/.codex/skills/xhs-cover-skill/scripts/generate.mjs \
  --image "/path/to/photo.jpg" \
  --style "hand-drawn-border" \
  --title "你的封面大标题" \
  --subtitle "副标题（可选）" \
  --aspect-ratio "3:4" \
  --count 1
```

**支持的参数：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--image` | 人物照片路径（必填） | - |
| `--style` | 风格ID（必填，见下方列表） | - |
| `--title` | 主标题（必填） | - |
| `--subtitle` | 副标题 | 空 |
| `--extra` | 额外要求 | 空 |
| `--count` | 生成数量（最多5） | 1 |
| `--aspect-ratio` | 比例：3:4 / 1:1 / 9:16 / 4:3 | 3:4 |
| `--output-dir` | 保存目录 | ~/Desktop/XHS封面 |
| `--api-key` | API Key | 读配置文件 |
| `--base-url` | API Base URL | 读配置文件 |
| `--api-endpoint` | 完整端点URL（Google适用） | 读配置文件 |
| `--model` | 模型名称 | 读配置文件 |
| `--rotate` | 手动旋转：90/180/270 | 自动EXIF |
| `--no-auto-orient` | 跳过EXIF自动旋转 | false |
| `--test` | 只测试API连通性 | false |

---

## 风格展示与列表

本 Skill 整合了 22 种各行业和自媒体最常用的排版与视觉风格：

### 1. 科技/AI/极客类

<table>
  <tr>
    <td align="center" width="20%">
      <img src="assets/styles/tech-finance-analytical.jpg" width="160"><br>
      <b>科技财经分析</b><br><code>tech-finance-analytical</code>
    </td>
    <td align="center" width="20%">
      <img src="assets/styles/geek-workflow-dialog.jpg" width="160"><br>
      <b>极客工作流</b><br><code>geek-workflow-dialog</code>
    </td>
    <td align="center" width="20%">
      <img src="assets/styles/dark-glow.jpg" width="160"><br>
      <b>深色发光</b><br><code>dark-glow</code>
    </td>
    <td align="center" width="20%">
      <img src="assets/styles/background-big-text.jpg" width="160"><br>
      <b>背景大字</b><br><code>background-big-text</code>
    </td>
    <td align="center" width="20%">
      <img src="assets/styles/workplace-big-text.jpg" width="160"><br>
      <b>职场大字</b><br><code>workplace-big-text</code>
    </td>
  </tr>
</table>

### 2. 搞笑/综艺/网感类

<table>
  <tr>
    <td align="center" width="20%">
      <img src="assets/styles/ai-avatar-sticker.jpg" width="160"><br>
      <b>AI大头贴</b><br><code>ai-avatar-sticker</code>
    </td>
    <td align="center" width="20%">
      <img src="assets/styles/hurricane-adventure.jpg" width="160"><br>
      <b>影视飓风</b><br><code>hurricane-adventure</code>
    </td>
    <td align="center" width="20%">
      <img src="assets/styles/hand-drawn-border.jpg" width="160"><br>
      <b>手绘边框</b><br><code>hand-drawn-border</code>
    </td>
    <td align="center" width="20%">
      <img src="assets/styles/sticker-energy.jpg" width="160"><br>
      <b>贴纸活力</b><br><code>sticker-energy</code>
    </td>
    <td align="center" width="20%">
      <img src="assets/styles/pink-yellow-playful.jpg" width="160"><br>
      <b>粉黄俏皮</b><br><code>pink-yellow-playful</code>
    </td>
  </tr>
</table>

### 3. 职场/知性/学习类

<table>
  <tr>
    <td align="center" width="20%">
      <img src="assets/styles/professional-clean.jpg" width="160"><br>
      <b>专业简洁</b><br><code>professional-clean</code>
    </td>
    <td align="center" width="20%">
      <img src="assets/styles/professional-woman.jpg" width="160"><br>
      <b>职场女性</b><br><code>professional-woman</code>
    </td>
    <td align="center" width="20%">
      <img src="assets/styles/study-room-intellectual.jpg" width="160"><br>
      <b>书房知性</b><br><code>study-room-intellectual</code>
    </td>
    <td align="center" width="20%">
      <img src="assets/styles/thinking-question.jpg" width="160"><br>
      <b>思考提问</b><br><code>thinking-question</code>
    </td>
    <td align="center" width="20%">
      <img src="assets/styles/home-motivation.jpg" width="160"><br>
      <b>居家励志</b><br><code>home-motivation</code>
    </td>
  </tr>
</table>

### 4. 日常/居家/生活类

<table>
  <tr>
    <td align="center" width="25%">
      <img src="assets/styles/cozy-home.jpg" width="160"><br>
      <b>温馨居家</b><br><code>cozy-home</code>
    </td>
    <td align="center" width="25%">
      <img src="assets/styles/outdoor-handwriting.jpg" width="160"><br>
      <b>户外手写</b><br><code>outdoor-handwriting</code>
    </td>
    <td align="center" width="25%">
      <img src="assets/styles/dashed-decoration.jpg" width="160"><br>
      <b>虚线装饰</b><br><code>dashed-decoration</code>
    </td>
    <td align="center" width="25%">
      <img src="assets/styles/split-screen-tags.jpg" width="160"><br>
      <b>分屏标签</b><br><code>split-screen-tags</code>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="assets/styles/yellow-pink-banner.jpg" width="160"><br>
      <b>黄粉横幅</b><br><code>yellow-pink-banner</code>
    </td>
    <td align="center" width="25%">
      <img src="assets/styles/neon-contrast.jpg" width="160"><br>
      <b>霓虹撞色</b><br><code>neon-contrast</code>
    </td>
    <td align="center" width="25%">
      <img src="assets/styles/multi-layer-layout.jpg" width="160"><br>
      <b>多层排版</b><br><code>multi-layer-layout</code>
    </td>
    <td align="center" width="25%">
      -
    </td>
  </tr>
</table>

---

## 注意事项

- 图片会自动读取 EXIF 方向信息并旋转（手机拍摄的竖版照片无需手动处理）
- 图片超过 4MB 会自动压缩
- 建议每次生成间隔 8 秒以上，避免 API 连接问题
- 生成耗时约 30-60 秒

---

## 贡献指南

欢迎提交 PR！以下几类贡献特别受欢迎：

### 新增风格
在 `styles/` 目录下新建一个 JSON 文件（如 `styles/my-style.json`）：

```json
{
  "name": "风格中文名",
  "prompt": "详细的中文设计提示词..."
}
```

参考现有风格格式，确保包含【布局要求】【文字样式】【核心特效】【禁止事项】【氛围】几个区块。同时附上一张效果参考图放到 `assets/styles/` 目录。

### 改进现有提示词
如果你发现某个风格生成效果不好（比如文字乱码、构图不对），欢迎直接修改对应的 `prompt` 并附上改进前后的对比截图。

### 其他贡献
- 增加新的图片处理功能（如自动抠图、滤镜）
- 支持更多 API 提供商
- 改进 Onboarding 流程
- 修复 Bug

提交 PR 前请简单描述改动内容，如有效果图更好！

---

## License

MIT — 作者：[sammyteng](https://github.com/sammyteng/xhs-cover-skill)
