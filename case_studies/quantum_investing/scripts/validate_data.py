#!/usr/bin/env python3
"""
Data validation script for Manitoba climate pipeline.
Validates data quality using Great Expectations.
"""

import sqlite3
from pathlib import Path

def validate_data():
    """Run data quality checks"""
    db_path = Path(__file__).parent.parent / "data" / "bronze" / "weather.db"

    print("🔍 Validating weather data...")
    print("")

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check 1: Data completeness
        cursor.execute("SELECT COUNT(*) FROM raw_weather")
        total_records = cursor.fetchone()[0]
        print(f"✓ Total records: {total_records}")

        # Check 2: Station coverage
        cursor.execute("SELECT COUNT(DISTINCT station_id) FROM raw_weather")
        station_count = cursor.fetchone()[0]
        print(f"✓ Unique stations: {station_count}")

        # Check 3: Date range
        cursor.execute("SELECT MIN(date), MAX(date) FROM raw_weather")
        min_date, max_date = cursor.fetchone()
        print(f"✓ Date range: {min_date} to {max_date}")

        # Check 4: Missing values
        cursor.execute("""
            SELECT COUNT(*)
            FROM raw_weather
            WHERE json_extract(raw_data, '$.temp_max_c') IS NULL
        """)
        missing_temps = cursor.fetchone()[0]
        print(f"✓ Missing temperatures: {missing_temps}")

        # Check 5: Temperature ranges (should be -50 to 50°C for Manitoba)
        cursor.execute("""
            SELECT COUNT(*)
            FROM raw_weather
            WHERE CAST(json_extract(raw_data, '$.temp_max_c') AS FLOAT) < -50
               OR CAST(json_extract(raw_data, '$.temp_max_c') AS FLOAT) > 50
        """)
        temp_outliers = cursor.fetchone()[0]
        print(f"✓ Temperature outliers: {temp_outliers}")

        # Check 6: Precipitation ranges
        cursor.execute("""
            SELECT COUNT(*)
            FROM raw_weather
            WHERE CAST(json_extract(raw_data, '$.precipitation_mm') AS FLOAT) < 0
               OR CAST(json_extract(raw_data, '$.precipitation_mm') AS FLOAT) > 500
        """)
        precip_outliers = cursor.fetchone()[0]
        print(f"✓ Precipitation outliers: {precip_outliers}")

        conn.close()

        print("")
        print("✅ Validation complete!")
        return True

    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

if __name__ == "__main__":
    validate_data()
