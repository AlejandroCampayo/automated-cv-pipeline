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

## Format & style (lato_luxembourg, the preferred template)
This layout landed an interview — reproduce it, don't redesign it.

- **Keep the template's preamble verbatim**: document class, packages, colours, margins,
  `parskip`, list spacing and `titlespacing`. Only the content between sections changes.
- **Preferred sections, in order**: Summary → Experience → Selected Projects → Education →
  Additional Information. You MAY add ONE extra section (e.g. Certifications, Publications)
  if the data clearly supports it and it helps the role — but **never a standalone "Skills"
  block**. Fold skills into the Summary, the bullets, and Additional Information.
- **Header**: accents exactly as in the data; show the FULL url as the link text
  (`linkedin.com/in/...`, `github.com/...`), not the word "LinkedIn". Citizenship/work
  authorization goes in Additional Information, not the header line.
- **Summary**: one dense ~3-line paragraph carrying the role's key tools/keywords.
- **Experience**: present duration as tenure ("2 years", add "(Current position)" if
  ongoing) using the data's `Tenure:` hint when present; otherwise the date range.
- **Selected Projects**: ~3, most-relevant-first, one bullet each. If a project has Demo/repo
  links in the data, render them right after the title — bold, underlined, slate (`emphasis`)
  colour — with the date `\hfill`-right; otherwise just the date on the right.
- **Additional Information**: Languages (with levels), Work authorization, and a one-line
  Collaboration statement — all from the data.

## Constraints
- No hallucinated employers, dates, or responsibilities.
- Use consistent tense and role-appropriate keywords.
- Keep to one page unless the template is designed for two pages.
- Escape LaTeX specials: `&`, `%`, `_`, `#`. Inside `\href{...}` URLs a literal `#` must be
  written `\#` (e.g. a `...#demo` anchor) or it will fail to compile.
