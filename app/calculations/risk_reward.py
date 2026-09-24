def calculate_risk(
    entry_price: float,
    stop_loss_price: float,
) -> float:
    """Calculate the amount at risk in a trade setup."""
    return entry_price - stop_loss_price


def calculate_reward(
    entry_price: float,
    target_price: float,
) -> float:
    """Calculate the potential reward in a trade setup."""
    return target_price - entry_price


def risk_reward_ratio(
    entry_price: float,
    stop_loss_price: float,
    target_price: float,
) -> float:
    """Calculate the risk/reward ratio for a trade setup.

    Args:
        entry_price: The price at which the trade is entered.
        stop_loss_price: The price where the trade would be exited to cap loss.
        target_price: The price where the trade target is expected.

    Returns:
        The reward-to-risk ratio, calculated as reward divided by risk.
        A ratio above 1.0 indicates a larger potential reward than risk.
    """
    risk = calculate_risk(entry_price, stop_loss_price)
    reward = calculate_reward(entry_price, target_price)

    ratio = reward / risk
    return ratio


if __name__ == "__main__":
    risk = calculate_risk(60, 54)
    reward = calculate_reward(60, 78)
    ratio = risk_reward_ratio(60, 54, 78)

    print(f"Risk: {risk}")
    print(f"Reward: {reward}")
    print(f"Risk/reward ratio: {ratio}")