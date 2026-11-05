import sys
sys.stdout.reconfigure(encoding='utf-8')

# Aurora theme colors
bg_colors = ['#1e2a4a', '#252b4b', '#2d2c4b', '#342d4c', '#3c2d4d', '#432e4e', '#4b2f4e']

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def bg(hex_c):
    r, g, b = hex_to_rgb(hex_c)
    return f'\033[48;2;{r};{g};{b}m'

def fg(hex_c):
    r, g, b = hex_to_rgb(hex_c)
    return f'\033[38;2;{r};{g};{b}m'

rst = '\033[0m'

pills = [
    ('📁 project', '#88c0d0', '#1e2a4a'),
    (' main*', '#ecc487', '#252b4b'),
    ('⚡ Gemini 3.8 Flash', '#c5a8d8', '#2d2c4b'),
    ('ctx 18%', '#a3be8c', '#342d4c'),
    ('Google AI Pro', '#9aa5c4', '#3c2d4d')
]

line1_capsule = ' '.join([f'{fg(bg_c)}\ue0b6{bg(bg_c)}{fg(txt_c)} {txt} {rst}{fg(bg_c)}\ue0b4{rst}' for txt, txt_c, bg_c in pills])

line2_pills = [
    ('gemini 5h ▰▰▰▰▱▱▱▱▱▱ 35% · ⟳ 16:00', '#ebcb8b', '#252b4b'),
    ('7d ▰▰▱▱▱▱▱▱▱▱ 18% · ⟳ nov 10, 20:00', '#a3be8c', '#342d4c')
]
line2_capsule = ' '.join([f'{fg(bg_c)}\ue0b6{bg(bg_c)}{fg(txt_c)} {txt} {rst}{fg(bg_c)}\ue0b4{rst}' for txt, txt_c, bg_c in line2_pills])

print('=== STYLE 1: ROUNDED CAPSULES ===')
print(line1_capsule)
print(line2_capsule)
print()

print('=== STYLE 2: POWERLINE GRADIENT ===')
pl_out = ''
for i, (txt, txt_c, bg_c) in enumerate(pills):
    next_bg = pills[i+1][2] if i < len(pills) - 1 else None
    if i == 0:
        pl_out += f'{fg(bg_c)}\ue0b6{bg(bg_c)}{fg(txt_c)} {txt} '
    else:
        pl_out += f'{bg(bg_c)}{fg(txt_c)} {txt} '
    
    if next_bg:
        pl_out += f'{bg(next_bg)}{fg(bg_c)}\ue0b0'
    else:
        pl_out += f'{rst}{fg(bg_c)}\ue0b4{rst}'
print(pl_out)

pl_out2 = ''
for i, (txt, txt_c, bg_c) in enumerate(line2_pills):
    next_bg = line2_pills[i+1][2] if i < len(line2_pills) - 1 else None
    if i == 0:
        pl_out2 += f'{fg(bg_c)}\ue0b6{bg(bg_c)}{fg(txt_c)} {txt} '
    else:
        pl_out2 += f'{bg(bg_c)}{fg(txt_c)} {txt} '
    
    if next_bg:
        pl_out2 += f'{bg(next_bg)}{fg(bg_c)}\ue0b0'
    else:
        pl_out2 += f'{rst}{fg(bg_c)}\ue0b4{rst}'
print(pl_out2)
print()

print('=== STYLE 3: MINIMAL MODERN ===')
m1 = f'{fg("#88c0d0")}📁 project{rst} {fg("#4a5568")}›{rst} {fg("#ecc487")} main*{rst} {fg("#4a5568")}›{rst} {fg("#c5a8d8")}⚡ Gemini 3.8 Flash{rst} {fg("#4a5568")}›{rst} {fg("#a3be8c")}ctx 18%{rst} {fg("#4a5568")}│{rst} {fg("#9aa5c4")}Google AI Pro{rst}'
m2 = f'{fg("#9aa5c4")}gemini 5h{rst} {fg("#ebcb8b")}▰▰▰▰▱▱▱▱▱▱ 35%{rst} {fg("#6b7280")}⟳ 16:00{rst}  {fg("#4a5568")}·{rst}  {fg("#9aa5c4")}7d{rst} {fg("#a3be8c")}▰▰▱▱▱▱▱▱▱▱ 18%{rst} {fg("#6b7280")}⟳ nov 10, 20:00{rst}'
print(m1)
print(m2)
