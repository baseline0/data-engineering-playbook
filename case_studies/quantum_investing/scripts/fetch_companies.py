#!/usr/bin/env python3
"""
Fetch quantum computing company data and load to bronze layer.

This is a placeholder implementation. In production, this would:
- Integrate with Crunchbase API
- Fetch from SEC EDGAR
- Pull from Yahoo Finance
- Query PitchBook or AngelList

For now, we generate synthetic quantum company data.
"""

import sqlite3
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import random

def init_database():
    """Initialize SQLite database for bronze layer."""
    db_path = Path(__file__).parent.parent / 'data' / 'bronze' / 'quantum.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT UNIQUE,
            name TEXT NOT NULL,
            founded_date TEXT,
            industry_focus TEXT,
            stage TEXT,
            headquarters TEXT,
            raw_metadata TEXT,
            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funding_rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            round_date TEXT,
            amount_usd REAL,
            round_type TEXT,
            investors TEXT,
            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    conn.commit()
    return conn

def generate_quantum_companies():
    """Generate synthetic quantum computing company data"""
    companies = [
        {
            "ticker": "IBM",
            "name": "IBM Quantum",
            "founded": 2016,
            "stage": "public",
            "hq": "Armonk, NY",
            "focus": "superconducting qubits"
        },
        {
            "ticker": "IONQ",
            "name": "IonQ",
            "founded": 2015,
            "stage": "public",
            "hq": "College Park, MD",
            "focus": "trapped ion"
        },
        {
            "ticker": "RIGETTI",
            "name": "Rigetti Computing",
            "founded": 2013,
            "stage": "private",
            "hq": "Berkeley, CA",
            "focus": "superconducting qubits"
        },
        {
            "ticker": "DWAV",
            "name": "D-Wave Systems",
            "founded": 2001,
            "stage": "public",
            "hq": "Burnaby, BC",
            "focus": "quantum annealing"
        },
        {
            "ticker": "ATOM",
            "name": "Atom Computing",
            "founded": 2018,
            "stage": "series_b",
            "hq": "Boulder, CO",
            "focus": "neutral atom"
        },
        {
            "ticker": "QUANTINUUM",
            "name": "Quantinuum",
            "founded": 2021,
            "stage": "private",
            "hq": "Broomfield, CO",
            "focus": "trapped ion systems"
        },
        {
            "ticker": "PSIQ",
            "name": "PsiQuantum",
            "founded": 2015,
            "stage": "private",
            "hq": "Palo Alto, CA",
            "focus": "fault-tolerant quantum"
        },
        {
            "ticker": "MSFT",
            "name": "Microsoft Azure Quantum",
            "founded": 2018,
            "stage": "public",
            "hq": "Redmond, WA",
            "focus": "topological qubits"
        },
    ]
    return companies

def generate_funding_round(company: dict, year: int):
    """Generate realistic funding data"""
    if company["stage"] == "public":
        return None  # Public companies don't have traditional funding rounds

    # Simulate funding progression
    years_since_founded = year - company["founded"]
    if years_since_founded < 0:
        return None

    # Series progression: Seed (year 0-1), Series A (1-2), B (2-3), C+ (3+)
    if years_since_founded < 1:
        round_type = "seed"
        amount = random.randint(1, 5) * 1_000_000
    elif years_since_founded < 2:
        if random.random() > 0.6:  # Not all get series A
            return None
        round_type = "series_a"
        amount = random.randint(5, 20) * 1_000_000
    elif years_since_founded < 3:
        if random.random() > 0.5:
            return None
        round_type = "series_b"
        amount = random.randint(15, 50) * 1_000_000
    else:
        if random.random() > 0.4:
            return None
        round_type = "series_c"
        amount = random.randint(30, 150) * 1_000_000

    return {
        "round_type": round_type,
        "amount": amount,
        "date": f"{year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    }

def fetch_company_data():
    """Fetch company data and load to bronze layer"""
    conn = init_database()
    cursor = conn.cursor()

    companies = generate_quantum_companies()
    inserted_count = 0

    print("🔬 Fetching quantum computing company data...")

    for company in companies:
        try:
            cursor.execute("""
                INSERT INTO companies (ticker, name, founded_date, industry_focus, stage, headquarters, raw_metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                company["ticker"],
                company["name"],
                f"{company['founded']}-01-01",
                company["focus"],
                company["stage"],
                company["hq"],
                json.dumps({
                    "technology": company["focus"],
                    "stage": company["stage"],
                    "year_founded": company["founded"]
                })
            ))

            company_id = cursor.lastrowid

            # Generate funding rounds for the past 5 years
            for year in range(company["founded"], datetime.now().year + 1):
                funding = generate_funding_round(company, year)
                if funding:
                    cursor.execute("""
                        INSERT INTO funding_rounds (company_id, round_date, amount_usd, round_type, investors)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        company_id,
                        funding["date"],
                        funding["amount"],
                        funding["round_type"],
                        json.dumps([])  # Placeholder for investors
                    ))

            inserted_count += 1
            print(f"  ✓ {company['name']} ({company['stage']})")

        except sqlite3.IntegrityError:
            print(f"  ⊘ {company['name']} already exists")

    conn.commit()
    conn.close()

    print(f"\n✓ Loaded {inserted_count} quantum computing companies to bronze layer")
    return inserted_count

def main():
    parser = argparse.ArgumentParser(
        description='Fetch quantum computing company data to bronze layer'
    )
    parser.add_argument(
        '--regenerate',
        action='store_true',
        help='Regenerate all data (clears existing data)'
    )

    args = parser.parse_args()

    if args.regenerate:
        db_path = Path(__file__).parent.parent / 'data' / 'bronze' / 'quantum.db'
        if db_path.exists():
            db_path.unlink()
            print("Cleared existing database...")

    print("Fetching quantum company data...\n")
    count = fetch_company_data()
    print(f"\nSuccess! Loaded {count} companies.")

if __name__ == '__main__':
    main()
