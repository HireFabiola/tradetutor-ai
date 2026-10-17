"""Regression checks for numeric grounding and negated certainty claims."""

import pytest

from app.services.evaluation_service import (
    detect_ratio_certainty_misconception,
    detect_risk_reward_swap_misconception,
    evaluate_reasoning,
)


@pytest.mark.parametrize("text", [
    "A favorable ratio does not guarantee a successful trade.",
    "Profit is not guaranteed.",
    "This isn't guaranteed to work.",
    "A good ratio is never a sure thing.",
    "There is no guarantee of profit.",
])
def test_negated_certainty_is_not_a_misconception(text):
    assert not detect_ratio_certainty_misconception(text)


@pytest.mark.parametrize("text", [
    "This trade is guaranteed to profit.",
    "A ratio of three is always a good trade.",
    "It is not guaranteed, but this trade will definitely profit.",
    "There is no guarantee. However, it is a sure thing.",
])
def test_positive_certainty_is_detected_even_after_negated_claim(text):
    assert detect_ratio_certainty_misconception(text)


def test_correct_calculation_and_interpretation_receive_full_credit():
    text = (
        "My risk was $6 and my reward was $18. "
        "For every $1 I risk, I could earn $3 if the target is reached."
    )
    assert evaluate_reasoning(text, 6, 18)["total"] == 3


@pytest.mark.parametrize("text", [
    "Risk is $18 and reward is $6, which means I earn $18 per dollar risked.",
    "Risk is $60 and reward is $180, which means profit.",
    "I wrote 6 and 18 many times. Risk and reward.",
])
def test_keywords_and_wrong_amounts_do_not_receive_numeric_credit(text):
    scores = evaluate_reasoning(text, 6, 18)
    assert scores["calculation_process"] == 0
    assert scores["interpretation"] == 0
    assert scores["total"] < 3


def test_wrong_per_unit_interpretation_loses_credit():
    text = "Risk is $6 and reward is $18. For every $1 I risk, I earn $18."
    assert evaluate_reasoning(text, 6, 18)["interpretation"] == 0


def test_decimal_amounts_are_not_truncated():
    text = "My risk is $1.25 and reward is $2.50."
    assert evaluate_reasoning(text, 1.25, 2.5)["calculation_process"] == 1
    assert detect_risk_reward_swap_misconception(
        "Risk is $2.50 and reward is $1.25.", 1.25, 2.5
    )


def test_equal_risk_and_reward_are_not_a_swap():
    assert not detect_risk_reward_swap_misconception("Risk is $6 and reward is $6.", 6, 6)
