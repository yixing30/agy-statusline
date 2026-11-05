#!/bin/bash
set -f
export LC_NUMERIC=C
export LC_TIME=C

input=$(cat)

if [ -z "$input" ]; then
    printf "agy"
    exit 0
fi

# ── Colors (24-bit TrueColor, matching Ranteck/agy-statusline) ──────────────
blue='\033[38;2;0;153;255m'
orange='\033[38;2;255;176;85m'
green='\033[38;2;0;175;80m'
cyan='\033[38;2;86;182;194m'
red='\033[38;2;255;85;85m'
yellow='\033[38;2;230;200;0m'
white='\033[38;2;220;220;220m'
magenta='\033[38;2;180;140;255m'
dim='\033[2m'
bold='\033[1m'
reset='\033[0m'

sep=" ${dim}│${reset} "
dot=" ${dim}·${reset} "

# ── Helpers ─────────────────────────────────────────────────────────────────
# Color for context usage % (higher = worse)
color_for_used_pct() {
    local pct=${1:-0}
    if [ "$pct" -ge 90 ] 2>/dev/null; then printf "$red"
    elif [ "$pct" -ge 70 ] 2>/dev/null; then printf "$yellow"
    elif [ "$pct" -ge 50 ] 2>/dev/null; then printf "$orange"
    else printf "$green"
    fi
}

# Color for remaining quota % (higher = better, matching /usage)
color_for_rem_pct() {
    local pct=${1:-100}
    if [ "$pct" -le 10 ] 2>/dev/null; then printf "$red"
    elif [ "$pct" -le 30 ] 2>/dev/null; then printf "$yellow"
    elif [ "$pct" -le 50 ] 2>/dev/null; then printf "$orange"
    else printf "$green"
    fi
}

format_countdown() {
    local sec=${1:-0}
    [ -z "$sec" ] || [ "$sec" -le 0 ] 2>/dev/null && return
    local d=$(( sec / 86400 ))
    local h=$(( (sec % 86400) / 3600 ))
    local m=$(( (sec % 3600) / 60 ))
    if [ "$d" -gt 0 ]; then
        printf "%dd%dh" "$d" "$h"
    elif [ "$h" -gt 0 ]; then
        printf "%dh%02dm" "$h" "$m"
    else
        [ "$m" -le 0 ] && m=1
        printf "%dm" "$m"
    fi
}

# Cross-platform (macOS BSD date + Linux GNU date) reset time & countdown formatter
format_reset_info() {
    local reset_iso=$1
    local reset_sec=$2
    local style=$3       # "time" (5h), "datetime" (7d), or "short_date" (narrow 7d)
    local show_cd=$4     # "both" (countdown + clock), "cd_only", or "clock_only"

    local now_ts
    now_ts=$(date +%s 2>/dev/null)
    local epoch=""

    # 1. Parse ISO-8601 reset_time first (deterministic & exact)
    if [ -n "$reset_iso" ] && [ "$reset_iso" != "null" ]; then
        local clean_iso="${reset_iso%%.*}"
        clean_iso="${clean_iso%Z}Z"
        epoch=$(TZ=UTC date -j -f "%Y-%m-%dT%H:%M:%SZ" "$clean_iso" +%s 2>/dev/null || date -d "$reset_iso" +%s 2>/dev/null)
    fi

    # 2. Fallback to reset_in_seconds if ISO-8601 parsing failed or was omitted
    if [ -z "$epoch" ] && [ -n "$reset_sec" ] && [ "$reset_sec" != "null" ] && [ "$reset_sec" -gt 0 ] 2>/dev/null; then
        [ -n "$now_ts" ] && epoch=$(( now_ts + reset_sec ))
    fi

    # Compute remaining seconds if not explicitly provided
    if { [ -z "$reset_sec" ] || [ "$reset_sec" = "null" ] || [ "$reset_sec" -le 0 ] 2>/dev/null; } && [ -n "$epoch" ] && [ -n "$now_ts" ]; then
        reset_sec=$(( epoch - now_ts ))
    fi

    local cd_str=""
    if [ "$show_cd" != "clock_only" ] && [ -n "$reset_sec" ] && [ "$reset_sec" -gt 0 ] 2>/dev/null; then
        cd_str=$(format_countdown "$reset_sec")
    fi

    local clock_str=""
    if [ "$show_cd" != "cd_only" ] && [ -n "$epoch" ]; then
        if [ "$style" = "time" ]; then
            clock_str=$(date -r "$epoch" +"%H:%M" 2>/dev/null || date -d "@$epoch" +"%H:%M" 2>/dev/null)
        elif [ "$style" = "short_date" ]; then
            clock_str=$( (date -r "$epoch" +"%b %-d" 2>/dev/null || date -d "@$epoch" +"%b %-d" 2>/dev/null) | tr '[:upper:]' '[:lower:]' )
        else
            clock_str=$( (date -r "$epoch" +"%b %-d,%H:%M" 2>/dev/null || date -d "@$epoch" +"%b %-d,%H:%M" 2>/dev/null) | tr '[:upper:]' '[:lower:]' )
        fi
    fi

    if [ -n "$cd_str" ] && [ -n "$clock_str" ]; then
        printf "%s ${dim}(%s)${reset}" "$cd_str" "$clock_str"
    elif [ -n "$cd_str" ]; then
        printf "%s" "$cd_str"
    elif [ -n "$clock_str" ]; then
        printf "%s" "$clock_str"
    fi
}

