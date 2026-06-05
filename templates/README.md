# Templates

Reusable, content-free CV templates and their assets.

Templates:
- `templates/latex/altacv_two_column` — two-column AltaCV style (good for fairs / visual CVs).
- `templates/latex/single_column_article` — clean single-column style (good for ATS / formal applications).

How to use:
1. Let your LLM assistant pick a template per offer (see `prompts/agent_guide.md`), or copy one manually into `outputs/<job>/`.
2. Rename `cv_template.tex` to `cv.tex`.
3. Fill in content from `data/` and build with `latexmk -pdf cv.tex`.

Notes:
- Keep templates minimal and free of job-specific content.
- See `examples/output_northwind_ml_engineer/cv.tex` for a filled single-column example.
