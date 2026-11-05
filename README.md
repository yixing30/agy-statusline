# agy-statusline (Enhanced for macOS & Antigravity CLI)

参考 [Ranteck/agy-statusline](https://github.com/Ranteck/agy-statusline) 设计的 **Antigravity CLI (`agy`)** 响应式增强版状态栏。

## 核心特性与优化

1. **紧凑双行布局 + 终端宽度三级自适应 (`.terminal_width`)**：
   - 将 `5h` 与 `7d` 配额条合并至第 2 行并排显示（移除空行），总高度从 4 行压缩至 **2 行**。
   - **宽屏 (`>= 110` 列)**：完整展示所有字段、10 格进度条、倒计时+时刻、以及另一模型池的配额余量速览。
   - **中屏 (`80 ~ 109` 列)**：自动隐藏常态次要信息（如 `sandbox off`、`plan_tier`），配额条缩减为 8 格，防止折行。
   - **窄屏 (`< 80` 列，如分屏窗口)**：自动缩写模型名（移除括号后缀）、精简徽标、配额条缩为 5 格且仅展示核心倒计时/短日期。
2. **上下文与配额深度增强**：
   - **Token 实数与 200k 阈值预警**：显示 `✍️ 14% (149k)`；当上下文超过 200k Token 时自动高亮告警 `✍️ 23% (⚠️ 244k)`。
   - **配额剩余倒计时 (`reset_in_seconds`)**：同时展示距离重置的剩余时间与具体重置时刻，如 `⟳ 3h35m (03:10)`。
   - **双模型池同屏预览**：主模型池高亮展示进度条，若另一模型池（`gemini` / `claude`）也有配额数据，在宽屏行尾自动以暗色显示速览（如 `│ claude 5h:48% 7d:85%`）。
3. **macOS 原生兼容与单次 `jq` 极致性能**：
   - 同时兼容 **macOS (BSD `date -j` / `date -r`)** 与 **Linux (GNU `date -d`)**。
   - 所有 JSON 字段提取、百分比换算、Token 单位格式化（`k`/`M`）、费用舍入均在**单次 `jq` 调用**内完成。

## 显示效果示例

### 宽屏模式 (`>= 110` 列)
```text
Gemini 4 Argon (Medium) │ ctx 23% │ [working] my-project (main*) │ mode:plan │ subagents:1/2 · tasks:1 · artifacts:2 │ sandbox:off │ 💰 $0.42 │ Google AI Pro
gemini 5h 1% reset 1h21m (19:02) │ argon 7d 36% reset 5d17h (nov 11,11:39)
```

### 中屏模式 (`80 ~ 109` 列)
```text
Gemini 3.1 Pro (High) │ ctx 14% │ my-project (main) │ mode:auto │ 💰 $0.15
gemini 5h 1% reset 1h21m (19:02) │ 7d 3% reset nov 11,14:59
```

### 窄屏分屏模式 (`< 80` 列)
```text
Claude Sonnet 4.6 │ ctx 45% │ [tool] my-project (feat/ui*) │ mode:edits │ sandbox:on
claude 5h 0% reset 4h45m │ 7d 51% reset nov 11
```

## 安装与更新

```bash
git clone https://github.com/yixing30/agy-statusline.git ~/agy-statusline
bash ~/agy-statusline/bin/install.sh
```

`install.sh` 会自动将 `~/.gemini/statusline.sh` 软链接至 `~/agy-statusline/bin/statusline.sh` 并写入 `~/.gemini/antigravity-cli/settings.json`，后续对脚本的任何修改都会实时热更新生效。

### 卸载

```bash
bash ~/agy-statusline/bin/uninstall.sh
```
