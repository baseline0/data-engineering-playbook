# Case Study: Quantum Computing Investment Intelligence Platform

## Overview

A data platform for tracking and analyzing quantum computing companies, breakthroughs, investments, and market developments.

**What you'll build:**
- Automated data ingestion from multiple sources (company data, research, funding)
- Multi-layer data transformation (Bronze → Silver → Gold)
- Investment-focused metrics and dashboards
- REST API for portfolio analysis
- GitHub Actions scheduled updates

**Cost**: ~$0/month  
**Data**: Quantum computing companies, public datasets, research metadata  
**Time to deploy**: 30 minutes

**Status**: Working foundation with placeholders for domain-specific data sources

---

## Architecture

```
Data Sources (tickers, funding data, research)
         ↓
Python ingestion script (normalize + load)
         ↓
Bronze Layer (raw, as-received data)
         ↓
dbt transformations
         ↓
Silver Layer (cleaned, conformed)
         ↓
dbt aggregations
         ↓
Gold Layer (investment metrics ready)
         ↓
REST API + Analytics
```

---

## Quick Start (5 minutes)

### Prerequisites
- Python 3.9+
- Just (justfile runner)

### 1. Setup
```bash
just setup
```

### 2. Run Pipeline
```bash
just run-case-study
```

This will:
- Fetch/generate quantum company data
- Transform through medallion layers
- Validate data quality
- Generate investment metrics

### 3. Start API
```bash
just dev-api
```

Then visit:
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Data Model (Placeholder Structure)

### Bronze Layer (Raw Data)
```
companies
├── ticker
├── name
├── founded_date
├── industry_focus  (e.g., "quantum_computing")
├── stage           (e.g., "series_b", "public")
└── raw_metadata    (JSON for future expansion)

funding_rounds
├── company_id
├── round_date
├── amount_usd
├── round_type      (series_a, b, c, ipo, etc)
└── investors

research_events
├── date
├── company_id
├── event_type      (breakthrough, patent, partnership)
├── description
└── source
```

### Silver Layer (Cleaned)
```
companies_clean
├── company_id
├── ticker_symbol
├── company_name
├── founding_year
├── industry_segment
├── current_stage
├── headquarters_country
└── last_updated
```

### Gold Layer (Investment Ready)
```
company_metrics
├── company_id
├── total_funding_usd
├── num_funding_rounds
├── avg_round_size
├── time_since_founding
├── recent_breakthroughs_count
├── investor_diversity_score
└── investment_risk_score (placeholder)

funding_timeline
├── company_id
├── fiscal_year
├── total_raised
├── num_rounds
├── runway_est (calculated)

market_insights
├── date
├── total_companies
├── active_startups
├── total_capital_deployed
├── average_funding_round
```

---

## File Structure

```
quantum_investing/
├── README.md                      # This file
├── requirements.txt               # Dependencies
│
├── scripts/
│   ├── fetch_companies.py         # [TODO] Fetch company data
│   ├── fetch_funding.py           # [TODO] Fetch funding data
│   └── validate_data.py           # Data quality checks
│
├── dbt/
│   ├── models/
│   │   ├── bronze/
│   │   │   ├── stg_companies.sql
│   │   │   └── stg_funding.sql
│   │   ├── silver/
│   │   │   └── companies_clean.sql
│   │   └── gold/
│   │       ├── company_metrics.sql
│   │       └── funding_timeline.sql
│   ├── tests/
│   └── dbt_project.yml
│
├── api/
│   └── serve.py                   # FastAPI server
│
└── data/
    ├── bronze/
    │   └── quantum.db
    ├── silver/
    └── gold/
```

---

## Data Sources (To Be Integrated)

### Current (Placeholder)
- Generated synthetic data for demo purposes

### To Add
- [ ] **Company data**: Crunchbase API (startup profiles)
- [ ] **Public companies**: Yahoo Finance, SEC filings
- [ ] **Funding data**: PitchBook, AngelList (if accessible)
- [ ] **Research**: ArXiv (quantum computing papers), patents
- [ ] **News**: RSS feeds, news APIs for quantum breakthroughs
- [ ] **Social**: GitHub activity for quantum projects

---

## API Endpoints

### Base Information
```bash
GET /                    # API overview
GET /health             # Health check
```

