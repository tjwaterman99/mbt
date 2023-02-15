{% macro generate_alias_name(custom_alias_name=none, node=none) %}
{{ target.name ~ '_' ~ node.name }} 
{% endmacro %}