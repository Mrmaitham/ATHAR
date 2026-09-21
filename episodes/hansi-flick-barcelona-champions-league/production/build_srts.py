# -*- coding: utf-8 -*-
import json

durations = [37.146122, 18.520816, 21.394286, 13.949388, 36.440816, 12.930612,
             17.319184, 58.514286, 28.995918, 45.557551, 50.991020, 49.867755,
             17.005714, 33.488980, 38.347755, 37.146122]

starts = []
acc = 0.0
for d in durations:
    starts.append(acc)
    acc += d
ends = [starts[i] + durations[i] for i in range(len(durations))]

english = {
1: ["Barcelona have just won back-to-back league titles under Hansi Flick.",
    "They have more attacking talent on that pitch than almost anyone else in Europe.",
    "And for the second year running, their season ended the same way: not with the trophy that actually matters to them, but with a Champions League exit that exposed the exact same weakness both times.",
    "So this is the real question going into this season: is Hansi Flick actually the coach who fixes that?",
    "Or is he the coach who's shown us, twice now, precisely where the ceiling is?"],
2: ["Start with what we know for certain: Flick can win the Champions League.",
    "In November 2019, he took over Bayern Munich as an emergency appointment, an assistant thrown into the job mid-season.",
    "Six months later, Bayern had won everything there was to win."],
3: ["The Bundesliga. The German Cup.",
    "The Champions League, won in the final without losing a single game that campaign.",
    "Then the UEFA Super Cup, the German Super Cup, and the Club World Cup followed in the months after.",
    "Six trophies. This wasn't a coach getting lucky once — this was total, generational domination."],
4: ["And yet, a year later, he was gone — a breakdown in his relationship with Bayern's sporting director over transfer strategy left him walking away from the best job in German football, at the peak of his powers."],
5: ["What happened next is the part that should make everyone cautious about assuming Flick simply solves problems by showing up.",
    "He took the Germany national team job in 2021. It did not go well.",
    "A group-stage exit at the 2022 World Cup. Poor form through 2023.",
    "And in September of that year, after a heavy defeat to Japan, Flick was sacked — the first head coach in the history of the German national team to be dismissed mid-tenure.",
    "The same coach. A completely different outcome."],
6: ["So when Barcelona hired him in July 2024 to replace Xavi, they weren't just betting on the Bayern version of Hansi Flick.",
    "They were betting he'd learned something from the Germany version too."],
7: ["On the domestic front, it's hard to argue with the results.",
    "In his very first season, Flick won the treble at home: La Liga, the Copa del Rey, and the Spanish Super Cup.",
    "Barcelona looked, week to week, like the most dangerous attacking team in Europe."],
8: ["To understand why Barcelona keep hitting the same wall in Europe, you have to understand how Flick actually builds his team.",
    "This Barcelona plays with an extremely high defensive line, using a synchronized offside trap almost as an attacking weapon in itself — squeezing the pitch so the opposition barely has room to build.",
    "In front of that line, Pedri drops deep to control possession before pushing into advanced pockets, while Lamine Yamal, Raphinha and Ferran Torres are given license to attack the space in behind at real pace.",
    "Across the 2024-25 season, it produced an average of nearly three goals a game.",
    "It's also, by design, a high-risk system — one that only works if the back line's timing is perfect, every single time, against every opponent."],
9: ["Then came the Champions League semi-final against Inter Milan, and this tie is where the story of Flick's Barcelona really starts to take shape.",
    "The first leg at Montjuïc, on the 30th of April 2025, was end-to-end chaos in the best possible way — 3 to 3, Barcelona twice pulled back from behind.",
    "Nothing was decided. Everything would come down to the second leg, away, at the San Siro."],
10: ["Away at the San Siro, needing something special, Barcelona fell two goals behind by half-time.",
     "They didn't fold. They came storming back, and by the 88th minute, they were ahead, 3 to 2 on the night, on the verge of a final.",
     "Then it slipped away in the cruelest possible way.",
     "Francesco Acerbi equalized in the third minute of stoppage time. Extra time couldn't save them either — Davide Frattesi scored the winner in the 99th minute.",
     "Final score: 4 to 3. Barcelona were out, 7 to 6 on aggregate, in one of the most dramatic semi-finals the competition has ever produced."],
11: ["It would be easy to write that off as one chaotic night.",
     "Except the 2025-26 season told almost exactly the same story again — just earlier.",
     "Barcelona did retain the La Liga title, eight points clear of Real Madrid, genuinely dominant at home for a second straight year.",
     "But this time, in the Champions League quarter-finals, it was Atlético Madrid waiting for them.",
     "Barcelona fell two goals behind in the tie. They fought back again, through Yamal and Ferran Torres, the same players, the same instinct.",
     "And they conceded again, at the wrong moment, going out 3 to 2 on aggregate.",
     "Same comeback. Same collapse. A different opponent, and this time, an even earlier exit."],
12: ["So what's actually going on here?",
     "Twice now, against two different opponents, in two different rounds, the pattern is identical: Barcelona in total control domestically, and structurally exposed in Europe specifically.",
     "Both times, it traces back to that same high line and that same offside trap — a system that manufactures huge attacking overloads against sides willing to sit off, but leaves real space in behind against the kind of elite, patient, ruthless opponents the Champions League's later rounds are built from.",
     "Inter didn't out-play Barcelona for ninety minutes. Neither did Atlético.",
     "They waited for exactly those gaps, and they punished them when it mattered most."],
13: ["Barcelona's own hierarchy seems to agree with that diagnosis.",
     "This past summer, the club made it clear that going deep in Europe — not just winning Spain again — was the actual priority behind a significant reshaping of Flick's squad."],
14: ["Three signings tell you what they think the fix looks like.",
     "Rodri arrives as exactly the kind of tempo-controlling midfield presence Barcelona have lacked — a player whose entire game is built around not conceding the exact transitions that beat them against both Inter and Atlético.",
     "Anthony Gordon and Karim Adeyemi both add pace and directness in wide areas, attackers who can finish games early rather than leaving them stretched out until the moment the Champions League bites back."],
15: ["On paper, that's a squad built to solve two straight years of the same specific failure.",
     "But new signings changing a shape on a whiteboard is very different from a manager actually being willing to sacrifice attacking risk for defensive control — and that's the tension that's followed Flick his entire career.",
     "Bayern in 2020 was daring and still won everything. Germany was daring and it got him sacked.",
     "Which version of that instinct shows up in Barcelona's biggest European nights this time is still an open question."],
16: ["Hansi Flick has already proven he can win the biggest prize in club football.",
     "He's also proven, with a different team, that the same approach can completely fall apart.",
     "Barcelona now have two league titles, two eliminations built from the identical flaw, and a rebuilt squad aimed directly at it.",
     "Whether that's enough to finally get Flick to a European final — or whether Barcelona are simply building toward a third straight collapse in the same place — is exactly what this season is going to answer."],
}

arabic = json.load(open("arabic_sentences.json", encoding="utf-8"))
arabic = {int(k): v for k, v in arabic.items()}

def ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)

def build(lang_dict, outfile):
    idx = 1
    lines = []
    for scene in range(1, 17):
        groups = lang_dict[scene]
        assert len(groups) == len(arabic[scene]), f"scene {scene} count mismatch"
        s0, s1 = starts[scene - 1], ends[scene - 1]
        total_chars = sum(len(g) for g in groups)
        cursor = s0
        for gi, g in enumerate(groups):
            share = len(g) / total_chars
            dur = share * (s1 - s0)
            cue_start = cursor
            cue_end = min(cursor + dur, s1) - (0.12 if gi < len(groups) - 1 else 0)
            lines.append(f"{idx}\n{ts(cue_start)} --> {ts(cue_end)}\n{g}\n")
            idx += 1
            cursor += dur
    open(outfile, "w", encoding="utf-8").write("\n".join(lines))
    print(outfile, "cues:", idx - 1)

build(english, "subtitles_en.srt")
build(arabic, "subtitles_ar.srt")
