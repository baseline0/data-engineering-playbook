-- Silver layer: Cleaned daily weather observations
-- Purpose: Standardize and validate raw weather data
-- Materialization: Table
-- Frequency: Daily

with source as (
    select
        station_id,
        date,
        raw_data,
        fetched_at
    from {{ source('bronze', 'raw_weather') }}
    where raw_data is not null
)

, parsed as (
    -- Extract JSON fields
    select
        date::date as observation_date,
        station_id,
        json_extract_path_text(raw_data, 'temp_max_c')::numeric as temp_max_c,
        json_extract_path_text(raw_data, 'temp_min_c')::numeric as temp_min_c,
        json_extract_path_text(raw_data, 'precipitation_mm')::numeric as precipitation_mm,
        json_extract_path_text(raw_data, 'wind_speed_kmh')::numeric as wind_speed_kmh,
        json_extract_path_text(raw_data, 'humidity_percent')::integer as humidity_percent,
        json_extract_path_text(raw_data, 'pressure_mb')::numeric as pressure_mb,
        fetched_at
    from source
)

, cleaned as (
    select
        observation_date,
        station_id,
        temp_max_c,
        temp_min_c,
        round((temp_max_c + temp_min_c) / 2.0, 1) as temp_avg_c,
        coalesce(precipitation_mm, 0) as precipitation_mm,
        wind_speed_kmh,
        humidity_percent,
        pressure_mb,
        current_timestamp as processed_at,

        -- Data quality flags
        case
            when temp_max_c < -50 or temp_max_c > 50 then 'temperature_out_of_range'
            when precipitation_mm < 0 or precipitation_mm > 500 then 'precipitation_out_of_range'
            when wind_speed_kmh < 0 or wind_speed_kmh > 200 then 'wind_out_of_range'
            else 'valid'
        end as data_quality_flag

    from parsed
    where observation_date is not null
        and station_id is not null
)

, final as (
    select
        row_number() over (partition by station_id order by observation_date) as record_id,
        observation_date,
        station_id,
        temp_max_c,
        temp_min_c,
        temp_avg_c,
        precipitation_mm,
        wind_speed_kmh,
        humidity_percent,
        pressure_mb,
        processed_at,
        data_quality_flag
    from cleaned
)

select distinct *
from final
where data_quality_flag = 'valid'
order by observation_date desc, station_id
