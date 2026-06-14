# xhs-saas-content

为 SaaS / 软件 / AI 工具一键产出**可直接发小红书**的内容草稿：第一人称长文（3 候选标题+标签）+ **配图建议** + 一个**左图右文、单文件、只读的发布模拟器**。含**内容合规检测**（P0 红线 + P1 风险）。

> ⚙️ **通用版默认只产「文案 + 配图建议」，不依赖任何生图 key**；要自动出图见下方「（可选）配图」。

## 它能干嘛

**先选「内容从哪来」（3 选 1）**：
1. **知识库提取**：给一个资料来源（文件夹 / 若干文件 .md/.txt/.pdf / 一段文本），它自己读、自己挑选题挖卖点（通用，不绑定特定知识库）。
2. **直接给**：直接提供产品名 + 卖点（默认）。
3. **历史自动出题**：什么都不给，按记住的产品简介 + 历史发文自动出个不重复的新选题（需先用模式 1/2 跑过一次）。

然后输出：
1. JTBD 卖点提炼（自动完成，结果写入 content.json）。
2. 选一种小红书文章风格（行业锐评 / 教程 / 选型 / 背书 / 效率 / 认知 / 吐槽 / 快讯，共 8 种）。
3. **先写文案**：去过「AI 腔」的真人感长文，**给 3 个候选标题（各≤20 字符）** + 标签。
4. **配图建议**：按正文规划 1-9 条「该配什么图」（默认只给建议、不出图；要出图见下方「（可选）配图」，先文案后生图）。
5. **内容合规检测**：扫正文/标题/标签，P0 红线拦截（虚假体验/违禁词/站外导流等；AIGC 标识默认关闭），P1 风险标注。（出图时再补扫「图上印的字」）
6. 生成 HTML 模拟器（左图右文、单文件、只读；**无图时图位显示「配图建议」占位**，文案照常预览）。

**交付物 = `content.json`（文案+配图建议）+ 模拟器（单文件只读）**。配图为可选。

## 安装依赖

**核心（文案 + 模拟器）：零三方依赖**，纯 Python 标准库就能跑。

**只有要自动配图时才装**（默认不配图）：

```bash
pip install playwright && playwright install chromium   # HTML 卡片出图（免 key、中文零错字）
# 生图模型按需装其一：
pip install openai          # OpenAI GPT Image（默认 image-2 = gpt-image-2）→ OPENAI_API_KEY
pip install google-genai    # Gemini（中文最准，备选）→ GEMINI_API_KEY
# 豆包即梦 ark / 通义万相 dashscope 同理（见 image-styles.md 生图模型表）
export OPENAI_API_KEY=你的key
```

## （可选）配图

默认**不出图**，只给「配图建议」。要自动出图时（环境有生图能力）：封面优先用 `../xhs-cover-skill`（需配它自己的 API），内页图用 `gen_image.py`（默认 image-2）或 HTML 卡片兜底；出图后回填 `content.json` 的 `images` 重跑模拟器。完整步骤见 SKILL.md 文末「附 · （可选）配图」。

## 怎么用

把 SKILL.md 交给你的 Agent（或 Claude），按里面的工作流跑即可。手动跑核心脚本：

```bash
# 默认流程：有了 content.json（文案+配图建议）后，直接生成模拟器（无图时图位显示配图建议占位）
python3 scripts/build_simulator.py --content content.json --out xhs-output/小红书模拟器.html --embed

# （可选）要自动配图时才用，提示词参考 image-styles.md 的「避免 AI 味」负面清单：
python3 scripts/gen_image.py --provider openai --model gpt-image-2 --aspect 3:4 \
  --prompt "..." --out xhs-output/img1.png        # 默认 image-2；中文老出错可换 --provider gemini --model pro
python3 scripts/shot.py --html card.html --out xhs-output/img2.png --selector "#card" --w 1080 --h 1350  # HTML 卡片，免 key、零错字
# 出图后把路径回填 content.json 的 images[]，再重跑上面的 build_simulator
```

`content.json` 格式见 `examples/content.sample.json`（含 `titles[3]`、`image_prompts` 和 `compliance`）。

- **交付版** `小红书模拟器.html`：左图右文、单文件、图片内嵌、只读，直接发给别人不丢图。
- （可选编辑版：不加 `--embed` 生成，配合 `serve.py` 可改文案/换图；默认不交付。）
- 建议发布前确认内容，自动化场景可跳过确认直接交付。

## 内容合规检测

发布前自动扫描标题/正文/标签/配图文字，依据 **2026 现行官方文本**（社区公约 2.0 / 社区规范 / AIGC 标识办法 / 交易导流细则等）蒸馏，分两级：

