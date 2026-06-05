"""Find REAL hiring contacts for a job — never fabricates.

Two free sources:
  1. The job posting text itself (emails, "contact:" lines).
  2. A SerpAPI Google search for the company's recruiters on LinkedIn
     (uses your existing SERPAPI_KEY; ~100 searches/month free).

Only called for strong matches, so SerpAPI usage stays low. Returns whatever it
actually finds; the caller passes these to the how_to_apply generator as the ONLY
contacts the model is allowed to use.
"""
import os
import re
import requests

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SERPAPI_URL = "https://serpapi.com/search.json"
TIMEOUT = 25

# Emails that are almost never a real human contact.
_NOISE_EMAIL = ("noreply", "no-reply", "donotreply", "example.com", "sentry", "wordpress")


def from_posting(job):
    """Extract any contact emails the posting already lists."""
    text = f"{job.get('description', '')} {job.get('url', '')}"
    found = []
    for email in sorted(set(EMAIL_RE.findall(text))):
        if any(n in email.lower() for n in _NOISE_EMAIL):
            continue
        found.append({"type": "email", "value": email, "source": "posting"})
    return found


def _name_from_title(title):
    # LinkedIn result titles look like "Jane Smith - Talent Acquisition - Acme | LinkedIn"
    first = re.split(r"\s[-–|]\s", title)[0].strip()
    return first or None


def from_serpapi(job, max_results=3):
    """Search Google for the company's recruiters/HR on LinkedIn. Real names + URLs."""
    key = os.getenv("SERPAPI_KEY")
    company = (job.get("company") or "").strip()
    if not key or not company:
        return []

    q = (f'"{company}" (recruiter OR "talent acquisition" OR "people team" OR HR) '
         f'site:linkedin.com/in')
    try:
        r = requests.get(SERPAPI_URL,
                         params={"engine": "google", "q": q, "num": 10, "api_key": key},
                         timeout=TIMEOUT)
        r.raise_for_status()
        results = r.json().get("organic_results", [])
    except Exception as e:
        print(f"      contact search failed: {e}")
        return []

    out = []
    for res in results:
        link = res.get("link", "")
        if "linkedin.com/in" not in link:
            continue
        title = res.get("title", "")
        out.append({
            "type": "linkedin",
            "name": _name_from_title(title),
            "headline": title.replace(" | LinkedIn", "").strip(),
            "url": link,
            "source": "serpapi",
        })
        if len(out) >= max_results:
            break
    return out


def find_contacts(job):
    """Return a list of real contacts found in the posting + via SerpAPI."""
    return from_posting(job) + from_serpapi(job)


def format_contacts(contacts):
    """Render contacts as a fact block for the how_to_apply prompt."""
    if not contacts:
        return ("NONE FOUND. Do not invent a contact — advise searching LinkedIn for "
                "the company's recruiter or the hiring manager for this role.")
    lines = []
    for c in contacts:
        if c["type"] == "email":
            lines.append(f"- Email listed in the posting: {c['value']}")
        else:
            who = c.get("name") or "LinkedIn profile"
            lines.append(f"- {who} — {c.get('headline', '')} — {c['url']}")
    return "\n".join(lines)
