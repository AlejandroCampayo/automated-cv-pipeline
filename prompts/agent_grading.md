# Agent Guide (CV Grading)

Goal: Produce a `grading.md` that objectively scores a tailored CV against its job offer, exposing decoupled sub-scores, missing keywords, unfulfilled requirements, and a calibrated interview-callback probability.

## Inputs
- The job offer file in `job_offers/`.
- The tailored `cv.tex` in the matching `outputs/job_offers/<folder>/`.
- Source data in `data/` (to verify nothing was fabricated and to spot real-but-omitted strengths).

## Output
- Write `grading.md` inside the same `outputs/job_offers/<folder>/` as the CV.

## Scoring model (decoupled sub-scores)
Score each dimension 0-10 with a one-line justification. Do NOT average blindly — weight per the role.

| Dimension | What it measures | Default weight |
|---|---|---|
| Keyword / ATS match | Share of the offer's concrete keywords present in the CV | 20% |
| Must-have requirements | Hard requirements explicitly met (years, degree, mandatory tools, language, nationality) | 30% |
| Seniority & experience | Years and scope vs. what the role expects | 15% |
| Domain fit | Industry / problem-domain alignment | 15% |
| Tooling / tech stack | Named technologies the candidate genuinely has vs. required | 15% |
| Communication / soft fit | Stakeholder, collaboration, language, location signals | 5% |

- Compute a weighted overall score (0-100).
- Re-weight when a role clearly emphasizes something (e.g. a hard language gate). State any re-weighting.
- **Core-stack / domain gate (prevents false "strong"):** judge against the role's actual
  day-to-day stack, not its title. If the core stack or domain is outside the candidate's
  (e.g. a Power Platform / Microsoft 365 / low-code IT-infrastructure role, or a stated
  must-have like "2+ years with X" the candidate lacks) it is at most a **consider** — do not
  award "strong" (80+) on a shared word like "AI" or generic keyword overlap. A "strong"
  requires the candidate to plausibly do the core work the role is actually hiring for.

## Interview-callback probability
Give a single % band (e.g. 35-45%) for "gets contacted for next round if applying cold via the portal." Calibrate against:
- Any hard gate that is unmet (language, nationality, mandatory tool, min years) caps probability sharply.
- Volume/competition of the channel (mass job board < niche posting < direct).
State the 2-3 factors that most move the number.

## Formatting
- Output ONLY the finished `grading.md` in GitHub-flavoured Markdown. Do not restate these
  instructions or wrap the whole thing in a code fence.
- Start with a single H1 title: `# CV Grading — <Company>: <Role>`, then a short bullet block:
  `- CV: [cv.pdf](cv.pdf) / [cv.tex](cv.tex)`, `- Offer: [<relative path to the offer .md>](...)`,
  `- Graded: <YYYY-MM-DD>`. Use RELATIVE links, never absolute filesystem paths.
- If an overall score is provided to you, use THAT as the Overall score and decompose it; do
  not invent a different overall number.

## Required sections in grading.md
1. **Header** — the title + bullet block described under Formatting.
2. **Overall** — weighted score /100 + callback probability band + one-sentence verdict.
3. **Decoupled scores** — the table above, filled, each with justification.
4. **Missing keywords** — concrete terms in the offer absent from the CV (ATS risk). Mark which are fabricatable-NO (candidate lacks it) vs. addable-YES (candidate has it in `data/` but it was omitted).
5. **Unfulfilled / partially-met requirements** — hard vs. soft, with the gap.
6. **Strengths to lead with** — the candidate's strongest matches.
7. **Fix list** — concrete, ranked edits that would raise the score, separating "honest additions from data/" vs. "genuine gaps you can't close on paper."

## Constraints
- Never recommend fabricating experience. "Addable" only means it already exists in `data/`.
- Be blunt about hard gates; a polished CV does not beat an unmet mandatory requirement.
- Keep justifications one line; the document is a decision aid, not an essay.
