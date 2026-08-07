import os

import matplotlib.pyplot as plt


def generate_chart(
    symbol,
    data,
    support=None,
    resistance=None,
    output_folder="data/charts"
):
    """
    Generates a price chart and saves it as a PNG.
    """

    os.makedirs(output_folder, exist_ok=True)

    plt.figure(figsize=(14, 7))

    plt.plot(
        data.index,
        data["Close"],
        label="Close Price",
        linewidth=2
    )

    current_price = float(data["Close"].iloc[-1])

    plt.axhline(
        current_price,
        linestyle="--",
        linewidth=2,
        label=f"Current: ${current_price:.2f}"
    )

    if support:

        plt.axhspan(
            support["zone_low"],
            support["zone_high"],
            alpha=0.30,
            label="Support Zone"
        )

    if resistance:

        plt.axhspan(
            resistance["zone_low"],
            resistance["zone_high"],
            alpha=0.30,
            label="Resistance Zone"
        )

    plt.title(f"{symbol} Price Chart")

    plt.xlabel("Date")

    plt.ylabel("Price ($)")

    plt.legend()

    plt.grid(True)

    output_path = os.path.join(
        output_folder,
        f"{symbol}.png"
    )

    plt.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight"
    )

    print(f"Chart created: {output_path}")

    plt.close()

    return output_path