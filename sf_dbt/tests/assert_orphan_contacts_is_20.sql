select orphan_count
from (
    select count(*) as orphan_count
    from {{ ref('int_contacts_resolved') }}
    where is_orphan_account
)
where orphan_count != 200