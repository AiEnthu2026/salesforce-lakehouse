select
    contact_id,
    account_id,
    title,
    department,
    lead_source,
    mailing_state,
    mailing_country,
    created_at
from {{ source('gold', 'dim_contact') }}