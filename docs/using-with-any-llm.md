# Using this with any LLM assistant

The CV-builder half of this repo is just **prompts + your `data/` + LaTeX templates**.
That's deliberately tool-agnostic. Any capable coding/chat assistant can drive it.

The mental model is always the same:

```
job offer  +  data/*.md  +  prompts/agent_guide.md   ──►   outputs/<job>/cv.tex
```

The model's only job is to **select and compress facts from `data/`** into a tailored
CV — it must not invent anything. Then optionally run the grading and apply prompts
on the result.

---

## Claude Code (this repo's default)

```
Read prompts/agent_guide.md and build a CV for examples/job_offer.md
using data/ and the single_column_article template. Write it to outputs/northwind/cv.tex.
```

A `PostToolUse` hook in [`.claude/settings.json`](../.claude/settings.json) auto-runs
`pdflatex` whenever a `cv.tex` is written, so you see build success/failure immediately.

## Cursor

Open the chat, then reference files with `@`:

```
@prompts/agent_guide.md  @examples/job_offer.md  @data
Build a tailored cv.tex into outputs/northwind/ using the single_column_article template.
```

## GitHub Copilot Chat

Use `#file:` references in the chat panel:

```
Using #file:prompts/agent_guide.md and the facts in #file:data/profile.md
#file:data/experience.md #file:data/projects.md #file:data/skills.md, build a
tailored CV for #file:examples/job_offer.md as LaTeX.
```

## Plain ChatGPT / Claude.ai (no repo access)

Paste, in one message:
1. The contents of `prompts/agent_guide.md`.
2. The contents of your `data/*.md` files.
3. The job offer text.
4. A template `.tex` from `templates/latex/`.

Then ask for a tailored `cv.tex`. Paste back into the repo and build locally.

---

## The four prompts

| Prompt | Output |
|---|---|
| [`agent_guide.md`](../prompts/agent_guide.md) | The tailored `cv.tex` (the main one) |
| [`agent_grading.md`](../prompts/agent_grading.md) | `grading.md` — honest CV-vs-offer scorecard |
| [`agent_application_strategy.md`](../prompts/agent_application_strategy.md) | `how_to_apply.md` — apply vs. cold-email + draft |
| `agent_{experience,projects,skills,education}.md` | Helpers for shaping each `data/` section |

See [`../examples/output_northwind_ml_engineer/`](../examples/output_northwind_ml_engineer/)
for a full generated set.
