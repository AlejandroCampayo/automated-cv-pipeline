#!/usr/bin/env python3
"""
Daily job search, grading, and CV generation pipeline.
Runs daily at 8 AM to:
1. Search all available sources (Moovijob, Arbeitnow, Remotive, Google Jobs)
2. Grade them in a single Gemini API call
3. For strong matches (with --full-pipeline): auto-generate tailored CV + grading + how-to-apply
4. Send email with matches (tailored CV PDFs attached)
"""

import sys
import os
import argparse
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.job_search import batch_search_jobs
from src.job_grader import grade_all_jobs, format_grading_for_email
from src.email_sender import send_daily_digest
from src.config_loader import load_job_preferences, get_user_profile
from dotenv import load_dotenv

load_dotenv('.env.local')


def main(dry_run=False, test_limit=None, full_pipeline=False, strong_threshold=None,
         template=None, one_page=None, track_seen=False):
    print(f"\n{'='*60}")
    print(f"🚀 Daily Job Pipeline - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"DRY RUN: {dry_run}")
    print(f"{'='*60}\n")

    # Load configuration
    try:
        config = load_job_preferences()
        user_profile = get_user_profile(config)
        email_recipient = config.get('email_recipient') or os.getenv('GMAIL_ADDRESS')
        if not email_recipient:
            print("❌ No email recipient. Set 'Primary' in config/job_preferences.md or GMAIL_ADDRESS in .env.local")
            return False
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False

    print(f"📋 Config: {', '.join(config['locations'])} | Min salary: €{config['salary_min']:,}\n")

    # Search all available sources
    print("🔍 Searching job sources...")
    jobs = batch_search_jobs(
        roles=config.get('roles'),
        locations=config.get('locations'),
        limit=test_limit,
        test_mode=dry_run,
    )

    if not jobs:
        print("❌ No jobs found")
        return False

    print(f"✅ Found {len(jobs)} jobs\n")

    # Opt-in: only process offers we haven't seen before (scheduled production run).
    # Done before grading so already-seen jobs don't even cost Gemini tokens.
    all_fetched = list(jobs)
    seen = {}
    if track_seen:
        from src.seen_store import load_seen, filter_new, mark_seen, save_seen
        seen = load_seen()
        jobs = filter_new(jobs, seen)
        print(f"🆕 {len(jobs)} new of {len(all_fetched)} jobs (already-seen filtered)\n")
        if not jobs:
            print("No new jobs since last run — nothing to grade/email.")
            save_seen(mark_seen(seen, all_fetched))
            return True

    # Grade all jobs in a single API call
    print(f"📊 Grading {len(jobs)} jobs (single API call)...")
    try:
        gradings = grade_all_jobs(jobs, user_profile)
    except Exception as e:
        print(f"❌ Grading failed: {e}")
        return False

    # Organise results
    matches_by_type = {'strong': [], 'good': [], 'consider': [], 'skip': []}
    grading_results = []

    for job, grading in zip(jobs, gradings):
        score = grading.get('overall_score', 0)
        # Optional one-off override: treat anything at/above this score as a strong match.
        if strong_threshold is not None and score >= strong_threshold:
            grading['match_type'] = 'strong'
        match_type = grading.get('match_type', 'skip')
        formatted = format_grading_for_email(job, grading)
        matches_by_type[match_type].append(formatted)
        grading_results.append({'job': job, 'grading': grading})
        print(f"  {score:3}/100 [{match_type:8}] {job['title']} @ {job['company']}")

    print()
    print("📈 Summary:")
    for t in ['strong', 'good', 'consider', 'skip']:
        print(f"  {t.upper():8}: {len(matches_by_type[t])}")

    # Save results
    if not dry_run:
        results_file = f"outputs/job_search_results_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json"
        os.makedirs('outputs', exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(grading_results, f, indent=2, default=str)
        print(f"\n  Saved: {results_file}")

    # Phase 2: full pipeline (tailored CV + grading + how-to-apply) for strong matches.
    # Best-effort — never let a generation failure block the digest email.
    cv_attachments = []
    if full_pipeline:
        strong_pairs = [(r['job'], r['grading']) for r in grading_results
                        if r['grading'].get('match_type') == 'strong']
        if strong_pairs:
            print(f"\n🛠️  Full pipeline for {len(strong_pairs)} strong match(es)...")
            try:
                from src.full_pipeline import run_for_strong_matches, resolve_template
                # CLI overrides config; config provides the defaults.
                tmpl = resolve_template(template if template is not None else config.get('template'))
                use_one_page = one_page if one_page is not None else config.get('one_page', True)
                print(f"  Template: {tmpl} | one-page: {use_one_page}")
                artifacts = run_for_strong_matches(
                    strong_pairs, template_path=tmpl, one_page=use_one_page)
                # Attach the full deliverable set per match: cv.pdf, cv.tex, grading.md,
                # how_to_apply.md, offer.md.
                for a in artifacts:
                    cv_attachments.extend(a.get('files', []))
                n_cv = sum(1 for a in artifacts if a.get('pdf'))
                print(f"  ✅ Generated {n_cv} CV(s); attaching {len(cv_attachments)} file(s)")
            except Exception as e:
                print(f"  ⚠️  Full pipeline error (digest still sends): {e}")
        else:
            print("\n🛠️  Full pipeline: no strong matches to build.")

    # Send email
    print("\n📧 Sending email...")
    if send_daily_digest(email_recipient, matches_by_type, dry_run=dry_run,
                         attachments=cv_attachments):
        print("✅ Email sent")
    else:
        print("❌ Email failed")

    # Record everything we fetched this run so the next run only shows new offers.
    if track_seen:
        from src.seen_store import mark_seen, save_seen
        seen = save_seen(mark_seen(seen, all_fetched))
        print(f"💾 seen-jobs state updated ({len(seen)} ids)")

    print(f"\n{'='*60}")
    print(f"✅ Pipeline complete")
    print(f"{'='*60}\n")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily job search and CV pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Use test jobs, don't send email")
    parser.add_argument("--limit", type=int, default=None, help="Max jobs to scrape")
    parser.add_argument("--full-pipeline", action="store_true",
                        help="Auto-generate tailored CV + grading + how-to-apply for strong matches")
    parser.add_argument("--strong-threshold", type=int, default=None,
                        help="One-off: treat any match scoring >= this (0-100) as 'strong'. "
                             "Useful to force the full pipeline to fire during testing.")
    parser.add_argument("--template", default=None,
                        help="CV template name (folder under templates/latex/) or path. "
                             "Overrides the 'Template:' config value.")
    parser.add_argument("--one-page", dest="one_page", action="store_true", default=None,
                        help="Force the CV to fit one page (trims content, keeps font readable).")
    parser.add_argument("--no-one-page", dest="one_page", action="store_false",
                        help="Allow the CV to spill onto multiple pages.")
    parser.add_argument("--track-seen", action="store_true",
                        help="Only process offers not seen in a previous --track-seen run "
                             "(persists state/seen_jobs.json). Off by default, so testing "
                             "keeps the current behavior.")

    args = parser.parse_args()

    try:
        success = main(dry_run=args.dry_run, test_limit=args.limit,
                       full_pipeline=args.full_pipeline,
                       strong_threshold=args.strong_threshold,
                       template=args.template, one_page=args.one_page,
                       track_seen=args.track_seen)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
