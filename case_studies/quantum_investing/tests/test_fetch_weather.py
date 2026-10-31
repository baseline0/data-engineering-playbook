"""Tests for the fetch_weather pure functions and its Typer wiring."""

import json
import random
import sqlite3
from datetime import datetime
from pathlib import Path

import fetch_weather
import pytest
from fetch_weather import (
    STATIONS,
    fetch_weather_data,
    generate_realistic_weather,
    init_database,
    load_weather,
)
from typer.testing import CliRunner

runner = CliRunner()

END = datetime(2025, 7, 15, 12, 0, 0)


def test_generated_weather_has_expected_fields_and_ranges() -> None:
    random.seed(1)

    row = generate_realistic_weather("2025-07-15", "brandon")

    assert row["date"] == "2025-07-15"
    assert row["station_id"] == "brandon"
    assert row["temp_max_c"] > row["temp_min_c"]
    assert row["precipitation_mm"] >= 0
    assert 5 <= row["wind_speed_kmh"] <= 30
    assert 40 <= row["humidity_percent"] <= 95
    assert 1003 <= row["pressure_mb"] <= 1023


def test_init_database_creates_raw_weather_table(tmp_path: Path) -> None:
    conn = init_database(tmp_path / "nested" / "weather.db")
    try:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        conn.close()

    assert "raw_weather" in tables


def test_load_weather_inserts_inclusive_range_per_station(tmp_path: Path) -> None:
    conn = init_database(tmp_path / "weather.db")
    try:
        load = load_weather(conn, END, days=2)
    finally:
        conn.close()

    # days=2 covers END-2, END-1, END: three days per station
    assert load.inserted_by_station == dict.fromkeys(STATIONS, 3)
    assert load.total == 6


def test_load_weather_skips_existing_rows(tmp_path: Path) -> None:
    conn = init_database(tmp_path / "weather.db")
    try:
        load_weather(conn, END, days=2)
        again = load_weather(conn, END, days=2)
    finally:
        conn.close()

    assert again.total == 0


def test_fetch_weather_data_commits_dates_and_json(tmp_path: Path) -> None:
    db_path = tmp_path / "weather.db"

    load = fetch_weather_data(db_path, END, days=1)

    assert load.total == 2 * len(STATIONS)
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute("SELECT station_id, date, raw_data FROM raw_weather ORDER BY id").fetchall()
    finally:
        conn.close()
    assert [r[1] for r in rows if r[0] == "brandon"] == ["2025-07-14", "2025-07-15"]
    assert json.loads(rows[0][2])["station_id"] == rows[0][0]


def test_cli_default_fetches_seven_days(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(fetch_weather, "DEFAULT_DB_PATH", tmp_path / "weather.db")

    result = runner.invoke(fetch_weather.app, ["--days", "7"])

    assert result.exit_code == 0
    assert "Fetching 7 days of weather data..." in result.output
    assert f"Success! Loaded {8 * len(STATIONS)} records." in result.output


def test_cli_days_flag_controls_range(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(fetch_weather, "DEFAULT_DB_PATH", tmp_path / "weather.db")

    result = runner.invoke(fetch_weather.app, ["--days", "2"])

    assert result.exit_code == 0
    assert "Fetching 2 days of weather data..." in result.output
    assert f"Success! Loaded {3 * len(STATIONS)} records." in result.output
