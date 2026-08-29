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


S3_BUCKET = "trading-analytics-data"

SNS_TOPIC_ARN = (
    "arn:aws:sns:us-east-1:"
    "829279763167:trading-alerts"
)


def make_json_safe(value):
    """
    Convert values returned by pandas / numpy into
    normal Python values that json.dumps can serialize.
    """

    if isinstance(value, dict):
        return {
            key: make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            make_json_safe(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            make_json_safe(item)
            for item in value
        ]

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    return value


def run_collector():

    print("Trading Analytics Bot Started")

    watchlist = (
        PROJECT_ROOT
        / "watchlist.txt"
    )

    with open(
        watchlist,
        "r"
    ) as file:

        stocks = [
            line.strip()
            for line in file
            if line.strip()
        ]

    print("=" * 50)

    print(
        f"Loaded {len(stocks)} stocks "
        f"from watchlist."
    )

    print("=" * 50)

    s3 = boto3.client("s3")

    today = (
        datetime.today()
        .strftime("%Y-%m-%d")
    )

    dashboard_results = []

    failed_stocks = []


    for symbol in stocks:

        try:

            print(
                f"\nCollecting {symbol}..."
            )


            stock = yf.Ticker(
                symbol
            )


            history = stock.history(
                period="1y",
                interval="1d"
            )


            if history.empty:

                print(
                    f"No market data returned "
                    f"for {symbol}."
                )

                failed_stocks.append(
                    symbol
                )

                continue


            if os.environ.get(
                "AWS_LAMBDA_FUNCTION_NAME"
            ):

                output_folder = (
                    Path("/tmp")
                    / "data"
                    / "local"
                    / symbol
                )

            else:

                output_folder = (
                    PROJECT_ROOT
                    / "data"
                    / "local"
                    / symbol
                )


            output_folder.mkdir(
                parents=True,
                exist_ok=True
            )


            output_file = (
                output_folder
                / f"{today}.csv"
            )


            history.to_csv(
                output_file
            )


            s3.upload_file(
                str(output_file),
                S3_BUCKET,
                f"raw/{symbol}/{today}.csv"
            )


            analysis = evaluate_stock(
                history
            )


            print(
                type(analysis)
            )

            print(
                analysis
            )


            support = make_json_safe(
                analysis.get(
                    "support"
                )
            )


            resistance = make_json_safe(
                analysis.get(
                    "resistance"
                )
            )


            reasoning = make_json_safe(
                analysis.get(
                    "reasoning",
                    []
                )
            )


            why_not = make_json_safe(
                analysis.get(
                    "why_not",
                    []
                )
            )


            dashboard_results.append({
                "symbol":
                    symbol,

                "recommendation":
                    make_json_safe(
                        analysis.get(
                            "recommendation"
                        )
                    ),

                "current_price":
                    make_json_safe(
                        analysis.get(
                            "current_price"
                        )
                    ),

                "rsi":
                    make_json_safe(
                        analysis.get(
                            "rsi"
                        )
                    ),

                "confidence":
                    make_json_safe(
                        analysis.get(
                            "confidence"
                        )
                    ),

                "reward_risk":
                    make_json_safe(
                        analysis.get(
                            "reward_risk"
                        )
                    ),

                "support":
                    support,

                "resistance":
                    resistance,

                "reasoning":
                    reasoning,

                "why_not":
                    why_not,

                "chart":
                    f"charts/{symbol}.png"
            })


            chart_path = generate_chart(
                symbol=symbol,
                data=history,
                support=analysis["support"],
                resistance=analysis["resistance"]
            )


            s3.upload_file(
                chart_path,
                S3_BUCKET,
                f"charts/{symbol}.png"
            )


            print(
                f"Saved {symbol} "
                f"to {output_file}"
            )


            print(
                f"Uploaded {symbol} CSV "
                f"to Amazon S3"
            )


            print(
                f"Uploaded {symbol} Chart "
                f"to Amazon S3"
            )


            print(
                f"Chart saved: "
                f"{chart_path}"
            )


            print(
                f"Recommendation: "
                f"{analysis['recommendation']}"
            )


            print(
                f"RSI: "
                f"{analysis['rsi']}"
            )


            print(
                f"Confidence: "
                f"{analysis['confidence']}"
            )


            print(
                f"Reward/Risk: "
                f"{analysis.get('reward_risk')}"
            )


            print(
                f"Support: "
                f"{support}"
            )


            print(
                f"Resistance: "
                f"{resistance}"
            )


            print(
                "Reasoning:"
            )


            for reason in reasoning:

                print(
                    f"- {reason}"
                )


            if why_not:

                print(
                    "Why Not:"
                )


                for reason in why_not:

                    print(
                        f"- {reason}"
                    )


        except Exception as error:

            failed_stocks.append(
                symbol
            )

            print(
                f"Error processing "
                f"{symbol}: {error}"
            )


    dashboard_payload = {

        "generated_at":
            datetime.utcnow()
            .isoformat()
            + "Z",

        "watchlist_count":
            len(stocks),

        "processed_count":
            len(
                dashboard_results
            ),

        "failed_count":
            len(
                failed_stocks
            ),

        "failed_symbols":
            failed_stocks,

        "results":
            dashboard_results

    }


    dashboard_json = json.dumps(
        dashboard_payload,
        indent=2
    )


    s3.put_object(
        Bucket=S3_BUCKET,
        Key=(
            "dashboard/"
            "latest-results.json"
        ),
        Body=dashboard_json,
        ContentType=(
            "application/json"
        )
    )


    print(
        "Dashboard results "
        "uploaded to Amazon S3."
    )


    print(
        f"Processed: "
        f"{len(dashboard_results)}"
        f"/{len(stocks)}"
    )


    if failed_stocks:

        print(
            "Failed symbols: "
            + ", ".join(
                failed_stocks
            )
        )


    sns = boto3.client(
        "sns"
    )


    sns.publish(
        TopicArn=
            SNS_TOPIC_ARN,

        Subject=
            "AWS Trading Analytics "
            "Bot Run Complete",

        Message=f"""
Trading Analytics Bot completed a scheduled run.

Stocks attempted: {len(stocks)}
Stocks processed: {len(dashboard_results)}
Stocks failed: {len(failed_stocks)}
Failed symbols: {", ".join(failed_stocks) if failed_stocks else "None"}
Date: {today}

Market data, strategy results, and charts have been uploaded to Amazon S3.

The dashboard now includes support/resistance data, RSI, confidence, reward/risk, and strategy reasoning.

Check CloudWatch for the complete analysis results.
"""
    )


    print(
        "SNS completion "
        "notification sent."
    )


if __name__ == "__main__":

    run_collector()