---
name: xhs-saas-content
description: 把 SaaS/AI 工具卖点做成可发布的小红书图文（长文+1-9配图）+可编辑发布模拟器
---

# xhs-saas-content · 小红书 SaaS 内容生成器

把一个软件/SaaS/AI 工具的卖点，做成一篇**能直接发小红书**的图文：第一人称长文 + 1-9 张不踩 AI 味的配图 + 一个可在线编辑的「发布模拟器」。

## 1. 目标定义（终态）

运行结束时，产出目录里**已经具备**一篇可发布的小红书内容：
- 一份去过 AI 味、贴合所选风格的正文（**3 个候选标题**[各≤20字符] + 长文 + 标签）。
- **1-9 张**视觉语言统一、且**不踩「一眼 AI」雷区**的配图（数量按内容定，不固定）。
- 一个**可编辑** `小红书模拟器.html`：点标题切换、点正文直接改、单图改提示词重生成/换图、「确认内容」保存。
- 一个 `小红书模拟器_分享版.html`：**图片全部 base64 内嵌成单文件**，发给别人不丢图（只读）。
- 一份 `content.json`（含 titles/body/tags/images/image_prompts）。

不是「给一段建议」，而是**交付一套能直接用、能在线改、能直接分享的成品**。

## 2. 验收清单（全满足才算完成）

- [ ] `content.json` 存在，含 **titles（3 个，各≤20 字符）** / body / tags / images / image_prompts，正文非空。
- [ ] 正文已过 `styles/writing-deai.md` 自检：排比≤1、金句≤1、破折号≤1、有真人语气与不确定表达。
- [ ] 图片数量 **1-9 张**，视觉语言统一；**逐张过 `image-styles.md` 的「负面清单」**，无霓虹/赛博/悬浮芯片/发光3D字等「一眼 AI」元素。
- [ ] `小红书模拟器.html`（编辑版）能打开：图片轮播正常、3 标题可点选、正文/标题可编辑、单图提示词框在。
- [ ] `小红书模拟器_分享版.html` 是单文件、图片已内嵌（`grep data:image` 命中），断网也能看图。
- [ ] 产出目录自包含；**不打「AI生成」水印**。

未全部勾掉前，不得向用户报「完成」。

## 3. 输入契约

用户需提供：
- **产品信息**：产品名 + 一句话定位 + 3-6 个卖点/数据（必填）。
- **内容类型**：行业观点 / 教程 / 选型 / 经验 / 种草 / 测评 / 速报（用于推荐风格）。
- **生图 API key**（任选一家，按 provider）——若要用 LLM 生图（风格1/2）。没有任何 key 时，可只用风格3（HTML 渲染）出图。
    - `gemini`：`GEMINI_API_KEY` / `GOOGLE_AI_API_KEY`
    - `openai`：`OPENAI_API_KEY`（支持 `--base-url` 接兼容聚合站）
    - `ark`（豆包·即梦/Seedream）：`ARK_API_KEY`
    - `dashscope`（通义万相）：`DASHSCOPE_API_KEY`
- 默认值：文章风格按内容类型推荐并让用户 N 选 1；**标题产出 3 个候选（各≤20 字符）**；**配图按内容定 1-9 张**（不固定）；输出目录默认 `./xhs-output`。

## 4. 工作流（含自循环）

