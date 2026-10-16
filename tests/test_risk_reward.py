"""Check deterministic risk/reward calculations for fictional long trades."""

import pytest

from app.calculations.risk_reward import (
    calculate_reward,
    calculate_risk,
    risk_reward_ratio,
)


@pytest.mark.parametrize(
    "entry, stop_loss, expected",
    [(60.0, 54.0, 6.0), (25.50, 24.25, 1.25), (10.10, 10.00, 0.10)],
)
def test_calculate_risk(entry: float, stop_loss: float, expected: float) -> None:
    assert calculate_risk(entry, stop_loss) == pytest.approx(expected)


@pytest.mark.parametrize(
    "entry, target, expected",
    [(60.0, 78.0, 18.0), (25.50, 28.00, 2.50), (10.10, 10.40, 0.30)],
)
def test_calculate_reward(entry: float, target: float, expected: float) -> None:
    assert calculate_reward(entry, target) == pytest.approx(expected)


@pytest.mark.parametrize(
    "entry, stop_loss, target, expected",
    [
        (60.0, 54.0, 78.0, 3.0),  # Reward is three times risk.
        (60.0, 54.0, 66.0, 1.0),  # Equal potential reward and risk.
        (60.0, 54.0, 63.0, 0.5),  # Potential reward is smaller than risk.
        (10.10, 10.00, 10.40, 3.0),  # Decimal prices require float tolerance.
        (60.0, 54.0, 60.0, 0.0),  # No potential reward.
    ],
)
def test_ratio_is_reward_divided_by_risk(
    entry: float, stop_loss: float, target: float, expected: float
) -> None:
    assert risk_reward_ratio(entry, stop_loss, target) == pytest.approx(expected)


def test_zero_risk_raises_instead_of_returning_a_ratio() -> None:
    # Documents current behavior; explicit input validation is not implemented yet.
    with pytest.raises(ZeroDivisionError):
        risk_reward_ratio(60.0, 60.0, 78.0)
