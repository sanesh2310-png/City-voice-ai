"""
CityVoice AI - core classification + policy lookup logic.

This module does the real work described in the project design:
  1. classify_complaint()  -> works out a category + urgency level for a
     citizen complaint, using simple keyword matching by default, or a
     real LLM call if an ANTHROPIC_API_KEY is configured (see USE_LLM below).
  2. lookup_policy()       -> a lightweight "RAG" style lookup: given a
     category, retrieve the right department and SLA (service-level
     timeline) from policy_kb.json instead of hard-coding it in the model.
  3. draft_response()      -> builds the citizen-facing acknowledgment
     message with a generated tracking ID.

No advanced coding is required to run this - see README.md for setup.
"""

import json
import os
import random
import string

HERE = os.path.dirname(os.path.abspath(__file__))
POLICY_KB_PATH = os.path.join(HERE, "policy_kb.json")

# High-urgency signal words. In a real deployment these would be tuned
# with real complaint data and reviewed for fairness (see README ->
# Responsible AI notes).
URGENCY_KEYWORDS = [
    "danger", "dangerous", "urgent", "emergency", "school", "hospital",
    "accident", "child", "children", "safety", "collapsed", "electrocut",
    "fire", "flooding", "flood", "sparking", "exposed wire",
]

USE_LLM = bool(os.environ.get("ANTHROPIC_API_KEY"))


def _load_policy_kb():
    with open(POLICY_KB_PATH, "r") as f:
        return json.load(f)


def _rule_based_classify(text):
    """Keyword-based fallback classifier. Deterministic and free to run,
    so the project works out of the box without any API key."""
    text_lower = text.lower()
    kb = _load_policy_kb()

    best_category = "general"
    best_hits = 0
    for category, info in kb.items():
        hits = sum(1 for kw in info["keywords"] if kw in text_lower)
        if hits > best_hits:
            best_hits = hits
            best_category = category

    urgency = "high" if any(kw in text_lower for kw in URGENCY_KEYWORDS) else "normal"
    return best_category, urgency


def _llm_classify(text):
    """Optional real-LLM classification path. Only used if ANTHROPIC_API_KEY
    is set in the environment. Falls back to rule-based on any error so the
    demo never breaks."""
    try:
        import anthropic

        client = anthropic.Anthropic()
        kb = _load_policy_kb()
        categories = list(kb.keys())

        prompt = (
            "You are a civic-complaint triage assistant. Classify the complaint "
            f"below into exactly one of these categories: {categories}. "
            "Also decide urgency as 'high' or 'normal' (high = safety risk, "
            "near schools/hospitals, or affecting many people). "
            "Respond ONLY as JSON: {\"category\": \"...\", \"urgency\": \"...\"}\n\n"
            f"Complaint: {text}"
        )

        model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
        response = client.messages.create(
            model=model,
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)
        category = parsed.get("category", "general")
        urgency = parsed.get("urgency", "normal")
        if category not in kb:
            category = "general"
        if urgency not in ("high", "normal"):
            urgency = "normal"
        return category, urgency
    except Exception:
        # Any problem (no key, bad response, network issue) -> safe fallback
        return _rule_based_classify(text)


def classify_complaint(text):
    """Returns (category, urgency) for a complaint string."""
    if USE_LLM:
        return _llm_classify(text)
    return _rule_based_classify(text)


def lookup_policy(category, urgency):
    """RAG-style retrieval: look up department + SLA for a category from
    the policy knowledge base, instead of hard-coding it in prompts/code."""
    kb = _load_policy_kb()
    info = kb.get(category, kb["general"])
    sla_hours = info["sla_hours_high"] if urgency == "high" else info["sla_hours_normal"]
    return info["department"], sla_hours


def _generate_tracking_id():
    return "CV-" + "".join(random.choices(string.digits, k=4))


def draft_response(category, urgency, department, sla_hours):
    """Builds the citizen-facing acknowledgment message."""
    tracking_id = _generate_tracking_id()
    priority_label = "High" if urgency == "high" else "Standard"
    message = (
        f"Thank you for reporting this. Your complaint (ID: {tracking_id}) "
        f"has been classified as '{category}' with {priority_label} priority "
        f"and routed to the {department}. Expected resolution: within "
        f"{sla_hours} hours."
    )
    return tracking_id, message


def process_complaint(text):
    """End-to-end pipeline matching the workflow diagram in the project
    PDF: classify -> policy lookup -> draft response."""
    category, urgency = classify_complaint(text)
    department, sla_hours = lookup_policy(category, urgency)
    tracking_id, message = draft_response(category, urgency, department, sla_hours)
    return {
        "complaint_text": text,
        "category": category,
        "urgency": urgency,
        "department": department,
        "sla_hours": sla_hours,
        "tracking_id": tracking_id,
        "response": message,
    }
