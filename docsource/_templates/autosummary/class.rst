.. rst-class:: detail

{{ objname }}
{{ underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

    {% block methods %}
    {% if methods %}

    .. rubric:: Methods

    .. autosummary::
        :toctree:

    {% for item in methods %}
    {%- if item not in inherited_members %}
        ~{{ name }}.{{ item }}
    {%- endif %}
    {%- endfor %}

    .. rubric:: Inherited Methods

    .. autosummary::
        :toctree:

    {% for item in methods %}
    {%- if item in inherited_members %}
        ~{{ name }}.{{ item }}
    {%- endif %}
    {%- endfor %}

    {% endif %}
    {% endblock %}
