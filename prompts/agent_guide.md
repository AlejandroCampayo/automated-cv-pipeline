# Agent Guide (CV Builder)

Goal: Build a tailored CV for a specific job offer and chosen template using data/*.md as the source of truth.

## Inputs
- Job offer file in job_offers/
- Chosen template in templates/
- Source data in data/

## Steps
1) Read the job offer and extract the top 5-7 responsibilities and requirements.
2) Select the most relevant experiences and projects from data/.
3) Tailor the profile summary to match the role, keep it factual.
4) Prioritize outcomes and impact; keep bullets short and evidence-based.
5) Use only details present in data/ unless the user explicitly adds new facts.

## Output
- Create a new folder in outputs/YYYY-MM-DD_company_role/.
- Produce a LaTeX file (cv.tex) and compile to PDF if requested.
- Keep a short build note if a template requires special steps.

## Pipeline (per job offer)
After the CV is built, each output folder should contain:
1. `cv.tex` + `cv.pdf` — the tailored CV (this guide).
2. `grading.md` — CV-vs-offer scorecard. See prompts/agent_grading.md.
3. `how_to_apply.md` — apply-vs-coldmail strategy + recruiter/email research + cold-email draft. See prompts/agent_application_strategy.md.
4. `README.md` — template source + build notes.

## Constraints
- No hallucinated employers, dates, or responsibilities.
- Use consistent tense and role-appropriate keywords.
- Keep to one page unless the template is designed for two pages.
