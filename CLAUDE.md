# xhs-saas-content

为 SaaS / 软件 / AI 工具一键产出**可直接发小红书**的图文内容**生成器**。纯内容生成——不含浏览器自动化、不操作账号、**不自动发布**。

## 定位

输入「产品信息 / 一个参考链接 / 啥都不给」，输出一个完整的小红书内容成品：
内容来源（本地素材 或 在线链接经 `agent-reach` 抓取 / 直接给 / 历史出题）→ JTBD 卖点提炼 → 先写文案（3 候选标题 + 正文 + 标签，不招骂）→ 内容合规检测（P0 红线 + P1 风险）→ 封面与配图（有 key 用 AI 图、无 key 用 HTML 卡片）→ 单文件只读发布模拟器。

交付物 = `content.json` + 模拟器（单文件只读）+ 封面与配图（**成品含图**：有 key 用 AI 图、无 key 用 HTML 卡片，必出真图）。只生成、**不发布**。

## 架构

单层结构：纯 Python 脚本 + `styles/` 配置。无服务端、无 CLI、无浏览器扩展。

- `SKILL.md` — 主流程（7 章：目标 / 验收 / 输入 / 工作流 / 合规 / 权限 / 失败回执）
- `styles/` — 文风 / 合规 / 去 AI 味 / 角度矩阵 / 封面联动等配置
- `scripts/` — A 层脚本（见下表）
- `examples/` `demo*/` — 示例与样例产出
- `cover/` — **已并入的封面生成器**（22 种人物封面风格 + `generate.mjs`，Node+sharp）；`node cover/scripts/generate.mjs` 调用，首次 `cd cover && npm install`。人物照封面走它（`--image` 必填、需用户自配 chat-image key）；纯设计封面走 `gen_image.py`。**仓库不含任何 key**（用户自配）。

### scripts/ 一览

| 脚本 | 作用 |
|--|--|
| `gen_image.py` | 多模型文生图（gemini / openai / ark·即梦 / dashscope） |
| `shot.py` | HTML → PNG（playwright，LLM 生图兜底，中文零错字） |
| `build_simulator.py` | content.json → 模拟器 HTML（`--embed` 出图片内嵌分享版） |
| `serve.py` | 编辑版模拟器本地后端（单图重生成 / 换图） |
| `profile.py` | 风格 / 品牌偏好记忆（show / set / reset） |
| `diversity.py` | 反同质化引擎（pick / check / record） |
| `title_utils.py` | 标题长度计算（≤20 字符校验） |
| `watermark.py` | 加 AI生成 水印工具（当前流程默认不调用） |

## Git 工作流

- 所有代码修改必须在分支上进行，禁止直接推送 main 分支
- 分支开发完成后通过 PR 合入 main

## 开发命令

```bash
ruff check scripts/        # Lint 检查
ruff format scripts/       # 代码格式化
```

## 代码规范

- 行长度上限 100 字符
- 完整 type hints，使用 `from __future__ import annotations`
- 用户可见错误信息使用中文
- JSON 输出 `ensure_ascii=False`

### 安全约束

- API key 仅从环境变量读取，**绝不写入任何文件**
- 只写用户指定输出目录（默认 `./xhs-output`）+ 偏好/历史账本（`~/.config/xhs-saas-content/`），其余路径不碰
- 不就地覆盖原图（重生成/换图都写新文件名），不删除用户文件
- 不发送飞书 / 钉钉 / 邮件等任何外部渠道通知，不自动发布到小红书
