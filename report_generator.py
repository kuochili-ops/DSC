
from jinja2 import Template

def create_html_report(fda_data, taiwan_data):
    template = """
    <h2>FDA 最新藥品安全通訊摘要</h2>
    {% for item in taiwan_data %}
        <h3>{{ item.fda_drug }}</h3>
        <ul>
        {% for drug in item.taiwan_matches %}
            <li>{{ drug.tw_id }} | {{ drug.tw_c_brand }} | {{ drug.tw_e_brand }} | {{ drug.tw_form }} | {{ drug.tw_company }}</li>
        {% endfor %}
        </ul>
    {% endfor %}
    """
    return Template(template).render(taiwan_data=taiwan_data)