### Company Data
```bash
GET /api/companies      # List companies
GET /api/companies/{id} # Company details
GET /api/companies/search?query=...  # Search companies
```

### Funding Data
```bash
GET /api/funding        # Funding rounds
GET /api/funding/{company_id}       # Funding for specific company
```

### Investment Metrics
```bash
GET /api/metrics        # Company investment metrics
GET /api/metrics/{company_id}       # Specific company metrics
GET /api/market-summary # Overall market statistics
```

### Analysis Endpoints
```bash
GET /api/risk-analysis  # Investment risk scores
GET /api/timeline       # Funding timeline analysis
```

---

## Example Queries (Once Data Sources Integrated)

```python
# All quantum computing companies by funding
SELECT company_name, total_funding_usd 
FROM company_metrics 
ORDER BY total_funding_usd DESC

# Recent breakthroughs
SELECT company_name, event_type, date
FROM research_events
WHERE date > DATE('now', '-30 days')
ORDER BY date DESC

# Series A to B transitions
SELECT c.company_name, rf.amount_usd, rf.round_date
FROM funding_rounds rf
JOIN companies c ON rf.company_id = c.id
WHERE rf.round_type = 'series_b'
AND c.industry_focus = 'quantum_computing'
```

---

## Next Steps

### Phase 1: Data Sources (Currently Here)
- [ ] Integrate Crunchbase API for company data
- [ ] Fetch Yahoo Finance data for public companies
- [ ] Create ArXiv paper crawler for research events
- [ ] Add SEC filing parser for disclosures

### Phase 2: Enrichment
- [ ] Calculate investment risk scores (ML model)
- [ ] Add patent analysis
- [ ] Integrate GitHub activity metrics
- [ ] Track leadership changes and key hires

### Phase 3: Analytics
- [ ] Portfolio optimization recommendations
- [ ] Competitive landscape analysis
- [ ] Technology trend tracking
- [ ] Market timing signals

### Phase 4: Production
- [ ] Deploy to cloud
- [ ] Add authentication
- [ ] Build web dashboard
- [ ] Enable real-time alerts

---

## Development

### Run locally
```bash
just setup
just run-case-study
just dev-api
```

### Add a new data source
1. Create script in `scripts/fetch_*.py`
2. Add Bronze model in `dbt/models/bronze/`
3. Add Silver model in `dbt/models/silver/`
4. Add Gold metrics in `dbt/models/gold/`
5. Add API endpoint in `api/serve.py`
6. Run `just dbt && just test`

### Test data quality
```bash
just test
```

### View dbt documentation
```bash
just docs
```

---

## Key Metrics to Track

**Company Level:**
- Total funding raised
- Funding runway
- Number of investors
- Time to next funding
- Board composition
- Patent count
- Research publication rate

**Market Level:**
- Total capital deployed in quantum
- Number of active startups
- Average Series round size
- Time to exit (IPO/acquisition)
- Sector concentration
- Geographic distribution

**Technology Level:**
- Breakthrough frequency
- Patent novelty scores
- Research collaboration network
- Technology maturity level
- Competitive positioning

---

## Use Cases

1. **Portfolio Construction**: Identify high-potential quantum companies for investment
2. **Risk Assessment**: Evaluate company health and runway
3. **Market Timing**: Detect sector trends and funding cycles
4. **Competitive Analysis**: Track competitive positioning
5. **Due Diligence**: Automate background research for investments
6. **Trend Analysis**: Monitor quantum computing progress and adoption

---

## Notes

- This is a **foundation** with placeholders for data sources
- All data models are **extensible** via JSON fields
- API is **production-ready** once data sources are connected
- Pipeline is **cost-effective** for personal/small-team use
- Graduation path: SQLite → PostgreSQL → Data Warehouse when scale increases

---

## Resources

**Quantum Computing Companies** (to research):
- IBM Quantum
- IonQ
- Rigetti
- D-Wave
- Atom Computing
- Quantinuum
- PsiQuantum
- Microsoft Azure Quantum

**Data Sources** (to evaluate):
- Crunchbase API
- Yahoo Finance API
- SEC EDGAR
- ArXiv API
- GitHub API
- USPTO Patent API

---

**Questions?** This is a placeholder structure ready for integration with real data sources. See the main playbook README for architecture principles.
