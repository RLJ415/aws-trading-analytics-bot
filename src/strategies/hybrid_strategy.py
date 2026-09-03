from src.analysis.rsi import calculate_rsi
from src.analysis.support_resistance import find_support_resistance


RECENT_TOUCH_LOOKBACK = 7
SIGNAL_SCORE_THRESHOLD = 65
MAX_BUY_RSI = 60
MIN_SELL_RSI = 45
MAX_ZONE_DISTANCE_PERCENT = 5
MIN_BUY_REWARD_RISK = 1.25


def _empty_result(
    current_price=None,
    rsi=None,
    reasoning=None,
    why_not=None,
):
    return {
        "recommendation": "HOLD",
        "current_price": current_price,
        "rsi": rsi,
        "support": None,
        "resistance": None,
        "all_supports": [],
        "all_resistances": [],
        "confidence": 0,
        "reward_risk": None,
        "reasoning": reasoning or [],
        "why_not": why_not or [],
        "swing_highs": [],
        "swing_lows": [],
    }


def _distance_to_zone_percent(
    price,
    zone,
):
    if not zone:
        return None

    price = float(price)

    zone_low = float(
        zone["zone_low"]
    )

    zone_high = float(
        zone["zone_high"]
    )

    if (
        zone_low
        <= price
        <= zone_high
    ):
        return 0.0

    if price < zone_low:
        distance = (
            zone_low
            - price
        )

    else:
        distance = (
            price
            - zone_high
        )

    if price <= 0:
        return None

    return (
        distance
        / price
        * 100
    )


def _distance_score(
    distance_percent,
):
    if distance_percent is None:
        return 0

    if distance_percent <= 1.5:
        return 20

    if distance_percent <= 3:
        return 15

    if distance_percent <= 5:
        return 10

    if distance_percent <= 8:
        return 5

    return 0


def _find_recent_zone_touch(
    df,
    zone,
    lookback=RECENT_TOUCH_LOOKBACK,
):
    if not zone:
        return None

    recent_data = df.tail(
        min(
            lookback,
            len(df),
        )
    )

    zone_low = float(
        zone["zone_low"]
    )

    zone_high = float(
        zone["zone_high"]
    )

    for offset in range(
        1,
        len(recent_data) + 1,
    ):
        row = recent_data.iloc[
            -offset
        ]

        candle_low = float(
            row["Low"]
        )

        candle_high = float(
            row["High"]
        )

        if (
            candle_low <= zone_high
            and candle_high >= zone_low
        ):
            return offset - 1

    return None


def _calculate_reward_risk(
    current_price,
    support,
    resistance,
):
    if (
        not support
        or not resistance
    ):
        return None

    stop_loss = (
        float(
            support["zone_low"]
        )
        * 0.99
    )

    target_price = float(
        resistance["zone_low"]
    )

    risk_per_share = (
        current_price
        - stop_loss
    )

    reward_per_share = (
        target_price
        - current_price
    )

    if (
        risk_per_share <= 0
        or reward_per_share <= 0
    ):
        return None

    return round(
        reward_per_share
        / risk_per_share,
        2,
    )


def _buy_rsi_score(
    latest_rsi,
    rsi_rising,
):
    if latest_rsi <= 30:
        return 20

    if latest_rsi <= 40:
        return 16

    if latest_rsi <= 50:
        return 10

    if (
        latest_rsi <= 60
        and rsi_rising
    ):
        return 6

    return 0


def _sell_rsi_score(
    latest_rsi,
    rsi_falling,
):
    if latest_rsi >= 70:
        return 20

    if latest_rsi >= 60:
        return 16

    if latest_rsi >= 50:
        return 10

    if (
        latest_rsi >= 40
        and rsi_falling
    ):
        return 6

    return 0


