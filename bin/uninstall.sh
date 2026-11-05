#!/bin/bash
set -e

AGY_DIR="$HOME/.gemini/antigravity-cli"
SETTINGS_FILE="$AGY_DIR/settings.json"
STATUSLINE_DEST="$HOME/.gemini/statusline.sh"

blue='\033[38;2;0;153;255m'
green='\033[38;2;0;175;80m'
yellow='\033[38;2;230;200;0m'
dim='\033[2m'
reset='\033[0m'

ok()   { echo -e "  ${green}✓${reset} $1"; }
warn() { echo -e "  ${yellow}!${reset} $1"; }

echo
echo -e "  ${blue}agy-statusline uninstaller${reset}"
echo -e "  ${dim}──────────────────────────${reset}"
echo

if [ -f "${STATUSLINE_DEST}.bak" ]; then
    mv "${STATUSLINE_DEST}.bak" "$STATUSLINE_DEST"
    ok "Restored backup ${dim}statusline.sh.bak${reset}"
elif [ -f "$STATUSLINE_DEST" ]; then
    rm -f "$STATUSLINE_DEST"
    ok "Removed ${dim}$STATUSLINE_DEST${reset}"
else
    warn "No statusline script found at ${dim}$STATUSLINE_DEST${reset}"
fi

if [ -f "$SETTINGS_FILE" ]; then
    tmp=$(mktemp)
    jq 'del(.statusLine)' "$SETTINGS_FILE" > "$tmp" && mv "$tmp" "$SETTINGS_FILE"
    ok "Removed statusLine entry from ${dim}settings.json${reset}"
fi

echo
echo -e "  ${green}Uninstalled!${reset} Restart agy to restore the default status line."
echo
