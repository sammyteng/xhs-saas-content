---
name: xhs-saas-content
description: 把 SaaS/AI 工具卖点做成可发布的小红书图文（长文+6-9配图）+发布模拟器
---

# xhs-saas-content · 小红书 SaaS 内容生成器

把一个软件/SaaS/AI 工具的卖点，做成一篇**能直接发小红书**的图文：第一人称长文 + 6-9 张统一风格的配图 + 一个左右两屏的「发布模拟器」预览。所有图和文都带「AI生成」标注。

## 1. 目标定义（终态）

运行结束时，产出目录里**已经具备**一篇可发布的小红书内容：
- 一份去过 AI 味、贴合所选风格的正文（标题 + 长文 + 标签）。
- 6-9 张配色构图统一、且都已打上「AI生成」水印的图片。
- 一个 `小红书模拟器.html`，左屏可翻图、右屏看完整文案，含「本内容由 AI 生成」标注。
- 一份 `content.json` 记录全部文案与图片清单。

不是「给一段建议」，而是**交付一套能直接用的成品**。

## 2. 验收清单（全满足才算完成）

- [ ] `content.json` 存在，含 title / body / tags / images，正文非空。
- [ ] 正文已过 `styles/writing-deai.md` 自检：排比≤1、金句≤1、破折号≤1、有真人语气与不确定表达。
- [ ] 图片数量在 6-9 张之间，且来自同一配色/构图语言。
- [ ] 每张图右下角都有「AI生成」水印（80% 不透明度）——运行过 `scripts/watermark.py`。
- [ ] `小红书模拟器.html` 能打开，图片轮播正常，右屏文案完整无截断，含「AI生成」标注。
- [ ] 产出目录自包含：把 html 和图片放一起就能直接看。

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
- 默认值：文章风格按内容类型推荐并让用户 N 选 1；图片默认 6 张；输出目录默认 `./xhs-output`。

## 4. 工作流（含自循环）

```
STEP 0  复述：把「目标定义」和「验收清单」打印到 stdout，确认听懂了再动手。
STEP 0b 读 styles/article-styles.json，按内容类型推荐 2-3 个风格 → 用户 N 选 1。
STEP 1  写初稿正文（标题+长文+标签），套用所选风格的人设与结构。
STEP 2  按 styles/writing-deai.md 改写去 AI 味。
STEP 3  读 styles/image-styles.md，根据正文内容推荐 3 条生图提示词 → 用户确认/微调。
STEP 4  出图 6-9 张：
          - 风格1/2：python3 scripts/gen_image.py --provider <gemini|openai|ark|dashscope> --prompt "..." --out xxx.png [--model pro] [--aspect 9:16]
          - 风格3：写 HTML → python3 scripts/shot.py --html card.html --out xxx.png --selector "#card"
STEP 5  打水印：python3 scripts/watermark.py --dir <输出目录>
STEP 6  写 content.json（文案+images 列表）。
STEP 7  生成模拟器：python3 scripts/build_simulator.py --content content.json --out 小红书模拟器.html
STEP 8  ★自检循环★ 逐条核对「验收清单」：
          - 不满足 → 定位是哪条 → 回到对应 STEP 修复 → 重新自检
          - 全满足 → 写一行成功摘要 → 退出（码 0），把输出目录与模拟器路径交给用户
          - 循环 ≥3 轮仍未全满足 → 写「未达成」清单（缺哪条+原因）到 <输出目录>/build.log，
            标 [TODO]，按「失败回执」返回（码 2），不假装完成
```

**自循环要点**：图少了就补图；有错字回 STEP1；图风格不统一就改提示词重出；水印漏了重跑 STEP5。改完一定重新走 STEP8，别跳。

## 5. 副作用与权限

- **写入**：只写用户指定的输出目录（默认 `./xhs-output`），不碰其他路径。
- **网络/API**：风格1/2 调用所选生图模型（Gemini / OpenAI / 豆包·即梦 / 通义万相）。所有 key **从环境变量读取，绝不写死在文件里**。
- **依赖**：`pip install pillow playwright` + `playwright install chromium`（风格3）；生图按所选 provider 装其一：`google-genai` / `openai` / `volcengine-python-sdk[ark]` / `dashscope`。
- **破坏性**：watermark.py 会就地覆盖图片，但首次会把原图备份到 `<dir>/orig/`，可还原。不删除任何用户文件。
- **发布**：本 skill 只生成内容，**不自动发布**到小红书。

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
- `scripts/watermark.py` — 批量打「AI生成」水印
- `scripts/build_simulator.py` — content.json → 小红书模拟器 HTML
- `examples/content.sample.json` — 示例文案（虚构产品，可直接套改）
