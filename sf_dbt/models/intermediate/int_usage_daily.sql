{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='usage_day_key'
) }}

with usage as (
    select
        to_date(cast(date_key as string), 'yyyyMMdd') as usage_date,
        account_id,
        service,
        units,
        amount_aud
    from {{ ref('stg_gold__fact_usage') }}
)

select
    concat_ws('|', cast(usage_date as string), account_id, service) as usage_day_key,
    usage_date,
    account_id,
    service,
    count(*) as usage_events,
    sum(units) as units,
    sum(amount_aud) as amount_aud
from usage
{% if is_incremental() %}
where usage_date >= date_sub((select max(usage_date) from {{ this }}), {{ var('usage_lookback_days') }})
{% endif %}
group by usage_date, account_id, service