import re

def score_calculation_process(reasoning_text: str, risk: float, reward: float) -> float:
    text = reasoning_text.lower()
    if str(int(risk)) in text or str(int(reward)) in text:
        return 1.0
    return 0.0


def score_interpretation(reasoning_text: str) -> float:
    text = reasoning_text.lower()
    interpretive_phrases = ["for every", "per dollar", "times", "means"]
    if any(phrase in text for phrase in interpretive_phrases):
        return 1.0
    return 0.0


def score_terminology(reasoning_text: str) -> float:
    text = reasoning_text.lower()
    risk_words = ["risk", "risked", "risking"]
    reward_words = ["reward", "earn", "earned", "earning", "gain", "profit"]
    has_risk_word = any(word in text for word in risk_words)
    has_reward_word = any(word in text for word in reward_words)
    if has_risk_word and has_reward_word:
        return 1.0
    return 0.0


def evaluate_reasoning(reasoning_text: str, risk: float, reward: float) -> dict:
    scores = {
        "calculation_process": score_calculation_process(reasoning_text, risk, reward),
        "interpretation": score_interpretation(reasoning_text),
        "terminology": score_terminology(reasoning_text),
    }
    scores["total"] = sum(scores.values())
    return scores

def detect_ratio_certainty_misconception(reasoning_text: str) -> bool:
    """
    Flags reasoning that treats a favorable ratio as a guarantee of success,
    ignoring that a ratio alone says nothing about likelihood (the exact
    misconception named in the lesson's "why the ratio alone isn't the
    whole story" section).
    """
    text = reasoning_text.lower()
    certainty_phrases = [
        "always a good trade",
        "always better",
        "guaranteed",
        "guarantee",
        "sure thing",
        "definitely profit",
        "will definitely",
        "always means a better trade",
    ]
    return any(phrase in text for phrase in certainty_phrases)

def extract_number_near_word(text: str, word: str) -> float | None:
    # Look for the word, then capture the first number that appears
    # shortly after it (within roughly 20 characters)
    pattern = rf"{word}\w*[^0-9]{{0,20}}\$?(\d+)"
    match = re.search(pattern, text.lower())
    if match:
        return float(match.group(1))
    return None

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

    return stated_risk == reward and stated_reward == risk


def detect_misconceptions(reasoning_text: str, risk: float, reward: float) -> list[str]:
    found = []
    if detect_ratio_certainty_misconception(reasoning_text):
        found.append("ratio_implies_certainty")
    if detect_risk_reward_swap_misconception(reasoning_text, risk, reward):
        found.append("risk_reward_swapped")
    return found


if __name__ == "__main__":
    risk = 6.0
    reward = 18.0

    test_cases = {
        "strong": (
            "My risk was $6 (the difference between the $60 entry and $54 "
            "stop-loss), and my reward was $18 (the difference between $60 "
            "and the $78 target). Dividing 18 by 6 gives a ratio of 3.0, "
            "meaning for every $1 I risk, I could earn $3 if the trade hits "
            "its target."
        ),
        "middle": "I risked $6 and could earn $18, so the ratio is 3 to 1.",
        "weak": "The ratio is 3.0.",
        "off_topic": "I think Meridian Robotics sounds like a cool company to invest in.",
        "certainty_misconception": (
            "The ratio is 3.0, which is great, so this is guaranteed to be a "
            "profitable trade."
        ),
        "swap_misconception": (
            "My risk was $18 and my reward was $6, giving a ratio of 3.0."
        ),
    }

    for label, text in test_cases.items():
        result = evaluate_reasoning(text, risk, reward)
        print(f"{label}: {result}")

        found = detect_misconceptions(text, risk, reward)
        print(f"{label}: {found}") 