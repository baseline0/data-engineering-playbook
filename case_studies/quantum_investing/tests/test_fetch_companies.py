"""Tests for the fetch_companies pure functions and its Typer wiring."""

import random
import sqlite3
from pathlib import Path

import fetch_companies
import pytest
from fetch_companies import (
    LoadStatus,
    clear_database,
    fetch_company_data,
    generate_funding_round,
    generate_quantum_companies,
    init_database,
    inserted_count,
    load_companies,
)
from typer.testing import CliRunner

runner = CliRunner()


def _company(stage: str = "private", founded: int = 2015) -> dict:
    return {
        "ticker": "T",
        "name": "Test Co",
        "founded": founded,
        "stage": stage,
        "hq": "Nowhere",
        "focus": "test",
    }


def test_generated_companies_have_unique_tickers_and_required_keys() -> None:
    companies = generate_quantum_companies()

    assert len(companies) == 8
    assert len({c["ticker"] for c in companies}) == len(companies)
    for company in companies:
        assert {"ticker", "name", "founded", "stage", "hq", "focus"} <= company.keys()


def test_public_company_never_gets_a_funding_round() -> None:
    assert generate_funding_round(_company(stage="public"), 2020) is None


def test_year_before_founding_gets_no_round() -> None:
    assert generate_funding_round(_company(founded=2020), 2019) is None


def test_first_year_is_always_seed_round(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(random, "randint", lambda a, b: a)

    round_ = generate_funding_round(_company(founded=2020), 2020)

    assert round_ is not None
    assert round_["round_type"] == "seed"
    assert round_["amount"] == 1_000_000
    assert round_["date"].startswith("2020-")


def test_later_rounds_are_skipped_when_random_draw_is_high(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(random, "random", lambda: 0.99)

    assert generate_funding_round(_company(founded=2015), 2016) is None  # series_a
    assert generate_funding_round(_company(founded=2015), 2017) is None  # series_b
    assert generate_funding_round(_company(founded=2015), 2018) is None  # series_c


def test_init_database_creates_both_tables(tmp_path: Path) -> None:
    conn = init_database(tmp_path / "nested" / "quantum.db")
    try:
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
    finally:
        conn.close()

    assert {"companies", "funding_rounds"} <= tables


def test_clear_database_removes_existing_file_only(tmp_path: Path) -> None:
    db_path = tmp_path / "quantum.db"
    assert clear_database(db_path) is False

    db_path.write_bytes(b"")
    assert clear_database(db_path) is True
    assert not db_path.exists()


def test_load_companies_reports_loaded_then_exists(tmp_path: Path) -> None:
    conn = init_database(tmp_path / "quantum.db")
    try:
        companies = generate_quantum_companies()
        first = load_companies(conn, companies, current_year=2025)
        second = load_companies(conn, companies, current_year=2025)
    finally:
        conn.close()

    assert inserted_count(first) == len(companies)
    assert all(result.status is LoadStatus.LOADED for result in first)
    assert inserted_count(second) == 0
    assert all(result.status is LoadStatus.EXISTS for result in second)


def test_fetch_company_data_commits_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "quantum.db"

    results = fetch_company_data(db_path, current_year=2025)

    assert inserted_count(results) == 8
    conn = sqlite3.connect(str(db_path))
    try:
        (count,) = conn.execute("SELECT COUNT(*) FROM companies").fetchone()
    finally:
        conn.close()
    assert count == 8


def test_cli_prints_summary_and_exits_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(fetch_companies, "DEFAULT_DB_PATH", tmp_path / "quantum.db")
    random.seed(0)

    result = runner.invoke(fetch_companies.app, [])

    assert result.exit_code == 0
    assert "Fetching quantum company data..." in result.output
    assert "Success! Loaded 8 companies." in result.output


def test_cli_regenerate_clears_existing_database(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "quantum.db"
    db_path.write_bytes(b"")
    monkeypatch.setattr(fetch_companies, "DEFAULT_DB_PATH", db_path)

    result = runner.invoke(fetch_companies.app, ["--regenerate"])

    assert result.exit_code == 0
    assert result.output.startswith("Cleared existing database...\n")
    assert "Success! Loaded 8 companies." in result.output
