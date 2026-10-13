select
    concat_ws('|', account_id, cast(month_start as string)) as account_month_key,
    account_id,
    month_start,
    cases_opened,
    cases_opened_now_closed,
    cases_escalated,
    avg_hours_to_close,
    usage_events,
    usage_units,
    usage_amount_aud,
    account_name,
    industry,
    rating,
    revenue_band
from {{ source('gold', 'agg_account_monthly') }}