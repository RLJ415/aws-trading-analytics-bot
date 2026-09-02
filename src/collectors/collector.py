from datetime import datetime, timezone
from pathlib import Path
import sys
import os
import json

import boto3
import yfinance as yf


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.strategies.hybrid_strategy import evaluate_stock
from src.visualization.chart_generator import generate_chart


S3_BUCKET = os.environ.get(
    "S3_BUCKET",
    "trading-analytics-data",
)

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

    if isinstance(value, (list, tuple)):
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


def format_market_date(value):
    """
    Convert a pandas / datetime index value into
    YYYY-MM-DD format for TradingView chart markers.
    """

    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")

    return str(value).split(" ")[0]


def decision_color(recommendation):
    """
    Return the dashboard color for a strategy decision.
    """

    colors = {
        "BUY": "green",
        "SELL": "red",
        "HOLD": "yellow",
    }

    return colors.get(
        recommendation,
        "yellow",
    )


def run_collector():
    print("Trading Analytics Bot Started")

    watchlist = (
        PROJECT_ROOT
        / "watchlist.txt"
    )

    with open(
        watchlist,
        "r",
        encoding="utf-8",
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
        datetime.now()
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
                interval="1d",
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
                exist_ok=True,
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
                f"raw/{symbol}/{today}.csv",
            )

            analysis = evaluate_stock(
                history
            )

            recommendation = make_json_safe(
                analysis.get(
                    "recommendation",
                    "HOLD",
                )
            )

            current_price = make_json_safe(
                analysis.get(
                    "current_price"
                )
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

            all_supports = make_json_safe(
                analysis.get(
                    "all_supports",
                    [],
                )
            )

            all_resistances = make_json_safe(
                analysis.get(
                    "all_resistances",
                    [],
                )
            )

            swing_highs = make_json_safe(
                analysis.get(
                    "swing_highs",
                    [],
                )
            )

            swing_lows = make_json_safe(
                analysis.get(
                    "swing_lows",
                    [],
                )
            )

            reasoning = make_json_safe(
                analysis.get(
                    "reasoning",
                    [],
                )
            )

            why_not = make_json_safe(
                analysis.get(
                    "why_not",
                    [],
                )
            )

            latest_market_date = (
                format_market_date(
                    history.index[-1]
                )
            )

            decision = {
                "time": latest_market_date,
                "price": current_price,
                "type": recommendation,
                "color": decision_color(
                    recommendation
                ),
            }

            dashboard_results.append({
                "symbol": symbol,
                "recommendation": recommendation,
                "current_price": current_price,
                "rsi": make_json_safe(
                    analysis.get(
                        "rsi"
                    )
                ),
                "confidence": make_json_safe(
                    analysis.get(
                        "confidence",
                        0,
                    )
                ),
                "reward_risk": make_json_safe(
                    analysis.get(
                        "reward_risk"
                    )
                ),
                "support": support,
                "resistance": resistance,
                "all_supports": all_supports,
                "all_resistances": all_resistances,
                "reasoning": reasoning,
                "why_not": why_not,
                "swing_highs": swing_highs,
                "swing_lows": swing_lows,
                "decision": decision,
                "chart": f"charts/{symbol}.png",
            })

            chart_path = generate_chart(
                symbol=symbol,
                data=history,
                support=analysis.get(
                    "support"
                ),
                resistance=analysis.get(
                    "resistance"
                ),
            )

            s3.upload_file(
                str(chart_path),
                S3_BUCKET,
                f"charts/{symbol}.png",
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
                f"Recommendation: "
                f"{recommendation}"
            )

            print(
                f"Decision Date: "
                f"{latest_market_date}"
            )

            print(
                f"Decision Color: "
                f"{decision['color']}"
            )

            print(
                f"RSI: "
                f"{analysis.get('rsi')}"
            )

            print(
                f"Confidence: "
                f"{analysis.get('confidence')}"
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
                f"Swing Highs: "
                f"{len(swing_highs)}"
            )

            print(
                f"Swing Lows: "
                f"{len(swing_lows)}"
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
        "generated_at": (
            datetime.now(
                timezone.utc
            )
            .isoformat()
            .replace(
                "+00:00",
                "Z",
            )
        ),
        "watchlist_count": len(stocks),
        "processed_count": len(
            dashboard_results
        ),
        "failed_count": len(
            failed_stocks
        ),
        "failed_symbols": failed_stocks,
        "results": dashboard_results,
    }

    dashboard_json = json.dumps(
        dashboard_payload,
        indent=2,
    )

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=(
            "dashboard/"
            "latest-results.json"
        ),
        Body=dashboard_json,
        ContentType="application/json",
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
        TopicArn=SNS_TOPIC_ARN,
        Subject=(
            "AWS Trading Analytics "
            "Bot Run Complete"
        ),
        Message=f"""
Trading Analytics Bot completed a scheduled run.

Stocks attempted: {len(stocks)}
Stocks processed: {len(dashboard_results)}
Stocks failed: {len(failed_stocks)}
Failed symbols: {", ".join(failed_stocks) if failed_stocks else "None"}
Date: {today}

Market data, strategy results, charts, confirmed zones,
peaks, valleys, and BUY/HOLD/SELL decision markers
have been uploaded to Amazon S3.

Check CloudWatch for the complete analysis results.
""".strip(),
    )

    print(
        "SNS completion "
        "notification sent."
    )


if __name__ == "__main__":
    run_collector()