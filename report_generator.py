
from jinja2 import Template

def create_html_report(taiwan_data):
    template = """
    <h2>FDA 最新藥品安全通訊摘要</h2>
    {% for item in taiwan_data %}
        <h3>{{ item.fda_title }}</h3>
        {% if item.taiwan_matches %}
            <table border="1">
                <tr><th>藥證字號</th><th>中文品名</th><th>英文品名</th><th>劑型</th><th>藥商</th></tr>
                {% for drug in item.taiwan_matches %}
                    <tr>
                        <td>{{ drug.tw_id }}</td>
                        <td>{{ drug.tw_c_brand }}</td>
                        <td>{{ drug.tw_e_brand }}</td>
                        <td>{{ drug.tw_form }}</td>
                        <td>{{ drug.tw_company }}</td>
                    </tr>
                {% endfor %}
            </table>
        {% else %}
            <p>未找到對應的台灣藥品</p>
        {% endif %}
    {% endfor %}
    """
    return Template(template).render(taiwan_data=taiwan_data)
