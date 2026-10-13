with accounts as (
    select * from {{ ref('stg_gold__dim_account') }}
),

contact_totals as (
    select
        account_id,
        count(*) as contact_count
    from {{ ref('int_contacts_resolved') }}
    group by account_id
),

case_totals as (
    select
        account_id,
        count(*) as cases_total,
        sum(case when is_closed then 0 else 1 end) as cases_open,
        sum(case when is_closed then 1 else 0 end) as cases_closed,
        sum(case when is_escalated then 1 else 0 end) as cases_escalated,
        sum(case when priority = 'High' then 1 else 0 end) as cases_high_priority,
        avg(case when is_closed then hours_to_close end) as avg_hours_to_close
    from {{ ref('stg_gold__fact_case') }}
    group by account_id
),

usage_totals as (
    select
        account_id,
        count(*) as lifetime_usage_events,
        sum(units) as lifetime_usage_units,
        sum(amount_aud) as lifetime_usage_aud
    from {{ ref('stg_gold__fact_usage') }}
    group by account_id
),

latest_month as (
    select
        account_id,
        month_start as latest_month_start,
        commit_status as latest_commit_status,
        utilisation_pct as latest_utilisation_pct
    from (
        select
            account_id,
            month_start,
            commit_status,
            utilisation_pct,
            row_number() over (partition by account_id order by month_start desc) as rn
        from {{ ref('mart_account_monthly_health') }}
    ) ranked
    where rn = 1
)

select
    a.account_id,
    a.account_id = 'UNKNOWN' as is_unknown_account,
    a.account_name,
    a.account_type,
    a.industry,
    a.billing_state,
    a.billing_country,
    a.rating,
    a.revenue_band,
    a.contract_tier,
    a.created_at,
    coalesce(ct.contact_count, 0) as contact_count,
    coalesce(c.cases_total, 0) as cases_total,
    coalesce(c.cases_open, 0) as cases_open,
    coalesce(c.cases_closed, 0) as cases_closed,
    coalesce(c.cases_escalated, 0) as cases_escalated,
    coalesce(c.cases_high_priority, 0) as cases_high_priority,
    c.avg_hours_to_close,
    coalesce(u.lifetime_usage_events, 0) as lifetime_usage_events,
    coalesce(u.lifetime_usage_units, 0) as lifetime_usage_units,
    coalesce(u.lifetime_usage_aud, 0) as lifetime_usage_aud,
    lm.latest_month_start,
    lm.latest_commit_status,
    lm.latest_utilisation_pct
from accounts a
left join contact_totals ct on a.account_id = ct.account_id
left join case_totals c on a.account_id = c.account_id
left join usage_totals u on a.account_id = u.account_id
left join latest_month lm on a.account_id = lm.account_id