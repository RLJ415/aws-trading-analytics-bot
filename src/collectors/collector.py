from datetime import datetime
from pathlib import Path
import sys

import boto3
import yfinance as yf


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_ROOT))

from strategies.hybrid_strategy import evaluate_stock


print("Trading Analytics Bot Started")

watchlist = PROJECT_ROOT / "watchlist.txt"

with open(watchlist, "r") as file:
    stocks = [
        line.strip()
        for line in file
        if line.strip()
    ]

print("=" * 50)
print(f"Loaded {len(stocks)} stocks from watchlist.")
print("=" * 50)

s3 = boto3.client("s3")
today = datetime.today().strftime("%Y-%m-%d")

for symbol in stocks:

    try:
        print(f"\nCollecting {symbol}...")

        stock = yf.Ticker(symbol)
        history = stock.history(period="6mo", interval="1d")

        if history.empty:
            print(f"No market data returned for {symbol}.")
            continue

        output_folder = (
            PROJECT_ROOT
            / "data"
            / "local"
            / symbol
        )

        output_folder.mkdir(parents=True, exist_ok=True)

        output_file = output_folder / f"{today}.csv"

        history.to_csv(output_file)

        s3.upload_file(
            str(output_file),
            "trading-analytics-data",
            f"raw/{symbol}/{today}.csv",
        )

        analysis = evaluate_stock(history)

        print(f"Saved {symbol} to {output_file}")
        print(f"Uploaded {symbol} to Amazon S3")
        print(f"Recommendation: {analysis['recommendation']}")
        print(f"RSI: {analysis['rsi']}")

        print("Reasoning:")

        for reason in analysis["reasoning"]:
            print(f"- {reason}")

    except Exception as error:
        print(f"Error processing {symbol}: {error}")