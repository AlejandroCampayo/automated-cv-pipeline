"""Generate a tailored cv.tex from data/ + a job offer, then compile it to PDF.

Used by the optional "full pipeline" step for strong matches. Everything is
best-effort: if generation or compilation fails, the caller still sends the
digest — it just won't have a CV attached for that offer.

Templates live in templates/latex/<name>/ as a folder containing a
`cv_template.tex` plus any assets it needs (a `.cls`, images, fonts, sidebars).
Switch templates by pointing `template_path` at a different folder's
`cv_template.tex` (see config key "Template:" in job_preferences.md).

A template can declare its compile engine with a magic comment on the first lines:
    % engine: xelatex      (or: lualatex / pdflatex — default is pdflatex)
"""
import os
import re
import glob
import shutil
import subprocess

from .llm import generate_text, strip_code_fences

DEFAULT_TEMPLATE = "templates/latex/single_column_article/cv_template.tex"

# latexmk flag per engine, and a fallback chain when the preferred binary is absent.
_ENGINE_FLAG = {"pdflatex": "-pdf", "lualatex": "-lualatex", "xelatex": "-xelatex"}
_ENGINE_FALLBACK = {
    "xelatex": ["xelatex", "lualatex", "pdflatex"],
    "lualatex": ["lualatex", "xelatex", "pdflatex"],
    "pdflatex": ["pdflatex", "lualatex"],
}


def _load_data(data_dir="data"):
    """Concatenate all data/*.md into one block the model can read.

    Lines marked TODO/placeholder are dropped so they can't become filler bullets."""
    parts = []
    for path in sorted(glob.glob(os.path.join(data_dir, "*.md"))):
        with open(path, "r", encoding="utf-8") as f:
            clean = "\n".join(l for l in f.read().splitlines() if "TODO" not in l)
        parts.append(f"### FILE: {os.path.basename(path)}\n{clean}")
    return "\n\n".join(parts)


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _detect_engine(template_text):
    """Read a '% engine: xelatex' or '% !TEX program = xelatex' hint; default pdflatex."""
    head = "\n".join(template_text.splitlines()[:5]).lower()
    m = re.search(r"%\s*(?:engine|!tex\s+program)\s*[:=]\s*(pdflatex|xelatex|lualatex)", head)
    return m.group(1) if m else "pdflatex"


def _resolve_engine(requested):
    """Pick an installed engine, falling back if the preferred one is missing."""
    for eng in _ENGINE_FALLBACK.get(requested, ["pdflatex"]):
        if shutil.which(eng):
            return eng, _ENGINE_FLAG[eng]
    return None, None


def _copy_template_assets(template_path, out_dir):
    """Copy everything in the template folder (its .cls, images, sidebars, fonts)
    into out_dir EXCEPT the main template .tex (which becomes the generated cv.tex)."""
    template_dir = os.path.dirname(template_path)
    main = os.path.basename(template_path)
    for name in os.listdir(template_dir):
        if name in (main, "README.md"):
            continue
        src = os.path.join(template_dir, name)
        dst = os.path.join(out_dir, name)
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        except Exception as e:
            print(f"      ⚠️  could not copy template asset {name}: {e}")


def _error_excerpt(log, max_chars=1200):
    """Pull the meaningful LaTeX error (the '! ...' line + its 'l.NN' context) from the
    log. The error is near the END of the log, so naive truncation hides it."""
    lines = (log or "").splitlines()
    idx = next((i for i, l in enumerate(lines) if l.startswith("!")), None)
    if idx is None:
        return (log or "")[-max_chars:]  # fall back to the TAIL, not the head
    return "\n".join(lines[idx:idx + 14])[:max_chars]


def _page_count(pdf_path, log):
    """Best-effort page count: parse the LaTeX log, then fall back to pdfinfo."""
    m = re.search(r"Output written on \S+ \((\d+) pages?", log or "")
    if m:
        return int(m.group(1))
    if shutil.which("pdfinfo"):
        try:
            out = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True, timeout=15)
            mm = re.search(r"Pages:\s+(\d+)", out.stdout)
            if mm:
                return int(mm.group(1))
        except Exception:
            pass
    return None


def compile_tex(tex, out_dir, template_path=None, engine="pdflatex"):
    """Write tex to out_dir/cv.tex (with template assets) and compile to cv.pdf.

    Returns (pdf_path or None, log_text, page_count or None).
    """
    os.makedirs(out_dir, exist_ok=True)
    if template_path:
        _copy_template_assets(template_path, out_dir)

    with open(os.path.join(out_dir, "cv.tex"), "w", encoding="utf-8") as f:
        f.write(tex)

    if not shutil.which("latexmk"):
        return None, "No LaTeX toolchain (latexmk) installed.", None
    eng, flag = _resolve_engine(engine)
    if not eng:
        return None, f"No usable LaTeX engine for '{engine}'.", None

    cmd = ["latexmk", flag, "-interaction=nonstopmode", "-halt-on-error", "cv.tex"]
    try:
        proc = subprocess.run(cmd, cwd=out_dir, capture_output=True, text=True, timeout=180)
        log = proc.stdout + "\n" + proc.stderr
    except subprocess.TimeoutExpired:
        return None, "LaTeX compilation timed out.", None

    pdf_path = os.path.join(out_dir, "cv.pdf")
    if os.path.exists(pdf_path):
        return pdf_path, log, _page_count(pdf_path, log)
    return None, log, None


