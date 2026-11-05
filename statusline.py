#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern Aesthetic Status Line for Antigravity CLI (agy)
Supports: Powerline, Rounded Capsules, and Minimal styles
Dynamic color themes: Aurora, Sunset, Forest, Gray Ramp, Nord, Catppuccin
Auto-matches quota pool (Claude / Argon 4 / Gemini 3.8 Flash) based on active model
Real-time session cost estimation (💰 $0.94) based on token usage and model rates
"""

import sys
import io
import os
import json
import subprocess
from datetime import datetime

# ── Force UTF-8 input/output on Windows ─────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        except Exception:
            pass

if sys.stdin.encoding and sys.stdin.encoding.lower() != 'utf-8':
    try:
        sys.stdin.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, io.UnsupportedOperation):
        pass

# Enable VT100 ANSI sequences on Windows console
if sys.platform == "win32":
    try:
        os.system("")
    except Exception:
        pass

# ── Palettes & Themes ───────────────────────────────────
THEMES = {
    'aurora': {
        'name': 'Aurora',
        'bg': ['#1e2a4a', '#252b4b', '#2d2c4b', '#342d4c', '#3c2d4d', '#432e4e', '#4b2f4e', '#52304f'],
        'accent': '#88c0d0',
        'git': '#ecc487',
        'model': '#c5a8d8',
        'tier': '#9aa5c4',
        'cost': '#ebcb8b',
    },
    'sunset': {
        'name': 'Sunset',
        'bg': ['#241f42', '#2c2142', '#352442', '#3d2642', '#452942', '#4d2b42', '#562e41', '#5e3041'],
        'accent': '#f6c177',
        'git': '#eb6f92',
        'model': '#c4a7e7',
        'tier': '#908caa',
        'cost': '#f6c177',
    },
    'forest': {
        'name': 'Forest',
        'bg': ['#163a34', '#193a39', '#1c3a3d', '#1f3a42', '#233a47', '#263a4c', '#293a50', '#2c3a52'],
        'accent': '#89dceb',
        'git': '#a6e3a1',
        'model': '#b4befe',
        'tier': '#9399b2',
        'cost': '#f9e2af',
    },
    'gray': {
        'name': 'Gray Ramp',
        'bg': ['#3a3d45', '#33363e', '#2c2f36', '#26282e', '#202227', '#1a1c21', '#15161a', '#101114'],
        'accent': '#61afef',
        'git': '#e5c07b',
        'model': '#c678dd',
        'tier': '#abb2bf',
        'cost': '#e5c07b',
    },
    'catppuccin': {
        'name': 'Catppuccin Mocha',
        'bg': ['#313244', '#36384d', '#3c3e56', '#41445f', '#464968', '#4c4f72', '#51557b', '#575b85'],
        'accent': '#89dceb',
        'git': '#f9e2af',
        'model': '#cba6f7',
        'tier': '#a6adc8',
        'cost': '#f9e2af',
    },
    'nord': {
        'name': 'Nord',
        'bg': ['#2e3440', '#3b4252', '#434c5e', '#4c566a', '#3b4252', '#434c5e', '#2e3440', '#252932'],
        'accent': '#88c0d0',
        'git': '#ebcb8b',
        'model': '#b48ead',
        'tier': '#d8dee9',
        'cost': '#ebcb8b',
    }
}

DEFAULT_CONFIG = {
    "theme": "aurora",
    "style": "powerline",
    "layout": "two-lines",
    "nerd_fonts": True,
    "progress_bar": "smooth",
    "show_quota": True,
    "show_cost": True,
    "quota_mode": "auto"  # "auto" | "all" | "claude" | "argon" | "gemini"
}

# ── Color Utilities ──────────────────────────────────────
def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def fg(hex_code):
    r, g, b = hex_to_rgb(hex_code)
    return f"\033[38;2;{r};{g};{b}m"

def bg(hex_code):
    r, g, b = hex_to_rgb(hex_code)
    return f"\033[48;2;{r};{g};{b}m"

RESET = "\033[0m"
DIM = "\033[2m"
BOLD = "\033[1m"

def get_color_for_pct(pct):
    if pct >= 90:
        return "#e06c75"  # Soft red
    elif pct >= 70:
        return "#ebcb8b"  # Warm yellow
    elif pct >= 50:
        return "#d08770"  # Orange
    else:
        return "#a3be8c"  # Sage green

def build_bar(pct, width=8, style="smooth"):
    pct = max(0, min(100, pct))
    filled = int(round(pct * width / 100.0))
    empty = width - filled
    c_hex = get_color_for_pct(pct)

    if style == "smooth":
        fill_ch = "▰"
        empty_ch = "▱"
    elif style == "blocks":
        fill_ch = "■"
        empty_ch = "□"
    else:  # dots
        fill_ch = "●"
        empty_ch = "○"

    return f"{fg(c_hex)}{fill_ch * filled}{DIM}{empty_ch * empty}{RESET}"

def format_reset_time(reset_iso, style="time"):
    if not reset_iso or reset_iso == "null":
        return ""
    try:
        iso_clean = reset_iso.replace("Z", "+00:00")
        dt = datetime.fromisoformat(iso_clean).astimezone()
        if style == "time":
            return dt.strftime("%H:%M")
        else:
            month_abbr = dt.strftime("%b").lower()
            return f"{month_abbr} {dt.day}, {dt.strftime('%H:%M')}"
    except Exception:
        return ""

def load_config():
    config_paths = [
        os.path.join(os.path.dirname(__file__), "statusline.config.json"),
        os.path.expanduser("~/.gemini/statusline.config.json")
    ]
    for p in config_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    res = DEFAULT_CONFIG.copy()
                    res.update(cfg)
                    return res
            except Exception:
                pass
    return DEFAULT_CONFIG.copy()

# ── Dynamic Quota Pool Matching ──────────────────────────
def extract_quota_pools(data, quota_mode="auto"):
    """
    Intelligently extracts quota pools based on the active model and quota payload.
    Supports:
    - Claude (3p-5h, 3p-weekly)
    - Gemini 4 Argon (gemini-5h / argon-5h, gemini-argon-wtu-weekly)
    - Gemini 3.8 Flash / Standard Gemini (gemini-5h, gemini-weekly)
    Returns: list of (pool_label, q5h_info, qwk_info)
    """
    model_obj = data.get("model")
    model_str = ""
    if isinstance(model_obj, dict):
        model_str = f"{model_obj.get('id', '')} {model_obj.get('display_name', '')} {model_obj.get('name', '')}".lower()
    elif isinstance(model_obj, str):
        model_str = model_obj.lower()

    extra_str = f"{data.get('model_id', '')} {data.get('model_name', '')} {data.get('active_model', '')}".lower()
    full_model_str = f"{model_str} {extra_str}".strip()

    quota = data.get("quota") or {}

    # Priority order: check "argon" BEFORE generic "gemini" because Argon's name is "Gemini 4 Argon"
    pools_def = {
        'claude': {
            'keywords': ("claude", "anthropic", "sonnet", "opus", "haiku", "3p"),
            '5h': ["3p-5h", "claude-5h", "anthropic-5h", "3p_5h", "claude_5h"],
            'weekly': ["3p-weekly", "claude-weekly", "3p-7d", "claude-7d", "anthropic-weekly"]
        },
        'argon': {
            'keywords': ("argon", "argon4", "gemini 4", "gemini-4"),
            '5h': ["gemini-argon-wtu-5h", "gemini-argon-5h", "argon-5h", "gemini-5h"],
            'weekly': ["gemini-argon-wtu-weekly", "gemini-argon-weekly", "argon-weekly", "gemini-argon-7d"]
        },
        'flash': {
            'keywords': ("flash", "3.8", "3-8"),
            '5h': ["gemini-flash-5h", "gemini-5h", "google-5h"],
            'weekly': ["gemini-flash-weekly", "gemini-weekly", "google-weekly", "gemini-7d"]
        },
        'gemini': {
            'keywords': ("gemini", "google", "pro", "ultra"),
            '5h': ["gemini-5h", "google-5h", "gemini_5h", "gemini-5-hour"],
            'weekly': ["gemini-weekly", "google-weekly", "gemini-7d", "gemini_weekly"]
        }
    }

    def get_pool_data(p_name):
        defn = pools_def.get(p_name, {})
        q5h = None
        for k in defn.get('5h', []):
            if k in quota:
                q5h = quota[k]
                break
        if not q5h and p_name == 'argon':
            for k, v in quota.items():
                if 'argon' in k and '5h' in k:
                    q5h = v
                    break

        qwk = None
        for k in defn.get('weekly', []):
            if k in quota:
                qwk = quota[k]
                break
        if not qwk and p_name == 'argon':
            for k, v in quota.items():
                if 'argon' in k and ('weekly' in k or '7d' in k):
                    qwk = v
                    break
        return q5h, qwk

    if quota_mode == "all":
        results = []
        for p_name in ("claude", "argon", "gemini"):
            q5h, qwk = get_pool_data(p_name)
            if q5h or qwk:
                results.append((p_name, q5h, qwk))
        if results:
            return results

    if quota_mode in pools_def:
        target_pool = quota_mode
    else:
        # Auto-match by model in strict priority order: Claude -> Argon -> Flash -> Gemini
        if any(k in full_model_str for k in pools_def['claude']['keywords']):
            target_pool = "claude"
        elif any(k in full_model_str for k in pools_def['argon']['keywords']):
            target_pool = "argon"
        elif any(k in full_model_str for k in pools_def['flash']['keywords']):
            target_pool = "flash"
        elif any(k in full_model_str for k in pools_def['gemini']['keywords']):
            target_pool = "gemini"
        else:
            target_pool = "gemini"

    q5h, qwk = get_pool_data(target_pool)

    # Graceful fallback if target pool has no data
    if not q5h and not qwk:
        for fallback_pool in ("gemini", "argon", "claude"):
            alt_5h, alt_wk = get_pool_data(fallback_pool)
            if alt_5h or alt_wk:
                target_pool = fallback_pool
                q5h, qwk = alt_5h, alt_wk
                break

    return [(target_pool, q5h, qwk)]

# ── Session Cost Estimation ──────────────────────────────
MODEL_PRICING = [
    # (keywords, input_per_1m, output_per_1m)
    (('opus',), 15.00, 75.00),
    (('sonnet',), 3.00, 15.00),
    (('haiku',), 0.80, 4.00),
    (('claude', '3p', 'anthropic'), 3.00, 15.00),
    (('flash', '3.8', '2.0-flash', '1.5-flash'), 0.10, 0.40),
    (('argon', 'gemini 4', 'gemini-4'), 1.25, 5.00),
    (('gemini', 'google', 'pro'), 1.25, 5.00),
]

def calculate_session_cost(data):
    """
    Calculates estimated session cost in USD based on session tokens and model rates.
    """
    for key in ("cost", "session_cost", "estimated_cost"):
        if isinstance(data.get(key), (int, float)):
            return float(data[key])

    ctx = data.get("context_window") or {}
    for key in ("cost", "session_cost", "estimated_cost"):
        if isinstance(ctx.get(key), (int, float)):
            return float(ctx[key])

    total_in = ctx.get("total_input_tokens")
    total_out = ctx.get("total_output_tokens")
    if total_in is None and total_out is None:
        cur = ctx.get("current_usage") or {}
        total_in = cur.get("input_tokens", 0)
        total_out = cur.get("output_tokens", 0)
    else:
        total_in = total_in or 0
        total_out = total_out or 0

    model_obj = data.get("model")
    m_str = ""
    if isinstance(model_obj, dict):
        m_str = f"{model_obj.get('id', '')} {model_obj.get('display_name', '')} {model_obj.get('name', '')}".lower()
    elif isinstance(model_obj, str):
        m_str = model_obj.lower()
    extra_str = f"{data.get('model_id', '')} {data.get('model_name', '')} {data.get('active_model', '')}".lower()
    full_m = f"{m_str} {extra_str}".strip()

    in_rate = 1.25
    out_rate = 5.00
    for kw_list, ir, or_ in MODEL_PRICING:
        if any(kw in full_m for kw in kw_list):
            in_rate = ir
            out_rate = or_
            break

    cost = (total_in * in_rate + total_out * out_rate) / 1_000_000.0
    return cost

# ── Renderers ────────────────────────────────────────────
def render_rounded(segments, colors):
    """Capsule / Pill Badges: (  text  ) (  text  )"""
    pills = []
    for i, seg in enumerate(segments):
        c_bg = colors[i % len(colors)]
        c_fg = seg.get('color', '#ffffff')
        txt = seg.get('text', '')
        sub = seg.get('sub', '')
        sub_c = seg.get('sub_color', '#abb2bf')

        pill = f"{fg(c_bg)}\ue0b6{bg(c_bg)}{fg(c_fg)} {txt}"
        if sub:
            pill += f"{fg(sub_c)}{sub}"
        pill += f" {RESET}{fg(c_bg)}\ue0b4{RESET}"
        pills.append(pill)
    return " ".join(pills)

def render_powerline(segments, colors):
    """Connected Powerline with gradient background:  seg1  seg2  seg3 """
    if not segments:
        return ""
    out = ""
    n = len(segments)
    for i, seg in enumerate(segments):
        c_bg = colors[i % len(colors)]
        next_bg = colors[(i + 1) % len(colors)] if i < n - 1 else None
        c_fg = seg.get('color', '#ffffff')
        txt = seg.get('text', '')
        sub = seg.get('sub', '')
        sub_c = seg.get('sub_color', '#abb2bf')

        if i == 0:
            out += f"{fg(c_bg)}\ue0b6{bg(c_bg)}{fg(c_fg)} {txt}"
        else:
            out += f"{bg(c_bg)}{fg(c_fg)} {txt}"

        if sub:
            out += f"{fg(sub_c)}{sub}"
        out += " "

        if next_bg:
            out += f"{bg(next_bg)}{fg(c_bg)}\ue0b0"
        else:
            out += f"{RESET}{fg(c_bg)}\ue0b4{RESET}"
    return out

def render_minimal(segments):
    """Clean modern minimalist line with subtle dividers: seg1 › seg2 › seg3"""
    parts = []
    div = f" {fg('#4a5568')}›{RESET} "
    for seg in segments:
        c_fg = seg.get('color', '#ffffff')
        txt = seg.get('text', '')
        sub = seg.get('sub', '')
        sub_c = seg.get('sub_color', '#6b7280')

        item = f"{fg(c_fg)}{txt}{RESET}"
        if sub:
            item += f" {fg(sub_c)}{sub}{RESET}"
        parts.append(item)
    return div.join(parts)

# ── Main ─────────────────────────────────────────────────
def main():
    try:
        if hasattr(sys.stdin, 'buffer'):
            raw_bytes = sys.stdin.buffer.read()
            if not raw_bytes or not raw_bytes.strip():
                sys.stdout.write("agy")
                sys.exit(0)
            try:
                raw_input = raw_bytes.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    raw_input = raw_bytes.decode('gbk')
                except Exception:
                    raw_input = raw_bytes.decode('utf-8', errors='replace')
        else:
            raw_input = sys.stdin.read()
    except Exception:
        raw_input = ""

    if not raw_input or not raw_input.strip():
        sys.stdout.write("agy")
        sys.exit(0)

    try:
        data = json.loads(raw_input)
    except Exception:
        sys.stdout.write("agy")
        sys.exit(0)

    cfg = load_config()
    theme_key = cfg.get("theme", "aurora").lower()
    theme = THEMES.get(theme_key, THEMES['aurora'])
    style = cfg.get("style", "powerline").lower()
    layout = cfg.get("layout", "two-lines").lower()
    use_nerd = cfg.get("nerd_fonts", True)
    bar_style = cfg.get("progress_bar", "smooth")
    show_quota = cfg.get("show_quota", True)
    show_cost = cfg.get("show_cost", True)
    quota_mode = cfg.get("quota_mode", "auto").lower()

    # Icons
    icon_folder = " " if use_nerd else "📁 "
    icon_git = " " if use_nerd else " "
    icon_agent = "⚡ "
    icon_model = "󰘚 " if use_nerd else "◈ "
    icon_ctx = "󰘚 " if use_nerd else ""
    icon_quota = "󰾆 " if use_nerd else "⏳ "
    icon_sync = "⟳"

    # 1. Directory
    cwd = data.get("cwd") or os.getcwd()
    try:
        dirname = os.path.basename(os.path.normpath(cwd)) or cwd
    except Exception:
        dirname = cwd

    # 2. Git Status
    git_branch = ""
    git_dirty = ""
    vcs = data.get("vcs")
    if isinstance(vcs, dict) and vcs.get("branch"):
        git_branch = vcs.get("branch")
        if vcs.get("dirty"):
            git_dirty = "*"

    if not git_branch:
        try:
            res = subprocess.run(
                ["git", "-C", cwd, "symbolic-ref", "--short", "HEAD"],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=1
            )
            if res.returncode == 0 and res.stdout:
                git_branch = res.stdout.decode('utf-8', errors='replace').strip()
            else:
                res = subprocess.run(
                    ["git", "-C", cwd, "rev-parse", "--short", "HEAD"],
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=1
                )
                if res.returncode == 0 and res.stdout:
                    git_branch = res.stdout.decode('utf-8', errors='replace').strip()

            if git_branch:
                res_d = subprocess.run(
                    ["git", "-C", cwd, "--no-optional-locks", "status", "--porcelain"],
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=1
                )
                if res_d.returncode == 0 and res_d.stdout and res_d.stdout.strip():
                    git_dirty = "*"
        except Exception:
            pass

    # 3. Model & Agent State
    model_obj = data.get("model")
    model_name = ""
    if isinstance(model_obj, dict):
        model_name = model_obj.get("display_name") or model_obj.get("name") or model_obj.get("id") or "agy"
    elif isinstance(model_obj, str):
        model_name = model_obj
    else:
        model_name = data.get("model_name") or data.get("active_model") or data.get("model_id") or "agy"

    agent_state = str(data.get("agent_state") or "").lower()

    # Format model display name cleanly
    model_display = model_name
    if "Sonnet" in model_display or "Opus" in model_display or "Haiku" in model_display:
        model_display = model_display.replace("Claude ", "").replace(" (Thinking)", " 🧠")
    elif "Argon" in model_display:
        model_display = model_display.replace(" (Medium)", " ✦ Med").replace(" (High)", " ✦ High")
    elif "Gemini" in model_display:
        model_display = model_display.replace(" (High)", " ⚡").replace(" (Medium)", " · Med")

    # 4. Context Usage
    ctx_obj = data.get("context_window") or {}
    raw_ctx = ctx_obj.get("used_percentage", 0)
    try:
        ctx_pct = round(float(raw_ctx))
    except (ValueError, TypeError):
        ctx_pct = 0
    ctx_color = get_color_for_pct(ctx_pct)

    # 5. Session Cost
    seg_cost = None
    if show_cost:
        cost = calculate_session_cost(data)
        if cost is not None:
            seg_cost = {
                'text': f"💰 ${cost:.2f}",
                'color': theme.get('cost', '#ebcb8b')
            }

    # 6. Plan Tier
    plan_tier = data.get("plan_tier") or ""

    # Build Line 1 Segments
    seg_folder = {
        'text': f"{icon_folder}{dirname}",
        'color': theme['accent']
    }

    seg_git = None
    if git_branch:
        seg_git = {
            'text': f"{icon_git}{git_branch}",
            'color': theme['git'],
            'sub': git_dirty,
            'sub_color': '#e06c75'
        }

    state_prefix = icon_agent if agent_state in ("working", "running") else ""
    seg_model = {
        'text': f"{state_prefix}{icon_model}{model_display}",
        'color': theme['model']
    }

    seg_ctx = {
        'text': f"{icon_ctx}ctx {ctx_pct}%",
        'color': ctx_color
    }

    seg_tier = None
    if plan_tier and plan_tier != "null":
        seg_tier = {
            'text': plan_tier,
            'color': theme['tier']
        }

    # 7. Build Quota Segments (Automatically matched by selected model)
    quota_segs = []
    first_pool_summary = None

    if show_quota:
        pools_data = extract_quota_pools(data, quota_mode)
        for pool_label, q5h_info, qwk_info in pools_data:
            q5h_pct = None
            if q5h_info and q5h_info.get("remaining_fraction") is not None:
                try:
                    q5h_pct = round((1.0 - float(q5h_info["remaining_fraction"])) * 100)
                except Exception:
                    q5h_pct = 0
                bar = build_bar(q5h_pct, 6, bar_style)
                rst_time = format_reset_time(q5h_info.get("reset_time"), "time")
                sub_txt = f" ({icon_sync} {rst_time})" if rst_time else ""
                quota_segs.append({
                    'text': f"{icon_quota}{pool_label} 5h {bar} {fg(get_color_for_pct(q5h_pct))}{q5h_pct}%",
                    'color': '#abb2bf',
                    'sub': sub_txt,
                    'sub_color': '#6b7280'
                })

            if qwk_info and qwk_info.get("remaining_fraction") is not None:
                try:
                    qwk_pct = round((1.0 - float(qwk_info["remaining_fraction"])) * 100)
                except Exception:
                    qwk_pct = 0
                bar = build_bar(qwk_pct, 6, bar_style)
                rst_time = format_reset_time(qwk_info.get("reset_time"), "datetime")
                sub_txt = f" ({icon_sync} {rst_time})" if rst_time else ""
                quota_segs.append({
                    'text': f"{pool_label} 7d {bar} {fg(get_color_for_pct(qwk_pct))}{qwk_pct}%",
                    'color': '#abb2bf',
                    'sub': sub_txt,
                    'sub_color': '#6b7280'
                })

            if first_pool_summary is None and q5h_pct is not None:
                first_pool_summary = (pool_label, q5h_pct)

    # Assemble Rows according to layout
    palette = theme['bg']

    if layout == "one-line":
        row1 = [seg_folder]
        if seg_git: row1.append(seg_git)
        row1.append(seg_model)
        row1.append(seg_ctx)
        if seg_cost: row1.append(seg_cost)
        if first_pool_summary:
            p_lbl, p_pct = first_pool_summary
            row1.append({
                'text': f"{icon_quota}{p_lbl} 5h {build_bar(p_pct, 5, bar_style)} {p_pct}%",
                'color': '#abb2bf'
            })
        if seg_tier: row1.append(seg_tier)

        if style == "powerline":
            out = render_powerline(row1, palette)
        elif style == "rounded":
            out = render_rounded(row1, palette)
        else:
            out = render_minimal(row1)

    else:  # two-lines
        row1 = [seg_folder]
        if seg_git: row1.append(seg_git)
        row1.append(seg_model)
        row1.append(seg_ctx)
        if seg_cost: row1.append(seg_cost)
        if seg_tier: row1.append(seg_tier)

        row2 = quota_segs

        if style == "powerline":
            line1_str = render_powerline(row1, palette)
            line2_str = render_powerline(row2, palette[2:]) if row2 else ""
        elif style == "rounded":
            line1_str = render_rounded(row1, palette)
            line2_str = render_rounded(row2, palette[2:]) if row2 else ""
        else:
            line1_str = render_minimal(row1)
            line2_str = render_minimal(row2) if row2 else ""

        if line2_str:
            out = f"{line1_str}\n{line2_str}"
        else:
            out = line1_str

    sys.stdout.write(out)
    sys.stdout.flush()

if __name__ == "__main__":
    main()
