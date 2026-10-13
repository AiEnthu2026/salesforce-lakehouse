{% macro write_probe(schema_name) %}
    {% set probe_sql %}
        create or replace table {{ env_var('DBT_CATALOG') }}.{{ schema_name }}.dbt_write_probe as select 1 as x
    {% endset %}
    {% do run_query(probe_sql) %}
    {{ log('create table in ' ~ schema_name ~ ' SUCCEEDED', info=True) }}
{% endmacro %}

{% macro drop_probe(schema_name) %}
    {% do run_query('drop table if exists ' ~ env_var('DBT_CATALOG') ~ '.' ~ schema_name ~ '.dbt_write_probe') %}
    {{ log('probe table in ' ~ schema_name ~ ' dropped', info=True) }}
{% endmacro %}