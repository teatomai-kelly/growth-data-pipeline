# Growth Data Pipeline

An end-to-end analytics engineering project demonstrating data ingestion, transformation, dimensional modeling, data quality checks, and analytics-ready growth metrics.

## Business problem

A subscription business needs a reliable view of customer acquisition, activation, retention, revenue, and marketing performance. Source systems contain customer, order, and marketing-event data that must be standardized before analysts can use it confidently.

## Pipeline

```text
Raw CSV sources
    |
    v
Ingestion / validation
    |
    v
Staging models
    |
    v
Business transformations
    |
    +--> Customer dimension
    +--> Order fact
    +--> Daily growth metrics
    |
    v
Data quality checks
    |
    v
Analytics-ready outputs
```

## Tech stack

- Python
- pandas
- SQL
- pytest
- Git/GitHub
- Dimensional modeling concepts

## Repository structure

```text
growth-data-pipeline/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   └── data_model.md
├── sql/
│   ├── staging/
│   └── marts/
├── src/
│   ├── ingestion/
│   ├── models/
│   ├── quality/
│   └── transformations/
├── tests/
├── .gitignore
└── requirements.txt
```

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

The project intentionally uses synthetic data so the repository is safe to publish publicly.

## Key metrics

- New customers
- Activation rate
- Orders
- Gross revenue
- Average order value
- Repeat-purchase rate
- Revenue by acquisition channel

## Portfolio focus

This project is designed to show practical data-engineering and analytics-engineering skills: reusable transformations, explicit business logic, validation, test coverage, documented models, and a clear path from source data to stakeholder-facing metrics.
