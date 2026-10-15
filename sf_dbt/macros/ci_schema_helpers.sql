{# Shared by the CI cleanup macros: guards plus the schema listing #}

{% macro guard_ci_target() %}
  {% if target.name != 'staging' %}
    {{ exceptions.raise_compiler_error('refusing to run on target ' ~ target.name ~ ': only staging is allowed') }}
  {% endif %}
  {% if not target.schema.startswith('dbt_') %}
    {{ exceptions.raise_compiler_error('refusing to run on non-dbt schema: ' ~ target.schema) }}
  {% endif %}
{% endmacro %}


{% macro list_schema_relations() %}
  {% set list_sql %}
    select table_name, table_type
    from {{ target.database }}.information_schema.tables
    where table_schema = '{{ target.schema }}'
  {% endset %}
  {% set result = run_query(list_sql) %}
  {{ return(result.rows) }}
{% endmacro %}