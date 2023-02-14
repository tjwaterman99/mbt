{% macro generate_alias_name(custom_alias_name=none, node=none) %}
{% if target.name == 'prod' %}
{{ "prod_" ~  node.name }}
{% else %}
{{ node.name }}
{% endif %}
{% endmacro %}