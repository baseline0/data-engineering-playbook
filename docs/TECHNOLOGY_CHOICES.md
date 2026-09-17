# Technology Choices: Why These Tools?

This playbook advocates for specific technologies. Here's why.

---

## The Philosophy

**Maximize value. Minimize cost. Minimize complexity.**

We chose tools that:
1. Are **free or very cheap** at small scale
2. **Integrate well** together
3. Have **vibrant communities**
4. Allow **graduation** to larger systems without rewrite
5. Are **open-source** (no vendor lock-in)

---

## Storage: SQLite (Small), PostgreSQL (Medium), Data Warehouse (Large)

### SQLite (Default for Small Projects)

**What it is**: A file-based SQL database included with Python.

**Why SQLite:**
- ✅ Zero setup, zero cost
- ✅ Single file (portable, easy to backup)
- ✅ Full SQL support
- ✅ ACID transactions
- ✅ Suitable for <100 GB
- ❌ Single-writer limitation
- ❌ No network access

**When to use**: Local development, small datasets, internal dashboards.

**Cost**: $0/month

---

### PostgreSQL (Medium Projects)

**What it is**: A powerful, open-source relational database.

**Why PostgreSQL:**
- ✅ Free and open-source
- ✅ Advanced features (JSON, arrays, window functions)
- ✅ Multi-user, multi-writer
- ✅ Excellent performance
- ✅ Great community
- ❌ Requires server management
- ❌ More complex than SQLite

**When to use**: Multiple applications, >100 GB, transaction guarantees needed.

**Cost**: $15-100+/month (self-hosted or managed service)

---

### Data Warehouse (Snowflake, BigQuery, Redshift)

**What it is**: Massively parallel analytic databases optimized for aggregations.

**Trade-off:**
- ✅ Unlimited scale, speed, analytics
- ✅ Built-in ML, time-series, geospatial
- ❌ Expensive ($1000+/month)
- ❌ Vendor lock-in

**When to use**: >1 TB data, hundreds of concurrent users, analytical queries dominate.

**Recommendation**: Start with PostgreSQL. Migrate when it becomes a bottleneck (6-12 months for typical growth).

---

## Transformation: dbt (SQL-First)

**What it is**: A framework that turns SQL into a software engineering practice.

**Why dbt:**
- ✅ Transforms SQL into modular, reusable components
- ✅ Version-controlled transformation logic
- ✅ Built-in testing and documentation
- ✅ Works with any database (SQLite, Postgres, Snowflake, BigQuery, etc.)
- ✅ Large ecosystem of packages
- ✅ Free and open-source
- ❌ Steeper learning curve than raw SQL
- ❌ Best for SQL workloads (not Spark/Python)

**Comparison:**

| dbt | Airflow | Spark |
|-----|---------|-------|
| SQL-first | Python-first | Distributed compute |
| Easy to learn | Complex | Hard to learn |
| Good for <100 pipelines | Good for 100+ pipelines | Good for large data |
| Data lineage built-in | Manual lineage | Manual lineage |
| Free | Must host ($200+) | Must host |

**When to use**: Almost always, unless you need distributed computing or heavy Python logic.

**Cost**: $0/month (open-source) or $1000+/month (dbt Cloud)

---

## Validation: Great Expectations

**What it is**: A framework for continuous data quality validation.

**Why Great Expectations:**
- ✅ Declarative, reusable expectations
- ✅ Automatic data docs and reports
- ✅ Actionable failures (not just "validation failed")
- ✅ Open-source and free
- ✅ Python-based (integrates with dbt, Pandas, Spark)
- ❌ Setup takes time

**Example:**
```python
validator.expect_column_values_to_not_be_null('email')
validator.expect_column_values_to_match_regex('email', r'^[\w\.-]+@[\w\.-]+$')
validator.expect_table_row_count_to_be_between(min_value=1000, max_value=1000000)
```

**Comparison:**

| Great Expectations | dbt Tests | Custom Assertions |
|-------------------|-----------|------------------|
| Data quality focused | SQL/dbt focused | Flexible |
| Rich documentation | Minimal output | No docs |
| Community standards | Opinionated | All custom |
| Easy to extend | Limited extensibility | Maximum flexibility |

**When to use**: After dbt (in the pipeline). Validates transformed data quality.

**Cost**: $0/month

---

## Orchestration: GitHub Actions (Small), Airflow (Large)

### GitHub Actions (Default for Small Projects)

**What it is**: GitHub's built-in workflow automation, free for public repos.

**Why GitHub Actions:**
- ✅ 2000 free minutes/month
- ✅ YAML workflows live in Git
- ✅ Seamless Git integration
- ✅ Perfect for 1-10 pipelines
- ❌ Limited to 6-hour job timeout
- ❌ Poor UI for complex DAGs

**Example:**
```yaml
name: Daily Pipeline
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily

jobs:
  pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: python scripts/ingest.py
      - run: dbt run
      - run: dbt test
```

