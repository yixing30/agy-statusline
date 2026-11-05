#!/usr/bin/env bash
# Shell Installer for Antigravity Modern Statusline (Linux & macOS)
set -e

echo -e "\033[1;36m\n=== Antigravity Modern Statusline Installer ===\033[0m"

# 1. Check Python
echo -e "\033[1;33m[1/4] Checking Python 3...\033[0m"
if command -v python3 >/dev/null 2>&1; then
    PY_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PY_BIN="python"
else
    echo -e "\033[0;31mError: Python 3 was not found in PATH.\033[0m"
    exit 1
fi
echo -e "\033[0;32m      Found: $($PY_BIN --version)\033[0m"

# 2. Target Directory (~/.gemini)
GEMINI_DIR="$HOME/.gemini"
echo -e "\033[1;33m[2/4] Target directory: $GEMINI_DIR\033[0m"
mkdir -p "$GEMINI_DIR"

# 3. Copy Files
echo -e "\033[1;33m[3/4] Installing statusline scripts...\033[0m"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/statusline.py" "$GEMINI_DIR/statusline.py"
chmod +x "$GEMINI_DIR/statusline.py"
echo -e "\033[0;32m      Installed: $GEMINI_DIR/statusline.py\033[0m"

if [ ! -f "$GEMINI_DIR/statusline.config.json" ]; then
    cp "$SCRIPT_DIR/statusline.config.json" "$GEMINI_DIR/statusline.config.json"
    echo -e "\033[0;32m      Installed default config: $GEMINI_DIR/statusline.config.json\033[0m"
else
    echo -e "\033[0;36m      Existing config preserved: $GEMINI_DIR/statusline.config.json\033[0m"
fi

# 4. Settings notice
SETTINGS_FILE="$GEMINI_DIR/antigravity-cli/settings.json"
echo -e "\033[1;36m\n=== Installation Complete! ===\033[0m"
echo -e "\nEnsure your \033[1m$SETTINGS_FILE\033[0m contains:"
echo -e "\033[1;33m{\n  \"statusLine\": \"python3 $GEMINI_DIR/statusline.py\"\n}\033[0m"
echo -e "\n\033[1;32mLaunch 'agy' in any directory to see your new statusline!\033[0m\n"
