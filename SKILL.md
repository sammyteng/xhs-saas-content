---
name: xhs-saas-content
description: 通用小红书内容生成器：内容来源（知识库/直接给/历史出题）→ JTBD 卖点提炼 → 文案（3 候选标题+正文+标签）→ 合规检测 → 封面与配图 → 只读发布模拟器。**默认产出含图成品**（有 key 用 AI 图、没 key 用 HTML 卡片，必出真图）；可问偏好但不卡流程；仓库不含 key。
---

# xhs-saas-content · 通用小红书内容生成器

把一个软件/SaaS/AI 工具的原始卖点，经过 JTBD 框架提炼，做成一篇**能直接发小红书**的内容草稿：卖点分析 + 去 AI 味第一人称长文（3 候选标题+标签）+ 配图建议 + 内容合规检测 + 一个只读「发布模拟器」预览。

> ⚙️ **默认产出完整成品（含图），不交半成品**：配图走降级链——有生图能力/key → AI 生图；**没有 → HTML 卡片出图（免 key、中文零错字）**。任何环境都出真图、都交成品，绝不留「配图建议」占位当交付。可问用户偏好（风格 / 要不要用 AI 图），但**不阻塞**：用户不答就由 AI 判断合理默认，直接产出完整成品。生图细节见文末「附 · 配图」。

## 1. 目标定义（终态）

运行结束时，产出目录里**已经具备一份可直接发小红书的完整图文成品**：
- 一份去过 AI 味、贴合所选风格的正文（**3 个候选标题**[各≤20字符] + 长文 + 标签）。
- **封面 + 1-9 张内页配图**（数量按内容定）：有生图能力/key 用 AI 图，否则用 HTML 卡片——**任何情况都出真图**，且不踩「一眼 AI」雷区。
- 一份 `content.json`（含 titles/body/tags/images/image_prompts/product_analysis/compliance）。
- 一个 `小红书模拟器.html`：**左图右文、单文件、图片内嵌、只读**，发给别人不丢图。

**交付物 = `content.json` + 模拟器（单文件只读）+ 封面与配图**。这是**成品**——`images` 必须有图（降级链保证），不是「文案 + 建议」的半成品。不额外生成中间分析文档（JTBD 结果写入 `product_analysis`）。

> **配图不可省、默认就生成**。出图优先级：① Agent 自带生图 / 配了 key（AI 图，封面 skill 或 gen_image）② 都没有 → HTML 卡片（playwright，免 key、零错字）。**可问偏好但不卡流程**，AI 判断默认值直接交成品。

**发布确认**：建议发布前由用户确认内容，自动化场景可跳过。本 skill 只生成内容，**不自动发布**到小红书。

## 2. 验收清单（全满足才算完成）

- [ ] `content.json` 存在，含 **titles（3 个，各≤20 字符）** / body / tags / **images（1-9 张真实图片路径，非空）** / image_prompts / product_analysis / compliance；正文非空。
- [ ] 正文已过 `styles/writing-deai.md` 自检：排比≤1、金句≤1、破折号≤1、真人语气、**不招骂**（不唱衰/取代读者职业，AI 帮手不替代）。
- [ ] 正文字数落在所选风格的 `word_count` 区间内（不超 1000 字）；标签 6-10 个、符合 `article-styles.json` 的 `tag_strategy`。
- [ ] **内容合规检测已通过**：P0（9 类红线）与 P1（8 类风险）均零命中，记入 `compliance`。
- [ ] **无虚假体验**（P0-2）：第一人称未假装亲历、未编造身份战绩与效果数据。（AI 声明默认关闭 🔕，不要求 `ai_disclosure`。）
- [ ] **封面 + 配图已真实生成（成品，非建议占位）**：`images` 已填 1-9 张真图——有 key 用 AI 图 / 无 key 用 HTML 卡片，总之**有图**。逐张过 `image-styles.md` 负面清单（无霓虹/赛博/发光3D字、无畸形手指/塑料皮肤、无乱码伪文字、无厂商水印）。
- [ ] **图上文字合规复检通过**：配图内嵌文字过 P0-6（违禁词）/P0-2（虚假数据）/P1-2（模糊功效），记入 `compliance` 且 `location=image_text`。
- [ ] `小红书模拟器.html` 能打开：**左图右文、单文件、图片已内嵌**（`grep data:image` 命中）、只读、断网也能看图。
- [ ] 偏好已落盘：首次写了 profile（品牌 + 内容风格），二次运行能复用、未重复询问。
- [ ] 防同质化：本篇创意维度经 `diversity.py check` 与最近 6 篇无 ≥3 维撞车，且已 `record` 记账。

