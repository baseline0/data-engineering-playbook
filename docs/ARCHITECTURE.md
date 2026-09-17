# Data Engineering Architecture Principles

This document outlines the core architectural principles behind the Data Engineering Playbook.

---

## Core Principles

### 1. **Simplicity Over Complexity**

Start simple. Add complexity only when needed.

- ✅ Use SQLite before PostgreSQL
- ✅ Use dbt before Airflow
- ✅ Use GitHub Actions before Kubernetes
- ❌ Don't build a data lake if you only have 100 GB of data

**Why**: Complexity is a tax. Every tool, database, and service is operational overhead. Simple systems are easier to debug, maintain, and understand.

---

### 2. **Gradual Graduation**

Build systems that grow with your needs.

**Progression:**
```
SQLite → PostgreSQL → Data Warehouse (Snowflake/BigQuery)
Local dbt → dbt Cloud → Orchestrated pipeline (Airflow/Kestra)
Local Python → GitHub Actions → Cloud scheduler → Event-driven
```

You should be able to outgrow each tool without rewriting your logic.

---

### 3. **Zero Cost When Possible**

Use open-source and free tiers aggressively.

- **Storage**: SQLite (free), S3 (free tier), Parquet (free format)
- **Transformation**: dbt (open-source), Spark (open-source)
- **Orchestration**: GitHub Actions (2000 free min/month)
- **Validation**: Great Expectations (open-source)
- **APIs**: Flask (open-source), local hosting

**Cost Model**: 
- Small team (< 100 GB): $0/month possible
- Growing team (100 GB - 1 TB): $50-200/month
- Enterprise (> 1 TB): $1000+/month, justified by ROI

---

### 4. **Separation of Concerns**

Clear layers with explicit contracts.

**Bronze Layer** (Ingestion)
- Responsibility: Fetch data from source, validate schema, load to storage
- Output: Raw data exactly as received
- No transformations, no business logic
- Immutable (append-only)

**Silver Layer** (Cleaning)
- Responsibility: Clean, standardize, deduplicate
- Output: Conformed, high-quality data
- Generic transformations (type casting, null handling)
- Ready for analysis but not yet aggregated

**Gold Layer** (Business Logic)
- Responsibility: Aggregate, create metrics, apply business rules
- Output: Ready-to-consume datasets
- Domain-specific logic (e.g., "Active Customer")
- Optimized for queries

**Semantic Layer** (Serving)
- Responsibility: Define consistent metrics, serve via APIs
- Output: Metric definitions, REST endpoints
- Single source of truth for key metrics

---

### 5. **Quality as a First-Class Concern**

Data quality is not an afterthought.

```
Ingestion
    ↓ (validate schema)
Bronze
    ↓ (dbt tests)
Silver
    ↓ (Great Expectations)
Gold
    ↓ (API validation)
Consumer
```

**Testing Strategy:**
- **dbt tests**: Generic (not_null, unique, relationships) + specific (business logic)
- **Great Expectations**: Data quality suite with expectations
- **API tests**: Validate endpoints and response formats
- **Integration tests**: Validate end-to-end pipeline

---

### 6. **Version Control Everything**

All logic, tests, and infrastructure definitions live in Git.

```
dbt models       → Git
SQL queries      → Git
Great Expectations → Git
GitHub Actions   → Git
Schemas          → Git
Documentation    → Git
```

**Benefits:**
- Reproducibility: Checkout any date and get that exact state
- Accountability: See who changed what and why
- Review: Pull requests for data changes, not just code
- Rollback: Revert bad changes easily

---

### 7. **Observable & Debuggable**

Build systems that tell you when something is wrong.

**Key Signals:**
- **Row count**: Alert if rows drop unexpectedly
- **Freshness**: Alert if latest data > 1 day old
- **Schema changes**: Alert if unexpected new columns
- **Data patterns**: Alert if distribution shifts (e.g., avg price doubles)
- **Lineage**: Track data through all transformations

---

### 8. **Modularity for Reuse**

Write dbt models, Python functions, and tools that others can reuse.

**Good**: A generic "de-duplicate by key" dbt macro
**Bad**: One-off models that only work for one table

**Pattern**: Seed reusable components in `/tools/` and document usage.

---

## Design Decisions

### Why dbt (Not SQL in Database)

