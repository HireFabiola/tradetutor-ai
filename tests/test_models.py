"""The scenario model must be importable and preserve its validation rules."""

import pytest
from pydantic import ValidationError

from app.database.models import ScenarioAnswer


def test_valid_scenario_answer():
    answer = ScenarioAnswer(
        numeric_answer=2, reasoning_text="Reward is twice the risk.",
        entry_price=40, stop_loss_price=35,
    )
    assert answer.numeric_answer == 2


@pytest.mark.parametrize("changes", [
    {"reasoning_text": "Because"},
    {"stop_loss_price": 40},
    {"numeric_answer": 0},
])
def test_invalid_scenario_answers_are_rejected(changes):
    values = dict(numeric_answer=2, reasoning_text="Reward is twice the risk.",
                  entry_price=40, stop_loss_price=35)
    values.update(changes)
    with pytest.raises(ValidationError):
        ScenarioAnswer(**values)
