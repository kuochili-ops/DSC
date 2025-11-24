
import pandas as pd
from utils.atc_mapper import map_to_atc

def match_taiwan_drugs(fda_data, csv_path):
    df = pd.read_csv(csv_path)
    results = []

    for item in fda_data:
        drug_name = item["title"].lower()  # 修正這裡
        matched = df[df["tw_ingredient"].str.lower().str.contains(drug_name)]

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
            "fda_title": item["title"],  # 改成 fda_title
            "taiwan_matches": enriched_matches
        })
    return results
