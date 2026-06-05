# Agent: Skills Extractor

Goal: Extract skills, tools, and languages from CV template sources and update data/skills.md.

Inputs:
- Files in CV template/ (page1sidebar*.tex, page2sidebar.tex, cv_*_content.tex)

Steps:
1) Extract technical skills, tools, and language proficiency.
2) Consolidate into Core, Tools, and Languages sections.
3) Remove duplicates and inconsistent naming.
4) Update data/skills.md.

Constraints:
- Use only items present in the sources.
- Keep language levels as shown.
