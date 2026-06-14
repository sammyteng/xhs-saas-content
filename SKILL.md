---
name: xhs-saas-content
description: 一站式小红书 SaaS 内容生成器：从产品卖点分析（JTBD）、爆款封面生成、内容正文创作、内页配图设计，到可编辑发布模拟器。含内容合规检测（P0 红线拦截 + P1 风险拦截）。
---

# xhs-saas-content · 一站式小红书 SaaS 内容生成器

把一个软件/SaaS/AI 工具的原始卖点，经过 JTBD 框架提炼、封面图与多图排版设计，做成一篇**能直接发小红书**的完整图文：一键生成卖点分析 + 爆款封面 + 1-9 张去 AI 味的配图 + 第一人称长文 + 一个可在线编辑的「发布模拟器」。

## 1. 目标定义（终态）

运行结束时，产出目录里**已经具备**一篇包含封面和内页的完整小红书内容包：
- **1 张爆款封面图**（`cover.png` 或 `cover.jpg`），符合小红书 3:4 比例，仅包含用户大标题、副标题与偏好品牌名（无系统风格角标，人物长相一致，但面部表情合理调整）。
- 一份去过 AI 味、贴合所选风格的正文（**3 个候选标题**[各≤20字符] + 长文 + 标签）。
- **1-9 张**视觉语言统一、且**不踩「一眼 AI」雷区**的配图（数量按内容定，不固定，使用 cover 的 `designToken` 映射实现色调和氛围一致）。
- 一份 `content.json`（含 titles/body/tags/images/image_prompts/designToken/compliance 等）。
- 一个**可编辑** `小红书模拟器.html`：可点标题切换、可编辑正文/标题、支持单图修改提示词重生成/换图。
- 一个 `小红书模拟器_分享版.html`：**图片全部 base64 内嵌成单文件**，发给别人不丢图（只读）。

**交付物 = `content.json` + 模拟器（编辑版 + 分享版）+ 封面图 + 内容配图**。不额外生成中间分析文档（JTBD 分析结果直接写入 `content.json` 的 `product_analysis` 字段）。

**发布确认**：建议在发布前由用户确认内容，但自动化场景可跳过确认直接交付。本 skill 只生成内容，**不自动发布**到小红书。

## 2. 验收清单（全满足才算完成）

- [ ] `cover.png`（或 `cover.jpg`）封面图存在，画面不带任何系统风格小字、分类名、栏目标签等，仅有用户大标题、副标题与配置的品牌名/Logo；人物如果存在，五官长相与输入人物照保持一致，表情允许调整。
- [ ] `content.json` 存在，含 **titles（3 个，各≤20 字符）** / body / tags / images / image_prompts / product_analysis / compliance（含 `ai_disclosure`），正文非空。
- [ ] 正文已过 `styles/writing-deai.md` 自检：排比≤1、金句≤1、破折号≤1、有真人语气与不确定表达。
- [ ] 正文字数落在所选风格的 `word_count` 区间内（不超 1000 字）；标签 6-10 个、符合 `article-styles.json` 的 `tag_strategy`（大词+场景词+长尾词+品牌词，全部贴合正文）。
- [ ] **内容合规检测已通过**：P0（9 类红线）与 P1（8 类风险）均零命中，结果记录在 `content.json` 的 `compliance` 字段。
- [ ] **AIGC 标识已落地（2026 头号红线）**：`compliance.ai_disclosure` 非空，正文/首图简介带 AI 声明，交付摘要提醒用户发布时勾选【内容类型声明→笔记包含 AI 合成内容】。
- [ ] **无虚假体验**：第一人称未假装亲历/未编造身份战绩与效果数据（除非确有真实体验且数据可追溯），否则按 P0-2 改为客观口径。
- [ ] 内容配图数量 **1-9 张**，视觉语言统一且与封面色调、氛围一致（通过 `cover-bridge.json` 映射）；**逐张过 `image-styles.md` 的「负面清单」**，无霓虹/赛博/悬浮芯片/发光3D字等「一眼 AI」元素。
- [ ] `小红书模拟器.html`（编辑版）能打开：包含封面图及内容配图，轮播正常、3 标题可点选、正文/标题可编辑。
- [ ] `小红书模拟器_分享版.html` 是单文件、图片已内嵌（`grep data:image` 命中），断网也能看图。
- [ ] 产出目录自包含；**不打「AI生成」水印**。
- [ ] 偏好已落盘：首次运行写了 profile，保存了 `brand_name`，二次运行 `profile.py show` 能读到并复用，未重复询问风格与品牌名。
- [ ] 防同质化：本篇创意维度经 `diversity.py check` 与最近 6 篇无 ≥3 维撞车，且已 `record` 记账。

