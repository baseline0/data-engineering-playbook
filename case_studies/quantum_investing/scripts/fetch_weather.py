#!/usr/bin/env python3
"""
Fetch historical weather data from Environment Canada.

This is a placeholder implementation. In production, you would:
1. Use the actual Environment Canada API or CSV downloads
2. Handle authentication if needed
3. Implement retry logic for network failures
4. Add logging and error handling

For now, we generate synthetic data that mimics real weather patterns.

Design Intent:
- Logic lives in pure functions that take paths, dates, and counts as arguments.
- The Typer command only parses flags, runs the pure functions, and prints the result.
"""

import json
import random
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(help="Fetch weather data to bronze layer")

DEFAULT_DB_PATH = Path(__file__).parent.parent / "data" / "bronze" / "weather.db"
STATIONS = ("winnipeg_pearson", "brandon")


@dataclass
class WeatherLoad:
    """Insert counts per station, plus the total."""

    inserted_by_station: dict[str, int] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(self.inserted_by_station.values())


def init_database(db_path: Path) -> sqlite3.Connection:
    """Initialize SQLite database for bronze layer."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id TEXT NOT NULL,
            date TEXT NOT NULL,
            raw_data TEXT NOT NULL,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_id, date)
        )
    """)

    conn.commit()
    return conn


def generate_realistic_weather(date: str, station_id: str) -> dict:
    """
    Generate realistic weather data.
    In production, this would fetch from Environment Canada API.
    """
    # Simulate seasonal temperature patterns
    month = datetime.strptime(date, "%Y-%m-%d").month

    # Base temperature varies by season
    base_temp = 10 * (1 - (month - 7) ** 2 / 49)  # Peaks in July

    # Add random variation
    daily_variation = random.uniform(-3, 3)
    temp_max = round(base_temp + daily_variation + random.uniform(2, 8), 1)
    temp_min = round(base_temp + daily_variation - random.uniform(2, 8), 1)

    # Precipitation more likely in summer
    precip_prob = 0.3 if 5 <= month <= 9 else 0.2
    precipitation = (
        round(random.expovariate(1.5) * 10, 1) if random.random() < precip_prob else 0
    )

    # Wind speed varies
    wind_speed = round(random.uniform(5, 30), 1)

    return {
        "date": date,
        "station_id": station_id,
        "temp_max_c": temp_max,
        "temp_min_c": temp_min,
        "precipitation_mm": precipitation,
        "wind_speed_kmh": wind_speed,
        "humidity_percent": random.randint(40, 95),
        "pressure_mb": round(1013 + random.uniform(-10, 10), 1),
    }


def load_weather(
    conn: sqlite3.Connection,
    end_date: datetime,
    days: int,
    stations: tuple[str, ...] = STATIONS,
) -> WeatherLoad:
    """Insert one row per station per day from end_date - days through end_date. Does not commit.

    Rows whose (station, date) already exists are skipped.
    """
    cursor = conn.cursor()
    start_date = end_date - timedelta(days=days)
    load = WeatherLoad()

    for station_id in stations:
        inserted = 0
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")

            # Generate weather data (in production, fetch from API)
            weather_data = generate_realistic_weather(date_str, station_id)

            try:
                cursor.execute(
                    """
                    INSERT INTO raw_weather (station_id, date, raw_data)
                    VALUES (?, ?, ?)
                """,
                    (station_id, date_str, json.dumps(weather_data)),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                # Record already exists
                pass

            current_date += timedelta(days=1)

        load.inserted_by_station[station_id] = inserted

    return load


def fetch_weather_data(db_path: Path, end_date: datetime, days: int) -> WeatherLoad:
    """Create the bronze database, load weather rows for every station, and commit.

    Args:
        db_path: SQLite file for the bronze layer.
        end_date: Last day to fetch (inclusive).
        days: Number of days of history before end_date to fetch.
    """
    conn = init_database(db_path)
    try:
        load = load_weather(conn, end_date, days)
        conn.commit()
    finally:
        conn.close()
    return load


@app.command()
def main(
    days: Annotated[
        int,
        typer.Option(help="Number of days of historical data to fetch (default: 7)"),
    ] = 7,
) -> None:
    """Fetch weather data to bronze layer."""
    typer.echo(f"Fetching {days} days of weather data...")
    load = fetch_weather_data(DEFAULT_DB_PATH, datetime.now(), days)

    for station_id in STATIONS:
        typer.echo(f"Fetching data for {station_id}...")
    typer.echo(f"✓ Inserted {load.total} weather records to bronze layer")
    typer.echo(f"Success! Loaded {load.total} records.")


if __name__ == "__main__":
    app()
