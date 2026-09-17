#!/usr/bin/env python3
"""
Fetch historical weather data from Environment Canada.

This is a placeholder implementation. In production, you would:
1. Use the actual Environment Canada API or CSV downloads
2. Handle authentication if needed
3. Implement retry logic for network failures
4. Add logging and error handling

For now, we generate synthetic data that mimics real weather patterns.
"""

import sqlite3
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import random

def init_database():
    """Initialize SQLite database for bronze layer."""
    db_path = Path(__file__).parent.parent / 'data' / 'bronze' / 'weather.db'
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

def generate_realistic_weather(date, station_id):
    """
    Generate realistic weather data.
    In production, this would fetch from Environment Canada API.
    """
    # Simulate seasonal temperature patterns
    month = datetime.strptime(date, '%Y-%m-%d').month
    day_of_year = datetime.strptime(date, '%Y-%m-%d').timetuple().tm_yday

    # Base temperature varies by season
    base_temp = 10 * (1 - (month - 7) ** 2 / 49)  # Peaks in July

    # Add random variation
    daily_variation = random.uniform(-3, 3)
    temp_max = round(base_temp + daily_variation + random.uniform(2, 8), 1)
    temp_min = round(base_temp + daily_variation - random.uniform(2, 8), 1)

    # Precipitation more likely in summer
    precip_prob = 0.3 if 5 <= month <= 9 else 0.2
    precipitation = round(random.expovariate(1.5) * 10, 1) if random.random() < precip_prob else 0

    # Wind speed varies
    wind_speed = round(random.uniform(5, 30), 1)

    return {
        'date': date,
        'station_id': station_id,
        'temp_max_c': temp_max,
        'temp_min_c': temp_min,
        'precipitation_mm': precipitation,
        'wind_speed_kmh': wind_speed,
        'humidity_percent': random.randint(40, 95),
        'pressure_mb': round(1013 + random.uniform(-10, 10), 1)
    }

def fetch_weather_data(days=7):
    """
    Fetch weather data and load to bronze layer.

    Args:
        days: Number of days of historical data to fetch
    """
    conn = init_database()
    cursor = conn.cursor()

    stations = ['winnipeg_pearson', 'brandon']
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    inserted_count = 0

    for station_id in stations:
        print(f"Fetching data for {station_id}...")

        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')

            # Generate weather data (in production, fetch from API)
            weather_data = generate_realistic_weather(date_str, station_id)

            try:
                cursor.execute("""
                    INSERT INTO raw_weather (station_id, date, raw_data)
                    VALUES (?, ?, ?)
                """, (station_id, date_str, json.dumps(weather_data)))
                inserted_count += 1
            except sqlite3.IntegrityError:
                # Record already exists
                pass

            current_date += timedelta(days=1)

    conn.commit()
    conn.close()

    print(f"✓ Inserted {inserted_count} weather records to bronze layer")
    return inserted_count

def main():
    parser = argparse.ArgumentParser(
        description='Fetch weather data to bronze layer'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days of historical data to fetch (default: 7)'
    )

    args = parser.parse_args()

    print(f"Fetching {args.days} days of weather data...")
    count = fetch_weather_data(days=args.days)
    print(f"Success! Loaded {count} records.")

if __name__ == '__main__':
    main()