未全部勾掉前，不得向用户报「完成」。**交付的是成品（含图），不是「文案 + 配图建议」的半成品。**

## 3. 输入契约

用户需提供：
- **内容来源**（3 选 1，决定选题/素材从哪来，见 STEP 0b）：
    - **模式 1 · 知识库提取**：给一个资料来源（文件夹 / 若干文件 .md/.txt/.pdf/.docx / 一段粘贴文本），Skill 自己读、自己挑选题挖卖点。通用，不绑定特定知识库。
    - **模式 2 · 直接给**：直接提供产品原始信息（默认）。
    - **模式 3 · 历史自动出题**：什么都不给，Skill 读 profile 的 `product_brief` + 历史账本自动出新选题（需先用模式 1/2 跑过一次存下 `product_brief`）。
- **产品原始信息**：产品名 + 功能描述 + 卖点/数据/特色等（**模式 1/2 必填**；模式 3 复用 profile 存的 `product_brief`，无需再给）。
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
- **偏好记忆（首轮一次配齐）**：首次运行一轮问齐 **品牌名 + 内容风格 + 图片风格 + 生图模型（默认 image-2 = OpenAI gpt-image-2）**，存进 profile（`scripts/profile.py`），之后**自动复用**。再次运行只问一句「沿用还是改风格」；想改随时说「改内容风格 / 改图片风格 / 改品牌 / 换生图模型」。
- **防同质化**：profile 只锁**品牌层**(作者/IP/语气/品牌名)；**创意层**(角度/风格/结构/钩子/配图/标题)由 `scripts/diversity.py` 每篇轮换并查重，多篇不撞。可 `profile.py set --rotate false` 关轮换、`--style-pool A,B,F` 限定风格池。撞车松紧可调：`--clash-dims N`(默认3)、`--window N`(默认6)，也可 `diversity.py check --clash-dims/--window` 临时覆盖、`diversity.py config` 看当前生效值。
- **封面联动**：本 Skill 在生成封面时会把封面使用的配色与设计参数输出为 `design-token.json`，内容配图自动加载该 Token 并通过 `cover-bridge.json` 映射适配内容图的色彩与氛围风格，确保封面与内页风格完美统一。

## 4. 工作流（含自循环）

