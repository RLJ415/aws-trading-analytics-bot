import pandas as pd


def find_support_resistance(df):
    """
    Finds the nearest valid support and resistance
    relative to the current market price.

    Also prints diagnostic information showing
    every accepted candidate zone.
    """

    swing_highs = []
    swing_lows = []

    current_price = float(df["Close"].iloc[-1])

    for i in range(2, len(df) - 2):

        if (
            df["High"].iloc[i] > df["High"].iloc[i - 1]
            and df["High"].iloc[i] > df["High"].iloc[i - 2]
            and df["High"].iloc[i] > df["High"].iloc[i + 1]
            and df["High"].iloc[i] > df["High"].iloc[i + 2]
        ):
            swing_highs.append(df["High"].iloc[i])

        if (
            df["Low"].iloc[i] < df["Low"].iloc[i - 1]
            and df["Low"].iloc[i] < df["Low"].iloc[i - 2]
            and df["Low"].iloc[i] < df["Low"].iloc[i + 1]
            and df["Low"].iloc[i] < df["Low"].iloc[i + 2]
        ):
            swing_lows.append(df["Low"].iloc[i])

    support_zones = group_price_levels(swing_lows)
    resistance_zones = group_price_levels(swing_highs)

    support_below = sorted(
        [
            zone
            for zone in support_zones
            if zone["zone_high"] <= current_price
        ],
        key=lambda zone: current_price - zone["zone_high"]
    )

    support_above = sorted(
        [
            zone
            for zone in support_zones
            if zone["zone_low"] > current_price
        ],
        key=lambda zone: zone["zone_low"] - current_price
    )

    resistance_above = sorted(
        [
            zone
            for zone in resistance_zones
            if zone["zone_low"] >= current_price
        ],
        key=lambda zone: zone["zone_low"] - current_price
    )

    resistance_below = sorted(
        [
            zone
            for zone in resistance_zones
            if zone["zone_high"] < current_price
        ],
        key=lambda zone: current_price - zone["zone_high"]
    )

    nearest_support = support_below[0] if support_below else None
    nearest_resistance = resistance_above[0] if resistance_above else None

    print("\n======================================")
    print("SUPPORT / RESISTANCE DIAGNOSTICS")
    print("======================================")
    print(f"Current Price: {current_price:.2f}")
    print(f"Swing Lows Found: {len(swing_lows)}")
    print(f"Swing Highs Found: {len(swing_highs)}")

    print("\nAccepted Support Candidates")

    if support_zones:
        for zone in support_zones:
            print(
                f"Zone: {zone['zone_low']:.2f} - "
                f"{zone['zone_high']:.2f} | "
                f"Touches: {zone['touches']} | "
                f"Strength: {zone['zone_strength']}"
            )
    else:
        print("None")

    print("\nAccepted Resistance Candidates")

    if resistance_zones:
        for zone in resistance_zones:
            print(
                f"Zone: {zone['zone_low']:.2f} - "
                f"{zone['zone_high']:.2f} | "
                f"Touches: {zone['touches']} | "
                f"Strength: {zone['zone_strength']}"
            )
    else:
        print("None")

    print("\nNearest Support")
    print(nearest_support)

    print("\nNearest Resistance")
    print(nearest_resistance)

    return {
        "support": nearest_support,
        "resistance": nearest_resistance,
        "all_supports": support_zones,
        "all_resistances": resistance_zones,
    }


def group_price_levels(levels, tolerance=0.01, min_touches=4):
    """
    Groups nearby price levels into support/resistance zones.

    Prints diagnostics showing how levels were grouped
    and why each zone was accepted or rejected.
    """

    zones = []

    print("\n======================================")
    print("GROUP PRICE LEVEL DIAGNOSTICS")
    print("======================================")
    print(f"Levels received: {len(levels)}")
    print(f"Tolerance: {tolerance * 100:.2f}%")
    print(f"Minimum touches required: {min_touches}")

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
    rejected_zones = []

    print(f"\nTotal grouped zones: {len(zones)}")

    for zone_number, zone in enumerate(zones, start=1):

        prices = zone["prices"]
        touches = len(prices)
        zone_low = min(prices)
        zone_high = max(prices)
        average_price = sum(prices) / touches

        print("\n--------------------------------------")
        print(f"Zone {zone_number}")
        print("--------------------------------------")
        print(f"Average price: {average_price:.2f}")
        print(f"Zone range: {zone_low:.2f} - {zone_high:.2f}")
        print(f"Touches: {touches}")
        print(
            "Prices: "
            + ", ".join(
                f"{price:.2f}"
                for price in prices
            )
        )

        if touches >= min_touches:

            if touches == 4:
                zone_strength = 70
            elif touches == 5:
                zone_strength = 80
            elif touches == 6:
                zone_strength = 90
            else:
                zone_strength = 100

            confirmed_zone = {
                "zone_low": zone_low,
                "zone_high": zone_high,
                "touches": touches,
                "zone_strength": zone_strength
            }

            confirmed_zones.append(confirmed_zone)

            print("Status: ACCEPTED")
            print(f"Zone strength: {zone_strength}")

        else:

            rejected_zone = {
                "zone_low": zone_low,
                "zone_high": zone_high,
                "touches": touches,
                "reason": (
                    f"Needs {min_touches} touches"
                )
            }

            rejected_zones.append(rejected_zone)

            print("Status: REJECTED")
            print(
                f"Reason: Needs {min_touches} touches"
            )

    print("\n======================================")
    print("GROUPING SUMMARY")
    print("======================================")
    print(f"Accepted zones: {len(confirmed_zones)}")
    print(f"Rejected zones: {len(rejected_zones)}")

    return confirmed_zones