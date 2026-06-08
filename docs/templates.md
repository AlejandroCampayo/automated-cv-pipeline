# CV templates — switching and adding

The CV generator fills a LaTeX **template** with your tailored content and compiles it
to PDF. Templates live in [`templates/latex/<name>/`](../templates/latex/), each a folder
containing a `cv_template.tex` plus any assets it needs (a `.cls`, images, fonts, sidebars).

## Switch template

One line in `config/job_preferences.md`:

```
## CV Options
- Template: single_column_article
- One page: yes
```

`Template:` is the folder name under `templates/latex/`. `One page: yes` forces the CV
onto a single page by **cutting the least-relevant/repetitive content** (not by shrinking
the font). Override per run on the CLI:

```bash
python scripts/daily_job_pipeline.py --full-pipeline --template altacv_two_column --one-page
```

## Add a new template (e.g. mAltaCV)

1. **Get the files.** Open the template on Overleaf → *Menu → Download → Source* (a `.zip`).
   For [mAltaCV](https://www.overleaf.com/latex/templates/maltacv/fkxzrrhfddgy) that's the
   `.cls` (e.g. `altacv.cls`), the main `.tex`, and any image/font assets.
2. **Drop them in a new folder** `templates/latex/maltacv/`, and rename the main `.tex`
   to `cv_template.tex`. Keep the `.cls`, images, and fonts alongside it.
3. **Declare the compile engine** if it isn't plain pdfLaTeX. AltaCV/mAltaCV variants that
   use `fontspec`/custom fonts need XeLaTeX or LuaLaTeX — add a magic comment on the first
   line of `cv_template.tex`:

   ```latex
   % engine: xelatex
   ```

   (Options: `pdflatex` (default), `xelatex`, `lualatex`. The generator auto-falls back to
   an installed engine if the preferred one is missing.)
4. **Point the config at it:** `Template: maltacv`.

That's it — the generator copies the whole folder's assets next to the generated `cv.tex`
before compiling, so the `.cls` and images are found.

### Good to know
- The generator keeps the template's `\documentclass` and packages and only changes the
  content, so the visual style is preserved.
- CI installs `texlive-xetex` and `texlive-luatex`, so xelatex/lualatex templates build on
  GitHub Actions too. Custom/non-TeXLive fonts won't be present on the runner — prefer
  fonts shipped in `texlive-fonts-extra` (Lato, Fira, etc.) or commit the font files.
- If a template fails to compile, the generator feeds the LaTeX error back to the model and
  retries; if it still fails, the digest email is sent without that CV (best-effort).
- The bundled `single_column_article` is the most tested template and uses plain pdfLaTeX
  (no extra packages) — start here.
- `altacv_two_column` is heavier: it pulls in `biblatex` (needs `biber`) and looks best with
  its icon fonts. CI installs those, but if you hit trouble, prefer `single_column_article`
  or a self-contained template.