未全部勾掉前，不得向用户报「完成」。

## 3. 输入契约

用户需提供：
- **产品原始信息**：产品名 + 功能描述 + 卖点/数据/特色等（必填，无需精细包装，由 Skill 自动提炼）。
- **内容类型**：行业观点 / 教程 / 选型 / 经验 / 种草 / 测评 / 速报（用于推荐风格）。
- **品牌名称** `brand_name`（必填，首次指定后存入 profile 自动复用）：图上显示的品牌或 Logo 文字，用以强化 IP。
- **封面人物照** `cover-image`（可选）：如果是需要人物半身像/大头贴的封面风格，提供一张人物照片路径。
- **封面风格** `cover-style`（可选）：22 种内置封面风格 ID 之一，默认根据产品性质自动匹配推荐。
- **生图能力**（二选一，自动判断）：
    - **Agent 自带生图**（推荐）：如在 Codex、Antigravity、Claude 等具备图片生成能力的 Agent 环境中运行，Agent 直接按提示词生图，**无需配置任何 API Key**，风格 1/2/3 均可使用。
    - **独立使用 / 手动配置 API**：若使用者自己运行脚本，可配置以下任一 API key（风格 1/2 需要）；没有 key 时可只用风格 3（HTML 渲染）出图。
    - `gemini`：`GEMINI_API_KEY` / `GOOGLE_AI_API_KEY`
    - `openai`：`OPENAI_API_KEY`（支持 `--base-url` 接兼容聚合站）
    - `ark`（豆包·即梦/Seedream）：`ARK_API_KEY`
    - `dashscope`（通义万相）：`DASHSCOPE_API_KEY`
- 默认值：文章风格按内容类型推荐并让用户 N 选 1；**标题产出 3 个候选（各≤20 字符）**；**配图按内容定 1-9 张**（不固定）；输出目录默认 `./xhs-output`。
- **偏好记忆**：首次选定的 文案/图片风格 + 生图参数 + 品牌名称 会存进 profile（`scripts/profile.py`），之后**自动复用、不再重复询问**；想改随时说「调整风格」或「修改品牌名」。
- **防同质化**：profile 只锁**品牌层**(作者/IP/语气/品牌名)；**创意层**(角度/风格/结构/钩子/配图/标题)由 `scripts/diversity.py` 每篇轮换并查重，多篇不撞。可 `profile.py set --rotate false` 关轮换、`--style-pool A,B,F` 限定风格池。撞车松紧可调：`--clash-dims N`(默认3)、`--window N`(默认6)，也可 `diversity.py check --clash-dims/--window` 临时覆盖、`diversity.py config` 看当前生效值。
- **封面联动**：本 Skill 在生成封面时会把封面使用的配色与设计参数输出为 `design-token.json`，内容配图自动加载该 Token 并通过 `cover-bridge.json` 映射适配内容图的色彩与氛围风格，确保封面与内页风格完美统一。

## 4. 工作流（含自循环）

