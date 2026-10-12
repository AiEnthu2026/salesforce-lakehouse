select
    usage_id,
    date_key,
    account_id,
    customer_ref,
    is_orphan_account,
    service,
    units,
    amount_aud
from {{ source('gold', 'fact_usage') }}