```
STEP 0   复述：把「目标定义」和「验收清单」打印到 stdout，确认听懂了再动手。
STEP 0a  ★读偏好 / 首轮一次配齐★：python3 scripts/profile.py show
          - **首次运行（profile 空）→ 问齐这几项并保存**（之后自动复用）：
             1. **品牌名** `brand_name`（图上/标签显示的品牌）。
             2. **内容风格**：按内容类型从 `article-styles.json` 的 8 种（A-H）推荐后选 1。
             3. **图片风格 + 生图方式**：照片写实 / 信息图 / HTML 卡片；生图用 Agent 自带能力或 API key（默认 image-2 = OpenAI gpt-image-2，也可 gemini/ark/dashscope），**没 key 就用 HTML 卡片（免 key、中文零错字）**。
             保存：`python3 scripts/profile.py set --brand "品牌名" --article-style X --image-style "..." [--provider openai --model gpt-image-2] [--product-brief "..."]`
          - **★可问不卡★**：以上偏好可以问用户；但**用户不答、或一句话就要成品**（如「给 X 产出一条内容」）时，**不要停下来等**——由 AI 判断合理默认（内容风格按内容类型自动选、图片走 Agent 自带生图或 HTML 卡片），**直接跑完、产出含图成品**。绝不因缺配置停在半成品。
          - **已配置 → 读取后可问一句**：「本篇沿用上次（内容风格 X / 图片风格 Y），还是改？」不答即沿用。用户随时说「改内容风格 / 改品牌 / 换生图方式」都走这里。
STEP 0b  ★选内容来源（3 选 1，决定本篇选题/素材从哪来）★：
          - **模式 1 · 知识库提取**：用户给一个资料来源——一个文件夹 / 若干文件（.md/.txt/.pdf/.docx 等）/ 一段粘贴文本。
            Agent 读取并消化这些材料，从中提炼【候选选题 + 产品卖点素材】。**不绑定任何特定知识库，给路径/文本即可，通用**。
          - **模式 2 · 直接给**：用户直接提供产品原始信息（产品名 + 功能 + 卖点/数据/特色），最直接。
          - **模式 3 · 历史自动出题**：用户不提供新信息。
            - 读 profile 的 `product_brief`（首次跑存下的产品简介）+ `diversity.py show` 历史账本（已发选题/角度）。
            - 自动挑一个与历史不撞的新选题角度（结合 STEP 0d 的防同质化矩阵）。
            - 若 profile 无 `product_brief`（从没跑过）→ 明确提示「模式 3 需先用模式 1/2 跑过至少一次」，请用户改选模式 1/2。
          - **不论哪种模式**：产出本篇的「产品/选题原料」；并在【首次确定产品】时把产品简介存入 profile 供模式 3 复用：
            `python3 scripts/profile.py set --product-brief "产品名 + 一句话定位 + 核心卖点"`。
          - 把本篇 `source_mode`（kb / direct / history）记入 content.json。
STEP 0c  产品卖点提炼 (JTBD)：基于 STEP 0b 得到的原料，参考 `styles/product-discovery.md`：
          1. 转化"产品语言"为"用户人话语言"。
          2. 完成 JTBD 提炼，输出一句话定位、3-5 个人话卖点、人群画像与竞品差异。
          3. 结果存入 content.json 的 `product_analysis` 字段（不单独生成 md 文件）。
          4. 顺带定 1-2 个封面风格方向（STEP 3 生成封面/配图会用到）。
STEP 0d  防同质化（创意维度轮换；内容风格已在 STEP 0a 定好）：
          - 运行 `python3 scripts/diversity.py pick` 确定本篇的创意矩阵维度（角度/结构/钩子等）。
          - 运行 `python3 scripts/diversity.py check` 确保创意与最近 6 篇无 ≥3 维撞车。
STEP 1   ★先写文案（图要照着文案做，必须先定内容）★：基于 JTBD 提炼结果和防同质化矩阵，写出 **3 个候选标题（各≤20字符）** + 长文 + 标签。
          - **字数**：按所选风格的 `word_count` 区间（见 `article-styles.json`）控制；小红书正文上限 1000 字，体感最优 600-800。
          - **标签**：按 `article-styles.json` 的 `tag_strategy` 出 6-10 个（品类大词 + 场景/人群中词 + 长尾词 + 1 品牌词），全部贴合正文、不堆无关热词。
          - **本地化**：把风格里科技/AI 味的人设与示例换成产品真实品类的说法（见 `article-styles.json._generalization`）。
          - **立意·别招骂**：别站到目标读者的对立面——不唱衰/取代他们的职业（写给客服别喊「AI 取代客服/全交给AI」），AI 是**帮手不是替代**；少用「全/都/迟早全+取代」绝对化唱衰。详见 `writing-deai.md`「别招骂」（招骂同时触 P1-4 制造对立）。
STEP 2   去 AI 味改写：根据 `styles/writing-deai.md` 规范自检改写正文。
STEP 2a  ★内容合规检测（文本层）★：按 `styles/content-compliance.md`（2026 现行）扫描标题+正文+标签（文本层）。
          （注：配图及图上印的标题/金句/数据/卖点文字此时尚未生成，其合规由 STEP 3a「图上文字合规复检」覆盖。）
          - **P0（9 类红线）**：命中任一 → 必须修改后才能继续，否则发布大概率被删帖/限流/封号。
            本工具是 AI 生成器，**P0-2 虚假体验** 必先过：第一人称不假装亲历、不编造身份战绩与效果数据（无真实体验就用「据官方介绍/从功能看」等客观口径）。
            （注：**P0-1 AIGC 标识当前默认关闭**，不要求带 AI 声明、`ai_disclosure` 可留空；详见 `styles/content-compliance.md`。）
          - **P1（8 类风险）**：命中任一 → 同样必须修改（软广特征/标题党/贬低竞品/无对比功效等）。
          - 检测结果写入 content.json 的 `compliance` 字段：
            { "ai_disclosure": "...", "p0_passed": true/false, "p0_issues": [...], "p1_passed": true/false, "p1_issues": [...], "checked_at": "ISO时间" }
            issues 元素：{ "rule": "P0-2", "text": "命中原文", "location": "title|body|tags|image_text", "fix": "建议改法" }（与 content-compliance.md 保持一致）。
          - P0 或 P1 未通过 → 回 STEP 1 重写相关部分，再重新检测，直到全部通过。
STEP 3   ★生成封面 + 配图（成品必出图，照 STEP 1 文案做）★：先按正文规划 1-9 张图的 `image_prompts`（第 1 张作封面：大标题+副标题），再**按降级链逐张真出图**：
          ① 有生图能力/key（Agent 自带 或 配了 API key）→ AI 生图：
             - 封面：**先问/判断有没有人物照**——有 → `cover/` 出**人物封面**（`node cover/scripts/generate.mjs --image 人物照 --style 风格ID --title ...`，首次 `cd cover && npm install`；22 风格、最像真人博主，读 `~/.config/xhs-cover/config.json` 的 key）；没有/不提供 → `gen_image.py` 出**纯设计封面**（默认 image-2）。导出 `design-token.json`。（可问不卡：没回应就按"无人物照"走设计封面。）
             - 内页：`python3 scripts/gen_image.py --provider openai --model gpt-image-2 --aspect 3:4 --prompt "..." --design-token design-token.json --out imgN.png`，按 `image_prompts` 逐张。
          ② 没 key/没生图能力 → **HTML 卡片出图**（playwright，免 key、中文零错字）：按 `image-styles.md` 卡片风格库写 HTML → `python3 scripts/shot.py --html card.html --out imgN.png --selector "#card" --w 1080 --h 1350`。封面与内页都可走这条。
          - **必出真图**：无论走①还是②，最终 `images` 都要填满真实图片路径——**不留空、不拿「配图建议」当交付**。
          - 逐张过 `image-styles.md` 负面清单（无霓虹/赛博/发光3D字、畸形手指/塑料皮肤、乱码伪文字、厂商水印）。封面联动 `design-token.json` → `cover-bridge.json` 让内页与封面同色调。
          - 配置/细节（provider/key/封面 skill/HTML 风格库）见文末「附 · 配图」。
STEP 3a  ★图上文字合规复检★：抽出每张图内嵌的文字（标题/金句/数据/卖点），复用 `content-compliance.md` 的 **P0-6（违禁词/极限词）/ P0-2（虚假数据）/ P1-2（模糊功效）** 再扫一遍；命中 → 改提示词或 HTML 文案重出该图，直到通过；结果并入 `compliance`，`location` 用 `image_text`。
STEP 4   写 content.json：整理标题、正文、标签、**`images`（真实图片路径，含封面）**、`image_prompts`、JTBD 分析、`source_mode`、合规结果（`compliance`；`ai_disclosure` 默认留空——P0-1 当前关闭）。
STEP 5   构建小红书模拟器（左图右文、单文件、图片内嵌、只读）：
          - 运行 `python3 scripts/build_simulator.py --content content.json --out 小红书模拟器.html --embed`
          - 图位显示真图（断网也能看）。这是交付的预览文件。（兜底：万一某图缺失，图位会显示该位配图建议占位——但成品不应缺图。）
STEP 6   ★自检循环★：
          - 逐一勾选「验收清单」，不符合返回对应 STEP 修正——**重点核「images 是否真有图、是不是成品」**。
          - 全部通过后，运行 `python3 scripts/diversity.py record` 记账，输出交付摘要，以退出码 0 正常结束。
          - 交付物：content.json + 模拟器（单文件只读）+ 图片。不额外生成其他文件；不发送飞书/钉钉/邮件，仅 stdout 摘要。
```

