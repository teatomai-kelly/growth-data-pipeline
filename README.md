# Growth Data Pipeline

An end-to-end data engineering portfolio project demonstrating ingestion, source validation, business transformations, dimensional modeling, incremental processing, data quality controls, automated testing, and analytics-ready growth metrics.

## Business problem

A subscription business needs a reliable view of customer acquisition, activation, revenue, and retention. Source systems contain customer, order, and marketing-event data that must be standardized and transformed before analysts and business stakeholders can use it confidently.

The project treats the modeled tables as a reusable data layer so downstream reporting does not have to repeatedly rebuild business logic from raw sources.

## Architecture

```text
Synthetic source data
        |
        v
  Ingestion + schema validation
        |
        v
      Staging
        |
        v
Business transformations
        |
   +----+---------+----------------+
   |              |                |
   v              v                v
Dim customer   Fact order     Fact marketing event
   |              |                |
   +--------------+----------------+
                  |
                  v
       Growth metrics + marts
                  |
                  v
        Data quality + tests
                  |
                  v
          Analytics-ready data
                  |
                  v
     Natural-language analytics
             assistant
```

## Tech stack

- Python
- pandas
- SQL
- pytest
- GitHub Actions
- Dimensional modeling
- Watermark-based incremental processing
- OpenAI Responses API (optional AI layer)

The implementation is intentionally lightweight so the engineering patterns remain easy to inspect. The same patterns can be transferred to distributed platforms such as Databricks/Spark.

## Repository structure

```text
growth-data-pipeline/
├── .github/workflows/ci.yml
├── data/
│   ├── raw/
│   │   ├── customers.csv
│   │   ├── orders.csv
│   │   └── marketing_events.csv
│   └── processed/
├── docs/
│   └── data_model.md
├── sql/
│   ├── staging/
│   └── marts/
│       └── daily_growth_metrics.sql
├── src/
│   ├── ai/
│   │   └── data_assistant.py
│   ├── ingestion/
│   │   ├── incremental.py
│   │   └── load_sources.py
│   ├── models/
│   │   ├── customer.py
│   │   ├── growth.py
│   │   ├── marketing_event.py
│   │   └── order.py
│   ├── quality/
│   │   └── checks.py
│   ├── transformations/
│   │   ├── growth_metrics.py
│   │   └── staging.py
│   └── run_pipeline.py
├── tests/
├── .gitignore
└── requirements.txt
```

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m src.run_pipeline
```

The pipeline writes modeled outputs to `data/processed/`.

## Natural-language analytics assistant

The project includes an optional AI layer for business questions. The assistant uses an LLM to classify a natural-language question into a **constrained analytics intent**, then executes that intent with deterministic Python logic against trusted modeled data.

Example questions:

- "Which acquisition channel generated the most revenue?"
- "How many customers came from referrals?"
- "What is the activation rate by acquisition channel?"
- "What is the repeat-purchase rate by signup month?"

The model is **not** allowed to generate arbitrary SQL or execute arbitrary code. Its output is restricted to an approved metric/grouping schema, and the application performs the actual calculation. This separation keeps the AI layer flexible while preserving control over business logic and data access.

To enable the assistant, set an API key in the environment:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

The implementation uses the OpenAI Responses API and structured output to produce the constrained intent. The API key is never stored in the repository.

## Engineering practices demonstrated

### Data ingestion and validation

Source files are loaded through a common ingestion layer that checks required columns before transformations begin.

### Business-ready data modeling

The project separates source cleanup from business logic and defines explicit grains for dimensions and facts:

- `dim_customer`: one row per customer
- `fct_order`: one row per order
- `fct_marketing_event`: one row per marketing event
- `mart_daily_growth`: one row per calendar date

### Data quality

Reusable checks cover required fields, uniqueness of keys, non-negative numeric measures, and referential consistency between marketing events and customers.

### Incremental processing

A reusable watermark utility demonstrates how a pipeline can process only records newer than the last successful processing boundary while retaining a full-load path for initial ingestion.

### Automated testing

Pytest validates model grains, revenue business logic, referential integrity, growth metrics, and incremental filtering. GitHub Actions runs the test suite on pushes and pull requests to `main`.

### Stakeholder-oriented analytics

The growth models turn raw operational records into reusable metrics such as revenue by acquisition channel, activation rate, and repeat-purchase behavior. The explicit metric layer is intended to keep business definitions centralized rather than duplicated across reports.

## Key metrics

- New customers
- Activation rate
- Completed orders
- Gross revenue
- Average order value
- Revenue by acquisition channel
- Customer conversion rate
- Repeat-purchase rate

## Assumptions and business logic

- Only `completed` orders contribute to recognized revenue.
- Cancelled and refunded orders remain available for operational analysis but contribute zero recognized revenue in the growth mart.
- Activation rate is calculated as activated customers divided by new customers for the same date; division by zero returns null.
- Modeled tables preserve source identifiers so records can be traced back to their originating dataset.

## Portfolio focus

This project is designed to demonstrate practical data-engineering and analytics-engineering skills: translating business requirements into reusable data structures, defining explicit business logic, building quality controls, documenting data models, delivering trusted datasets for downstream analysis, and creating a controlled natural-language interface for business questions.

All source data is synthetic and contains no employer or proprietary information.