```
STEP 0   复述：把「目标定义」和「验收清单」打印到 stdout，确认听懂了再动手。
STEP 0a  读偏好与品牌：python3 scripts/profile.py show
          - 已存且未调整偏好 → 读取 `brand_name`、封面风格、文章风格、图片风格、生图参数。
          - 首次运行或用户请求修改：
             1. 询问并保存用户偏好的品牌名称 `brand_name`。
             2. 运行 `python3 scripts/profile.py set --brand "品牌名" --provider ... ` 保存基本配置。
STEP 0b  产品卖点提炼 (JTBD)：根据用户输入的产品原始信息，参考 `styles/product-discovery.md`：
          1. 转化"产品语言"为"用户人话语言"。
          2. 完成 JTBD 提炼，输出一句话定位、3-5 个人话卖点、人群画像与竞品差异。
          3. 结果存入 content.json 的 `product_analysis` 字段（不单独生成 md 文件）。
          4. 推荐符合内容特征的 1-2 个封面风格 ID 与文章风格。
STEP 0c  防同质化与定风格：
          - 结合推荐与 profile，由用户选定本次封面风格与文章风格。
          - 运行 `python3 scripts/diversity.py pick` 确定本篇的创意矩阵维度（角度/结构/钩子等）。
          - 运行 `python3 scripts/diversity.py check` 确保创意与最近 6 篇无 ≥3 维撞车。
STEP 0d  生成封面（优先级递降）：
          ① LLM 生图 + 人物形象（最优）：如用户提供了 cover-image（人物照），优先用 LLM 生图能力
            （Agent 自带或 API）按风格模板 prompt + 人物参考照生成带人物的封面。
          ② LLM 生图（次优）：无人物照时，仍用 LLM 生图能力按风格 prompt 直接生成纯设计封面。
          ③ HTML 渲染兜底（最后）：LLM 生图不可用或连续失败时，退回 HTML 模板 + playwright 截图。
          - 调用封面 skill 脚本生成封面：
            `node ../xhs-cover-skill/scripts/generate.mjs --title "大标题" --subtitle "副标题" --brand "品牌名" --style "风格ID" --image "人物照路径" --output-dir "输出目录" --aspect-ratio "3:4"`
          - 封面生成脚本运行后会在输出目录产出 `cover.png` 和 `design-token.json`。
          - 检查封面图：确保不带多余的系统标签小字；人物面部五官身份未改变，仅表情合理匹配。
STEP 1   写正文初稿：基于 JTBD 提炼结果和防同质化矩阵，写出 **3 个候选标题（各≤20字符）** + 长文 + 标签。
          - **字数**：按所选风格的 `word_count` 区间（见 `article-styles.json`）控制；小红书正文上限 1000 字，体感最优 600-800。
          - **标签**：按 `article-styles.json` 的 `tag_strategy` 出 6-10 个（品类大词 + 场景/人群中词 + 长尾词 + 1 品牌词），全部贴合正文、不堆无关热词。
          - **本地化**：把风格里科技/AI 味的人设与示例换成产品真实品类的说法（见 `article-styles.json._generalization`）。
STEP 2   去 AI 味改写：根据 `styles/writing-deai.md` 规范自检改写正文。
STEP 2a  ★内容合规检测★：按 `styles/content-compliance.md`（2026 现行）扫描标题+正文+标签+配图文字：
          - **P0（9 类红线）**：命中任一 → 必须修改后才能继续，否则发布大概率被删帖/限流/封号。
            本工具是 AI 生成器，**P0-1 AIGC 标识** 与 **P0-2 虚假体验** 必先过：
            ① 生成 `ai_disclosure`（如「本文由 AI 辅助创作」），正文结尾/首图简介补一行 AI 声明；
            ② 第一人称不假装亲历、不编造身份战绩与效果数据（无真实体验就用「据官方介绍/从功能看」等客观口径）。
          - **P1（8 类风险）**：命中任一 → 同样必须修改（软广特征/标题党/贬低竞品/无对比功效等）。
          - 检测结果写入 content.json 的 `compliance` 字段：
            { "ai_disclosure": "...", "p0_passed": true/false, "p0_issues": [...], "p1_passed": true/false, "p1_issues": [...], "checked_at": "ISO时间" }
            issues 元素：{ "rule": "P0-2", "text": "命中原文", "location": "title|body|tags", "fix": "建议改法" }。
          - P0 或 P1 未通过 → 回 STEP 1 重写相关部分，再重新检测，直到全部通过。
STEP 3   设计内容配图提示词：
          - 自动加载步骤 0d 导出的 `design-token.json`，通过 `styles/cover-bridge.json` 映射内容配图的设计规范（色彩、氛围等）。
          - 根据正文逻辑规划 1-9 张内容配图，按照 `styles/image-styles.md` 生成包含 `designToken` 的提示词。
          - **务必对照「避免一眼 AI」负面清单**进行初步自检。
STEP 4   生成内容配图（优先级同封面）：
          ① LLM 生图（Agent 自带或 API）：优先用 LLM 按提示词直接生成配图。
          ② HTML 渲染兜底：LLM 不可用时，写 HTML → python3 scripts/shot.py 截图。
          - 生成后再次对照负面清单（无发光3D字、悬浮芯片等）自检。
STEP 5   写 content.json：整理所有标题、正文、标签、配图路径（含 `cover.png` 及内容配图）、提示词、JTBD 分析、合规检测结果（`compliance` 含 `ai_disclosure`）。正文结尾/首图简介须带 AI 声明（P0-1）。
STEP 6   构建小红书模拟器：
          - 运行 `python3 scripts/build_simulator.py --content content.json --out 小红书模拟器.html`
          - 运行 `python3 scripts/build_simulator.py --content content.json --out 小红书模拟器_分享版.html --embed`
STEP 7   ★自检循环★：
          - 逐一勾选「验收清单」，如有任何不符合，返回对应的 STEP 重新生成或修正。
          - 全部通过后，运行 `python3 scripts/diversity.py record` 记账，输出交付摘要，以退出码 0 正常结束。
          - 交付物：content.json + 模拟器（编辑版+分享版）+ 图片文件。不额外生成其他文件。
          - 交付摘要须提醒用户：**发布时在【设置→内容类型声明】勾选「笔记包含 AI 合成内容」**（P0-1 AIGC 标识，2026 红线）。
          - 不发送飞书/钉钉/邮件等渠道通知，仅在 stdout 输出交付摘要。
```

