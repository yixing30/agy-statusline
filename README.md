# 🚀 Antigravity Modern Statusline (agy-statusline)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows | macOS | Linux](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com)
[![Antigravity CLI](https://img.shields.io/badge/Antigravity-CLI-orange.svg)](https://github.com/google/antigravity)

A high-performance, aesthetic status line for the **Google Antigravity CLI (`agy`)**. Designed for seamless developer experience with Powerline gradients, rounded capsule badges, dynamic model-quota tracking, and real-time session cost estimation.

---

## ✨ Features

- **🎨 3 Visual Styles**:
  - `powerline`: Connected gradient bar with smooth pill caps (`` ... `` ... ``).
  - `rounded`: Elegant floating capsule pills (` text `).
  - `minimal`: Clean, modern separator layout (`text › text`).
- **🌈 6 Color Themes**: `aurora`, `sunset`, `forest`, `gray`, `catppuccin`, `nord`.
- **🧠 Dynamic Quota Auto-Matching**: Automatically detects active model and pulls the corresponding quota pool:
  - **Claude** (Sonnet / Opus / Haiku) $\rightarrow$ `3p-5h` & `3p-weekly`
  - **Gemini 4 Argon** $\rightarrow$ `gemini-5h` & `gemini-argon-wtu-weekly`
  - **Gemini 3.8 Flash / Standard** $\rightarrow$ `gemini-5h` & `gemini-weekly`
- **💰 Real-Time Session Cost Estimation**: Accurately tracks input/output token usage per turn and displays estimated session expenditure (`💰 $0.94`).
- **⚡ Blazing Fast**: Pure Python standard library, runs in ~30ms with zero heavy dependencies (`jq`/`bash` not required on Windows).
- **🪟 Windows UTF-8 Native**: Handles CP936/GBK/UTF-8 console codepages without crashing or mangling unicode symbols.
- **🌐 Interactive Web Builder**: Includes a built-in browser-based preview tool (`index.html`).

---

## 📸 Preview

### Powerline Two-Lines (Default)
```text
  project   main*  ⚡ 󰘚 Gemini 4 Argon ✦ Med  󰘚 ctx 21%  💰 $0.94  Google AI Pro 
 󰾆 argon 5h ▱▱▱▱▱▱ 5% (⟳ 14:54)  argon 7d ▰▰▱▱▱▱ 39% (⟳ nov 11, 10:39) 
```

### Rounded Capsules
```text
  project    main*   ⚡ 󰘚 Gemini 4 Argon ✦ Med   󰘚 ctx 21%   💰 $0.94   Google AI Pro 
 󰾆 argon 5h ▱▱▱▱▱▱ 5% (⟳ 14:54)   argon 7d ▰▰▱▱▱▱ 39% (⟳ nov 11, 10:39) 
```

### Single-Line Mode (`one-line`)
```text
  project   main*  ⚡ 󰘚 Gemini 4 Argon ✦ Med  󰘚 ctx 21%  💰 $0.94  󰾆 argon 5h ▱▱▱▱▱ 5%  Google AI Pro 
```

---

## 🚀 Quick Start & Installation

### Option 1: One-Click Installer

#### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

#### macOS / Linux (Bash)
```bash
bash install.sh
```

---

### Option 2: Manual Installation

1. Copy `statusline.py` and `statusline.config.json` to your `~/.gemini/` directory:
   ```bash
   # Windows PowerShell
   Copy-Item statusline.py, statusline.config.json -Destination "$HOME\.gemini\" -Force

   # macOS / Linux
   cp statusline.py statusline.config.json ~/.gemini/
   chmod +x ~/.gemini/statusline.py
   ```

2. Open `~/.gemini/antigravity-cli/settings.json` and configure the `statusLine` command:
   ```json
   {
     "statusLine": "python C:/Users/<YourUsername>/.gemini/statusline.py"
   }
   ```
   *(On macOS / Linux, use `"python3 /home/<user>/.gemini/statusline.py"`)*

3. Restart or start a new `agy` terminal session!

---

## ⚙️ Configuration (`statusline.config.json`)

Customize themes and styles by editing `~/.gemini/statusline.config.json`:

```json
{
  "theme": "aurora",
  "style": "powerline",
  "layout": "two-lines",
  "nerd_fonts": true,
  "progress_bar": "smooth",
  "show_quota": true,
  "show_cost": true,
  "quota_mode": "auto"
}
```

### Configuration Options

| Option | Type | Default | Choices / Description |
| :--- | :--- | :--- | :--- |
| `theme` | string | `"aurora"` | `"aurora"`, `"sunset"`, `"forest"`, `"gray"`, `"catppuccin"`, `"nord"` |
| `style` | string | `"powerline"` | `"powerline"`, `"rounded"`, `"minimal"` |
| `layout` | string | `"two-lines"` | `"two-lines"` (Row 1 info + Row 2 quota), `"one-line"` (compact) |
| `nerd_fonts` | boolean | `true` | Set `false` if your terminal does not use a Nerd Font |
| `progress_bar` | string | `"smooth"` | `"smooth"` (`▰▱`), `"blocks"` (`■□`), `"dots"` (`●○`) |
| `show_quota` | boolean | `true` | Show/hide rate limit quota progress bars |
| `show_cost` | boolean | `true` | Show/hide estimated session expenditure badge (`💰 $0.94`) |
| `quota_mode` | string | `"auto"` | `"auto"` (matches model automatically), `"all"`, `"claude"`, `"argon"`, `"gemini"` |

---

## 🧪 Testing in Terminal

Test the statusline locally with the included sample payload:

```bash
# Windows PowerShell
Get-Content sample_payload.json | python statusline.py

# macOS / Linux
cat sample_payload.json | python3 statusline.py
```

---

## 🌐 Live Web Preview

Open `index.html` in your web browser to visually customize and preview layouts, themes, and styles in real time before applying them.

---

## 🔤 Font Recommendation

For glyphs (``, ``, `󰘚`, `󰾆`, ``, ``, ``) to render properly, we recommend using any **Nerd Font**:
- [JetBrainsMono Nerd Font](https://www.nerdfonts.com/font-downloads) (Recommended)
- [FiraCode Nerd Font](https://www.nerdfonts.com/font-downloads)
- [MesloLGS NF](https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Regular.ttf)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
