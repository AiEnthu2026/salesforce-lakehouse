with monthly as (
    select * from {{ ref('stg_gold__agg_account_monthly') }}
),

contract as (
    select
        account_month_key,
        contract_id,
        contract_tier,
        committed_monthly_aud,
        variance_aud,
        utilisation_pct
    from {{ ref('stg_gold__agg_contract_vs_usage') }}
),

joined as (
    select
        m.account_month_key,
        m.account_id,
        m.month_start,
        m.account_name,
        m.industry,
        m.rating,
        m.revenue_band,
        m.cases_opened,
        m.cases_escalated,
        m.usage_events,
        m.usage_amount_aud,
        c.contract_id,
        c.contract_tier,
        c.committed_monthly_aud,
        c.variance_aud,
        c.utilisation_pct
    from monthly m
    left join contract c
        on m.account_month_key = c.account_month_key
),

windowed as (
    select
        *,
        lag(usage_amount_aud) over (partition by account_id order by month_start) as prev_usage_raw,
        lag(month_start) over (partition by account_id order by month_start) as prev_month_start,
        avg(usage_amount_aud) over (
            partition by account_id
            order by month_start
            rows between 2 preceding and current row
        ) as usage_avg_3m_aud
    from joined
),

lagged as (
    select
        *,
        case
            when prev_month_start = add_months(month_start, -1) then prev_usage_raw
        end as prev_month_usage_aud
    from windowed
)

select
    account_month_key,
    account_id,
    account_id = 'UNKNOWN' as is_unknown_account,
    month_start,
    account_name,
    industry,
    rating,
    revenue_band,
    contract_id,
    contract_tier,
    committed_monthly_aud,
    utilisation_pct,
    variance_aud,    
    case
        when committed_monthly_aud is null and coalesce(usage_events, 0) = 0 then 'no_usage'
        when committed_monthly_aud is null then 'no_commitment'
        when utilisation_pct < {{ var('util_under_pct') }} then 'under'
        when utilisation_pct <= {{ var('util_over_pct') }} then 'on_track'
        else 'over'
    end as commit_status,
    cases_opened,
    cases_escalated,
    {{ safe_divide('cases_escalated', 'cases_opened') }} as escalation_rate,
    usage_events,
    usage_amount_aud,
    usage_avg_3m_aud,
    prev_month_usage_aud,
    {{ safe_divide('usage_amount_aud - prev_month_usage_aud', 'prev_month_usage_aud') }} * 100 as usage_mom_change_pct
from lagged