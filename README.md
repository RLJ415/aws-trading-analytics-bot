# AWS Trading Analytics Bot

A cloud-based stock market analytics project built on AWS.

This project automatically collects historical market data, stores it in Amazon S3, catalogs it with AWS Glue, queries it with Amazon Athena, and evaluates trading opportunities using a custom Hybrid Trading Strategy built in Python.

The primary goal of this project is to demonstrate practical Cloud Engineering, Data Engineering, Python automation, SQL analytics, and AWS architecture skills while building a real trading analytics pipeline.

---

# Project Architecture

```
Yahoo Finance
        │
        ▼
Python Data Collector
        │
        ▼
Amazon S3
        │
        ▼
AWS Glue Data Catalog
        │
        ▼
Amazon Athena
        │
        ▼
SQL Analytics
        │
        ▼
Hybrid Trading Strategy
        │
        ▼
BUY / HOLD / SELL Recommendation
```

---

# AWS Services Used

- Amazon S3
- AWS IAM
- AWS Glue Data Catalog
- Amazon Athena
- Amazon SNS
- AWS Lambda
- Amazon EventBridge Scheduler
- Amazon CloudWatch
- AWS CLI

*Amazon QuickSight will be integrated after the AWS account setup issue is resolved.*

---

# Technologies

- Python 3.14
- boto3
- yfinance
- SQL
- Git
- GitHub

---

# Current Features

- Collects one year of historical market data
- Supports a 100-stock watchlist
- Saves market data locally as CSV files
- Automatically uploads CSV files to Amazon S3
- Generates technical analysis charts
- Automatically uploads chart images to Amazon S3
- Catalogs cloud data with AWS Glue
- Queries cloud data using Amazon Athena
- Calculates Relative Strength Index (RSI)
- Detects Support and Resistance zones
- Evaluates a Hybrid Trading Strategy
- Produces BUY, HOLD, and SELL recommendations
- Generates confidence scores
- Explains every trading decision

---

# Folder Structure

```text
aws-trading-analytics-bot/

├── data/
│   └── local/
│
├── src/
│   ├── analysis/
│   ├── collectors/
│   ├── strategies/
│   └── utils/
│
├── docs/
│
├── tests/
│
├── README.md
└── requirements.txt
```

---

# How to Run

Install dependencies

```bash
pip install -r requirements.txt
```

Run the trading bot

```bash
python src/collectors/collector.py
```

---

# Skills Demonstrated

- Python Automation
- AWS Cloud Storage
- IAM Security
- AWS CLI
- Data Pipelines
- SQL Analytics
- Market Data Processing
- Algorithm Design
- Git Version Control
- Cloud Architecture

---

# Project Status

## ✅ Day 1 Complete

- Built the project structure
- Created the market data collector
- Saved market data locally
- Verified Python environment

---

## ✅ Day 2 Complete

- Connected Amazon S3
- Automated cloud uploads
- Integrated AWS Glue
- Connected Amazon Athena
- Built the initial cloud analytics pipeline

---

## ✅ Day 3 Complete

- Expanded the watchlist to 100 stocks
- Built an RSI analysis engine
- Built a Support and Resistance engine
- Built the first Hybrid Trading Strategy
- Added confidence scoring
- Added reward-to-risk calculations
- Added recommendation reasoning
- Added "Why Not" diagnostics
- Tested against the complete 100-stock watchlist
- Verified the complete pipeline from data collection through trade analysis

---

# Current Trading Strategy

The Hybrid Strategy currently evaluates:

- Relative Strength Index (RSI)
- Support zones
- Resistance zones
- Current price location
- Bounce confirmation
- Rejection confirmation
- Reward-to-risk ratio
- Confidence score

Current recommendations:

- BUY
- HOLD
- SELL

---

# Lessons Learned

Testing against a 100-stock watchlist confirmed that the Hybrid Strategy is functioning correctly.

The primary area for improvement is the Support and Resistance engine. The next development phase will improve zone selection by:

- Using one year of historical market data
- Selecting the nearest valid support below the current price
- Selecting the nearest valid resistance above the current price
- Improving diagnostic reporting
- Adding chart snapshots for visual validation

---

# Roadmap

### Day 4

- Increase historical data window to one year ✅
- Improve Support and Resistance detection ✅
- Improve nearest zone selection ✅
- Generate technical analysis charts ✅
- Upload chart images to Amazon S3 ✅
- Configure Amazon SNS ✅
- Create AWS Lambda function ✅
- Create EventBridge Scheduler ✅
- Configure Lambda environment variables ✅
- Prepare cloud automation infrastructure ✅

## Future

- Deploy the complete trading bot to AWS Lambda
- Connect Scheduler to the production trading bot
- Resolve Amazon QuickSight account setup
- Build the QuickSight analytics dashboard
- Backtesting engine
- Paper trading
- Performance dashboard enhancements
- Trading reports
- Risk management improvements

---

# Author

Built by RJ as part of a Cloud Engineering, AWS, and Data Analytics portfolio.