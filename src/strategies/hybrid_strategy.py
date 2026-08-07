from analysis.rsi import calculate_rsi
from analysis.support_resistance import find_support_resistance


def evaluate_stock(df):
    """
    Evaluates a stock using confirmed support and resistance zones,
    RSI, price location, bounce or rejection confirmation, and
    estimated reward-to-risk.

    Returns a recommendation with supporting and opposing evidence.
    """

    if len(df) < 15:
        return {
            "recommendation": "HOLD",
            "current_price": None,
            "rsi": None,
            "support": None,
            "resistance": None,
            "confidence": 0,
            "reward_risk": None,
            "reasoning": [
                "Not enough market data to calculate the strategy."
            ],
            "why_not": [
                "At least 15 trading periods are required."
            ],
        }

    current_price = float(df["Close"].iloc[-1])
    previous_close = float(df["Close"].iloc[-2])

    rsi_series = calculate_rsi(df)
    latest_rsi = rsi_series.iloc[-1]

    if latest_rsi != latest_rsi:
        return {
            "recommendation": "HOLD",
            "current_price": round(current_price, 2),
            "rsi": None,
            "support": None,
            "resistance": None,
            "confidence": 0,
            "reward_risk": None,
            "reasoning": [
                "RSI could not be calculated."
            ],
            "why_not": [
                "The RSI value is unavailable."
            ],
        }

    latest_rsi = float(latest_rsi)

    zones = find_support_resistance(df)

    nearest_support = zones["support"]
    nearest_resistance = zones["resistance"]

    recommendation = "HOLD"
    confidence = 0
    reward_risk = None

    reasoning = []
    why_not = []

    near_support = False
    near_resistance = False

    bounce_confirmed = current_price > previous_close
    rejection_confirmed = current_price < previous_close

    if nearest_support:
        support_buffer = nearest_support["zone_high"] * 0.01

        near_support = (
            nearest_support["zone_low"] - support_buffer
            <= current_price
            <= nearest_support["zone_high"] + support_buffer
        )

    if nearest_resistance:
        resistance_buffer = nearest_resistance["zone_high"] * 0.01

        near_resistance = (
            nearest_resistance["zone_low"] - resistance_buffer
            <= current_price
            <= nearest_resistance["zone_high"] + resistance_buffer
        )

    if nearest_support and nearest_resistance:
        stop_loss = nearest_support["zone_low"] * 0.99
        target_price = nearest_resistance["zone_low"]

        risk_per_share = current_price - stop_loss
        reward_per_share = target_price - current_price

        if risk_per_share > 0 and reward_per_share > 0:
            reward_risk = round(
                reward_per_share / risk_per_share,
                2,
            )

    buy_score = 0

    if nearest_support:
        buy_score += int(
            nearest_support["zone_strength"] * 0.4
        )

    if latest_rsi < 30:
        buy_score += 30
    elif latest_rsi < 35:
        buy_score += 20

    if near_support:
        buy_score += 10

    if bounce_confirmed:
        buy_score += 10

    if reward_risk is not None and reward_risk >= 2:
        buy_score += 10

    buy_score = min(100, buy_score)

    sell_score = 0

    if nearest_resistance:
        sell_score += int(
            nearest_resistance["zone_strength"] * 0.4
        )

    if latest_rsi > 70:
        sell_score += 30
    elif latest_rsi > 65:
        sell_score += 20

    if near_resistance:
        sell_score += 10

    if rejection_confirmed:
        sell_score += 10

    sell_score = min(100, sell_score)

    if (
        nearest_support
        and near_support
        and latest_rsi < 35
        and bounce_confirmed
        and (
            reward_risk is None
            or reward_risk >= 2
        )
    ):
        recommendation = "BUY"
        confidence = buy_score

        reasoning.append(
            "Price is at or near a confirmed support zone."
        )
        reasoning.append(
            f"Support has {nearest_support['touches']} touches."
        )
        reasoning.append(
            f"Support zone strength is "
            f"{nearest_support['zone_strength']}."
        )
        reasoning.append(
            f"RSI is {round(latest_rsi, 2)}, "
            "showing weak momentum."
        )
        reasoning.append(
            "The latest close is above the previous close, "
            "confirming a possible bounce."
        )

        if reward_risk is not None:
            reasoning.append(
                f"Estimated reward-to-risk is {reward_risk}:1."
            )

        if nearest_resistance is None:
            why_not.append(
                "No confirmed resistance zone was found "
                "for a clear target."
            )

    elif (
        nearest_resistance
        and near_resistance
        and latest_rsi > 65
        and rejection_confirmed
    ):
        recommendation = "SELL"
        confidence = sell_score

        reasoning.append(
            "Price is at or near a confirmed resistance zone."
        )
        reasoning.append(
            f"Resistance has "
            f"{nearest_resistance['touches']} touches."
        )
        reasoning.append(
            f"Resistance zone strength is "
            f"{nearest_resistance['zone_strength']}."
        )
        reasoning.append(
            f"RSI is {round(latest_rsi, 2)}, "
            "showing strong momentum."
        )
        reasoning.append(
            "The latest close is below the previous close, "
            "confirming a possible rejection."
        )

    else:
        confidence = max(buy_score, sell_score)

        reasoning.append(
            "No complete high-confidence trade setup was confirmed."
        )

        if not nearest_support:
            why_not.append(
                "No support zone met the four-touch minimum."
            )
        elif not near_support:
            why_not.append(
                "Current price is not close enough "
                "to confirmed support."
            )

        if 35 <= latest_rsi <= 65:
            why_not.append(
                "RSI is neutral rather than stretched."
            )

        if near_support and not bounce_confirmed:
            why_not.append(
                "Price has not confirmed a bounce from support."
            )

        if near_resistance and not rejection_confirmed:
            why_not.append(
                "Price has not confirmed a rejection "
                "from resistance."
            )

        if reward_risk is not None and reward_risk < 2:
            why_not.append(
                f"Reward-to-risk is only {reward_risk}:1."
            )

        if not why_not:
            why_not.append(
                "The available evidence does not support a trade."
            )

    return {
        "recommendation": recommendation,
        "current_price": round(current_price, 2),
        "rsi": round(latest_rsi, 2),
        "support": nearest_support,
        "resistance": nearest_resistance,
        "confidence": confidence,
        "reward_risk": reward_risk,
        "reasoning": reasoning,
        "why_not": why_not,
    }