**自循环要点**：默认交**成品（含图）**——先定文案再生图、图照文案做；有 key 用 AI 图、没 key 用 HTML 卡片，**总之必出真图、不交半成品**；正文错字/超字回 STEP 1；合规没过回 STEP 1 重测；图上文字也要过合规复检（STEP 3a）；模拟器忘 `--embed` 会丢图。**可问偏好但不卡，不答就 AI 判断默认直接产出**。改完重走 STEP 6 自检，别跳。

## 5. 内容合规检测规范

> 发布前自动扫描标题、正文、标签、配图文字，分 P0（红线拦截）和 P1（风险拦截）两级。
> 依据 2026 现行官方文本（公约 2.0 / 社区规范 / AIGC 标识办法等）蒸馏，完整规则与依据见 `styles/content-compliance.md`。

### P0 · 红线拦截（命中任一 → 必须修改）

| 类别 | 规则 | 示例 / 依据 |
|------|------|------|
| ~~P0-1 AIGC 标识~~（🔕 默认关闭） | 用户当前选择不带 AI 声明，**不阻断** | ⚠️ 有限流/补标风险；开启见 `content-compliance.md` P0-1 |
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
- **本地服务**：`scripts/serve.py` 起本地 http 服务（默认 127.0.0.1:8000），供**可选**的编辑版模拟器调用单图重生成/换图（默认只交付只读分享版，用不到它）。
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
- `styles/image-styles.md` — 配图用：3 种图片风格 + HTML 卡片风格库 6 款 + 负面清单
- `styles/writing-deai.md` — 去 AI 味改写清单与自检
- `styles/angle-matrix.md` — 选题角度矩阵 + 钩子/结构/标题轮换池（防同质化）
- `styles/cover-bridge.json` — 封面 designToken → 内容图视觉适配映射表（bgTone/fontVibe 映射）
- `cover/` — **内置封面生成器**（人物照封面）：22 种风格（`cover/styles/`）+ `cover/scripts/generate.mjs`（Node+sharp，`--image` 必填）；首次 `cd cover && npm install`，需用户自配 chat-image key。纯设计封面用 gen_image.py、无 key 用 HTML 卡片。
- `scripts/gen_image.py` — 多模型文生图（openai·image-2/gemini/ark·即梦/dashscope）
- `scripts/shot.py` — HTML → 高清 PNG（playwright，仅作为 LLM 生图的兜底方案）
- `scripts/build_simulator.py` — content.json → 模拟器 HTML（左图右文；默认交付 `--embed` 的图内嵌只读分享版，不加 `--embed` 为可选编辑版）
- `scripts/serve.py` — 可选编辑版的本地后端（单图重生成/换图；默认不交付编辑版时用不到）
- `scripts/profile.py` — 风格/生图偏好记忆（show/set/reset），二次运行自动复用
- `scripts/diversity.py` — 反同质化引擎（pick/check/record + 历史账本），多篇轮换不撞
- `examples/content.sample.json` — 示例（含 3 候选标题 + image_prompts，虚构产品，可直接套改）

