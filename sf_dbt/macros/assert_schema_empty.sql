{% macro assert_schema_empty() %}
  {% do guard_ci_target() %}

  {% set rels = list_schema_relations() %}

  {# append mutates the list; a set inside a loop would not change the outer variable #}
  {% set leftovers = [] %}
  {% for row in rels %}
    {% do leftovers.append(row['table_name']) %}
  {% endfor %}

  {% if leftovers | length > 0 %}
    {{ exceptions.raise_compiler_error(
         target.database ~ '.' ~ target.schema ~ ' is not empty: ' ~ (leftovers | join(', '))
    ) }}
  {% endif %}

  {{ log(target.database ~ '.' ~ target.schema ~ ' is empty', info=True) }}
{% endmacro %}