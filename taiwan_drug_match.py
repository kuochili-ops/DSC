
import pandas as pd
from utils.atc_mapper import map_to_atc

def match_taiwan_drugs(fda_data, csv_path):
    df = pd.read_csv(csv_path)

    # 確保欄位沒有 NaN
    df["tw_ingredient"] = df["tw_ingredient"].fillna("").astype(str)

    results = []

    for item in fda_data:
        drug_name = item.get("title", "").lower().strip()

        # 如果 drug_name 是空字串，直接跳過
        if not drug_name:
            results.append({"fda_title": item.get("title", ""), "taiwan_matches": []})
            continue

        # 使用 na=False 避免 NaN 造成錯誤
        matched = df[df["tw_ingredient"].str.lower().str.contains(drug_name, na=False)]

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
            "fda_title": item.get("title", ""),
            "taiwan_matches": enriched_matches
        })

    return results
