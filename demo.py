"""
Run this file to see CityVoice AI work end-to-end on sample complaints:

    python demo.py

It will:
  1. Classify each sample complaint (category + urgency)
  2. Look up the right department + SLA (simulated RAG retrieval)
  3. Draft a citizen-facing acknowledgment message
  4. Print an aggregated "dashboard" summary by category, like the
     ward-official dashboard described in the project design.
"""

import json
from collections import Counter

from classify import process_complaint, USE_LLM


def main():
    with open("sample_complaints.json", "r") as f:
        complaints = json.load(f)

    print("=" * 70)
    print("CityVoice AI - Demo Run")
    mode = "LLM-based (ANTHROPIC_API_KEY detected)" if USE_LLM else "Rule-based (no API key set)"
    print(f"Classification mode: {mode}")
    print("=" * 70)

    results = []
    for i, text in enumerate(complaints, start=1):
        result = process_complaint(text)
        results.append(result)

        print(f"\nComplaint {i}: {text}")
        print(f"  Category : {result['category']}")
        print(f"  Urgency  : {result['urgency']}")
        print(f"  Routed to: {result['department']} (SLA: {result['sla_hours']}h)")
        print(f"  Reply    : {result['response']}")

    print("\n" + "=" * 70)
    print("Ward Dashboard Summary")
    print("=" * 70)
    category_counts = Counter(r["category"] for r in results)
    urgency_counts = Counter(r["urgency"] for r in results)

    print("\nComplaints by category:")
    for category, count in category_counts.most_common():
        print(f"  {category:12s}: {count}")

    print("\nComplaints by urgency:")
    for urgency, count in urgency_counts.most_common():
        print(f"  {urgency:12s}: {count}")


if __name__ == "__main__":
    main()
