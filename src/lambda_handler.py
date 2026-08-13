import json

from src.collectors.collector import run_collector


def lambda_handler(event, context):
    print("Trading Analytics Bot Lambda started.")

    run_collector()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Trading Analytics Bot run completed."
        })
    }