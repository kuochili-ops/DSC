from jinja2 import Template
import pandas as pd

def create_html_report(taiwan_data):
    template = """
    <h2>FDA 最新藥品安全通訊摘要</h2>
    {% for item in taiwan_data %}
        <h3>{{ item.fda_title }}</h3>
        {% if item.matches %}
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr>
                    <th>藥證字號</th>
                    <th>中文品名</th>
                    <th>英文品名</th>
                    <th>劑型</th>
                    <th>藥商</th>
                </tr>
                {% for drug in item.matches %}
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
            <p style="color:red;">未找到對應的台灣藥品</p>
        {% endif %}
        <hr>
    {% endfor %}
    """
    return Template(template).render(taiwan_data=taiwan_data)

def export_to_csv(taiwan_data, filename="FDA_Taiwan_Match.csv"):
    rows = []
    for item in taiwan_data:
        for drug in item["matches"]:
            rows.append({
                "FDA通報": item["fda_title"],
                "主成分": item["ingredient"],
                "藥證字號": drug["tw_id"],
                "中文品名": drug["tw_c_brand"],
                "英文品名": drug["tw_e_brand"],
                "劑型": drug["tw_form"],
                "藥商": drug["tw_company"]
            })
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False, encoding="utf-8-sig")
