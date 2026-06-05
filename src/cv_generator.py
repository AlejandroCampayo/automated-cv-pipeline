"""Generate a tailored cv.tex from data/ + a job offer, then compile it to PDF.

Used by the optional "full pipeline" step for strong matches. Everything is
best-effort: if generation or compilation fails, the caller still sends the
digest — it just won't have a CV attached for that offer.
"""
import os
import glob
import shutil
import subprocess

from .llm import generate_text, strip_code_fences

DEFAULT_TEMPLATE = "templates/latex/single_column_article/cv_template.tex"


def _load_data(data_dir="data"):
    """Concatenate all data/*.md into one block the model can read."""
    parts = []
    for path in sorted(glob.glob(os.path.join(data_dir, "*.md"))):
        with open(path, "r", encoding="utf-8") as f:
            parts.append(f"### FILE: {os.path.basename(path)}\n{f.read()}")
    return "\n\n".join(parts)


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _build_prompt(job, data_block, template_tex, guide, prior_error=None):
    fix = ""
    if prior_error:
        fix = (
            "\nThe previous LaTeX did NOT compile. Fix it. Compiler error excerpt:\n"
            f"{prior_error[:1500]}\n"
        )
    return f"""You are a LaTeX CV writer. Produce a complete, COMPILABLE one-page LaTeX CV
tailored to the job offer below, using the provided template as the structure.

HARD RULES:
- Use ONLY facts present in CANDIDATE DATA. Never invent employers, dates, numbers, or skills.
- Prioritize the experiences/skills most relevant to this specific offer.
- Output ONLY the LaTeX source. No markdown, no ``` fences, no commentary.
- Keep it to a single page. Escape LaTeX special characters (%, &, _, #).

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


def compile_tex(tex, out_dir):
    """Write tex to out_dir/cv.tex and compile to cv.pdf.

    Returns (pdf_path or None, log_text).
    """
    os.makedirs(out_dir, exist_ok=True)
    tex_path = os.path.join(out_dir, "cv.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex)

    if not shutil.which("latexmk") and not shutil.which("pdflatex"):
        return None, "No LaTeX toolchain (latexmk/pdflatex) installed."

    cmd = (["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "cv.tex"]
           if shutil.which("latexmk")
           else ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "cv.tex"])
    try:
        proc = subprocess.run(cmd, cwd=out_dir, capture_output=True, text=True, timeout=120)
        log = proc.stdout + "\n" + proc.stderr
    except subprocess.TimeoutExpired:
        return None, "LaTeX compilation timed out."

    pdf_path = os.path.join(out_dir, "cv.pdf")
    if os.path.exists(pdf_path):
        return pdf_path, log
    return None, log


def generate_cv(job, out_dir, data_dir="data", template_path=DEFAULT_TEMPLATE,
                guide_path="prompts/agent_guide.md", max_attempts=2):
    """Generate and compile a tailored CV. Returns the PDF path or None."""
    data_block = _load_data(data_dir)
    template_tex = _read(template_path)
    guide = _read(guide_path) if os.path.exists(guide_path) else ""

    prior_error = None
    for attempt in range(1, max_attempts + 1):
        prompt = _build_prompt(job, data_block, template_tex, guide, prior_error)
        try:
            tex = strip_code_fences(generate_text(prompt, temperature=0.2))
        except Exception as e:
            print(f"      CV generation call failed: {e}")
            return None
        if "\\documentclass" not in tex or "\\end{document}" not in tex:
            prior_error = "Output was not a complete LaTeX document."
            continue
        pdf_path, log = compile_tex(tex, out_dir)
        if pdf_path:
            print(f"      ✓ CV compiled (attempt {attempt})")
            return pdf_path
        print(f"      ✗ compile failed (attempt {attempt}); retrying with error feedback")
        prior_error = log
    return None
