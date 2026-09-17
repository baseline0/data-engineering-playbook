# Medallion Architecture Template

## Overview

The medallion (or lakehouse) architecture organizes data into three layers:

1. **Bronze Layer** — Raw, unprocessed data exactly as ingested
2. **Silver Layer** — Cleaned, deduplicated, conformed data
3. **Gold Layer** — Aggregated, business-ready datasets and metrics

This template shows how to implement medallion architecture using:
- **Ingestion**: Python scripts (free)
- **Storage**: SQLite or Parquet files (free)
- **Transformation**: dbt (free)
- **Testing**: Great Expectations (free)

---

## When to Use This Pattern

✅ **Use medallion when:**
- You're building a modern data platform
- You need data quality controls
- You want transformation logic versioned in Git
- You need to scale from small to medium datasets
- You want clear data lineage

❌ **Don't use when:**
- You only have a single small dataset
- No transformation needed
- Using a simple CSV → Dashboard pipeline

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                             │
│         (APIs, databases, files, streaming)                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼ (Python ingestion script)
┌──────────────────────────────────────────────────────────────┐
│                  BRONZE LAYER                                │
│     Raw data, minimal processing, immutable history          │
│     Schema: source_name, table_name, raw_data, loaded_at    │
│     Storage: SQLite tables or Parquet files                  │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼ (dbt: bronze_to_silver models)
┌──────────────────────────────────────────────────────────────┐
│                  SILVER LAYER                                │
│     Cleaned, deduplicated, standardized                       │
│     • Cast types, fill nulls, remove duplicates              │
│     • Add metadata (processing_date, record_id)              │
│     • Conform column names and formats                       │
│     Validations: Great Expectations tests                    │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼ (dbt: silver_to_gold models)
┌──────────────────────────────────────────────────────────────┐
│                   GOLD LAYER                                 │
│     Aggregated, business-ready, metric definitions           │
│     • Customer/product/time aggregations                     │
│     • Business KPIs and metrics                              │
│     • Conformed dimensions and facts                         │
│     Output: Ready for BI, ML, APIs                           │
└──────────────────┬───────────────────────────────────────────┘
                   │
          ┌────────┴────────┬──────────────┐
          ▼                 ▼              ▼
      Dashboards       ML Models    Business APIs
    (Metabase,       (MLflow,     (REST, GraphQL)
     Grafana)        Scikit-learn)
```

---

## Implementation Steps

### 1. Set Up Directory Structure

```
my_data_platform/
├── data/
│   ├── bronze/          # Raw data (SQLite or Parquet)
│   ├── silver/          # Cleaned data
│   └── gold/            # Business datasets
├── scripts/
│   ├── ingest.py        # Fetch from sources
│   └── validate.py      # Quality checks
├── dbt/
│   ├── models/
│   │   ├── bronze/      # Bronze tables (stg_ prefix)
│   │   ├── silver/      # Silver models (cleaned)
│   │   └── gold/        # Gold tables (aggregated)
│   ├── tests/           # dbt unit + data tests
│   ├── dbt_project.yml
│   └── profiles.yml
├── expectations/
│   └── suites/          # Great Expectations test suites
├── sql/
│   └── queries/         # Hand-written SQL queries
├── .github/
│   └── workflows/       # GitHub Actions CI/CD
└── README.md
```

### 2. Bronze Layer — Ingestion

```python
# scripts/ingest.py
import sqlite3
import requests
from datetime import datetime

