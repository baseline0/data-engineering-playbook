#!/usr/bin/env python3
"""
Manitoba Climate Analytics API
Serves weather data via REST endpoints with auto-generated documentation.

Run with:
    uvicorn api.serve:app --reload --host 0.0.0.0 --port 8000

Then visit:
    http://localhost:8000/docs (Swagger UI)
    http://localhost:8000/redoc (ReDoc)
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import sqlite3
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Manitoba Climate Analytics API",
    description="Serves weather metrics from the data pipeline",
    version="1.0.0",
)

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "gold" / "metrics.db"
BRONZE_DB = Path(__file__).parent.parent / "data" / "bronze" / "weather.db"


# Pydantic models for request/response validation
class WeatherObservation(BaseModel):
    """Single weather observation"""
    observation_date: str
    station_id: str
    temp_max_c: float
    temp_min_c: float
    temp_avg_c: float
    precipitation_mm: float
    wind_speed_kmh: Optional[float] = None
    humidity_percent: Optional[int] = None
    data_quality_flag: str


class MonthlyMetric(BaseModel):
    """Monthly aggregated weather metric"""
    month: str
    station_id: str
    avg_temperature: float
    total_precipitation: float
    max_temperature: float
    min_temperature: float
    observation_count: int


class PipelineStatus(BaseModel):
    """Pipeline execution status"""
    status: str
    last_updated: str
    raw_records: int
    message: str


# Health check endpoint
@app.get(
    "/health",
    summary="Health check",
    response_description="API is running"
)
async def health():
    """Check if API is running"""
    return {
        "status": "ok",
        "service": "Manitoba Climate Analytics API",
        "version": "1.0.0"
    }


# Weather observations endpoint
@app.get(
    "/api/observations",
    summary="Get weather observations",
    response_model=List[WeatherObservation],
    tags=["Weather Data"]
)
async def get_observations(
    station_id: Optional[str] = Query(None, description="Filter by station (winnipeg_pearson, brandon)"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    order: str = Query("desc", description="Sort order: asc or desc")
):
    """
    Get historical weather observations.

    Returns raw or cleaned weather data from the bronze/silver layer.
    """
    try:
        conn = sqlite3.connect(str(BRONZE_DB))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM raw_weather WHERE 1=1"
        params = []

        if station_id:
            query += " AND station_id = ?"
            params.append(station_id)

        query += f" ORDER BY date {order.upper()} LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except sqlite3.DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Monthly metrics endpoint
@app.get(
    "/api/monthly",
    summary="Get monthly metrics",
    response_model=List[MonthlyMetric],
    tags=["Aggregations"]
)
async def get_monthly_metrics(
    station_id: Optional[str] = Query(None, description="Filter by station"),
    year: Optional[int] = Query(None, description="Filter by year (e.g., 2024)")
):
    """
    Get monthly aggregated weather metrics.

    Returns aggregated temperature and precipitation by month.
    """
    try:
        conn = sqlite3.connect(str(BRONZE_DB))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Simple aggregation from raw data
        query = """
        SELECT
            strftime('%Y-%m', date) as month,
            station_id,
            ROUND(AVG(CAST(json_extract(raw_data, '$.temp_max_c') AS FLOAT)), 2) as avg_temperature,
            ROUND(SUM(CAST(json_extract(raw_data, '$.precipitation_mm') AS FLOAT)), 2) as total_precipitation,
            ROUND(MAX(CAST(json_extract(raw_data, '$.temp_max_c') AS FLOAT)), 2) as max_temperature,
            ROUND(MIN(CAST(json_extract(raw_data, '$.temp_min_c') AS FLOAT)), 2) as min_temperature,
            COUNT(*) as observation_count
        FROM raw_weather
        WHERE 1=1
        """
        params = []

        if station_id:
            query += " AND station_id = ?"
            params.append(station_id)

        query += " GROUP BY month, station_id ORDER BY month DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except sqlite3.DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Pipeline status endpoint
@app.get(
    "/api/status",
    summary="Pipeline status",
    response_model=PipelineStatus,
    tags=["Admin"]
)
async def pipeline_status():
    """Get data pipeline status"""
    try:
        conn = sqlite3.connect(str(BRONZE_DB))
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM raw_weather")
        record_count = cursor.fetchone()[0]

        cursor.execute("SELECT MAX(fetched_at) FROM raw_weather")
        last_updated = cursor.fetchone()[0] or "Never"

        conn.close()

        return PipelineStatus(
            status="operational" if record_count > 0 else "empty",
            last_updated=str(last_updated),
            raw_records=record_count,
            message=f"Pipeline has {record_count} weather observations"
        )

    except sqlite3.DatabaseError as e:
        return PipelineStatus(
            status="error",
            last_updated="unknown",
            raw_records=0,
            message=f"Database error: {str(e)}"
        )


# Summary statistics endpoint
@app.get(
    "/api/summary",
    summary="Get summary statistics",
    tags=["Analytics"]
)
async def get_summary():
    """Get summary statistics for the dataset"""
    try:
        conn = sqlite3.connect(str(BRONZE_DB))
        cursor = conn.cursor()

        # Station count
        cursor.execute("SELECT COUNT(DISTINCT station_id) as station_count FROM raw_weather")
        station_count = cursor.fetchone()[0]

        # Date range
        cursor.execute("""
            SELECT
                MIN(date) as start_date,
                MAX(date) as end_date,
                COUNT(*) as total_records
            FROM raw_weather
        """)
        stats = cursor.fetchone()

        conn.close()

        return {
            "stations": station_count,
            "date_range": {
                "start": stats[0],
                "end": stats[1]
            },
            "total_records": stats[2],
            "endpoints": [
                "/api/observations",
                "/api/monthly",
                "/api/summary",
                "/api/status"
            ]
        }

    except sqlite3.DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Root endpoint with documentation
@app.get("/", tags=["Info"])
async def root():
    """API root with documentation links"""
    return {
        "name": "Manitoba Climate Analytics API",
        "version": "1.0.0",
        "description": "REST API for weather and climate data from Manitoba case study",
        "docs": {
            "swagger": "http://localhost:8000/docs",
            "redoc": "http://localhost:8000/redoc",
            "openapi": "http://localhost:8000/openapi.json"
        },
        "endpoints": {
            "health": "GET /health",
            "observations": "GET /api/observations",
            "monthly": "GET /api/monthly",
            "summary": "GET /api/summary",
            "status": "GET /api/status"
        }
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Manitoba Climate Analytics API")
    print("📚 Swagger UI: http://localhost:8000/docs")
    print("📚 ReDoc: http://localhost:8000/redoc")
    print("")

    uvicorn.run(
        "serve:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
