"""
Simple tests - no test framework needed, run with:

    python tests/test_classify.py

(Run from the project root, or add the parent folder to your path.)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from classify import classify_complaint, lookup_policy, process_complaint


def test_pothole_is_roads_and_high_urgency():
    category, urgency = classify_complaint(
        "There's a dangerous pothole right outside the school gate."
    )
    assert category == "roads", f"expected roads, got {category}"
    assert urgency == "high", f"expected high, got {urgency}"
    print("PASS: test_pothole_is_roads_and_high_urgency")


def test_garbage_is_sanitation():
    category, urgency = classify_complaint(
        "Garbage has been piling up on our street for a week."
    )
    assert category == "sanitation", f"expected sanitation, got {category}"
    print("PASS: test_garbage_is_sanitation")


def test_lookup_policy_returns_department_and_sla():
    department, sla = lookup_policy("water", "high")
    assert department == "Water Supply Department"
    assert isinstance(sla, int)
    print("PASS: test_lookup_policy_returns_department_and_sla")


def test_process_complaint_end_to_end():
    result = process_complaint("No water supply in our area since yesterday.")
    assert result["category"] == "water"
    assert result["tracking_id"].startswith("CV-")
    assert "Water Supply Department" in result["response"]
    print("PASS: test_process_complaint_end_to_end")


if __name__ == "__main__":
    test_pothole_is_roads_and_high_urgency()
    test_garbage_is_sanitation()
    test_lookup_policy_returns_department_and_sla()
    test_process_complaint_end_to_end()
    print("\nAll tests passed.")