def _build_prompt(job, data_block, template_tex, guide, feedback=None):
    fix = f"\nFEEDBACK ON YOUR PREVIOUS ATTEMPT (address it):\n{feedback[:1500]}\n" if feedback else ""
    return f"""You are a LaTeX CV writer. Produce a complete, COMPILABLE one-page LaTeX CV
tailored to the job offer below, using the provided template as the structure.

HARD RULES:
- Use ONLY facts present in CANDIDATE DATA. Never invent employers, dates, numbers, or skills.
- CRITICAL — no keyword fabrication: every skill, tool, language, framework, or technology
  you put in the CV MUST appear in CANDIDATE DATA. NEVER copy a term from the JOB OFFER into
  the CV unless it is also in the data. If the offer wants something the candidate lacks
  (e.g. a language or tool not in the data), OMIT it — do not claim it.
- If an experience or project has no substantive detail in the data (only a placeholder),
  OMIT it entirely rather than writing a filler bullet.
- Prioritize the experiences/skills most relevant to this specific offer.
- Output ONLY the LaTeX source. No markdown, no ``` fences, no commentary.
- Keep it to a single page. Escape LaTeX special characters (%, &, _, #).
- Keep the template's document class and packages; only change the content.
- Use the template's OWN commands with EXACTLY the number of arguments shown in the
  template. Do not add or remove arguments (e.g. if the name command takes one argument
  with the full name, do not split it into two). Place the header/personal-info commands
  exactly where the template places them.

GUIDE:
{guide}

TEMPLATE (use as the structural starting point):
{template_tex}

CANDIDATE DATA:
{data_block}

JOB OFFER:
Title: {job.get('title')}
Company: {job.get('company')}
Location: {job.get('location')}
Description:
{job.get('description', '')[:2500]}
{fix}
Return the full LaTeX document now."""


def generate_cv(job, out_dir, data_dir="data", template_path=DEFAULT_TEMPLATE,
                guide_path="prompts/agent_guide.md", one_page=True, max_attempts=3):
    """Generate and compile a tailored CV. Returns the PDF path or None.

    If one_page is True, a CV that compiles to >1 page is regenerated with
    instructions to cut the least-relevant/repetitive content (NOT to shrink fonts).
    """
    data_block = _load_data(data_dir)
    template_tex = _read(template_path)
    guide = _read(guide_path) if os.path.exists(guide_path) else ""
    engine = _detect_engine(template_tex)

    feedback = None
    best_pdf = None
    for attempt in range(1, max_attempts + 1):
        prompt = _build_prompt(job, data_block, template_tex, guide, feedback)
        try:
            tex = strip_code_fences(generate_text(prompt, temperature=0.2))
        except Exception as e:
            print(f"      CV generation call failed: {e}")
            return best_pdf
        if "\\documentclass" not in tex or "\\end{document}" not in tex:
            feedback = "Output was not a complete LaTeX document."
            continue

        pdf_path, log, pages = compile_tex(tex, out_dir, template_path=template_path, engine=engine)
        if not pdf_path:
            first_err = next((l for l in (log or "").splitlines()
                              if l.startswith("!") or "not found" in l), "(no '!' line)")
            print(f"      ✗ compile failed (attempt {attempt}): {first_err.strip()[:140]}")
            feedback = ("The LaTeX did NOT compile. Fix it — pay attention to the line the "
                        "error points at (l.NN) and use each template command with EXACTLY "
                        "the arguments shown in the template. Compiler error:\n"
                        + _error_excerpt(log))
            continue

        best_pdf = pdf_path  # keep the latest compiling version
        if one_page and pages and pages > 1:
            print(f"      ⚠️  CV is {pages} pages (attempt {attempt}); trimming to one page")
            feedback = (
                f"The compiled CV is {pages} pages. It MUST be exactly ONE page. "
                f"Reduce length by cutting the least-relevant or repetitive content and "
                f"tightening bullet wording. Do NOT shrink the font below ~9pt or use "
                f"\\tiny/\\scriptsize/\\resizebox hacks — keep it readable."
            )
            continue

        print(f"      ✓ CV compiled (attempt {attempt}, {pages or '?'} page(s), {engine})")
        return pdf_path

    if best_pdf:
        print(f"      ⚠️  kept best compiling CV after {max_attempts} attempts (may exceed one page)")
    return best_pdf