**自循环要点**：图少了就补、多了就删（1-9 自由）；有错字回 STEP1；图踩 AI 味雷区就改提示词重出；分享版忘了 `--embed` 会丢图，重生成。改完一定重新走 STEP7，别跳。

## 5. 内容合规检测规范

> 发布前自动扫描标题、正文、标签、配图文字，分 P0（红线拦截）和 P1（风险拦截）两级。
> 依据 2026 现行官方文本（公约 2.0 / 社区规范 / AIGC 标识办法等）蒸馏，完整规则与依据见 `styles/content-compliance.md`。

### P0 · 红线拦截（命中任一 → 必须修改）

| 类别 | 规则 | 示例 / 依据 |
|------|------|------|
| **P0-1 AIGC 未标识** ⭐ | AI 内容必须显式标识，否则强制补标+限流 | 缺 `ai_disclosure`、正文无 AI 声明 ·《AIGC 标识办法》 |
| **P0-2 虚假体验/虚构人设** ⭐ | 不编造亲历经历/身份战绩/效果数据 | ❌「我亲测三个月」（实为 AI 据资料生成）· 公约2.0 第3/20条 |
| **P0-3 诱导互动** | 禁止互动换利益 | ❌「点赞+收藏，私信领教程」「双击❤️抽奖」 |
| **P0-4 免费送/福利引导** | 禁止以福利为钩子换互动 | ❌「免费领取」「转发抽送」「评论区送福利」 |
| **P0-5 互赞互关/涨粉** | 禁止求关注/养号话术 | ❌「互关互赞」「关注必回」「新号求关注」 |
| **P0-6 违禁词/极限词** | 禁《广告法》第九条极限词；无资质勿荐医疗/投资/购房 | ❌「全网最低」「国家级」「无副作用」·《广告法》第9条 |
| **P0-7 站外导流** | 禁联系方式（含谐音）/外链/二维码/口令/隐晦话术 | ❌「加V/V心：xxx」「淘宝搜索」「私信了解优惠」·《交易导流细则》 |
| **P0-8 批量无意义问答** | 禁自问自答刷互动 | ❌「Q: 好用吗？A: 超好用！」×5 条刷屏 |
| **P0-9 垂类准入**（条件触发） | 医疗/医美/金融荐股/教培/烟酒，无资质禁碰 | 2026-02 医疗医美三新规几乎全禁 |

### P1 · 风险拦截（命中任一 → 必须修改）

| 类别 | 说明 / 依据 |
|------|------|
| P1-1 软性引导互动 | 「觉得有用可以收藏一下」「欢迎评论区讨论」等轻度引导，限流风险，必须改掉 |
| P1-2 模糊功效/无对比 | 「效果立竿见影」「用了就回不去了」等无数据夸张，必须弱化或删除（公约2.0 第7条）|
| P1-3 对比贬低竞品 | 「比 XX 好用 100 倍」等无数据主观贬低，改为客观对比或删除（公约2.0 第24条）|
| P1-4 敏感话题边缘 | 薪资/裁员/政策评价、制造性别地域职业对立，规避或模糊化（公约2.0 第13条）|
| P1-5 外部提及 | 提到产品官网/其他平台名，有导流嫌疑，删除或模糊化 |
| P1-6 软广特征 | 无真实体验、堆砌官方宣传语句，翻成真人体感（社区规范 4.1.4）|
| P1-7 标题党/文题不符 | 夸张标题正文撑不起，改到名副其实（社区规范 4.1.2）|
| P1-8 炫富/夸大消费 | 炫耀远超常人消费、夸大财富，弱化（公约2.0 第5条）|

