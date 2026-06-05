# xhs-saas-content

为 SaaS / 软件 / AI 工具一键产出**可直接发小红书**的图文内容：第一人称长文 + **1-9 张不踩「AI 味」的配图** + 一个**可在线编辑的发布模拟器**（改文案、单图重生成、确认保存），并能导出**图片内嵌的单文件分享版**。

## 它能干嘛

输入「产品名 + 一句话定位 + 几个卖点」，输出：
1. 选一种小红书文章风格（行业锐评 / 教程 / 选型 / 背书 / 效率 / 认知 / 吐槽 / 快讯，共 8 种）。
2. 写成去过「AI 腔」的真人感长文，**给 3 个候选标题（各≤20 字符）**。
3. 配 1-9 张同一视觉语言的图（写实摄影 / 扁平信息图 / HTML 卡片三条路），**自动规避霓虹科技等一眼假的 AI 图**。
4. 生成 HTML 模拟器：左屏翻图、右屏看完整文案；编辑版可点标题切换、点正文直接改、单图改提示词重生成、确认保存。
5. 导出分享版：图片 base64 内嵌成**单个 html 文件**，发给谁都能打开、不丢图。

## 安装依赖

```bash
pip install playwright                    # HTML 渲染图（风格3）；其余功能纯标准库
playwright install chromium

# 生图模型按需装一个（任选其一）：
pip install google-genai                 # Gemini（默认，中文最准）→ GEMINI_API_KEY
pip install openai                       # GPT（gpt-image-1.5）      → OPENAI_API_KEY
pip install 'volcengine-python-sdk[ark]' # 豆包·即梦 / Seedream      → ARK_API_KEY
pip install dashscope                    # 通义万相                  → DASHSCOPE_API_KEY

export GEMINI_API_KEY=你的key             # 对应所选 provider 的 key
```

> 没有任何 API key 也能用：只走风格3（HTML 渲染）出图，中文零错字。
> 生图模型用 `gen_image.py --provider gemini|openai|ark|dashscope` 切换，详见 `styles/image-styles.md`。

## 怎么用

把 SKILL.md 交给你的 Agent（或 Claude），按里面的工作流跑即可。手动跑核心脚本：

```bash
# 1. 生图（LLM）——提示词请参考 image-styles.md 的「避免 AI 味」负面清单
python3 scripts/gen_image.py --provider gemini --model pro --aspect 9:16 \
  --prompt "..." --out xhs-output/cover.png

# 2. 生图（HTML 卡片，零错字、最不像 AI）
python3 scripts/shot.py --html card.html --out xhs-output/img_quote.png --selector "#card" --w 1080 --h 1350

# 3. 生成模拟器（编辑版 + 分享版）
python3 scripts/build_simulator.py --content content.json --out xhs-output/小红书模拟器.html
python3 scripts/build_simulator.py --content content.json --out xhs-output/小红书模拟器_分享版.html --embed

# 4. （可选）启本地后端：在编辑版里改图/确认保存
python3 scripts/serve.py xhs-output          # 然后浏览器打开 http://127.0.0.1:8000/小红书模拟器.html
```

`content.json` 格式见 `examples/content.sample.json`（含 `titles[3]` 和 `image_prompts`）。

- **编辑版** `小红书模拟器.html`：配合 `serve.py` 用，可改文案/换图/重生成/确认保存。
- **分享版** `小红书模拟器_分享版.html`：单文件、图片内嵌，直接发给别人。
- 点「✓ 确认内容」后，后端写 `content.confirmed.json` 并自动生成分享版（进入发布流程，发布动作暂未实现）。

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
- 想固定某风格：`profile.py set --rotate false`；想限定风格池：`--style-pool A,B,F`。

## 目录结构

```
xhs-saas-content/
├── SKILL.md                  # 主流程（7 章：目标/验收/输入/工作流/权限/失败回执）
├── README.md
├── styles/
│   ├── article-styles.json   # 8 种文章风格 + 内容类型推荐
│   ├── image-styles.md       # 3 种图片风格 + 提示词模板 + 「避免 AI 味」负面清单
│   ├── writing-deai.md       # 去 AI 味清单
│   └── angle-matrix.md       # 选题角度矩阵 + 轮换池（防同质化）
├── scripts/
│   ├── gen_image.py          # 多模型文生图（gemini/openai/ark·即梦/dashscope）
│   ├── shot.py               # HTML → PNG
│   ├── build_simulator.py    # 模拟器生成器（--embed 出内嵌分享版）
│   ├── serve.py              # 编辑版本地后端（重生成/换图/确认保存）
│   ├── profile.py            # 风格/生图偏好记忆（二次运行自动复用）
│   ├── diversity.py          # 反同质化引擎（多篇轮换不撞）
│   └── watermark.py          # （可选，默认不用）打水印工具
└── examples/
    └── content.sample.json   # 示例（虚构产品）
```

## 注意

- 本工具只**生成**内容，不自动发布到小红书。
- API key 仅从环境变量读取，不写入任何文件。
- 配图默认规避「一眼 AI」元素；请按平台规范使用 AI 生成内容。
