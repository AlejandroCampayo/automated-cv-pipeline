"""Thin wrapper around the free Gemini model, shared by generators."""
import os
import re
import time
import google.generativeai as genai

# Free-tier model. flash-lite has a far larger free DAILY quota than flash
# (flash is ~20 requests/day, unusable here). Override with GEMINI_MODEL if your key differs.
MODEL = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash-lite"  # empty env -> default

# Per-MINUTE limits are worth waiting out; per-DAY limits are not (they reset hours later).
MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "5"))


def _ensure_configured():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY")
    genai.configure(api_key=api_key)


def _is_rate_limit(err):
    s = str(err).lower()
    return "429" in s or "resource_exhausted" in s or "quota" in s or "rate limit" in s


def _is_daily_quota(err):
    """A per-DAY free-tier cap — no point backing off, it resets at midnight Pacific."""
    s = str(err).lower()
    return "perday" in s or "per day" in s or "requestsperday" in s


def _is_transient(err):
    """Temporary network/server hiccup (503, DNS, timeout) — worth a quick retry."""
    s = str(err).lower()
    return any(k in s for k in ("503", "500", "unavailable", "deadline",
                                "timeout", "lookup error", "dns"))


def _retry_seconds(err, default):
    """Honor the 'Please retry in Xs' hint the API returns, else use default."""
    m = re.search(r"retry in ([\d.]+)s", str(err))
    return float(m.group(1)) + 1 if m else default


class DailyQuotaExhausted(RuntimeError):
    """Raised when the per-day free-tier quota is gone, so callers can stop early."""


def call_model(prompt, temperature=0.3):
    """Call Gemini with retry/backoff. A 429 always gets a bounded backoff first —
    Gemini's error often lists BOTH the per-minute and per-day quotas, so we can't
    treat "PerDay appears in the text" as proof the daily cap is the real blocker.
    We only declare daily-exhaustion after a couple of waits fail to clear it."""
    _ensure_configured()
    model = genai.GenerativeModel(MODEL)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return model.generate_content(
                prompt, generation_config={"temperature": temperature}
            )
        except Exception as e:
            rate, daily, transient = _is_rate_limit(e), _is_daily_quota(e), _is_transient(e)
            # Daily-cited errors get fewer retries (likely really exhausted), but still
            # at least one wait — in case it's actually a mislabeled per-minute burst.
            allowed = 2 if daily else MAX_RETRIES
            if (rate or transient) and attempt < allowed:
                wait = (min(_retry_seconds(e, default=20 * attempt), 60) if rate
                        else min(3 * attempt, 15))
                label = "quota (daily?)" if daily else ("rate-limited" if rate else "transient")
                print(f"      ⏳ {label}; waiting {wait:.0f}s (attempt {attempt}/{allowed})")
                time.sleep(wait)
                continue
            if daily:
                raise DailyQuotaExhausted(
                    f"Free-tier quota for '{MODEL}' still exhausted after retries "
                    f"(per-day cap resets ~midnight Pacific). Try another GEMINI_MODEL or wait."
                ) from e
            raise


def generate_text(prompt, temperature=0.3):
    """Return the model's text response for a prompt (with rate-limit retries)."""
    resp = call_model(prompt, temperature=temperature)
    return (resp.text or "").strip()


def strip_code_fences(text, lang_hints=("latex", "tex", "markdown", "md", "")):
    """Remove a leading/trailing ``` fence the model may have wrapped output in."""
    t = text.strip()
    if t.startswith("```"):
        first_nl = t.find("\n")
        if first_nl != -1:
            t = t[first_nl + 1:]
        if t.rstrip().endswith("```"):
            t = t.rstrip()[:-3]
    return t.strip()
