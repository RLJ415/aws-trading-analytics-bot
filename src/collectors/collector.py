from pathlib import Path

import yfinance as yf

print("Trading Analytics Bot Started")

try:
    stock = yf.Ticker("AAPL")

    history = stock.history(period="5d")

    output_file = Path(__file__).resolve().parents[2] / "data" / "local" / "AAPL_5d.csv"

    history.to_csv(output_file)

    print(history)

    print(f"\nData saved to {output_file}")

except Exception as error:
    print(f"\nError collecting market data: {error}")