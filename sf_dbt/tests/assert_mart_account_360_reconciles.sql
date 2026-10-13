select 'row count differs from dim_account' as failure
from (
    select
        (select count(*) from {{ ref('mart_account_360') }}) as a,
        (select count(*) from {{ ref('stg_gold__dim_account') }}) as b
) t
where a != b

union all

select 'lifetime usage differs from fact_usage' as failure
from (
    select
        (select sum(lifetime_usage_aud) from {{ ref('mart_account_360') }}) as a,
        (select sum(amount_aud) from {{ ref('stg_gold__fact_usage') }}) as b
) t
where abs(a - b) > 0.01

union all

select 'case count differs from fact_case' as failure
from (
    select
        (select sum(cases_total) from {{ ref('mart_account_360') }}) as a,
        (select count(*) from {{ ref('stg_gold__fact_case') }}) as b
) t
where a != b

union all

select 'contact count differs from int_contacts_resolved' as failure
from (
    select
        (select sum(contact_count) from {{ ref('mart_account_360') }}) as a,
        (select count(*) from {{ ref('int_contacts_resolved') }}) as b
) t
where a != b