## 6. 副作用与权限

- **写入**：只写用户指定的输出目录（默认 `./xhs-output`）；偏好 `~/.config/xhs-saas-content/profile.json` 与历史账本 `~/.config/xhs-saas-content/history.json`（可用 `XHS_PROFILE`/`XHS_HISTORY` 改路径）。其余路径不碰。
- **网络/API**：Agent 自带生图时无需外部 API；独立使用时风格 1/2 调用所选生图模型（Gemini / OpenAI / 豆包·即梦 / 通义万相）。所有 key **从环境变量读取，绝不写死在文件里**。
- **依赖**：`pip install pillow playwright` + `playwright install chromium`（HTML 渲染兜底）；生图按所选 provider 装其一：`google-genai` / `openai` / `volcengine-python-sdk[ark]` / `dashscope`。
- **本地服务**：`scripts/serve.py` 起本地 http 服务（默认 127.0.0.1:8000），仅供编辑版模拟器调用单图重生成/换图。
- **破坏性**：不就地覆盖原图（重生成/换图都写新文件名）；不删除任何用户文件。
- **通知**：不发送飞书/钉钉/邮件/Slack 等任何外部渠道通知。所有交付信息仅通过 stdout 输出。
- **发布**：本 skill 只生成内容，**不自动发布**到小红书。建议发布前由用户确认，自动化场景可跳过确认直接交付内容包。

## 7. 失败回执（不静默退出）

任一步骤失败时：
1. **明确报错**：打印失败的 STEP、命令、原始错误信息。
2. **给备选方案**：
   - 没有 API key 且 Agent 无生图能力 / 生图失败 → 换一家 provider，或退回 HTML 渲染兜底出图。
   - playwright 没装 → 提示安装命令，或改用 LLM 生图。
   - 中文出错字 → 优先 `--provider gemini --model pro`，或退回 HTML 渲染兜底（零错字）。
   - 模型命中安全过滤 → 调整提示词重试（最多重试 1 次）。
3. **不假装成功**：未达成验收清单就如实说明缺哪条、卡在哪里，让用户决策。
4. **回执落盘**：把失败/未达成清单写入 `<输出目录>/build.log`（含时间、失败 STEP、原始报错）。
5. **退出码约定**：成功 `0`；验收未达成 `2`；脚本崩溃 `1`。便于被其它流程/调度判断。

## 文件索引

- `styles/product-discovery.md` — 产品卖点提炼与 JTBD 转化方法论
- `styles/content-compliance.md` — 小红书内容合规检测规范（P0 红线 + P1 风险）
- `styles/article-styles.json` — 8 种文章风格（A-H，各带 `word_count` 字数区间）+ 内容类型→风格推荐表 + `tag_strategy` 标签生成规范
- `styles/image-styles.md` — 3 种图片风格 + 提示词模板 + 配图清单
- `styles/writing-deai.md` — 去 AI 味改写清单与自检
- `styles/angle-matrix.md` — 选题角度矩阵 + 钩子/结构/标题轮换池（防同质化）
- `styles/cover-bridge.json` — 封面 designToken → 内容图视觉适配映射表（bgTone/fontVibe 映射）
- `scripts/gen_image.py` — 多模型文生图（gemini/openai/ark·即梦/dashscope）
- `scripts/shot.py` — HTML → 高清 PNG（playwright，仅作为 LLM 生图的兜底方案）
- `scripts/build_simulator.py` — content.json → 模拟器 HTML（默认编辑版；加 `--embed` 出图片内嵌的分享版）
- `scripts/serve.py` — 编辑版本地后端（单图重生成/换图）
- `scripts/profile.py` — 风格/生图偏好记忆（show/set/reset），二次运行自动复用
- `scripts/diversity.py` — 反同质化引擎（pick/check/record + 历史账本），多篇轮换不撞
- `examples/content.sample.json` — 示例（含 3 候选标题 + image_prompts，虚构产品，可直接套改）
