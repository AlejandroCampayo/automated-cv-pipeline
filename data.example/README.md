# `data/` — your source of truth

This folder is the **single source of truth** the LLM uses to write your CVs. The
golden rule enforced by every prompt in [`../prompts/`](../prompts/) is:

> **The model may only use facts that exist in `data/`.** It never invents
> employers, dates, numbers, or skills.

So the quality of your generated CVs is exactly as good as what you put here.
Write *more* than fits on a CV — long-form, with concrete outcomes and numbers.
The model's job is to **select and compress**, not to embellish.

## How to use

1. Copy this folder to `data/` (which is git-ignored, so your real info stays private):
   ```bash
   cp -r data.example data
   ```
2. Replace the fictional **Jane Doe** content with your own.
3. Keep one fact per place. If a degree or title can be framed differently for
   different roles, say so in a `Notes:` line (see `education.md`) — the model
   will pick the right framing per offer.

## Files

| File | What goes in it |
|---|---|
| `profile.md` | Name, tagline, location, availability, 1–2 sentence summary |
| `contact.md` | Email, phone, location, links (LinkedIn, GitHub, site) |
| `experience.md` | Every role, long-form, with measurable outcomes |
| `projects.md` | Projects with stack + highlights (the raw material for bullets) |
| `skills.md` | Skills grouped (core / tools / languages / other) |
| `education.md` | Degrees, grades, theses, notable framing notes |

## Tips for high-signal data

- **Lead with outcomes**: "cut report turnaround from 2 days to 10 min", not
  "built reports".
- **Name the stack** explicitly — the grader checks keyword/ATS overlap against it.
- **Mark anything ambiguous** with a `Notes:` line so the model knows your intent.
- It's fine to leave `TODO` markers; the model will simply skip them.