| dbt | Database SQL |
|-----|--------------|
| Modular, composable | Monolithic |
| Version control friendly | Hard to track changes |
| Built-in tests | Manual test writing |
| Portable (works across databases) | Database-specific |
| Community packages | No package ecosystem |

### Why SQLite (Not PostgreSQL)

| SQLite | PostgreSQL |
|--------|------------|
| Zero ops | Requires server management |
| Zero cost | Costs $15-100+/month |
| Single file | Network access needed |
| Good for <100GB | Good for any size |
| Easy local development | Needs Docker/local setup |

**Graduate to PostgreSQL when:** Multiple applications need concurrent access, >100 GB, or transactions are complex.

### Why GitHub Actions (Not Airflow)

| GitHub Actions | Airflow |
|----------------|---------|
| Free (2000 min/month) | Costs $200+/month to host |
| YAML configuration | Python code |
| Integrated with Git | Separate system |
| Suitable for <10 pipelines | Suitable for 100+ pipelines |
| Limited monitoring | Rich observability |

**Graduate to Airflow when:** 50+ data pipelines or complex dependencies.

### Why Great Expectations (Not Custom Tests)

| Great Expectations | Custom Tests |
|-------------------|--------------|
| Out-of-box validations | Must write each test |
| Expectations as living docs | Tests in code only |
| Automatic data docs | No auto-documentation |
| Community standards | Company-specific |
| Built for data quality | General-purpose testing |

---

## Reliability Patterns

### Idempotency

All pipelines must be idempotent: running twice = running once.

```sql
-- Good: INSERT OR REPLACE (upsert)
INSERT OR REPLACE INTO table_name ...

-- Bad: INSERT (fails if run twice)
INSERT INTO table_name ...
```

### Immutable Bronze

Never overwrite raw data. Always append.

```sql
-- Good: Bronze table with loaded_at
CREATE TABLE bronze_events (
    id INTEGER,
    event_data JSON,
    loaded_at TIMESTAMP
);

-- Bad: Updating raw data
UPDATE bronze_events SET ...
```

### Data Lineage

Track transformations explicitly.

```sql
-- dbt ref() creates lineage
SELECT * FROM {{ ref('silver_customers') }}
-- dbt knows: gold_model depends on silver_model
```

### Testing on Transformation

Test logic before publishing.

```yaml
# dbt_project.yml
models:
  gold:
    +columns:
      customer_id:
        +tests:
          - unique
          - not_null
```

---

## Operational Excellence

### Monitoring Priorities

1. **Freshness**: Latest data not stale
2. **Completeness**: Expected row counts present
3. **Validity**: No obvious bad values
4. **Consistency**: Metrics across systems agree

### Alerting Strategy

Alert on:
- ✅ Data pipeline failure
- ✅ Unexpected data distribution change
- ✅ Missing data (0 rows inserted)
- ✅ Schema change (new columns)

Don't alert on:
- ❌ Predicted variations (seasonal dips)
- ❌ Informational metrics

### Documentation Requirements

Minimum documentation:
- What: What does this data represent?
- Why: Why does it exist? What decision does it inform?
- How: How is it calculated? Where does raw data come from?
- When: How often is it updated?
- Who: Who owns it? Who can help debug?

---

## Scaling This Architecture

### Small: <1 TB, <5 pipelines
- ✅ SQLite for everything
- ✅ dbt local
- ✅ GitHub Actions for scheduling
- Cost: ~$0/month

### Medium: 1-10 TB, 10-50 pipelines
- ✅ PostgreSQL or Snowflake for storage
- ✅ dbt Cloud (optional)
- ✅ Airflow for orchestration
- Cost: $500-2000/month

### Large: >10 TB, 50+ pipelines
- ✅ Data Warehouse (Snowflake, BigQuery, Redshift)
- ✅ dbt Cloud with CI/CD
- ✅ Orchestrator (Airflow, Kestra, Prefect)
- ✅ Specialized tools: Feature stores, model serving
- Cost: $5000-50000+/month

**Key insight**: The architecture principles stay the same. Only the tools change.

---

## References

- Ralph Kimball's Dimensional Modeling
- Modern Data Stack philosophy
- dbt Best Practices
- Apache Arrow standards
- Open Data Best Practices
