# Agent: Experience Extractor

Goal: Extract experience entries from CV template sources and update data/experience.md.

Inputs:
- Files in CV template/ (cv_*_content.tex and cv_*.tex)

Steps:
1) Find Experience sections; collect role, company, dates, location, and bullets.
2) De-duplicate bullets; keep the strongest impact-focused versions.
3) Preserve factual claims and tool references only if present in sources.
4) Update data/experience.md with a consolidated long-form version.

Constraints:
- No new employers or responsibilities not present in sources.
- Keep dates consistent across entries.
