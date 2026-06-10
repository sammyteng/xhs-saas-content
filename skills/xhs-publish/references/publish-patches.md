# XHS Publish 脚本补丁记录

> 记录 `scripts/xhs/publish.py` 中针对 XHS 创作者平台 UI 变更所做的修复。

## 补丁 1: `_click_publish_tab` — 跳过被遮挡的 Tab

**位置**: `publish.py` ~L200

**问题**: XHS 发布页面存在多个同名 `.creator-tab` 元素（包括 `left: -9999px` 的隐藏副本和 `opacity: 1e-5` 的半透明副本）。`elementFromPoint` 检查被遮挡元素时返回 `'blocked'` 导致函数立即返回，无法到达真正的可见 tab。

**修复**: 将 `return 'blocked'` 改为 `continue`，让循环继续尝试下一个 tab：

```python
# 原代码:
                        return 'blocked';
                    }}
                }}

# 修复后:
                        // 被遮挡但跳过继续尝试下一个tab，而非立即返回blocked
                        continue;
                    }}
                }}
```

**影响**: `publish` 和 `fill-publish` 命令均已修复。

---

## 补丁 2: `click_publish_button` — 增加全量 button 搜索回退

**位置**: `publish.py` ~L120

**问题**: XHS 发布按钮的 CSS 类可能从 `button.bg-red` 变更为其他类名，导致选择器匹配不到。

**修复**: 在原有 `button.bg-red` 选择器之后增加全量 `button` 搜索作为回退：

```python
# 原代码:
            const btns = document.querySelectorAll('button.bg-red');
            for (const btn of btns) {
                ...
            }
            return false;

# 修复后:
            let btns = document.querySelectorAll('button.bg-red');
            for (const btn of btns) {
                ...
            }
            // 备用：找所有button，文本精确为"发布"
            btns = document.querySelectorAll('button');
            for (const btn of btns) {
                const text = btn.textContent.trim();
                if (text === '发布') {
                    btn.scrollIntoView({block: 'center'});
                    btn.click();
                    return true;
                }
            }
            return false;
```

---

## 常见问题: Bridge 扩展断连

**症状**: `Bridge 错误: Extension 未连接`

**原因**: Chrome 重启或用户手动刷新后，XHS Bridge 扩展可能未自动重连。

**处理流程**:
1. 先跑 `python scripts/cli.py check-login` 诊断
2. 若超时，提示用户确认 Chrome 扩展已启用
3. 用户回应「好了」后再重试

---

*创建: 2026-05-07 | 来源: Sam Altman 魔戒声明小红书发布任务*
