# Agent Guide (Application Strategy & Outreach)

Goal: Produce a `how_to_apply.md` that recommends HOW to apply (portal vs. direct cold outreach), identifies the right people to contact, infers reachable email addresses, and supplies a tailored cold-email draft.

## Inputs
- The job offer file in `job_offers/`.
- The matching `grading.md` (callback probability drives the apply-vs-coldmail call).
- Live web research (WebSearch / WebFetch).

## Output
- Write `how_to_apply.md` inside the same `outputs/job_offers/<folder>/` as the CV.

## Apply-vs-cold-email decision rule
- **High portal callback probability (>55%)** and a real ATS: apply normally first; outreach only as a follow-up nudge.
- **Medium (35-55%)**: apply via portal AND send one direct cold email to a recruiter/hiring manager to jump the queue.
- **Low (<35%) or aggregator/black-box channel (e.g. Jobgether-style matching)**: prioritize direct outreach; the portal alone is low-yield.
- Always note when the posting is via an intermediary/agency vs. the employer directly — outreach targets differ.

## Recruiter research (live)
For each company, use WebSearch to find:
1. People posting the role or with **#hiring / #OpenToWork-adjacent** signals tied to the company (talent acquisition, HR business partner, team lead, hiring manager).
2. The company careers page and any named recruiter on the posting.
3. The company's public **email-address pattern** (search "email format <company>", press releases, mailto links). Record the pattern and confidence.

## Email inference (be honest about confidence)
- Derive likely addresses from the verified pattern, e.g. `first.last@company.com`.
- NEVER assert a private personal email as confirmed. Label every inferred address **(inferred, unverified)** and give the pattern it came from.
- Prefer verifiable role inboxes (careers@, jobs@, talent@, recruitment@) when the personal pattern is uncertain.
- Suggest a verification step (e.g. email-permutation + verifier tools, LinkedIn message as fallback).

## Required sections in how_to_apply.md
1. **Header** — company, role, date.
2. **Recommendation** — one-line verdict (portal / portal+coldmail / coldmail-first) with the callback probability it is based on.
3. **Channel notes** — direct employer vs. agency/aggregator; where the real decision happens.
4. **Who to contact** — named people found (role, why them, LinkedIn URL), ranked. Note if none found.
5. **Reachable addresses** — verified role inboxes + inferred personal addresses (pattern + confidence + "(inferred, unverified)").
6. **Cold email draft** — subject + 120-160 word body tailored to the role, referencing 2-3 of the candidate's strongest matches from `grading.md`. Include a PDF-attached note.
7. **LinkedIn fallback** — short connection-request note (<300 chars).
8. **Timing & follow-up** — when to send, when to follow up once.

## Constraints
- Only use publicly available information; do not fabricate names or assert unverified emails as fact.
- Keep outreach honest — no fake mutual connections or invented referrals.
- Cold-email claims must match what the CV and `data/` actually support.
