
import re
import pandas as pd
from utils.atc_mapper import map_to_atc

def extract_drug_name(title):
    """
    從 FDA 標題中抽取藥品名稱：
    - 優先取括號內的內容（通常是成分名）
    - 如果沒有括號，取第一個單字（簡單策略）
    """
    if not title:
        return ""
    match = re.search(r"\((.*?)\)", title)
    if match:
        return match.group(1).lower()
    return title.split()[0].lower()

def match_taiwan_drugs(fda_data, csv_path):
    """
    比對 FDA 通報藥品與台灣藥品許可證資料
    :param fda_data: FDA 最新通報列表
    :param csv_path: 台灣藥品許可證 CSV 檔案路徑
    :return: 比對結果列表
    """
    # 讀取台灣藥品資料
    df = pd.read_csv(csv_path)
    df["tw_ingredient"] = df["tw_ingredient"].fillna("").astype(str)
    df["tw_e_brand"] = df["tw_e_brand"].fillna("").astype(str)

    results = []

    for item in fda_data:
        title = item.get("title", "")
        drug_name = extract_drug_name(title)

        if not drug_name:
            results.append({"fda_title": title, "taiwan_matches": []})
            continue

        # Step 1: 先比對主成分
        matched = df[df["tw_ingredient"].str.lower().str.contains(drug_name, na=False)]

        # Step 2: 如果沒找到，再比對英文品名
        if matched.empty:
            matched = df[df["tw_e_brand"].str.lower().str.contains(drug_name, na=False)]

        enriched_matches = []
        for _, row in matched.iterrows():
            atc_info = map_to_atc(row["tw_ingredient"])
            enriched_matches.append({
                "tw_id": row["tw_id"],
                "tw_c_brand": row["tw_c_brand"],
                "tw_e_brand": row["tw_e_brand"],
                "tw_form": row["tw_form"],
                "tw_company": row["tw_company"],
                "ATC_code": atc_info["ATC_code"],
                "ATC_class": atc_info["ATC_class"]
            })

        results.append({
            "fda_title": title,
            "taiwan_matches": enriched_matches
        })

    return results
