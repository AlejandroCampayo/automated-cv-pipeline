"""Gemini-based job offer grading module — batched to minimise API calls."""
import os
import json
import google.generativeai as genai


def init_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in .env.local")
    genai.configure(api_key=api_key)


def grade_all_jobs(job_postings, user_profile):
    """
    Grade all job postings in a SINGLE Gemini API call.

    Args:
        job_postings: List of job dicts
        user_profile: Dict with years_experience, skills, location_pref, salary_min

    Returns:
        List of grading dicts (same order as input)
    """
    init_gemini()

    # Build compact job list for the prompt
    jobs_text = ""
    for i, job in enumerate(job_postings):
        desc = job.get("description", "")
        if isinstance(desc, list):
            desc = " | ".join(desc)
        jobs_text += f"\nJOB {i+1}: {job.get('title')} @ {job.get('company')} ({job.get('location', 'Luxembourg')})\nDescription: {desc[:300]}\n"

    prompt = f"""You are an expert career coach grading Luxembourg job offers. Job titles may be in French, English, or German — treat them correctly (e.g. "Responsable IA" = AI Manager, "Développeur" = Developer, "Ingénieur" = Engineer).

CANDIDATE PROFILE:
- Experience: {user_profile.get('years_experience', '2-5')} years
- Skills: {', '.join(user_profile.get('skills', []))}
- Location: {user_profile.get('location_pref', 'Luxembourg')}
- Min salary: €{user_profile.get('salary_min', 60000)}/year
- Education: {user_profile.get('education', 'CS/Data Science degree')}

JOBS TO GRADE:
{jobs_text}

Respond ONLY with a valid JSON array with one object per job, in the same order:
[
  {{
    "job_index": 1,
    "overall_score": <0-100>,
    "match_type": "<strong|good|consider|skip>",
    "top_strengths": ["<strength1>"],
    "gaps": ["<gap1>"],
    "recommendation": "<1 sentence>"
  }},
  ...
]

match_type rules: strong=80+, good=60-79, consider=40-59, skip=<40
"""

    try:
        from .llm import call_model
        response = call_model(prompt, temperature=0.3)  # shared model + rate-limit backoff

        response_text = response.text.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        results = json.loads(response_text)

        if len(results) != len(job_postings):
            print(f"  Warning: got {len(results)} grades for {len(job_postings)} jobs")

        return results

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return [{"job_index": i+1, "overall_score": 0, "match_type": "skip", "recommendation": "Grading error"} for i in range(len(job_postings))]
    except Exception as e:
        print(f"Gemini API error: {e}")
        return [{"job_index": i+1, "overall_score": 0, "match_type": "skip", "recommendation": f"API error: {e}"} for i in range(len(job_postings))]


def format_grading_for_email(job, grading):
    """Format a graded job for email display."""
    score = grading.get("overall_score", 0)
    match = grading.get("match_type", "skip")
    emoji = {"strong": "🔥", "good": "✅", "consider": "⚠️", "skip": "❌"}.get(match, "❓")

    return (
        f"{emoji} <b>{job['title']}</b> @ {job['company']}<br>"
        f"Score: {score}/100 | {match.upper()}<br>"
        f"{grading.get('recommendation', '')}<br>"
        f"<a href='{job.get('url', '#')}'>View job →</a><br>"
        f"Posted: {job.get('posted_date', '')}"
    )
