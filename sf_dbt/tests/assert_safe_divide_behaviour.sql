select 'zero denominator should be null' as failure
from (select {{ safe_divide('1', '0') }} as v)
where v is not null

union all

select 'null denominator should be null' as failure
from (select {{ safe_divide('1', 'cast(null as int)') }} as v)
where v is not null

union all

select '6 divided by 3 should be 2' as failure
from (select {{ safe_divide('6', '3') }} as v)
where v is null or v != 2