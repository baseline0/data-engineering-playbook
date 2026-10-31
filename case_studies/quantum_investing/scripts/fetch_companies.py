#!/usr/bin/env python3
"""
Fetch quantum computing company data and load to bronze layer.

This is a placeholder implementation. In production, this would:
- Integrate with Crunchbase API
- Fetch from SEC EDGAR
- Pull from Yahoo Finance
- Query PitchBook or AngelList

For now, we generate synthetic quantum company data.

Design Intent:
- Logic lives in pure functions that take paths, years, and rows as arguments.
- The Typer command only parses flags, runs the pure functions, and prints the result.
"""

import json
import random
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(help="Fetch quantum computing company data to bronze layer")

DEFAULT_DB_PATH = Path(__file__).parent.parent / "data" / "bronze" / "quantum.db"


class LoadStatus(StrEnum):
    """Outcome of inserting one company into the bronze layer."""

    LOADED = "loaded"
    EXISTS = "exists"


@dataclass(frozen=True)
class CompanyLoad:
    """Result of loading one company."""

    name: str
    stage: str
    status: LoadStatus


def init_database(db_path: Path) -> sqlite3.Connection:
    """Initialize SQLite database for bronze layer."""
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


def clear_database(db_path: Path) -> bool:
    """Delete the bronze database file. Returns True if a file was removed."""
    if not db_path.exists():
        return False
    db_path.unlink()
    return True


def generate_quantum_companies() -> list[dict]:
    """Generate synthetic quantum computing company data"""
    companies = [
        {
            "ticker": "IBM",
            "name": "IBM Quantum",
            "founded": 2016,
            "stage": "public",
            "hq": "Armonk, NY",
            "focus": "superconducting qubits",
        },
        {
            "ticker": "IONQ",
            "name": "IonQ",
            "founded": 2015,
            "stage": "public",
            "hq": "College Park, MD",
            "focus": "trapped ion",
        },
        {
            "ticker": "RIGETTI",
            "name": "Rigetti Computing",
            "founded": 2013,
            "stage": "private",
            "hq": "Berkeley, CA",
            "focus": "superconducting qubits",
        },
        {
            "ticker": "DWAV",
            "name": "D-Wave Systems",
            "founded": 2001,
            "stage": "public",
            "hq": "Burnaby, BC",
            "focus": "quantum annealing",
        },
        {
            "ticker": "ATOM",
            "name": "Atom Computing",
            "founded": 2018,
            "stage": "series_b",
            "hq": "Boulder, CO",
            "focus": "neutral atom",
        },
        {
            "ticker": "QUANTINUUM",
            "name": "Quantinuum",
            "founded": 2021,
            "stage": "private",
            "hq": "Broomfield, CO",
            "focus": "trapped ion systems",
        },
        {
            "ticker": "PSIQ",
            "name": "PsiQuantum",
            "founded": 2015,
            "stage": "private",
            "hq": "Palo Alto, CA",
            "focus": "fault-tolerant quantum",
        },
        {
            "ticker": "MSFT",
            "name": "Microsoft Azure Quantum",
            "founded": 2018,
            "stage": "public",
            "hq": "Redmond, WA",
            "focus": "topological qubits",
        },
    ]
    return companies


def generate_funding_round(company: dict, year: int) -> dict | None:
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
        "date": f"{year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
    }


def load_companies(conn: sqlite3.Connection, companies: list[dict], current_year: int) -> list[CompanyLoad]:
    """Insert companies and their funding rounds. Does not commit.

    A company whose ticker already exists is reported as EXISTS and skipped.
    """
    cursor = conn.cursor()
    results: list[CompanyLoad] = []

    for company in companies:
        try:
            cursor.execute(
                """
                INSERT INTO companies (ticker, name, founded_date, industry_focus, stage, headquarters, raw_metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    company["ticker"],
                    company["name"],
                    f"{company['founded']}-01-01",
                    company["focus"],
                    company["stage"],
                    company["hq"],
                    json.dumps(
                        {
                            "technology": company["focus"],
                            "stage": company["stage"],
                            "year_founded": company["founded"],
                        }
                    ),
                ),
            )

            company_id = cursor.lastrowid

            # Generate funding rounds from the founding year through the current year
            for year in range(company["founded"], current_year + 1):
                funding = generate_funding_round(company, year)
                if funding:
                    cursor.execute(
                        """
                        INSERT INTO funding_rounds (company_id, round_date, amount_usd, round_type, investors)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            company_id,
                            funding["date"],
                            funding["amount"],
                            funding["round_type"],
                            json.dumps([]),  # Placeholder for investors
                        ),
                    )

            results.append(CompanyLoad(company["name"], company["stage"], LoadStatus.LOADED))

        except sqlite3.IntegrityError:
            results.append(CompanyLoad(company["name"], company["stage"], LoadStatus.EXISTS))

    return results


def fetch_company_data(db_path: Path, current_year: int) -> list[CompanyLoad]:
    """Create the bronze database, load the synthetic companies, and commit."""
    conn = init_database(db_path)
    try:
        results = load_companies(conn, generate_quantum_companies(), current_year)
        conn.commit()
    finally:
        conn.close()
    return results


def inserted_count(results: list[CompanyLoad]) -> int:
    """Number of companies that were newly loaded."""
    return sum(1 for result in results if result.status is LoadStatus.LOADED)


@app.command()
def main(
    regenerate: Annotated[
        bool,
        typer.Option("--regenerate/--no-regenerate", help="Regenerate all data (clears existing data)"),
    ],
) -> None:
    """Fetch quantum computing company data to bronze layer."""
    if regenerate and clear_database(DEFAULT_DB_PATH):
        typer.echo("Cleared existing database...")

    typer.echo("Fetching quantum company data...\n")
    typer.echo("🔬 Fetching quantum computing company data...")
    results = fetch_company_data(DEFAULT_DB_PATH, datetime.now().year)

    for result in results:
        if result.status is LoadStatus.LOADED:
            typer.echo(f"  ✓ {result.name} ({result.stage})")
        else:
            typer.echo(f"  ⊘ {result.name} already exists")

    count = inserted_count(results)
    typer.echo(f"\n✓ Loaded {count} quantum computing companies to bronze layer")
    typer.echo(f"\nSuccess! Loaded {count} companies.")


if __name__ == "__main__":
    app()
