from pathlib import Path
from datetime import datetime

import boto3
import yfinance as yf

print("Trading Analytics Bot Started")

watchlist = (
    Path(__file__).resolve().parents[2]
    / "watchlist.txt"
)

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

try:

    for symbol in stocks:

        print(f"\nCollecting {symbol}...")

        stock = yf.Ticker(symbol)

        history = stock.history(period="5d")

        today = datetime.today().strftime("%Y-%m-%d")

        output_folder = (
            Path(__file__).resolve().parents[2]
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

        print(history)
        print(f"Saved {symbol} to {output_file}")
        print(f"Uploaded {symbol} to Amazon S3")

except Exception as error:
    print(f"\nError collecting market data: {error}")