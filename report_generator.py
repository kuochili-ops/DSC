
from jinja2 import Template
from collections import defaultdict

def create_html_report(taiwan_data):
    atc_groups = defaultdict(list)
    for item in taiwan_data:
        for drug in item["taiwan_matches"]:
            atc_groups[drug["ATC_class"]].append(drug)

    template = """
    <h2>FDA 最新藥品安全通訊摘要</h2>
    {% for atc_class, drugs in atc_groups.items() %}
        <h3>{{ atc_class }}</h3>
        <table border="1">
            <tr><th>藥證字號</th><th>中文品名</th><th>英文品名</th><th>劑型</th><th>藥商</th><th>ATC code</th></tr>
            {% for drug in drugs %}
                <tr>
                    <td>{{ drug.tw_id }}</td>
                    <td>{{ drug.tw_c_brand }}</td>
                    <td>{{ drug.tw_e_brand }}</td>
                    <td>{{ drug.tw_form }}</td>
                    <td>{{ drug.tw_company }}</td>
                    <td>{{ drug.ATC_code }}</td>
                </tr>
            {% endfor %}
        </table>
    {% endfor %}
    """
    return Template(template).render(atc_groups=atc_groups)
