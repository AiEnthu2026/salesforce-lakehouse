{% macro clean_target_schema() %}
  {% do guard_ci_target() %}

  {% set rels = list_schema_relations() %}
  {{ log('cleaning ' ~ target.database ~ '.' ~ target.schema ~ ': ' ~ (rels | length) ~ ' relations', info=True) }}

  {% for row in rels %}
    {% set kind = 'view' if row['table_type'] == 'VIEW' else 'table' %}
    {% set fq = target.database ~ '.' ~ target.schema ~ '.' ~ row['table_name'] %}
    {{ log('dropping ' ~ kind ~ ' ' ~ fq, info=True) }}
    {% do run_query('drop ' ~ kind ~ ' if exists ' ~ fq) %}
  {% endfor %}
{% endmacro %}