# Data Engineering Playbook
## How to Build Enterprise Data Systems Without Enterprise Budgets

A practical, open-source guide to modern data engineering using free and low-cost tools. Reference implementations using Canadian public data.

**Target Audience**: Data engineers, analytics engineers, platform teams building data systems on budget constraints.

---

## 🎯 Core Principle

You don't need Databricks, Snowflake, or expensive data platforms to build world-class data architecture. This playbook shows how to implement enterprise patterns using:

- **dbt** (free, open-source transformation)
- **Spark** (free, open-source compute)
- **GitHub Actions** (free CI/CD)
- **SQLite/Parquet** (free storage, zero hosting)
- **Great Expectations** (free data validation)
- **MLflow** (free ML tracking)

**Result**: Systems that scale to production, with governance, quality, and observability—at ~1% of Snowflake's cost.

---

## 📁 What's Inside

### 1. **templates/** — Copy-Paste Reference Implementations

Start here to build your own system. Each template includes:
- Architecture diagram
- Code examples
- Cost breakdown
- Trade-offs documented

**Available Templates:**
- `medallion_architecture/` — Bronze/Silver/Gold layered data lakes
- `semantic_layer/` — Centralized metric definitions (dbt approach)
- `data_governance/` — Policies, RBAC, lineage tracking
- `data_validation/` — Quality gates, schema management
- `ci_cd_pipeline/` — Automated testing and deployment

### 2. **case_studies/** — Real Examples

Working examples using public Canadian datasets:

**Quantum Computing Investment Intelligence** (`quantum_investing/`)
- Ingest: Company data, funding rounds, research events (placeholder for real data sources)
- Transform: dbt medallion architecture (Bronze → Silver → Gold)
- Validate: Data quality checks and Great Expectations
- Serve: FastAPI REST endpoints with auto-generated docs
- Deploy: GitHub Actions scheduled jobs
- **Cost**: ~$0/month

### 3. **docs/** — Decision Guides

- `ARCHITECTURE.md` — Design principles and patterns
- `TECHNOLOGY_CHOICES.md` — Why dbt, SQLite, GitHub Actions, etc.
- `GOVERNANCE_FRAMEWORK.md` — Policy templates and audit trails
- `COST_BREAKDOWN.md` — Real cost comparisons

---

## 🚀 Quick Start

### Run the Case Study (5 minutes)
```bash
cd case_studies/manitoba_climate
cat README.md          # Understand the pattern
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/fetch_data.py      # Download public weather data
dbt run                           # Transform to Silver/Gold
great_expectations suite run      # Validate
python api/serve.py               # Start local API
curl http://localhost:5000/api/metrics
```

### Copy a Template
```bash
cp -r templates/medallion_architecture my_project
cd my_project
cat README.md
# Adapt to your data source
```

---

## 📊 Cost Comparison

| Component | This Playbook | Snowflake | BigQuery | Databricks |
|-----------|---------------|-----------|----------|-----------|
| Storage | $0 (SQLite) | $40/TB | $6.25/TB | $0.40/DPU |
| Compute | $0 (local) | Included | $6.25/query | $0.30-1.00/hour |
| Transformation | $0 (dbt) | SQL | SQL | SQL/Spark |
| ML Tracking | $0 (MLflow) | Extra | Extra | Mosaic AI |
| **Monthly (typical)** | **~$0** | **$1,000-5,000** | **$500-2,000** | **$2,000+** |

---

## 🏗️ Architecture

```
Data Sources (public APIs, CSVs, databases)
           ↓
   Ingestion Layer (Python, free)
           ↓
   Bronze Layer (raw, SQLite/Parquet)
           ↓
   dbt Transformation (free)
           ↓
   Silver Layer (cleaned, deduplicated)
           ↓
   Gold Layer (aggregated, business metrics)
           ↓
   Semantic Layer (dbt, REST APIs)
           ↓
   Dashboards, ML Models, Business Apps
```

---

## 💡 Why These Choices?

**dbt**: Modular, testable, version-controlled SQL transformations. Works with any database.

**SQLite**: Zero ops, zero cost, single file, good for <100GB. Graduate to Postgres/Snowflake when needed.

**GitHub Actions**: Free CI/CD, version controlled workflows, runs scheduled jobs.

**Great Expectations**: Data quality validation, prevents bad data from entering production.

**MLflow**: Track experiments, models, lineage. Free and open-source.

---

## 🤝 Contributing

We welcome:
- New templates for common patterns
- Case studies from other Canadian domains
- Improvements to docs
- Tools that solve real problems

See `CONTRIBUTING.md` for guidelines.

---

## 📝 License

MIT License — Use freely, modify, contribute back.

---

## 🚀 Next Steps

1. **Explore templates/** → Understand the patterns
2. **Run case_studies/manitoba_climate/** → See it work
3. **Read docs/** → Understand the "why"
4. **Build your system** → Adapt templates
5. **Share** → Contribute back

**Built by data engineers, for data engineers. No corporate agenda. Free forever.**