# ── Extract ALL JSON data in a SINGLE jq pass ──────────────────────────────
eval "$(
    printf "%s" "$input" | jq -r '
        def sh(k; v): "\(k)=\(v | tostring | @sh)";
        # Used % = 100 - floor(remaining %), consistent with official /usage remaining display
        def used_pct(rem):
            if rem == null or rem == "" then ""
            else (100 - ((rem | tonumber) * 100 | if . < 0 then 0 elif . > 100 then 100 else floor end))
            end;

        (.model.display_name // "agy") as $mname |
        (.model.id // "" | ascii_downcase) as $mid |
        ($mname | ascii_downcase) as $mname_low |
        (.model.effort // "") as $meffort |
        (.quota // {}) as $q |

        # Auto-detect active model pool: Claude (3p) vs Gemini Argon vs Standard Gemini
        (if ($mid | test("claude|anthropic|3p")) or ($mname_low | test("claude|anthropic")) then
            "claude"
         elif ($mid | test("argon")) or ($mname_low | test("argon")) then
            "argon"
         else
            "gemini"
         end) as $pool |

        (if $pool == "claude" then "claude" else "gemini" end) as $p5h_label |
        (if $pool == "claude" then "claude"
         elif $pool == "argon" then "argon"
         else "gemini" end) as $pwk_label |

        (if $pool == "claude" then ($q["3p-5h"] // {})
         else ($q["gemini-5h"] // {}) end) as $b5 |

        (if $pool == "claude" then ($q["3p-weekly"] // {})
         elif $pool == "argon" then ($q["gemini-argon-wtu-weekly"] // $q["gemini-weekly"] // {})
         else ($q["gemini-weekly"] // {}) end) as $bw |

        sh("model_name"; $mname),
        sh("model_short"; ($mname | split(" (")[0])),
        sh("model_effort"; $meffort),
        sh("effort_in_name"; (if $meffort != "" and ($mname_low | contains($meffort | ascii_downcase)) then "true" else "false" end)),
        sh("cwd"; (.workspace.current_dir // .cwd // "")),
        sh("cols"; (.terminal_width // 120)),
        sh("ctx_pct"; ((.context_window.used_percentage // 0) | round)),
        sh("agent_state"; (.agent_state // "idle")),
        sh("cycle_mode"; (.cycle_mode // "")),
        sh("plan_tier"; (.plan_tier // "")),
        sh("vcs_branch"; (.vcs.branch // "")),
        sh("vcs_dirty"; (if .vcs.dirty == true then "*" else "" end)),
        sh("sandbox_enabled"; (if .sandbox.enabled == true then "true" else "false" end)),
        sh("artifact_count"; (.artifact_count // 0)),
        sh("task_count"; (.task_count // 0)),
        sh("pending_input"; (.pending_input_count // 0)),
        sh("confirm_pending"; (if .tool_confirmation_pending == true then "true" else "false" end)),
        sh("subagents_running"; (if (.subagents | type) == "array" then ([.subagents[] | select(.status == "running")] | length) else 0 end)),
        sh("subagents_total"; (if (.subagents | type) == "array" then (.subagents | length) else 0 end)),
        sh("cost_fmt"; (
            ((.cost.total_usd // 0) | tonumber) as $reported_cost |
            (if $reported_cost > 0 then
                $reported_cost
             else
                # Fallback estimation when agy omits .cost (e.g. Gemini 4 Argon preview model)
                ((.context_window.total_input_tokens // 0) | tonumber) as $in_tok |
                ((.context_window.total_output_tokens // 0) | tonumber) as $out_tok |
                ((.context_window.current_usage.cache_read_input_tokens // 0) | tonumber) as $cache_tok |
                ([($in_tok - $cache_tok), 0] | max) as $uncached_in |
                if $pool == "claude" then
                    ($uncached_in * 3.0 + $cache_tok * 0.30 + $out_tok * 15.0) / 1000000
                else
                    ($uncached_in * 1.25 + $cache_tok * 0.3125 + $out_tok * 10.0) / 1000000
                end
             end) as $c |
            if $c <= 0 then "0.00"
            elif $c < 0.01 then ($c * 10000 | round / 10000 | tostring)
            else "\($c * 100 | round / 100)"
            end
        )),
        sh("p5h_label"; $p5h_label),
        sh("pwk_label"; $pwk_label),
        sh("q5h_pct"; used_pct($b5.remaining_fraction)),
        sh("q5h_iso"; ($b5.reset_time // "")),
        sh("q5h_sec"; ($b5.reset_in_seconds // "")),
        sh("qwk_pct"; used_pct($bw.remaining_fraction)),
        sh("qwk_iso"; ($bw.reset_time // "")),
        sh("qwk_sec"; ($bw.reset_in_seconds // ""))
    ' 2>/dev/null
)"

[ -z "$model_name" ] && model_name="agy"
[ -z "$model_short" ] && model_short="$model_name"
[ -z "$cwd" ] || [ "$cwd" = "null" ] && cwd=$(pwd)
dirname=$(basename "$cwd")
[ -z "$ctx_pct" ] && ctx_pct=0
[ -z "$cols" ] || [ "$cols" -le 0 ] 2>/dev/null && cols=120

# ── Responsive Layout Tier ──────────────────────────────────────────────────
# wide: >= 110 cols | medium: 80..109 cols | narrow: < 80 cols
if [ "$cols" -ge 110 ]; then
    layout="wide"
elif [ "$cols" -ge 80 ]; then
    layout="medium"
else
    layout="narrow"
fi

# ── Git info (use agy native .vcs if present, fallback to git) ─────────────
git_branch="$vcs_branch"
git_dirty="$vcs_dirty"
if [ -z "$git_branch" ] && git -C "$cwd" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git_branch=$(git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null || git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
    if [ -n "$(git -C "$cwd" --no-optional-locks status --porcelain 2>/dev/null)" ]; then
        git_dirty="*"
    fi
fi

# ── Agent state label ───────────────────────────────────────────────────────
state_badge=""
if [ "$confirm_pending" = "true" ]; then
    state_badge="${yellow}[confirm]${reset} "
else
    case "$agent_state" in
        working|running|thinking) state_badge="${yellow}[working]${reset} " ;;
        tool_use)                 state_badge="${magenta}[tool]${reset} " ;;
        reviewing)                state_badge="${cyan}[review]${reset} " ;;
        authenticating|initializing) state_badge="${blue}[init]${reset} " ;;
        error)                    state_badge="${red}[error]${reset} " ;;
        idle|*)                   state_badge="" ;;
    esac
fi

# ── LINE 1 Construction ─────────────────────────────────────────────────────
# 1. Model (+ effort if not already in display_name)
if [ "$layout" = "narrow" ]; then
    line1="${blue}${model_short}${reset}"
else
    line1="${blue}${model_name}${reset}"
    if [ -n "$model_effort" ] && [ "$model_effort" != "null" ] && [ "$effort_in_name" = "false" ]; then
        line1+=" ${dim}(${model_effort})${reset}"
    fi
fi

# 2. Context Window %
ctx_color=$(color_for_used_pct "$ctx_pct")
line1+="${sep}${dim}ctx${reset} ${ctx_color}${ctx_pct}%${reset}"

# 3. State + Directory + Git branch
line1+="${sep}${state_badge}${cyan}${dirname}${reset}"
if [ -n "$git_branch" ]; then
    line1+=" ${green}(${git_branch}${red}${git_dirty}${green})${reset}"
fi

# 4. Cycle Mode (Shift+Tab mode: plan / auto / accept-edits)
if [ -n "$cycle_mode" ] && [ "$cycle_mode" != "null" ]; then
    case "$cycle_mode" in
        plan)         line1+="${sep}${dim}mode:${reset}${magenta}plan${reset}" ;;
        auto)         line1+="${sep}${dim}mode:${reset}${yellow}auto${reset}" ;;
        accept-edits)
            if [ "$layout" = "narrow" ]; then
                line1+="${sep}${dim}mode:${reset}${green}edits${reset}"
            else
                line1+="${sep}${dim}mode:${reset}${green}accept-edits${reset}"
            fi
            ;;
        *)            line1+="${sep}${dim}mode:${reset}${cyan}${cycle_mode}${reset}" ;;
    esac
fi

# 5. Dynamic Activity Counters (Subagents / Tasks / Artifacts / Queued Input)
activity_parts=()
if [ "${subagents_running:-0}" -gt 0 ] 2>/dev/null; then
    activity_parts+=("${dim}subagents:${reset}${magenta}${subagents_running}/${subagents_total}${reset}")
elif [ "${subagents_total:-0}" -gt 0 ] 2>/dev/null && [ "$layout" != "narrow" ]; then
    activity_parts+=("${dim}subagents:${subagents_total}${reset}")
fi
if [ "${task_count:-0}" -gt 0 ] 2>/dev/null; then
    activity_parts+=("${dim}tasks:${reset}${yellow}${task_count}${reset}")
fi
if [ "${artifact_count:-0}" -gt 0 ] 2>/dev/null && [ "$layout" != "narrow" ]; then
    activity_parts+=("${dim}artifacts:${reset}${cyan}${artifact_count}${reset}")
fi
if [ "${pending_input:-0}" -gt 0 ] 2>/dev/null; then
    activity_parts+=("${dim}queue:${reset}${orange}${pending_input}${reset}")
fi

if [ "${#activity_parts[@]}" -gt 0 ]; then
    activity_str="${activity_parts[0]}"
    for ((i=1; i<${#activity_parts[@]}; i++)); do
        activity_str+="${dot}${activity_parts[$i]}"
    done
    line1+="${sep}${activity_str}"
fi

# 6. Sandbox Status (Wide: on/off; Medium/Narrow: only when on)
if [ "$sandbox_enabled" = "true" ]; then
    line1+="${sep}${dim}sandbox:${reset}${green}on${reset}"
elif [ "$layout" = "wide" ]; then
    line1+="${sep}${dim}sandbox:off${reset}"
fi

# 7. Estimated Cost (shown when > 0 on wide/medium)
if [ -n "$cost_fmt" ] && [ "$layout" != "narrow" ]; then
    # Pad 2 decimals if needed (e.g. 0.4 -> 0.40)
    case "$cost_fmt" in
        *.*)
            dec_part="${cost_fmt#*.}"
            [ "${#dec_part}" -eq 1 ] && cost_fmt="${cost_fmt}0"
            ;;
    esac
    line1+="${sep}💰 ${yellow}\$${cost_fmt}${reset}"
fi

# 8. Plan Tier (Wide layout only)
if [ "$layout" = "wide" ] && [ -n "$plan_tier" ] && [ "$plan_tier" != "null" ]; then
    line1+="${sep}${dim}${plan_tier}${reset}"
fi

# ── LINE 2: Single-Line Combined Quota (Remaining %) + Model/Alt Pool ──────
quota_parts=()

# 5h quota (with live countdown + clock time)
if [ -n "$q5h_pct" ]; then
    q5h_color=$(color_for_used_pct "$q5h_pct")
    if [ "$layout" = "narrow" ]; then
        q5h_reset_fmt=$(format_reset_info "$q5h_iso" "$q5h_sec" "time" "cd_only")
    else
        q5h_reset_fmt=$(format_reset_info "$q5h_iso" "$q5h_sec" "time" "both")
    fi

    part_5h="${white}${p5h_label} 5h${reset} ${q5h_color}${q5h_pct}%${reset}"
    [ -n "$q5h_reset_fmt" ] && part_5h+=" ${dim}reset${reset} ${white}${q5h_reset_fmt}${reset}"
    quota_parts+=("$part_5h")
fi

# 7d (weekly) quota
if [ -n "$qwk_pct" ]; then
    qwk_color=$(color_for_used_pct "$qwk_pct")
    if [ "$layout" = "narrow" ]; then
        qwk_reset_fmt=$(format_reset_info "$qwk_iso" "$qwk_sec" "short_date" "clock_only")
    elif [ "$layout" = "medium" ]; then
        qwk_reset_fmt=$(format_reset_info "$qwk_iso" "$qwk_sec" "datetime" "clock_only")
    else
        qwk_reset_fmt=$(format_reset_info "$qwk_iso" "$qwk_sec" "datetime" "both")
    fi

    # Omit repeated label before "7d" only if it matches the 5h label
    if [ "${#quota_parts[@]}" -gt 0 ] && [ "$pwk_label" = "$p5h_label" ]; then
        wk_prefix="${white}7d${reset}"
    else
        wk_prefix="${white}${pwk_label} 7d${reset}"
    fi
    part_wk="${wk_prefix} ${qwk_color}${qwk_pct}%${reset}"
    [ -n "$qwk_reset_fmt" ] && part_wk+=" ${dim}reset${reset} ${white}${qwk_reset_fmt}${reset}"
    quota_parts+=("$part_wk")
fi

line2=""
if [ "${#quota_parts[@]}" -gt 0 ]; then
    line2="${quota_parts[0]}"
    for ((i=1; i<${#quota_parts[@]}; i++)); do
        line2+="${sep}${quota_parts[$i]}"
    done
fi

# ── Output (Compact 2-line layout, no wasted blank line) ────────────────────
printf "%b" "$line1"
[ -n "$line2" ] && printf "\n%b" "$line2"

exit 0
