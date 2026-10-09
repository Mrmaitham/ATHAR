# Product Marketing Context — multi-project router

Each project has its own marketing agent (decided 2026-10-09, one agent = one project):
- أثر → `athar-agent` (`.claude/agents/athar-agent.md`)
- Little Wonder → `littlewonder-agent` (`.claude/agents/littlewonder-agent.md`)

Use a separate chat/session per project.

This repository markets **several projects**, so there is no single context document here.
Each project has its own folder:

| Project | Context file |
|---|---|
| Little Wonder (الأعجوبة الصغيرة) — English-language kids' animated series on YouTube (global audience, Arab touch) | `.agents/projects/little-wonder/context.md` |
| أثر (ATHAR brand) — Kuwaiti luxury fragrance brand; phase 1 = car-shaped car air fresheners. **Not** the BY ATHAR YouTube channel. | `.agents/projects/athar-brand/context.md` |

Shared knowledge for every project (Gulf/Arabic market, platforms, seasons) lives in `.agents/shared/`.

## Rules for every marketing skill

1. Work out which project the request is for. If the request does not name it clearly, **ask** —
   never guess, and never mix two projects' context in one piece of work.
2. Read that project's `context.md` (and any file in `.agents/shared/`) before asking questions.
3. Lines marked ❓ are unconfirmed. Do not present them as facts; ask, or flag the assumption.
4. Save campaign outputs and results under `.agents/projects/<project>/campaigns/`.
5. To create or update a project's context, use the `product-marketing` skill and write to
   `.agents/projects/<project>/context.md` — not to this file.