def ingest_from_api(source_url, table_name):
    """Fetch data from API and load to bronze"""
    response = requests.get(source_url)
    data = response.json()
    
    conn = sqlite3.connect('data/bronze/raw.db')
    cursor = conn.cursor()
    
    # Create bronze table (schema: source, table, data_json, loaded_at)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            source_system TEXT,
            raw_data TEXT,
            loaded_at TIMESTAMP
        )
    """)
    
    for record in data:
        cursor.execute(f"""
            INSERT INTO {table_name} (source_system, raw_data, loaded_at)
            VALUES (?, ?, ?)
        """, (source_url, json.dumps(record), datetime.now()))
    
    conn.commit()
    conn.close()
```

### 3. Silver Layer — Transformation (dbt)

```sql
-- dbt/models/silver/stg_customers.sql
-- Purpose: Clean and standardize customer data from bronze

with source as (
    select
        json_extract(raw_data, '$.id') as customer_id,
        json_extract(raw_data, '$.name') as customer_name,
        json_extract(raw_data, '$.email') as email,
        loaded_at
    from {{ source('bronze', 'customers') }}
)

, cleaned as (
    select
        customer_id,
        trim(upper(customer_name)) as customer_name,
        lower(trim(email)) as email,
        current_timestamp as processing_date
    from source
    where customer_id is not null
)

select distinct * from cleaned
```

### 4. Gold Layer — Business Datasets

```sql
-- dbt/models/gold/fact_customers.sql
-- Purpose: Customer metrics and dimensions

select
    customer_id,
    customer_name,
    email,
    case
        when email like '%@company.com' then 'internal'
        else 'external'
    end as customer_type,
    processing_date
from {{ ref('stg_customers') }}
where processing_date = current_date
```

### 5. Data Validation (Great Expectations)

```python
# expectations/suites/silver_customers.py
import great_expectations as gx

context = gx.get_context()

suite = context.create_expectation_suite("silver_customers")
validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name=suite.name
)

# customer_id must be unique
validator.expect_primary_key(column_set=['customer_id'])

# email must be valid format
validator.expect_column_values_to_match_regex(
    column='email',
    regex=r'^[\w\.-]+@[\w\.-]+\.\w+$'
)

# No nulls in required fields
validator.expect_column_values_to_not_be_null(column='customer_id')
validator.expect_column_values_to_not_be_null(column='email')

# Save suite
validator.save_expectation_suite(discard_failed_expectations=False)
```

### 6. CI/CD (GitHub Actions)

```yaml
# .github/workflows/medallion_pipeline.yml
name: Medallion Data Pipeline

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  medallion:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          cd dbt && dbt deps
      
      - name: Run ingestion
        run: python scripts/ingest.py
      
      - name: Run dbt
        run: cd dbt && dbt run
      
      - name: Run validations
        run: |
          cd dbt && dbt test
          python scripts/validate.py
      
      - name: Commit results
        run: |
          git config user.name "Data Pipeline"
          git add data/
          git commit -m "Automated: Daily medallion pipeline run"
          git push
```

---

## Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| Storage (SQLite, local) | $0 | File-based, no ops |
| Storage (S3, 100GB) | $2.50 | If using AWS |
| Compute (dbt local) | $0 | Runs on your machine |
| Compute (GitHub Actions) | $0 | 2000 free min/month |
| Great Expectations | $0 | Open-source |
| **Total** | **~$0-3** | Per month for typical usage |

---

## Trade-offs

| Pro | Con |
|-----|-----|
| Zero cost infrastructure | Limited to <100GB on single machine |
| Full version control of logic | Need to manage dbt dependencies |
| Simple to understand | No built-in scaling |
| Works with any DB | Requires manual GitHub Actions setup |
| Great data quality | Manual orchestration if no cloud scheduler |

---

## Graduation Path

When you outgrow this pattern:

1. **Storage**: SQLite → Postgres → Snowflake/BigQuery
2. **Transformation**: dbt local → dbt Cloud → Databricks
3. **Orchestration**: GitHub Actions → Airflow → Kestra
4. **Monitoring**: Great Expectations → DataHub → Collibra

The medallion pattern remains the same; only the infrastructure changes.

---

## Example Queries

### Query Bronze (Raw Data)
```sql
select * from bronze.raw_customers limit 10
```

### Query Silver (Cleaned)
```sql
select customer_id, customer_name from silver.stg_customers
```

### Query Gold (Metrics)
```sql
select 
    customer_type,
    count(*) as customer_count
from gold.fact_customers
group by customer_type
```

---

## Next Steps

1. **Copy this template** to your project
2. **Adapt ingestion script** to your data source
3. **Write dbt models** for your Silver/Gold layers
4. **Add Great Expectations tests** for quality
5. **Deploy via GitHub Actions** for automation

See the [Manitoba Climate case study](../../case_studies/manitoba_climate/) for a complete working example.
