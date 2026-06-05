# Agent: Education Extractor

Goal: Extract education entries from CV template sources and update data/education.md.

Inputs:
- Files in CV template/ (page1sidebar*.tex, page2sidebar.tex, and cv_*.tex)

Steps:
1) Scan for Education sections and extract degree, institution, dates, and location.
2) Merge duplicates; keep the most complete wording.
3) Add thesis/title notes only if explicitly stated.
4) Update data/education.md with clean, canonical entries.

Constraints:
- Do not invent dates or institutions.
- Prefer ASCII names unless the source explicitly uses non-ASCII and consistency is required.
