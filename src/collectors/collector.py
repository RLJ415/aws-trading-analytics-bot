from datetime import datetime
from pathlib import Path
import sys
import os
import json

import boto3
import yfinance as yf


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_ROOT))

from strategies.hybrid_strategy import evaluate_stock
from visualization.chart_generator import generate_chart


def run_collector():
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
    dashboard_results = []

    for symbol in stocks:
        try:
            print(f"\nCollecting {symbol}...")

            stock = yf.Ticker(symbol)
            history = stock.history(period="1y", interval="1d")

            if history.empty:
                print(f"No market data returned for {symbol}.")
                continue

            if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
                output_folder = Path("/tmp") / "data" / "local" / symbol
            else:
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

            print(type(analysis))
            print(analysis)

            dashboard_results.append({
                "symbol": symbol,
                "recommendation": analysis["recommendation"],
                "rsi": analysis["rsi"],
                "confidence": analysis["confidence"],
                "chart": f"charts/{symbol}.png"
            })

            chart_path = generate_chart(
                symbol=symbol,
                data=history,
                support=analysis["support"],
                resistance=analysis["resistance"],
            )

            s3.upload_file(
                chart_path,
                "trading-analytics-data",
                f"charts/{symbol}.png",
            )

            print(f"Saved {symbol} to {output_file}")
            print(f"Uploaded {symbol} CSV to Amazon S3")
            print(f"Uploaded {symbol} Chart to Amazon S3")
            print(f"Chart saved: {chart_path}")
            print(f"Recommendation: {analysis['recommendation']}")
            print(f"RSI: {analysis['rsi']}")

            print("Reasoning:")

            for reason in analysis["reasoning"]:
                print(f"- {reason}")

        except Exception as error:
            print(f"Error processing {symbol}: {error}")

    dashboard_json = json.dumps(
        dashboard_results,
        indent=2
    )

    s3.put_object(
        Bucket="trading-analytics-data",
        Key="dashboard/latest-results.json",
        Body=dashboard_json,
        ContentType="application/json"
    )

    print("Dashboard results uploaded to Amazon S3.")

    sns = boto3.client("sns")

    sns.publish(
        TopicArn="arn:aws:sns:us-east-1:829279763167:trading-alerts",
        Subject="AWS Trading Analytics Bot Run Complete",
        Message=f"""
Trading Analytics Bot completed its daily run.

Stocks scanned: {len(stocks)}
Date: {today}

Market data and charts have been uploaded to Amazon S3.
Check CloudWatch for the complete analysis results.
"""
    )

    print("SNS completion notification sent.")


if __name__ == "__main__":
    run_collector()