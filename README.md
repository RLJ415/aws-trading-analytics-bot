# AWS Trading Analytics Bot

A cloud-based stock market analytics pipeline built on AWS.

This project automatically collects live market data using Python, stores it in Amazon S3, catalogs it with AWS Glue, and analyzes it using Amazon Athena and SQL.

The goal is to demonstrate real-world cloud engineering, data engineering, and AWS analytics skills.

---

## Project Architecture

Yahoo Finance
↓
Python Collector
↓
Amazon S3
↓
AWS Glue Data Catalog
↓
Amazon Athena
↓
SQL Analytics

---

## AWS Services Used

- Amazon S3
- AWS IAM
- AWS Glue
- Amazon Athena
- AWS CLI

---

## Technologies

- Python 3.14
- boto3
- yfinance
- Git
- GitHub
- SQL

---

## Current Features

- Collects live Apple (AAPL) stock market data
- Saves data locally as CSV
- Automatically uploads CSV to Amazon S3
- Catalogs data using AWS Glue
- Queries cloud data using Amazon Athena
- Uses SQL to analyze market data

---

## Folder Structure

```
aws-trading-analytics-bot/

├── data/
│   └── local/
│       └── AAPL_5d.csv
│
├── src/
│   └── collectors/
│       └── collector.py
│
├── README.md
└── requirements.txt
```

---

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the collector:

```bash
python src/collectors/collector.py
```

---

## Skills Demonstrated

- Python automation
- AWS cloud storage
- IAM authentication
- AWS CLI
- Data pipelines
- SQL analytics
- Git version control
- Cloud architecture

---

## Current Status

✅ Day 1 Complete

- Live stock data collection
- Local CSV generation

✅ Day 2 Complete

- Amazon S3 integration
- Automatic cloud uploads
- AWS Glue Data Catalog
- Amazon Athena SQL queries

---

## Upcoming Features

- Multiple stock symbols
- Historical market data
- Automated scheduling with AWS Lambda
- EventBridge automation
- CloudWatch monitoring
- Web dashboard
- Trading signals
- Performance analytics

---

## Author

Built by RJ as part of a cloud engineering and AWS portfolio.