- **P0（红线）**：⭐虚假体验·虚构人设 / 诱导互动 / 免费送福利 / 互赞互关 / 违禁词·极限词 / 站外导流 / 批量问答 / 垂类准入（医疗医美·金融·教培·烟酒）→ 命中必改。（AIGC 标识为 P0-1，**当前默认关闭**。）
- **P1（8 类风险）**：软引导互动 / 模糊功效·无对比 / 贬低竞品 / 敏感话题·制造对立 / 外部提及 / 软广特征 / 标题党·文题不符 / 炫富夸大 → 同样命中必改

> ⚠️ **AI 声明（P0-1）当前默认关闭**：用户选择暂不带 AI 声明，故不强制 `ai_disclosure` / 正文声明 / 平台勾选。注意《AIGC 标识办法》要求 AI 内容显式标识，不带有限流/补标风险；想开启见 `styles/content-compliance.md` 的 P0-1 条。

检测结果写入 `content.json` 的 `compliance` 字段（含 `ai_disclosure`）。每条规则的官方依据详见 `styles/content-compliance.md`。

## 风格偏好记忆（少选一次）

首次**一轮配齐**：品牌 + 内容风格 + 图片风格 + 生图模型（默认 image-2 = OpenAI gpt-image-2），存下后自动复用；之后每篇只问一句「沿用还是改」，想改一句话改：

```bash
python3 scripts/profile.py show        # 看当前偏好（首次为空）
# 首轮一次配齐：品牌 + 内容风格 + 图片风格 + 生图模型（默认 image-2）
python3 scripts/profile.py set --brand "你的品牌" --article-style A --image-style "HTML卡片" \
    --provider openai --model gpt-image-2 --aspect 3:4 --product-brief "产品名+一句话定位+核心卖点"
python3 scripts/profile.py reset       # 想重新选风格时清空
```

- 默认存 `~/.config/xhs-saas-content/profile.json`；设 `XHS_PROFILE=别的路径` 可给不同设备/账号各存一份。
- 跑 skill 时它会先 `profile.py show`：有就直接用、跳过选择；没有或你说「调整风格」才重新选。

## 跨多篇防同质化

多篇内容容易"一个模子"。解法：profile 只锁**品牌层**(作者/IP/语气)，**创意层**每篇轮换并查重。

```bash
python3 scripts/diversity.py pick                       # 给本篇分配一组"不撞最近"的维度
python3 scripts/diversity.py check --combo '{...}'      # 与最近 6 篇查重（≥3 维相同=撞）
python3 scripts/diversity.py record --combo '{...}' --title "标题"   # 生成后记账
python3 scripts/diversity.py show                       # 看最近几篇的维度
```

- 轮换维度：选题角度 / 文章风格 / 结构 / 开头钩子 / 配图风格 / 标题套路（见 `styles/angle-matrix.md`）。
- 历史账本默认 `~/.config/xhs-saas-content/history.json`，按账号各存一份（`XHS_HISTORY` 可改）。

## 目录结构

```
xhs-saas-content/
├── SKILL.md                  # 主流程（7 章：目标/验收/输入/工作流/合规/权限/失败回执）
├── README.md
├── styles/
│   ├── content-compliance.md # 内容合规检测规范（P0 红线 + P1 风险）
│   ├── article-styles.json   # 8 种文章风格 + 内容类型推荐
│   ├── image-styles.md       # 图片风格 + 提示词模板 + 「避免 AI 味」负面清单
│   ├── writing-deai.md       # 去 AI 味清单
│   ├── cover-bridge.json     # 封面→内容图视觉适配映射
│   ├── product-discovery.md  # 产品卖点提炼与 JTBD 方法论
│   └── angle-matrix.md       # 选题角度矩阵 + 轮换池（防同质化）
├── scripts/
│   ├── gen_image.py          # 多模型文生图（gemini/openai/ark·即梦/dashscope）
│   ├── shot.py               # HTML → PNG（LLM 生图的兜底方案）
│   ├── build_simulator.py    # 模拟器生成器（左图右文；--embed 出图内嵌只读分享版）
│   ├── serve.py              # 可选编辑版的本地后端（重生成/换图）
│   ├── profile.py            # 风格/生图偏好记忆（二次运行自动复用）
│   └── diversity.py          # 反同质化引擎（多篇轮换不撞）
└── examples/
    └── content.sample.json   # 示例（虚构产品）
```

## 注意

- 本工具只**生成**内容，不自动发布到小红书。
- 不发送飞书/钉钉/邮件等任何渠道通知。
- API key 仅从环境变量读取，不写入任何文件。
- 配图默认规避「一眼 AI」元素；请按平台规范使用 AI 生成内容。
- 建议发布前确认内容，自动化场景可跳过确认直接交付。
