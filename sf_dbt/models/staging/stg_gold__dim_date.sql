select
    date_key,
    date,
    year,
    quarter,
    month,
    month_name,
    month_start,
    day_name,
    is_weekend
from {{ source('gold', 'dim_date') }}