---

## 附 · 配图（STEP 3 的生图方式与配置细节）

> 配图是**默认成品的一部分**（不是可选）。本节是 STEP 3 的展开：怎么按降级链出图、各 provider 怎么配 key。核心原则：**有 key 用 AI 图、没 key 用 HTML 卡片，总之必出真图**；key 由用户自配，**仓库不含任何 key**。

**前置生图能力（任一）**：① Agent 自带生图（Codex/Claude 等）；② API key（默认 image-2 = OpenAI `gpt-image-2`，或 `gemini`/`ark`/`dashscope`）；③ 都没有 → 用 HTML 卡片（playwright，免 key、中文零错字，见 `image-styles.md` 卡片风格库）。

**A · 封面**（照 STEP 1 已定的大标题做，三条路按你的素材 + key 选其一）：
- **有人物照 → 内置封面生成器 `cover/`**（22 种人物封面风格，已并入本 skill）：
  `node cover/scripts/generate.mjs --image 人物照 --title "大标题" --subtitle "副标题" --brand "品牌名" --style "风格ID" --output-dir 输出目录 --aspect-ratio 3:4`
  - 首次先装依赖：`cd cover && npm install`（装 sharp）。`--image` **必填**（这是人物封面生成器）；不带参数运行可列出 22 种风格。
  - 需**它自己的 key**（仓库不含，用户自配）：读 `~/.config/xhs-cover/config.json`（`apiType`/`baseUrl`/`model`/`apiKey`，**可能已配好**），或用 `--api-key`/`--base-url`/`--model` 覆盖。⚠️ 它走**聊天返图**接口——支持 Google 原生（apiType:google）或任意 OpenAI 兼容的聊天返图模型（如 `gemini-3-pro-image`/`nano-banana-pro-preview`/`gpt-4o-image`）；**不是 images API**（gpt-image-2 那种它用不了）。别用 `--api-key` 覆盖掉已配好的 key（会冲突报错）。
  - 产出「风格名_标题_日期.png」+ `design-token.json`（封面→内页配色联动）；实际文件名回填 `content.json` 的 `images[0]` 与 `cover`。
