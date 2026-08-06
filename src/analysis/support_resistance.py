import pandas as pd


def find_support_resistance(df):
    """
    Finds potential support and resistance zones
    from historical market data.

    Parameters:
        df: Pandas DataFrame containing
            High, Low, and Close prices.

    Returns:
        Dictionary containing support and resistance data.
    """

    swing_highs = []
    swing_lows = []

    for i in range(2, len(df) - 2):

        # Peak
        if (
            df["High"].iloc[i] > df["High"].iloc[i - 1]
            and df["High"].iloc[i] > df["High"].iloc[i - 2]
            and df["High"].iloc[i] > df["High"].iloc[i + 1]
            and df["High"].iloc[i] > df["High"].iloc[i + 2]
        ):
            swing_highs.append(df["High"].iloc[i])

        # Valley
        if (
            df["Low"].iloc[i] < df["Low"].iloc[i - 1]
            and df["Low"].iloc[i] < df["Low"].iloc[i - 2]
            and df["Low"].iloc[i] < df["Low"].iloc[i + 1]
            and df["Low"].iloc[i] < df["Low"].iloc[i + 2]
        ):
            swing_lows.append(df["Low"].iloc[i])

    support_zones = group_price_levels(swing_lows)
    resistance_zones = group_price_levels(swing_highs)

    return {
        "support": support_zones,
        "resistance": resistance_zones,
    }


def group_price_levels(levels, tolerance=0.01, min_touches=4):
    """
    Groups nearby price levels into support/resistance zones.
    """

    zones = []

    for level in sorted(levels):

        matched = False

        for zone in zones:

            average_price = sum(zone["prices"]) / len(zone["prices"])

            if abs(level - average_price) / average_price <= tolerance:

                zone["prices"].append(level)
                matched = True
                break

        if not matched:

            zones.append({
                "prices": [level]
            })

    confirmed_zones = []

    for zone in zones:

        if len(zone["prices"]) >= min_touches:

            touches = len(zone["prices"])

            if touches == 4:
                zone_strength = 70
            elif touches == 5:
                zone_strength = 80
            elif touches == 6:
                zone_strength = 90
            else:
                zone_strength = 100

            confirmed_zones.append({
                "zone_low": min(zone["prices"]),
                "zone_high": max(zone["prices"]),
                "touches": touches,
                "zone_strength": zone_strength
            })

    return confirmed_zones