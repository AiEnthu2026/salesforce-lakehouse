select
    account_id,
    customer_ref,
    account_name,
    account_type,
    industry,
    billing_city,
    billing_state,
    billing_country,
    annual_revenue,
    employee_count,
    rating,
    created_at,
    contract_tier,
    revenue_band
from {{ source('gold', 'dim_account') }}