- **无人物照 / 纯设计封面 → `gen_image.py`**（你的 images-API key，如 gpt-image-2）：
  `python3 scripts/gen_image.py --provider openai --model gpt-image-2 --aspect 3:4 --prompt "封面设计，含中文标题…" --out cover.png`（gpt-image-2 中文标题基本能渲染对）。
- **没任何 key → HTML 卡片当封面**：写卡片 HTML → `python3 scripts/shot.py`（中文零错字，见 image-styles.md 卡片风格库）。

**B · 内页配图**（照正文做，与封面同视觉）：
- 加载封面的 `design-token.json`，经 `styles/cover-bridge.json` 映射配色。
- 按 `image_prompts` 逐张生成：`python3 scripts/gen_image.py --provider openai --model gpt-image-2 --aspect 3:4 --prompt "..." --design-token design-token.json --out imgN.png`（无 key → 换 HTML 卡片 `shot.py`）。
- **逐张过 `image-styles.md` 负面清单**：无霓虹/赛博/发光3D字、无畸形手指/塑料皮肤、无乱码伪文字、无厂商水印。

**C · 图上文字合规复检**（出图后必做）：抽出每张图内嵌的文字，复用 `content-compliance.md` 的 P0-6（违禁词/极限词）/P0-2（虚假数据）/P1-2（模糊功效）再扫一遍；命中 → 改提示词重出；结果并入 `compliance`，`location` 用 `image_text`。

**D · 回填**：所有图（封面+内页）的真实路径填进 `content.json` 的 `images` → 跑 STEP 4-5 出 content.json + 模拟器 → 核验收清单（images 真有图、图上文字过复检、模拟器已内嵌）。