def evaluate_stock(df):
    """
    Swing-oriented hybrid strategy.

    Uses the existing four-touch support/resistance zones,
    removes incomplete OHLC rows, scores the setup, and
    applies quality guardrails before issuing BUY or SELL.
    """

    if df is None:
        return _empty_result(
            reasoning=[
                "No market data was provided to the strategy."
            ],
            why_not=[
                "A valid OHLC price history is required."
            ],
        )

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    if not all(
        column in df.columns
        for column in required_columns
    ):
        return _empty_result(
            reasoning=[
                "Required OHLC columns are missing from market data."
            ],
            why_not=[
                "Open, High, Low, and Close columns are required."
            ],
        )

    df = df.dropna(
        subset=required_columns
    ).copy()

    if len(df) < 15:
        return _empty_result(
            reasoning=[
                "Not enough valid market data to calculate the strategy."
            ],
            why_not=[
                "At least 15 complete OHLC trading periods are required."
            ],
        )

    current_price = float(
        df["Close"].iloc[-1]
    )

    previous_close = float(
        df["Close"].iloc[-2]
    )

    momentum_reference_close = float(
        df["Close"].iloc[-4]
    )

    rsi_series = calculate_rsi(
        df
    )

    latest_rsi = rsi_series.iloc[-1]

    if latest_rsi != latest_rsi:
        return _empty_result(
            current_price=round(
                current_price,
                2,
            ),
            reasoning=[
                "RSI could not be calculated."
            ],
            why_not=[
                "The RSI value is unavailable."
            ],
        )

    latest_rsi = float(
        latest_rsi
    )

    previous_rsi = None

    if len(rsi_series) >= 2:
        candidate_previous_rsi = (
            rsi_series.iloc[-2]
        )

        if (
            candidate_previous_rsi
            == candidate_previous_rsi
        ):
            previous_rsi = float(
                candidate_previous_rsi
            )

    zones = find_support_resistance(
        df
    )

    nearest_support = zones.get(
        "support"
    )

    nearest_resistance = zones.get(
        "resistance"
    )

    all_supports = zones.get(
        "all_supports",
        [],
    )

    all_resistances = zones.get(
        "all_resistances",
        [],
    )

    swing_highs = zones.get(
        "swing_highs",
        [],
    )

    swing_lows = zones.get(
        "swing_lows",
        [],
    )

    support_distance = (
        _distance_to_zone_percent(
            current_price,
            nearest_support,
        )
    )

    resistance_distance = (
        _distance_to_zone_percent(
            current_price,
            nearest_resistance,
        )
    )

    support_touch_days = (
        _find_recent_zone_touch(
            df,
            nearest_support,
        )
    )

    resistance_touch_days = (
        _find_recent_zone_touch(
            df,
            nearest_resistance,
        )
    )

    recent_support_touch = (
        support_touch_days
        is not None
    )

    recent_resistance_touch = (
        resistance_touch_days
        is not None
    )

    support_context = (
        recent_support_touch
        or (
            support_distance is not None
            and support_distance
            <= MAX_ZONE_DISTANCE_PERCENT
        )
    )

    resistance_context = (
        recent_resistance_touch
        or (
            resistance_distance
            is not None
            and resistance_distance
            <= MAX_ZONE_DISTANCE_PERCENT
        )
    )

    one_day_up = (
        current_price
        > previous_close
    )

    one_day_down = (
        current_price
        < previous_close
    )

    short_term_up = (
        current_price
        > momentum_reference_close
    )

    short_term_down = (
        current_price
        < momentum_reference_close
    )

    upward_confirmation = (
        one_day_up
        or short_term_up
    )

    downward_confirmation = (
        one_day_down
        or short_term_down
    )

    rsi_rising = (
        previous_rsi is not None
        and latest_rsi
        > previous_rsi
    )

    rsi_falling = (
        previous_rsi is not None
        and latest_rsi
        < previous_rsi
    )

    reward_risk = (
        _calculate_reward_risk(
            current_price,
            nearest_support,
            nearest_resistance,
        )
    )

    buy_score = 0

    if nearest_support:
        buy_score += min(
            20,
            int(
                nearest_support[
                    "zone_strength"
                ]
                * 0.20
            ),
        )

    buy_score += (
        _distance_score(
            support_distance
        )
    )

    if recent_support_touch:
        buy_score += 15

    buy_score += (
        _buy_rsi_score(
            latest_rsi,
            rsi_rising,
        )
    )

    if rsi_rising:
        buy_score += 5

    if one_day_up:
        buy_score += 5

    if short_term_up:
        buy_score += 10

    if reward_risk is not None:

        if reward_risk >= 2:
            buy_score += 10

        elif reward_risk >= 1.5:
            buy_score += 7

        elif reward_risk >= 1:
            buy_score += 4

    buy_score = min(
        100,
        buy_score,
    )

    sell_score = 0

    if nearest_resistance:
        sell_score += min(
            20,
            int(
                nearest_resistance[
                    "zone_strength"
                ]
                * 0.20
            ),
        )

    sell_score += (
        _distance_score(
            resistance_distance
        )
    )

    if recent_resistance_touch:
        sell_score += 15

    sell_score += (
        _sell_rsi_score(
            latest_rsi,
            rsi_falling,
        )
    )

    if rsi_falling:
        sell_score += 5

    if one_day_down:
        sell_score += 5

    if short_term_down:
        sell_score += 10

    sell_score = min(
        100,
        sell_score,
    )

    recommendation = "HOLD"

    confidence = max(
        buy_score,
        sell_score,
    )

    reasoning = []
    why_not = []

    buy_signal = (
        nearest_support
        and buy_score
        >= SIGNAL_SCORE_THRESHOLD
        and buy_score
        >= sell_score + 5
        and support_context
        and upward_confirmation
        and latest_rsi
        <= MAX_BUY_RSI
        and reward_risk is not None
        and reward_risk
        >= MIN_BUY_REWARD_RISK
    )

    sell_signal = (
        nearest_resistance
        and sell_score
        >= SIGNAL_SCORE_THRESHOLD
        and sell_score
        >= buy_score + 5
        and resistance_context
        and downward_confirmation
        and latest_rsi
        >= MIN_SELL_RSI
    )

    if buy_signal:

        recommendation = "BUY"
        confidence = buy_score

        reasoning.append(
            f"BUY setup score reached "
            f"{buy_score}/100."
        )

        reasoning.append(
            f"Support has "
            f"{nearest_support['touches']} touches "
            f"with strength "
            f"{nearest_support['zone_strength']}."
        )

        if support_distance is not None:
            reasoning.append(
                f"Price is "
                f"{support_distance:.2f}% "
                "from the nearest confirmed support zone."
            )

        if recent_support_touch:

            if support_touch_days == 0:
                reasoning.append(
                    "Price interacted with support today."
                )

            else:
                reasoning.append(
                    f"Support was tested "
                    f"{support_touch_days} trading day(s) ago."
                )

        if rsi_rising:
            reasoning.append(
                f"RSI is rising at "
                f"{latest_rsi:.2f}."
            )

        else:
            reasoning.append(
                f"RSI is "
                f"{latest_rsi:.2f}."
            )

        if one_day_up:
            reasoning.append(
                "The latest close is above the previous close."
            )

        if short_term_up:
            reasoning.append(
                "Price is above its short-term reference close."
            )

        reasoning.append(
            f"Estimated reward-to-risk is "
            f"{reward_risk}:1."
        )

    elif sell_signal:

        recommendation = "SELL"
        confidence = sell_score

        reasoning.append(
            f"SELL setup score reached "
            f"{sell_score}/100."
        )

        reasoning.append(
            f"Resistance has "
            f"{nearest_resistance['touches']} touches "
            f"with strength "
            f"{nearest_resistance['zone_strength']}."
        )

        if resistance_distance is not None:
            reasoning.append(
                f"Price is "
                f"{resistance_distance:.2f}% "
                "from the nearest confirmed resistance zone."
            )

        if recent_resistance_touch:

            if resistance_touch_days == 0:
                reasoning.append(
                    "Price interacted with resistance today."
                )

            else:
                reasoning.append(
                    f"Resistance was tested "
                    f"{resistance_touch_days} trading day(s) ago."
                )

        if rsi_falling:
            reasoning.append(
                f"RSI is falling at "
                f"{latest_rsi:.2f}."
            )

        else:
            reasoning.append(
                f"RSI is "
                f"{latest_rsi:.2f}."
            )

        if one_day_down:
            reasoning.append(
                "The latest close is below the previous close."
            )

        if short_term_down:
            reasoning.append(
                "Price is below its short-term reference close."
            )

    else:

        reasoning.append(
            "No directional setup passed all quality checks."
        )

        reasoning.append(
            f"BUY score: "
            f"{buy_score}/100. "
            f"SELL score: "
            f"{sell_score}/100."
        )

        if not nearest_support:

            why_not.append(
                "No support zone met the four-touch minimum."
            )

        elif not support_context:

            why_not.append(
                f"Price has no recent support interaction "
                f"and is more than "
                f"{MAX_ZONE_DISTANCE_PERCENT}% "
                "from confirmed support."
            )

        if not nearest_resistance:

            why_not.append(
                "No resistance zone met the four-touch minimum."
            )

        elif not resistance_context:

            why_not.append(
                f"Price has no recent resistance interaction "
                f"and is more than "
                f"{MAX_ZONE_DISTANCE_PERCENT}% "
                "from confirmed resistance."
            )

        if (
            buy_score
            >= SIGNAL_SCORE_THRESHOLD
            and latest_rsi
            > MAX_BUY_RSI
        ):

            why_not.append(
                f"BUY was blocked because RSI "
                f"{latest_rsi:.2f} is above "
                f"the {MAX_BUY_RSI} ceiling."
            )

        if (
            sell_score
            >= SIGNAL_SCORE_THRESHOLD
            and latest_rsi
            < MIN_SELL_RSI
        ):

            why_not.append(
                f"SELL was blocked because RSI "
                f"{latest_rsi:.2f} is below "
                f"the {MIN_SELL_RSI} floor."
            )

        if (
            buy_score
            >= SIGNAL_SCORE_THRESHOLD
            and (
                reward_risk is None
                or reward_risk
                < MIN_BUY_REWARD_RISK
            )
        ):

            why_not.append(
                f"BUY was blocked because reward-to-risk "
                f"did not reach "
                f"{MIN_BUY_REWARD_RISK}:1."
            )

        if (
            buy_score
            >= SIGNAL_SCORE_THRESHOLD
            and not upward_confirmation
        ):

            why_not.append(
                "BUY was blocked because upward momentum "
                "was not confirmed."
            )

        if (
            sell_score
            >= SIGNAL_SCORE_THRESHOLD
            and not downward_confirmation
        ):

            why_not.append(
                "SELL was blocked because downward momentum "
                "was not confirmed."
            )

        if (
            buy_score
            < SIGNAL_SCORE_THRESHOLD
            and sell_score
            < SIGNAL_SCORE_THRESHOLD
        ):

            why_not.append(
                f"Neither setup reached the "
                f"{SIGNAL_SCORE_THRESHOLD}-point signal threshold."
            )

        elif (
            abs(
                buy_score
                - sell_score
            )
            < 5
        ):

            why_not.append(
                "BUY and SELL evidence is too evenly matched."
            )

        if not why_not:

            why_not.append(
                "The available evidence does not justify "
                "a directional trade."
            )

    return {
        "recommendation": recommendation,
        "current_price": round(
            current_price,
            2,
        ),
        "rsi": round(
            latest_rsi,
            2,
        ),
        "support": nearest_support,
        "resistance": nearest_resistance,
        "all_supports": all_supports,
        "all_resistances": all_resistances,
        "confidence": confidence,
        "reward_risk": reward_risk,
        "reasoning": reasoning,
        "why_not": why_not,
        "swing_highs": swing_highs,
        "swing_lows": swing_lows,
    }