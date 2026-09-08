# CityVoice AI
**A Smart Civic Grievance Triage & Resolution Assistant**

Built for the 1M1B AI for Sustainability Virtual Internship (with IBM SkillsBuild & AICTE).
**Primary SDG:** SDG 11 — Sustainable Cities and Communities
**Secondary SDGs:** SDG 9 — Industry, Innovation & Infrastructure; SDG 16 — Peace, Justice & Strong Institutions

## Problem
Civic complaints (potholes, garbage, water leaks, broken streetlights) are reported through
scattered, informal channels and sorted manually by municipal staff. This is slow and
inconsistent — a safety-critical issue can sit in the same queue as a minor one — and city
officials have no aggregated view of where problems keep recurring.

## What this prototype does
This is a small, working, no-advanced-coding prototype that mirrors the workflow in the
project design document:

1. **Classify** — takes a citizen's complaint text and works out its category (roads,
   sanitation, water, electricity, general) and urgency (high/normal).
2. **Policy lookup (RAG-style)** — looks up the right department and expected resolution
   timeline (SLA) from `policy_kb.json`, a small knowledge base, instead of hard-coding it.
3. **Draft response** — generates a tracking ID and a citizen-facing acknowledgment message.
4. **Dashboard summary** — aggregates results by category/urgency, similar to the ward-level
   dashboard described for city officials in the design doc.

By default it runs with **simple keyword-based classification** (no API key, no cost, works
immediately). If you set an `ANTHROPIC_API_KEY` environment variable, it will automatically
use a real Claude model call for smarter classification instead — falling back safely to the
keyword method if anything goes wrong.

## Setup

```bash
git clone <your-repo-url>
cd cityvoice-ai
pip install -r requirements.txt
```

## Run the demo

```bash
python demo.py
```

This runs the pipeline on the sample complaints in `sample_complaints.json` and prints a
dashboard summary.

## Run the tests

```bash
python tests/test_classify.py
```

## Optional: enable real LLM-based classification

```bash
export ANTHROPIC_API_KEY="your-key-here"
python demo.py
```

You'll see the demo report `Classification mode: LLM-based` instead of rule-based.

## Project structure

```
cityvoice-ai/
├── classify.py            # core classification + policy lookup + response drafting
├── policy_kb.json          # small "knowledge base" of department + SLA per category
├── sample_complaints.json  # sample input complaints for the demo
├── demo.py                 # runs the full pipeline + prints a dashboard summary
├── tests/
│   └── test_classify.py    # simple tests, no framework needed
├── requirements.txt
└── README.md
```

## Responsible AI notes
- **Fairness:** keyword lists should be expanded/tested against real, varied complaint
  phrasing so no category or dialect is systematically misclassified.
- **Transparency:** the drafted reply always tells the citizen their complaint was
  classified and gives them a tracking ID; a real deployment should also offer a way to
  request human review.
- **Ethics:** classification here is meant to be *advisory* to municipal staff, not a fully
  automated final decision on public services.
- **Privacy:** no personal data beyond the complaint text itself is stored or processed by
  this prototype.

## Relation to the full project submission
This repository is the working prototype referenced in the project's PDF/PPT deliverable
(`CityVoice_AI_Project.pdf`) and the internship submission form. All problem statement,
solution description, and SDG alignment details match across both.
