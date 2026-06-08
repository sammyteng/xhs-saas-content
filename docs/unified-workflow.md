# \u5c01\u9762 + \u5185\u5bb9\u56fe \u7edf\u4e00\u89c6\u89c9\u5de5\u4f5c\u6d41

> \u5148\u7528 xhs-cover-skill \u751f\u6210\u5c01\u9762\uff0c\u518d\u7528 xhs-saas-content \u751f\u6210\u5185\u5bb9\u56fe\uff0c
> \u901a\u8fc7 `design-token.json` \u81ea\u52a8\u4fdd\u6301\u5168\u5957\u56fe\u89c6\u89c9\u7edf\u4e00\u3002

## \u5feb\u901f\u5f00\u59cb

```bash
# \u2460 \u751f\u6210\u5c01\u9762\uff08\u8f93\u51fa: \u5c01\u9762.png + design-token.json\uff09
node scripts/generate.mjs \
  --image ./me.jpg \
  --style hand-drawn-border \
  --title "\u4e09\u6b65\u641e\u5b9a AI \u5de5\u4f5c\u6d41" \
  --output-dir ./xhs-output

# \u2461 \u751f\u6210\u5185\u5bb9\u56fe\uff08\u81ea\u52a8\u8bfb\u53d6\u5c01\u9762\u8272\u5f69\uff09
# \u2014\u2014 LLM \u6587\u751f\u56fe\uff08\u98ce\u683c 1/2\uff09
python3 scripts/gen_image.py \
  --prompt "\u4e00\u4e2a\u5e72\u51c0\u7684\u529e\u516c\u684c\u4e0a\u653e\u7740\u7b14\u8bb0\u672c\u548c\u5496\u5561" \
  --design-token ./xhs-output/design-token.json \
  --aspect 4:5

# \u2014\u2014 HTML \u5361\u7247\u622a\u56fe\uff08\u98ce\u683c 3\uff09
python3 scripts/shot.py \
  --html card.html \
  --out ./xhs-output/img_quote.png \
  --design-token ./xhs-output/design-token.json
```

## \u5de5\u4f5c\u539f\u7406

```
xhs-cover-skill                      xhs-saas-content
\u2502                                     \u2502
\u2502  \u9009\u98ce\u683c\uff08\u5982 hand-drawn-border\uff09    \u2502
\u2502  \u2193                                 \u2502
\u2502  \u751f\u6210\u5c01\u9762.png                     \u2502
\u2502  \u2193                                 \u2502
\u2502  \u5bfc\u51fa design-token.json  ----\u2192  \u8bfb\u53d6 design-token.json
\u2502    \u251c\u2500 primaryColor               \u2502  \u2193
\u2502    \u251c\u2500 accentColor                \u2502  cover-bridge.json \u6620\u5c04
\u2502    \u251c\u2500 bgTone                     \u2502  \u2193
\u2502    \u251c\u2500 fontVibe                   \u2502  \u6ce8\u5165\u63d0\u793a\u8bcd\u8272\u5f69 + HTML \u914d\u8272
\u2502    \u251c\u2500 mood                       \u2502  \u2193
\u2502    \u2514\u2500 negativePromptHints        \u2502  \u8f93\u51fa\u89c6\u89c9\u7edf\u4e00\u7684\u5185\u5bb9\u56fe
```

## design-token.json \u793a\u4f8b

```json
{
  "source": "xhs-cover-skill",
  "coverStyleId": "hand-drawn-border",
  "coverStyleName": "\u624b\u7ed8\u8fb9\u6846",
  "generatedAt": "2025-01-15T10:30:00.000Z",
  "designToken": {
    "primaryColor": "#FFD93D",
    "accentColor": "#1A1A1A",
    "bgTone": "light",
    "fontVibe": "playful",
    "mood": "\u6d3b\u529b/\u7efc\u827a/\u6709\u8da3",
    "negativePromptHints": "no corporate feel, no dark moody style, no tech elements"
  }
}
```

## bgTone \u6620\u5c04\u89c4\u5219

| \u5c01\u9762 bgTone | \u5185\u5bb9\u56fe\u9002\u914d | HTML \u5361\u7247\u5e95\u8272 | \u6c1b\u56f4 |
|---|---|---|---|
| `dark` | \u6697\u8c03\u6446\u62cd + \u6697\u8272 HTML | `#1d1d1f` | \u4e13\u4e1a\u3001\u6df1\u5ea6 |
| `light` | \u660e\u4eae\u7b80\u7ea6 + \u6d45\u8272 HTML | `#f5f3ee` | \u5e72\u51c0\u3001\u6742\u5fd7 |
| `warm` | \u6696\u5149\u5b9e\u62cd + \u6696\u8272 HTML | `#faf6ef` | \u6e29\u99a8\u3001\u5c45\u5bb6 |

## \u53ef\u4ee5\u4e0d\u7528\u5c01\u9762\u8054\u52a8\u5417\uff1f

\u5b8c\u5168\u53ef\u4ee5\u3002\u4e0d\u4f20 `--design-token` \u65f6\uff0cxhs-saas-content \u5b8c\u5168\u72ec\u7acb\u5de5\u4f5c\uff0c\u548c\u4e4b\u524d\u4e00\u6837\u3002
\u5c01\u9762\u8054\u52a8\u662f\u53ef\u9009\u589e\u5f3a\uff0c\u4e0d\u662f\u5f3a\u5236\u4f9d\u8d56\u3002
