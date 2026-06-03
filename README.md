# xhs-saas-content

为 SaaS / 软件 / AI 工具一键产出**可直接发小红书**的图文内容：第一人称长文 + 6-9 张统一风格配图 + 左右两屏的「发布模拟器」预览。文与图全部带「AI生成」标注。

## 它能干嘛

输入「产品名 + 一句话定位 + 几个卖点」，输出：
1. 选一种小红书文章风格（行业锐评 / 教程 / 选型 / 背书 / 效率 / 认知 / 吐槽 / 快讯，共 8 种）。
2. 写成去过「AI 腔」的真人感长文。
3. 配 6-9 张同一视觉语言的图（LLM 生图 + HTML 卡片两条路）。
4. 生成一个 HTML 模拟器，左屏翻图、右屏看完整文案，所见即发布效果。

## 安装依赖

```bash
pip install pillow playwright            # 基础：水印 + HTML 渲染图
playwright install chromium              # 仅 HTML 渲染图（风格3）需要

# 生图模型按需装一个（任选其一）：
pip install google-genai                 # Gemini（默认，中文最准）→ GEMINI_API_KEY
pip install openai                       # GPT（gpt-image-1）        → OPENAI_API_KEY
pip install 'volcengine-python-sdk[ark]' # 豆包·即梦 / Seedream      → ARK_API_KEY
pip install dashscope                    # 通义万相                  → DASHSCOPE_API_KEY

export GEMINI_API_KEY=你的key             # 对应所选 provider 的 key
```

> 没有任何 API key 也能用：只走风格3（HTML 渲染）出图，中文零错字。
> 生图模型用 `gen_image.py --provider gemini|openai|ark|dashscope` 切换，详见 `styles/image-styles.md`。

## 怎么用

把 SKILL.md 交给你的 Agent（或 Claude），按里面的工作流跑即可。手动跑核心脚本：

```bash
# 1. 生图（LLM）
python3 scripts/gen_image.py --prompt "..." --out xhs-output/cover.png --model pro --aspect 9:16

# 2. 生图（HTML 卡片）
python3 scripts/shot.py --html card.html --out xhs-output/img6_quote.png --selector "#card" --w 1080 --h 1350

# 3. 打 AI生成 水印
python3 scripts/watermark.py --dir xhs-output

# 4. 生成小红书模拟器
python3 scripts/build_simulator.py --content content.json --out xhs-output/小红书模拟器.html
```

`content.json` 格式见 `examples/content.sample.json`。

## 目录结构

```
xhs-saas-content/
├── SKILL.md                  # 主流程（7 章：目标/验收/输入/工作流/权限/失败回执）
├── README.md
├── styles/
│   ├── article-styles.json   # 8 种文章风格 + 内容类型推荐
│   ├── image-styles.md       # 3 种图片风格 + 提示词模板
│   └── writing-deai.md       # 去 AI 味清单
├── scripts/
│   ├── gen_image.py          # Gemini 文生图
│   ├── shot.py               # HTML → PNG
│   ├── watermark.py          # AI生成 水印
│   └── build_simulator.py    # 模拟器生成器
└── examples/
    └── content.sample.json   # 示例（虚构产品）
```

## 注意

- 本工具只**生成**内容，不自动发布到小红书。
- API key 仅从环境变量读取，不写入任何文件。
- 所有产出均带「AI生成」标注，请按平台规范使用。
