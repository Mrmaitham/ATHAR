# -*- coding: utf-8 -*-
LRI = "⁦"
PDI = "⁩"

def iso(s):
    return LRI + s + PDI

def ts(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

HEADER = """[Script Info]
Title: BY ATHAR - motion graphics scoreboard overlay
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Neutral,DejaVu Sans,44,&H00FFFFFF,&H00FFFFFF,&H00000000,&H002E1A0A,1,0,0,0,100,100,0,0,3,0,0,8,60,60,150,1
Style: Goal,DejaVu Sans,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H001E1EC8,1,0,0,0,100,100,0,0,3,0,0,8,60,60,150,1
Style: Final,DejaVu Sans,48,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00141480,1,0,0,0,100,100,0,0,3,0,0,8,60,60,150,1
Style: Tick,DejaVu Sans,34,&H0000D7FF,&H0000D7FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,0,8,60,60,160,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

POP = r"{\fscx125\fscy125\t(0,220,\fscx100\fscy100)\fad(120,200)}"
POP_STRONG = r"{\fscx135\fscy135\t(0,180,\fscx100\fscy100)\fad(100,220)}"

cues = []

# 1. Context card
cues.append((0.30, 7.00, "Neutral", POP +
    f"نصف نهائي دوري أبطال أوروبا\\Nالإياب خارج الأرض: برشلونة متأخر بهدفين"))

# 2. Comeback lead
cues.append((7.90, 17.60, "Neutral", POP +
    f"الدقيقة 88\\Nبرشلونة {iso('3-2')} إنتر ميلان — على أعتاب النهائي"))

# 3. Tension tick
cues.append((18.10, 21.70, "Tick", r"{\fad(150,150)}" +
    "الوقت المحتسب بدل الضائع..."))

# 4. Acerbi equalizer
cues.append((22.10, 26.70, "Goal", POP_STRONG +
    f"الدقيقة 90+3 — أتشيربي ⚽\\Nالتعادل {iso('3-3')}"))

# 5. Frattesi winner
cues.append((27.10, 34.20, "Goal", POP_STRONG +
    f"الدقيقة 99 — فراتيزي ⚽\\Nإنتر يتقدم {iso('4-3')}"))

# 6. Final aggregate
cues.append((34.80, 45.30, "Final", POP_STRONG +
    f"النتيجة النهائية {iso('4-3')}\\Nالمجموع الكلي {iso('7-6')} — برشلونة خارج"))

lines = [HEADER]
for start, end, style, text in cues:
    lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},{style},,0,0,0,,{text}\n")

open("/tmp/claude-0/-home-user-ATHAR/e639d42b-0cc8-54e3-9a7a-db72f0bbc150/scratchpad/motiongfx/scoreboard.ass", "w", encoding="utf-8").write("".join(lines))
print("done")
