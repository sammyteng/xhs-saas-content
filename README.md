# xhs-saas-content

为 SaaS / 软件 / AI 工具一键产出**可直接发小红书**的图文内容：第一人称长文 + **1-9 张不踩「AI 味」的配图** + 一个**可在线编辑的发布模拟器**，并能导出**图片内嵌的单文件分享版**。含**内容合规检测**（P0 红线拦截 + P1 风险警告）。

## 它能干嘛

**先选「内容从哪来」（3 选 1）**：
1. **知识库提取**：给一个资料来源（文件夹 / 若干文件 .md/.txt/.pdf / 一段文本），它自己读、自己挑选题挖卖点（通用，不绑定特定知识库）。
2. **直接给**：直接提供产品名 + 卖点（默认）。
3. **历史自动出题**：什么都不给，按记住的产品简介 + 历史发文自动出个不重复的新选题（需先用模式 1/2 跑过一次）。

然后输出：
1. JTBD 卖点提炼（自动完成，结果写入 content.json）。
2. 选一种小红书文章风格（行业锐评 / 教程 / 选型 / 背书 / 效率 / 认知 / 吐槽 / 快讯，共 8 种）。
3. **先写文案**：去过「AI 腔」的真人感长文，**给 3 个候选标题（各≤20 字符）** + 标签。
4. **再照着定好的标题/正文做图**：1 张封面 + 1-9 张同一视觉语言的配图（LLM 生图优先 / HTML 卡片兜底），**自动规避霓虹科技等一眼假的 AI 图**（先文案后生图，图才贴内容）。
5. **内容合规检测（两道闸）**：文本层扫正文/标题/标签；图生成后再扫「图上印的字」，P0 红线拦截（虚假体验/违禁词/站外导流等；AIGC 标识默认关闭），P1 风险标注。
6. 生成 HTML 模拟器（编辑版可改文案/切标题/换图 + 分享版图片内嵌单文件）。

**交付物 = `content.json` + 模拟器（编辑版+分享版）+ 封面图 + 内容配图**。

## 安装依赖

```bash
pip install playwright                    # HTML 渲染兜底出图；其余功能纯标准库
playwright install chromium

# 生图模型按需装一个（任选其一）：
pip install google-genai                 # Gemini（默认，中文最准）→ GEMINI_API_KEY
pip install openai                       # GPT（gpt-image-1.5）      → OPENAI_API_KEY
pip install 'volcengine-python-sdk[ark]' # 豆包·即梦 / Seedream      → ARK_API_KEY
pip install dashscope                    # 通义万相                  → DASHSCOPE_API_KEY

export GEMINI_API_KEY=你的key             # 对应所选 provider 的 key
```

> **Agent 自带生图时无需配 key**：Codex / Antigravity / Claude 等具备图片生成能力的 Agent 直接按提示词生图。
> 没有 API key 且 Agent 无生图能力也能用：只走 HTML 渲染兜底出图，中文零错字。

## 封面生成优先级

封面图按以下顺序尝试生成（自动降级）：

1. **LLM + 人物形象**（最优）：有人物照时，用 LLM 生图 + 人物参考照生成带人物的封面
2. **LLM 生图**（次优）：无人物照，用 LLM 按风格 prompt 直接生图
3. **HTML 渲染兜底**（最后）：LLM 不可用或连续失败时，退回 HTML 模板 + playwright 截图

内容配图同理：优先 LLM 生图，不可用时退回 HTML 渲染。

## 怎么用

把 SKILL.md 交给你的 Agent（或 Claude），按里面的工作流跑即可。手动跑核心脚本：

```bash
# 1. 生图（LLM）——提示词请参考 image-styles.md 的「避免 AI 味」负面清单
python3 scripts/gen_image.py --provider gemini --model pro --aspect 9:16 \
  --prompt "..." --out xhs-output/cover.png

# 2. 生图（HTML 卡片，零错字、作为 LLM 生图的兜底方案）
python3 scripts/shot.py --html card.html --out xhs-output/img_quote.png --selector "#card" --w 1080 --h 1350

# 3. 生成模拟器（编辑版 + 分享版）
python3 scripts/build_simulator.py --content content.json --out xhs-output/小红书模拟器.html
python3 scripts/build_simulator.py --content content.json --out xhs-output/小红书模拟器_分享版.html --embed
```

`content.json` 格式见 `examples/content.sample.json`（含 `titles[3]`、`image_prompts` 和 `compliance`）。

- **编辑版** `小红书模拟器.html`：可改文案/换图/重生成。
- **分享版** `小红书模拟器_分享版.html`：单文件、图片内嵌，直接发给别人。
- 建议发布前确认内容，自动化场景可跳过确认直接交付。

## 内容合规检测

发布前自动扫描标题/正文/标签/配图文字，依据 **2026 现行官方文本**（社区公约 2.0 / 社区规范 / AIGC 标识办法 / 交易导流细则等）蒸馏，分两级：

- **P0（红线）**：⭐虚假体验·虚构人设 / 诱导互动 / 免费送福利 / 互赞互关 / 违禁词·极限词 / 站外导流 / 批量问答 / 垂类准入（医疗医美·金融·教培·烟酒）→ 命中必改。（AIGC 标识为 P0-1，**当前默认关闭**。）
- **P1（8 类风险）**：软引导互动 / 模糊功效·无对比 / 贬低竞品 / 敏感话题·制造对立 / 外部提及 / 软广特征 / 标题党·文题不符 / 炫富夸大 → 同样命中必改

> ⚠️ **AI 声明（P0-1）当前默认关闭**：用户选择暂不带 AI 声明，故不强制 `ai_disclosure` / 正文声明 / 平台勾选。注意《AIGC 标识办法》要求 AI 内容显式标识，不带有限流/补标风险；想开启见 `styles/content-compliance.md` 的 P0-1 条。

检测结果写入 `content.json` 的 `compliance` 字段（含 `ai_disclosure`）。每条规则的官方依据详见 `styles/content-compliance.md`。

## 风格偏好记忆（少选一次）

首次选定的文案风格 / 图片风格 / 生图参数会被记住，之后自动复用，不用每次重选：

```bash
python3 scripts/profile.py show        # 看当前偏好（首次为空）
python3 scripts/profile.py set --article-style A --image-style 1 \
    --provider gemini --model pro --aspect 9:16 --author "AI内容观察" --ip 上海
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
│   ├── build_simulator.py    # 模拟器生成器（--embed 出内嵌分享版）
│   ├── serve.py              # 编辑版本地后端（重生成/换图）
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
