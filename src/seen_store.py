"""Track which job offers we've already processed, so a run can show only NEW ones.

Each offer gets a stable id (a hash of its normalized URL, or of title+company when
there is no URL). The state is a small JSON file mapping id -> first-seen date, so old
entries can be pruned (boards don't keep postings forever; after the TTL a re-listed job
may resurface once, which is fine).

This is OPT-IN: the pipeline only consults/updates it when run with --track-seen
(the scheduled production run). Every other run behaves exactly as before.
"""
import os
import json
import hashlib
import datetime
from urllib.parse import urlsplit, urlunsplit

STATE_FILE = os.getenv("SEEN_STORE", "state/seen_jobs.json")
TTL_DAYS = int(os.getenv("SEEN_TTL_DAYS", "60"))


def job_id(job):
    """Stable short id identifying the exact offer."""
    url = (job.get("url") or "").strip()
    if url:
        p = urlsplit(url)
        # Drop query/fragment (tracking params) and trailing slash so the same posting
        # maps to one id across runs/sources.
        key = urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), "", ""))
    else:
        key = f"{job.get('title','').strip().lower()}|{job.get('company','').strip().lower()}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def load_seen(path=STATE_FILE):
    """Return {id: 'YYYY-MM-DD'} of previously seen offers (empty if none/unreadable)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return dict(data.get("seen", {}))
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return {}


def _prune(seen, today):
    cutoff = today - datetime.timedelta(days=TTL_DAYS)
    kept = {}
    for jid, ds in seen.items():
        try:
            if datetime.date.fromisoformat(ds) >= cutoff:
                kept[jid] = ds
        except (ValueError, TypeError):
            pass  # drop malformed dates
    return kept


def save_seen(seen, path=STATE_FILE):
    """Prune expired entries and write the state file."""
    today = datetime.date.today()
    seen = _prune(seen, today)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"seen": dict(sorted(seen.items()))}, f, indent=1)
    return seen


def filter_new(jobs, seen):
    """Return the subset of jobs whose id is NOT already in seen."""
    seen_ids = set(seen)
    return [j for j in jobs if job_id(j) not in seen_ids]


def mark_seen(seen, jobs):
    """Stamp today's date on every given job's id (refreshes still-listed offers)."""
    today = datetime.date.today().isoformat()
    for j in jobs:
        seen[job_id(j)] = today
    return seen
