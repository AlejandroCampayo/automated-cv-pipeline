"""Thin wrapper around the free Gemini model, shared by generators."""
import os
import re
import time
import google.generativeai as genai

# Free-tier model. Override with GEMINI_MODEL if your key has different quota.
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Free tiers are rate-limited (e.g. gemini-2.5-flash = ~5 req/min). Back off and retry.
MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "5"))


def _ensure_configured():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY")
    genai.configure(api_key=api_key)


def _is_rate_limit(err):
    s = str(err).lower()
    return "429" in s or "resource_exhausted" in s or "quota" in s or "rate limit" in s


def _retry_seconds(err, default):
    """Honor the 'Please retry in Xs' hint the API returns, else use default."""
    m = re.search(r"retry in ([\d.]+)s", str(err))
    return float(m.group(1)) + 1 if m else default


def call_model(prompt, temperature=0.3):
    """Call Gemini with retry/backoff on free-tier rate limits. Returns the response."""
    _ensure_configured()
    model = genai.GenerativeModel(MODEL)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return model.generate_content(
                prompt, generation_config={"temperature": temperature}
            )
        except Exception as e:
            if _is_rate_limit(e) and attempt < MAX_RETRIES:
                wait = _retry_seconds(e, default=min(20 * attempt, 60))
                print(f"      ⏳ rate-limited; waiting {wait:.0f}s (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(wait)
                continue
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
