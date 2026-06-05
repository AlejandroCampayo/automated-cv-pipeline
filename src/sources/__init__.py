"""Pluggable job sources.

Each source is a function that returns a list of normalized job dicts:

    {
        "title": str,
        "company": str,
        "location": str,
        "url": str,
        "posted_date": str,
        "description": str,
        "salary": str | None,
        "source": str,
    }

A source is "available" if its required credentials are present. Sources that
fail (network, parsing, rate limit) are skipped without breaking the run — the
pipeline keeps whatever the other sources returned.
"""
import os

from .moovijob import fetch as _moovijob
from .arbeitnow import fetch as _arbeitnow
from .remotive import fetch as _remotive
from .google_jobs import fetch as _google_jobs

# (name, fetch_fn, is_available_fn)
_REGISTRY = [
    ("Moovijob", _moovijob, lambda: True),
    ("Arbeitnow", _arbeitnow, lambda: True),
    ("Remotive", _remotive, lambda: True),
    ("GoogleJobs", _google_jobs, lambda: bool(os.getenv("SERPAPI_KEY"))),
]

# Keywords used to keep only relevant postings from the broad API sources.
RELEVANT_KEYWORDS = [
    "machine learning", "ml engineer", " ai ", "artificial intelligence",
    "data scientist", "data science", "deep learning", "computer vision",
    "nlp", "llm", "neural", "pytorch", "tensorflow", "data engineer",
    "perception", "algorithm", "research engineer", "mlops",
]


def is_relevant(job):
    """True if the title (or, as a fallback, description) looks AI/ML/data related."""
    hay = (job.get("title", "") + " " + job.get("description", "")[:200]).lower()
    return any(kw in hay for kw in RELEVANT_KEYWORDS)


def _dedup_key(job):
    return (
        job.get("title", "").strip().lower(),
        job.get("company", "").strip().lower(),
    )


def fetch_all(roles=None, locations=None, relevant_only=True):
    """Run every available source, merge, and de-duplicate.

    Args:
        roles: list of role keywords (used by keyword-driven sources like Google Jobs)
        locations: list of locations (e.g. ["Luxembourg", "Remote"])
        relevant_only: drop postings that don't match RELEVANT_KEYWORDS

    Returns:
        Merged, de-duplicated list of normalized job dicts.
    """
    roles = roles or ["machine learning engineer", "data scientist", "ai engineer"]
    locations = locations or ["Luxembourg"]

    all_jobs = []
    seen = set()

    for name, fetch_fn, available in _REGISTRY:
        if not available():
            print(f"  · {name}: skipped (no credentials)")
            continue
        try:
            print(f"  · {name}: fetching...")
            jobs = fetch_fn(roles=roles, locations=locations) or []
            kept = 0
            for job in jobs:
                if relevant_only and not is_relevant(job):
                    continue
                key = _dedup_key(job)
                url = job.get("url", "")
                if key in seen or (url and url in seen):
                    continue
                seen.add(key)
                if url:
                    seen.add(url)
                all_jobs.append(job)
                kept += 1
            print(f"    → {kept} relevant ({len(jobs)} raw)")
        except Exception as e:
            print(f"    ! {name} failed: {e}")

    print(f"  Total after merge+dedup: {len(all_jobs)} jobs")
    return all_jobs
