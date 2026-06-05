# Example output — Northwind Labs ML Engineer

This folder is a **complete worked example** of what the pipeline produces for one
job offer. It was generated from [`../job_offer.md`](../job_offer.md) and the
fictional candidate in [`../../data.example/`](../../data.example/).

| File | Produced by |
|---|---|
| `cv.tex` | [`prompts/agent_guide.md`](../../prompts/agent_guide.md) — tailored CV |
| `grading.md` | [`prompts/agent_grading.md`](../../prompts/agent_grading.md) — CV-vs-offer scorecard |
| `how_to_apply.md` | [`prompts/agent_application_strategy.md`](../../prompts/agent_application_strategy.md) — apply strategy + cold email |

- **Template used:** `single_column_article`.
- **Build:** `latexmk -pdf cv.tex` (needs a LaTeX install with the `lato` font).
- Everything in `cv.tex` traces back to a fact in `data.example/` — nothing invented.