**Cost**: $0/month (for public repos)

---

### Apache Airflow (Large Projects)

**What it is**: A workflow orchestration platform with DAG visualization.

**Why Airflow:**
- ✅ Complex dependency management
- ✅ Beautiful UI for DAGs
- ✅ Rich monitoring and alerting
- ✅ Mature ecosystem
- ✅ Self-hosted (no vendor lock-in)
- ❌ Complex to operate ($200+/month to host)
- ❌ Steep learning curve
- ❌ Usually overkill for <50 pipelines

**When to use**: 50+ pipelines, complex dependencies, need self-hosted orchestration.

**Cost**: $200-1000+/month (self-hosted on cloud)

---

## APIs: FastAPI (Default), Flask (Legacy)

### FastAPI (Recommended)

**What it is**: A modern, async Python web framework with automatic documentation.

**Why FastAPI:**
- ✅ Async by default (better concurrency)
- ✅ Automatic interactive API docs (Swagger + ReDoc)
- ✅ Type hints built-in (using Pydantic)
- ✅ Fast performance (as fast as Node.js)
- ✅ Free and open-source
- ✅ Python 3.7+
- ✅ Validates request/response automatically

**Example:**
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Metric(BaseModel):
    temperature: float
    humidity: int

@app.get("/api/metrics", response_model=Metric)
async def get_metrics():
    return Metric(temperature=25.3, humidity=65)

# Auto-generated docs at: /docs (Swagger) or /redoc (ReDoc)
```

**Cost**: $0/month (host locally, or free tier on Railway/Render)

---

### Flask (Legacy)

**What it is**: A lightweight Python web framework (established).

**Comparison:**
| FastAPI | Flask |
|---------|-------|
| Modern, async | Simpler, synchronous |
| Auto-docs | Manual docs |
| Faster | Good enough |
| Type hints | Dict-based |

**When to use Flask**: Existing projects, need minimal dependencies.

**Cost**: Same as FastAPI

---

### Uvicorn (ASGI Server)

**What it is**: High-performance ASGI web server (powers FastAPI).

**Why Uvicorn:**
- ✅ Fast (async)
- ✅ Production-ready
- ✅ Easy to deploy
- ✅ Free and open-source

**Usage:**
```bash
pip install fastapi uvicorn
uvicorn main:app --reload  # Development
uvicorn main:app --host 0.0.0.0 --port 8000  # Production
```

---

## Monitoring: Great Expectations + Simple Alerts

**What it is**: Data quality monitoring combined with simple alerting.

**Setup:**
```python
# Run validations after each pipeline
expectations.run()

# Alert if failures
if expectations.failed:
    send_slack_alert(f"Data quality check failed: {expectations.failures}")
```

**When to add more:**
- 50+ metrics → Monitoring dashboard (Grafana)
- 100+ pipelines → Observability platform (DataHub, OpenMetadata)
- High-SLA requirements → Incident management (PagerDuty)

---

## Summary: The Stack

**Tier 1 (Essential)**
- Storage: SQLite (graduate to PostgreSQL when needed)
- Transformation: dbt
- Validation: Great Expectations
- Orchestration: GitHub Actions
- APIs: Flask
- **Cost**: $0/month

**Tier 2 (As You Grow)**
- PostgreSQL instead of SQLite
- dbt Cloud (CI/CD)
- More sophisticated alerting
- **Cost**: $100-500/month

**Tier 3 (Enterprise)**
- Data Warehouse (Snowflake)
- Airflow for orchestration
- Observability platform
- ML serving infrastructure
- **Cost**: $5000+/month

---

## Graduation Paths

**Storage**
```
SQLite (free) → PostgreSQL ($50) → Snowflake ($1000+)
```

**Transformation**
```
dbt local (free) → dbt Cloud ($1000) → Databricks (expensive)
```

**Orchestration**
```
GitHub Actions (free) → Airflow ($500) → Cloud Composer ($1000+)
```

**Monitoring**
```
Great Expectations (free) → DataHub ($1000+) → Databand (expensive)
```

---

## What We Don't Use

### Kafka (for now)
- **Why**: Overkill for <100 TB scale
- **When to add**: Real-time requirements, streaming sources
- **Cost**: $500+/month

### Spark (for now)
- **Why**: dbt handles most transformations
- **When to add**: Distributed computing needed, unstructured data
- **Cost**: $300+/month (cluster) + engineering overhead

### Airflow (initially)
- **Why**: GitHub Actions sufficient for small pipelines
- **When to add**: 50+ pipelines or complex DAGs
- **Cost**: $500+/month

### Machine Learning Platforms
- **Why**: Most work starts with simpler models
- **When to add**: A/B testing, real-time serving, model ops
- **Cost**: $1000+/month

---

## The Bottom Line

**Start small, stay simple, graduate when needed.**

The best tech stack is the one you understand and can maintain. This playbook chooses boring, well-established tools that scale from $0 to millions in cost and complexity.
