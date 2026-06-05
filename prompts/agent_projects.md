# Agent: Projects Extractor

Goal: Extract projects from CV template sources and update data/projects.md.

Inputs:
- Files in CV template/ (cv_*_content.tex and available_projects.tex)

Steps:
1) Collect project name, date, and description.
2) Merge overlapping projects under one canonical entry.
3) Keep tools and metrics only if explicitly stated.
4) Update data/projects.md with complete entries and dates.

Constraints:
- No invented dates or outcomes.
- Prefer the most detailed source text.