```
STEP 0  复述：把「目标定义」和「验收清单」打印到 stdout，确认听懂了再动手。
STEP 0b 读 styles/article-styles.json，按内容类型推荐 2-3 个风格 → 用户 N 选 1。
STEP 1  写初稿：**3 个候选标题（各≤20 字符）** + 长文 + 标签，套用所选风格的人设与结构。
STEP 2  按 styles/writing-deai.md 改写去 AI 味。
STEP 3  读 styles/image-styles.md，**先读头部「避免一眼 AI」负面清单**，按内容定 1-9 张配图，
        逐张推荐提示词（默认偏写实/扁平/HTML，不要霓虹科技风）→ 用户确认/微调。
STEP 4  出图：
          - 风格1/2：python3 scripts/gen_image.py --provider <gemini|openai|ark|dashscope> --prompt "..." --out xxx.png [--model pro] [--aspect 9:16]
          - 风格3：写 HTML → python3 scripts/shot.py --html card.html --out xxx.png --selector "#card"
        每张出完**对照负面清单自检**，命中「霓虹/赛博/悬浮芯片/发光3D字/HUD」等就改提示词重出。
STEP 5  写 content.json（titles[3] / body / tags / images[1-9] / image_prompts / gen）。
STEP 6  生成模拟器：
          - 编辑版：python3 scripts/build_simulator.py --content content.json --out 小红书模拟器.html
          - 分享版：python3 scripts/build_simulator.py --content content.json --out 小红书模拟器_分享版.html --embed
        （需在线改图/确认保存时：python3 scripts/serve.py <输出目录> 起后端再用浏览器打开编辑版）
STEP 7  ★自检循环★ 逐条核对「验收清单」：
          - 不满足 → 定位是哪条 → 回到对应 STEP 修复 → 重新自检
          - 全满足 → 写一行成功摘要 → 退出（码 0），交付输出目录 + 两个 html 路径
          - 循环 ≥3 轮仍未全满足 → 写「未达成」清单（缺哪条+原因）到 <输出目录>/build.log，
            标 [TODO]，按「失败回执」返回（码 2），不假装完成
```

**自循环要点**：图少了就补、多了就删（1-9 自由）；有错字回 STEP1；图踩 AI 味雷区就改提示词重出；分享版忘了 `--embed` 会丢图，重生成。改完一定重新走 STEP7，别跳。

## 5. 副作用与权限

- **写入**：只写用户指定的输出目录（默认 `./xhs-output`），不碰其他路径。
- **网络/API**：风格1/2 调用所选生图模型（Gemini / OpenAI / 豆包·即梦 / 通义万相）。所有 key **从环境变量读取，绝不写死在文件里**。
- **依赖**：`pip install pillow playwright` + `playwright install chromium`（风格3）；生图按所选 provider 装其一：`google-genai` / `openai` / `volcengine-python-sdk[ark]` / `dashscope`。
- **本地服务**：`scripts/serve.py` 起本地 http 服务（默认 127.0.0.1:8000），仅供编辑版模拟器调用单图重生成/换图；「确认内容」写 `content.confirmed.json` 并自动生成分享版 html。
- **破坏性**：不就地覆盖原图（重生成/换图都写新文件名）；不删除任何用户文件。
- **发布**：本 skill 只生成内容，**不自动发布**到小红书（确认后进入发布流程，发布动作暂未实现）。

## 6. 失败回执（不静默退出）

任一步骤失败时：
1. **明确报错**：打印失败的 STEP、命令、原始错误信息。
2. **给备选方案**：
   - 没有 API key / 生图失败 → 换一家 provider，或退回风格3（HTML 渲染）出图。
   - playwright 没装 → 提示安装命令，或改用 LLM 生图。
   - 中文出错字 → 优先 `--provider gemini --model pro`，或退回风格3（HTML，零错字）。
   - 模型命中安全过滤 → 调整提示词重试（最多重试 1 次）。
3. **不假装成功**：未达成验收清单就如实说明缺哪条、卡在哪里，让用户决策。
4. **回执落盘**：把失败/未达成清单写入 `<输出目录>/build.log`（含时间、失败 STEP、原始报错）。
5. **退出码约定**：成功 `0`；验收未达成 `2`；脚本崩溃 `1`。便于被其它流程/调度判断。

## 文件索引

- `styles/article-styles.json` — 8 种文章风格（A-H）+ 内容类型→风格推荐表
- `styles/image-styles.md` — 3 种图片风格 + 提示词模板 + 配图清单
- `styles/writing-deai.md` — 去 AI 味改写清单与自检
- `scripts/gen_image.py` — 多模型文生图（gemini/openai/ark·即梦/dashscope）
- `scripts/shot.py` — HTML → 高清 PNG（playwright）
- `scripts/build_simulator.py` — content.json → 模拟器 HTML（默认编辑版；加 `--embed` 出图片内嵌的分享版）
- `scripts/serve.py` — 编辑版本地后端（单图重生成/换图/确认保存+自动生成分享版）
- `scripts/watermark.py` — （可选，默认不用）批量打水印工具
- `examples/content.sample.json` — 示例（含 3 候选标题 + image_prompts，虚构产品，可直接套改）
