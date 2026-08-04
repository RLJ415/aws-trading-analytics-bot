from pathlib import Path

import boto3
import yfinance as yf

print("Trading Analytics Bot Started")

try:
    stock = yf.Ticker("AAPL")

    history = stock.history(period="5d")

    output_file = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "local"
        / "AAPL_5d.csv"
    )

    history.to_csv(output_file)

    s3 = boto3.client("s3")

    s3.upload_file(
        str(output_file),
        "trading-analytics-data",
        "raw/AAPL_5d.csv",
    )

    print(history)
    print(f"\nData saved to {output_file}")
    print("File uploaded to Amazon S3")

except Exception as error:
    print(f"\nError collecting market data: {error}")