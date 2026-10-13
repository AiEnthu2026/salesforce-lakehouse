select
    concat_ws('|', account_id, cast(month_start as string)) as account_month_key,
    account_id,
    customer_ref,
    account_name,
    month_start,
    contract_id,
    contract_tier,
    committed_monthly_aud,
    usage_events,
    usage_amount_aud,
    variance_aud,
    utilisation_pct
from {{ source('gold', 'agg_contract_vs_usage') }}