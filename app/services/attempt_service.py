from app.calculations.risk_reward import (
    calculate_risk,
    calculate_reward,
    risk_reward_ratio,
)
from app.database.db import save_attempt
from app.services.evaluation_service import (
    evaluate_reasoning,
    detect_misconceptions,
)


def process_attempt(
    scenario_id: str,
    entry_price: float,
    stop_loss_price: float,
    target_price: float,
    numeric_answer: float,
    reasoning_text: str,
):
    risk = calculate_risk(entry_price, stop_loss_price)
    reward = calculate_reward(entry_price, target_price)

    correct_answer = risk_reward_ratio(
        entry_price,
        stop_loss_price,
        target_price,
    )

    is_correct = numeric_answer == correct_answer

    scores = evaluate_reasoning(
        reasoning_text,
        risk,
        reward,
    )

    misconceptions = detect_misconceptions(
        reasoning_text,
        risk,
        reward,
    )

    save_attempt(
        scenario_id=scenario_id,
        numeric_answer=numeric_answer,
        is_correct=is_correct,
        reasoning_text=reasoning_text,
        rubric_score=scores["total"],
        misconceptions=misconceptions,
    )

    return {
        "correct_answer": correct_answer,
        "is_correct": is_correct,
        "scores": scores,
        "misconceptions": misconceptions,
    }

if __name__ == "__main__":
    result = process_attempt(
        scenario_id="meridian_001",
        entry_price=60,
        stop_loss_price=54,
        target_price=78,
        numeric_answer=3.0,
        reasoning_text=(
            "My risk was $6 and my reward was $18. "
            "The ratio is 3.0, so this trade is guaranteed to be profitable."
        ),
    )

    print(result)