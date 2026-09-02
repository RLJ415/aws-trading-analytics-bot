def find_support_resistance(df):
    """
    Finds the nearest valid support and resistance
    relative to the current market price.

    Also identifies dated swing highs and swing lows
    for interactive chart markers.
    """

    swing_highs = []
    swing_lows = []

    current_price = float(df["Close"].iloc[-1])

    for i in range(2, len(df) - 2):
        date_value = df.index[i]

        if hasattr(date_value, "strftime"):
            swing_date = date_value.strftime("%Y-%m-%d")
        else:
            swing_date = str(date_value).split(" ")[0]

        if (
            df["High"].iloc[i] > df["High"].iloc[i - 1]
            and df["High"].iloc[i] > df["High"].iloc[i - 2]
            and df["High"].iloc[i] > df["High"].iloc[i + 1]
            and df["High"].iloc[i] > df["High"].iloc[i + 2]
        ):
            swing_highs.append({
                "time": swing_date,
                "price": float(df["High"].iloc[i]),
            })

        if (
            df["Low"].iloc[i] < df["Low"].iloc[i - 1]
            and df["Low"].iloc[i] < df["Low"].iloc[i - 2]
            and df["Low"].iloc[i] < df["Low"].iloc[i + 1]
            and df["Low"].iloc[i] < df["Low"].iloc[i + 2]
        ):
            swing_lows.append({
                "time": swing_date,
                "price": float(df["Low"].iloc[i]),
            })

    support_levels = [
        point["price"]
        for point in swing_lows
    ]

    resistance_levels = [
        point["price"]
        for point in swing_highs
    ]

    support_zones = group_price_levels(
        support_levels
    )

    resistance_zones = group_price_levels(
        resistance_levels
    )

    support_below = sorted(
        [
            zone
            for zone in support_zones
            if zone["zone_high"] <= current_price
        ],
        key=lambda zone: current_price - zone["zone_high"],
    )

    resistance_above = sorted(
        [
            zone
            for zone in resistance_zones
            if zone["zone_low"] >= current_price
        ],
        key=lambda zone: zone["zone_low"] - current_price,
    )

    nearest_support = (
        support_below[0]
        if support_below
        else None
    )

    nearest_resistance = (
        resistance_above[0]
        if resistance_above
        else None
    )

    print("\n======================================")
    print("SUPPORT / RESISTANCE DIAGNOSTICS")
    print("======================================")
    print(f"Current Price: {current_price:.2f}")
    print(f"Swing Lows Found: {len(swing_lows)}")
    print(f"Swing Highs Found: {len(swing_highs)}")
    print(f"Confirmed Support Zones: {len(support_zones)}")
    print(f"Confirmed Resistance Zones: {len(resistance_zones)}")
    print(f"Nearest Support: {nearest_support}")
    print(f"Nearest Resistance: {nearest_resistance}")

    return {
        "support": nearest_support,
        "resistance": nearest_resistance,
        "all_supports": support_zones,
        "all_resistances": resistance_zones,
        "swing_highs": swing_highs,
        "swing_lows": swing_lows,
    }


def group_price_levels(
    levels,
    tolerance=0.01,
    min_touches=4,
):
    """
    Groups nearby price levels into confirmed
    support/resistance zones.

    Four touches = 70 strength
    Five touches = 80 strength
    Six touches = 90 strength
    Seven or more = 100 strength
    """

    zones = []

    for level in sorted(levels):
        level = float(level)
        matched = False

        for zone in zones:
            zone_low = min(zone["prices"])
            zone_high = max(zone["prices"])

            expanded_low = zone_low * (1 - tolerance)
            expanded_high = zone_high * (1 + tolerance)

            if expanded_low <= level <= expanded_high:
                zone["prices"].append(level)
                matched = True
                break

        if not matched:
            zones.append({
                "prices": [level]
            })

    confirmed_zones = []

    for zone in zones:
        prices = zone["prices"]
        touches = len(prices)

        if touches < min_touches:
            continue

        zone_low = min(prices)
        zone_high = max(prices)

        if touches == 4:
            zone_strength = 70
        elif touches == 5:
            zone_strength = 80
        elif touches == 6:
            zone_strength = 90
        else:
            zone_strength = 100

        confirmed_zones.append({
            "zone_low": zone_low,
            "zone_high": zone_high,
            "touches": touches,
            "zone_strength": zone_strength,
        })

    return confirmed_zones