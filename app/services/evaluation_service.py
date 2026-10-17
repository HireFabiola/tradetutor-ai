"""Conservative, deterministic checks for explicit risk/reward explanations.

These rules recognize supported numeric statements; they do not assess arbitrary
natural-language reasoning or establish that a fictional trade will succeed.
"""

import math
import re

NUMBER = r"(?<![\w.])-?\d+(?:\.\d+)?(?!\w|\.\d)"
TERMS = {
    "risk": r"risk(?:ed|ing)?",
    "reward": r"(?:reward|earn(?:ed|ing)?|gain|profit)",
}


def extract_number_near_word(text: str, word: str) -> float | None:
    """Read an amount directly associated with a term, including decimal amounts."""
    term = TERMS.get(word, re.escape(word))
    after = rf"\b{term}\b\s*(?:(?:was|is|of|equals?|would be|could be)\s*)?\$?({NUMBER})"
    before = rf"\$?({NUMBER})\s*(?:I\s+)?(?:of\s+)?{term}\b"
    match = re.search(after, text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    match = re.search(before, text, re.IGNORECASE)
    return float(match.group(1)) if match else None


def score_calculation_process(reasoning_text: str, risk: float, reward: float) -> float:
    """Require both amounts to be attached to their correct concepts."""
    stated_risk = extract_number_near_word(reasoning_text, "risk")
    stated_reward = extract_number_near_word(reasoning_text, "reward")
    return float(
        stated_risk is not None and stated_reward is not None
        and math.isclose(stated_risk, risk, rel_tol=1e-6, abs_tol=1e-9)
        and math.isclose(stated_reward, reward, rel_tol=1e-6, abs_tol=1e-9)
    )


def score_interpretation(reasoning_text: str, risk: float, reward: float) -> float:
    """Recognize an explicit, correct reward amount for each unit of risk."""
    if risk <= 0:
        return 0.0
    # Limit matching to the explanation following 'for every', so earlier
    # scenario amounts cannot stand in for a per-unit interpretation.
    for explanation in re.split(r"\bfor every\b", reasoning_text.lower())[1:]:
        explanation = re.split(r"[;!?]|\.(?!\d)", explanation, maxsplit=1)[0]
        unit_risk = extract_number_near_word(explanation, "risk")
        unit_reward = extract_number_near_word(explanation, "reward")
        if (unit_risk is not None and unit_risk > 0 and unit_reward is not None
                and math.isclose(unit_reward / unit_risk, reward / risk, rel_tol=1e-6)):
            return 1.0
    return 0.0


def score_terminology(reasoning_text: str) -> float:
    return float(all(
        re.search(rf"\b{term}\b", reasoning_text, re.IGNORECASE)
        for term in TERMS.values()
    ))


def evaluate_reasoning(reasoning_text: str, risk: float, reward: float) -> dict:
    scores = {
        "calculation_process": score_calculation_process(reasoning_text, risk, reward),
        "interpretation": score_interpretation(reasoning_text, risk, reward),
        "terminology": score_terminology(reasoning_text),
    }
    scores["total"] = sum(scores.values())
    return scores


def detect_ratio_certainty_misconception(reasoning_text: str) -> bool:
    """Check certainty claims within clauses, respecting explicit negation."""
    text = reasoning_text.lower().replace("’", "'")
    certainty = (r"\b(?:always a good trade|always better|guarantee(?:d|s)?|"
                 r"sure thing|definitely profit|will definitely|always means a better trade)\b")
    for clause in re.split(r"[.!?;,]|\b(?:but|however|yet)\b", text):
        for match in re.finditer(certainty, clause):
            prefix = clause[:match.start()]
            suffix = clause[match.end():]
            negated = re.search(
                r"\b(?:not|never|no|cannot|can't|isn't|aren't|doesn't|don't|won't)"
                r"(?:\s+[a-z]+){0,3}\s*$", prefix
            )
            # Also recognize 'a guarantee is not possible'.
            negated_after = re.match(r"\s+(?:is|are)\s+(?:not|never)\b", suffix)
            if not negated and not negated_after:
                return True
    return False

def detect_risk_reward_swap_misconception(reasoning_text: str, risk: float, reward: float) -> bool:
    """
    Finds the number associated with "risk" and the number associated with
    "reward" by proximity in the text, then checks whether they're swapped
    relative to the scenario's actual values.
    """
    stated_risk = extract_number_near_word(reasoning_text, "risk")
    stated_reward = extract_number_near_word(reasoning_text, "reward")

    if stated_risk is None or stated_reward is None:
        return False  # can't confidently judge if either number wasn't found

    return risk != reward and stated_risk == reward and stated_reward == risk


def detect_misconceptions(reasoning_text: str, risk: float, reward: float) -> list[str]:
    found = []
    if detect_ratio_certainty_misconception(reasoning_text):
        found.append("ratio_implies_certainty")
    if detect_risk_reward_swap_misconception(reasoning_text, risk, reward):
        found.append("risk_reward_swapped")
    return found
