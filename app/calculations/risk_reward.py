def risk_reward_ratio(entry_price: float, stop_loss_price: float, target_price: float) -> float:
    """Calculate the risk/reward ratio for a trade setup.

    Args:
        entry_price: The price at which the trade is entered.
        stop_loss_price: The price where the trade would be exited to cap loss.
        target_price: The price where the trade target is expected.

    Returns:
        The reward-to-risk ratio, calculated as reward divided by risk. A ratio above 1.0 indicates a larger
        potential reward than risk.

    """
    risk = entry_price - stop_loss_price
    reward = target_price - entry_price

    ratio = reward / risk
    return ratio

if __name__ == "__main__":
    ratio = risk_reward_ratio(40, 40, 77)
    print(ratio)