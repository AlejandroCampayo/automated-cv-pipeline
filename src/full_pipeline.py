"""Per-offer 'full pipeline' for strong matches.

For each strong match it produces, in outputs/job_offers/<slug>/:
  - cv.tex + cv.pdf       (tailored, compiled)
  - grading.md            (detailed scorecard)
  - how_to_apply.md       (apply strategy + cold-email draft)

All steps are best-effort and isolated: a failure in one offer never stops the
others, and the daily digest is sent regardless.
"""
import os
import re
import datetime

from .llm import generate_text, strip_code_fences
from .cv_generator import generate_cv

TEMPLATE_ROOT = "templates/latex"


def resolve_template(name_or_path):
    """Accept a template short name ('maltacv'), a folder, or a full .tex path.

    Returns the path to the template's cv_template.tex (falls back to the
    single-column default if it can't be found)."""
    default = os.path.join(TEMPLATE_ROOT, "single_column_article", "cv_template.tex")
    if not name_or_path:
        return default
    if name_or_path.endswith(".tex") and os.path.exists(name_or_path):
        return name_or_path
    candidate = os.path.join(TEMPLATE_ROOT, name_or_path, "cv_template.tex")
    if os.path.exists(candidate):
        return candidate
    if os.path.isdir(name_or_path) and os.path.exists(os.path.join(name_or_path, "cv_template.tex")):
        return os.path.join(name_or_path, "cv_template.tex")
    print(f"    ⚠️  template '{name_or_path}' not found; using single_column_article")
    return default


def slugify(job, date=None):
    date = date or datetime.date.today().isoformat()
    raw = f"{job.get('company', 'company')}_{job.get('title', 'role')}"
    slug = re.sub(r"[^a-z0-9]+", "_", raw.lower()).strip("_")[:60]
    return f"{date}_{slug}"


def _read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def _gen_doc(prompt_path, job, extra=""):
    """Generate a markdown doc by FOLLOWING a prompt guide (not echoing it)."""
    guide = _read(prompt_path)
    today = datetime.date.today().isoformat()
    prompt = f"""You are completing the task described in the INSTRUCTIONS below.

Output rules:
- Produce ONLY the final deliverable document — do NOT restate the instructions,
  their title, or their meta-scaffolding. Do not start with "# Agent Guide...".
- No ``` code fences around the whole output. Use plain GitHub-flavored Markdown.
- Use ONLY facts from the candidate data and the job offer. Never invent employers,
  names, numbers, or dates.
- You have NO web access. Do NOT invent recruiter/contact names, emails, or titles.
  Where the instructions ask for a contact, say to find the hiring manager on
  LinkedIn / the company site instead of fabricating a person.
- Today's date is {today}. Use it wherever the document needs a date.

INSTRUCTIONS:
{guide}

JOB OFFER:
Title: {job.get('title')}
Company: {job.get('company')}
Location: {job.get('location')}
Description:
{job.get('description', '')[:2500]}

{extra}

Write the final document now."""
    return strip_code_fences(generate_text(prompt, temperature=0.3))


def run_for_job(job, grading, data_dir="data", out_root="outputs/job_offers",
                template_path="templates/latex/single_column_article/cv_template.tex",
                one_page=True):
    """Run the full pipeline for one strong match. Returns a dict of artifacts."""
    out_dir = os.path.join(out_root, slugify(job))
    os.makedirs(out_dir, exist_ok=True)
    artifacts = {"dir": out_dir, "pdf": None}

    # Cache the offer text alongside the outputs for traceability.
    with open(os.path.join(out_dir, "offer.md"), "w", encoding="utf-8") as f:
        f.write(f"# {job.get('title')} @ {job.get('company')}\n\n"
                f"{job.get('url','')}\n\n{job.get('description','')}\n")

    data_block = ""  # generators load data themselves; passed for prompt context
    for name in ("profile.md", "experience.md", "projects.md", "skills.md"):
        data_block += _read(os.path.join(data_dir, name)) + "\n"

    # 1. Tailored CV (LaTeX -> PDF)
    try:
        pdf = generate_cv(job, out_dir, data_dir=data_dir,
                          template_path=template_path, one_page=one_page)
        artifacts["pdf"] = pdf
    except Exception as e:
        print(f"    CV step failed: {e}")

    # 2. Detailed grading.md
    try:
        score = grading.get("overall_score", "?")
        doc = _gen_doc("prompts/agent_grading.md", job,
                       extra=f"Digest score so far: {score}/100.\nCANDIDATE DATA:\n{data_block}")
        with open(os.path.join(out_dir, "grading.md"), "w", encoding="utf-8") as f:
            f.write(doc)
    except Exception as e:
        print(f"    grading.md step failed: {e}")

    # 3. how_to_apply.md — with REAL contacts (posting + SerpAPI), never fabricated.
    try:
        from .contact_finder import find_contacts, format_contacts
        contacts_block = format_contacts(find_contacts(job))
        extra = (f"CANDIDATE DATA:\n{data_block}\n\n"
                 f"VERIFIED CONTACTS (use ONLY these for the outreach section; if NONE "
                 f"FOUND, advise searching LinkedIn — do not invent anyone):\n{contacts_block}")
        doc = _gen_doc("prompts/agent_application_strategy.md", job, extra=extra)
        with open(os.path.join(out_dir, "how_to_apply.md"), "w", encoding="utf-8") as f:
            f.write(doc)
        artifacts["how_to_apply"] = os.path.join(out_dir, "how_to_apply.md")
    except Exception as e:
        print(f"    how_to_apply.md step failed: {e}")

    # Collect the deliverables to attach to the email (skip LaTeX build junk).
    deliverables = ["cv.pdf", "cv.tex", "grading.md", "how_to_apply.md", "offer.md"]
    artifacts["files"] = [os.path.join(out_dir, f) for f in deliverables
                          if os.path.exists(os.path.join(out_dir, f))]
    return artifacts


def run_for_strong_matches(strong_jobs_with_grades, **kwargs):
    """strong_jobs_with_grades: list of (job, grading). Returns list of artifacts."""
    results = []
    for i, (job, grading) in enumerate(strong_jobs_with_grades, 1):
        print(f"  [{i}/{len(strong_jobs_with_grades)}] {job.get('title')} @ {job.get('company')}")
        try:
            results.append(run_for_job(job, grading, **kwargs))
        except Exception as e:
            print(f"    Full pipeline failed for this offer: {e}")
    return results
