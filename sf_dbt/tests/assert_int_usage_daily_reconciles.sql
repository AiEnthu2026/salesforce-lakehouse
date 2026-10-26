select 1
from (
    select sum(amount_aud) as a from {{ ref('int_usage_daily') }}
) i
cross join (
    select sum(amount_aud) as b from {{ ref('stg_gold__fact_usage') }}
) f
where abs(i.a - f.b) > 0.01