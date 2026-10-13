with contacts as (
    select * from {{ ref('stg_gold__dim_contact') }}
),

accounts as (
    select account_id from {{ ref('stg_gold__dim_account') }}
)

select
    c.contact_id,
    c.account_id as source_account_id,
    coalesce(a.account_id, 'UNKNOWN') as account_id,
    a.account_id is null as is_orphan_account,
    c.title,
    c.department,
    c.lead_source,
    c.mailing_state,
    c.mailing_country,
    c.created_at
from contacts c
left join accounts a
    on c.account_id = a.account_id