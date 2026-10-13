select account_month_key, escalation_rate
from {{ ref('mart_account_monthly_health') }}
where escalation_rate < 0 or escalation_rate > 1