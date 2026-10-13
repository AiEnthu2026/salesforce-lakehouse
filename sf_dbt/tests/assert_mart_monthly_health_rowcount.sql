select mart_rows, source_rows
from (
    select
        (select count(*) from {{ ref('mart_account_monthly_health') }}) as mart_rows,
        (select count(*) from {{ ref('stg_gold__agg_account_monthly') }}) as source_rows
)
where mart_rows != source_rows