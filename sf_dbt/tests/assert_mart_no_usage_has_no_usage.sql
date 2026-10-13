select account_month_key, commit_status, usage_events
from {{ ref('mart_account_monthly_health') }}
where commit_status = 'no_usage' and coalesce(usage_events, 0) != 0