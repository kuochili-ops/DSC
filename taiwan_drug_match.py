
import re
import pandas as pd

def extract_drug_name(title):
    if not title:
        return ""
    match = re.search(r"\((.*?)\)", title)
    if match:
        return match.group(1).lower()
    return title.split()[0].lower()

def match_taiwan_drugs(fda_data, csv_path):
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

        matched = df[df["tw_ingredient"].str.lower().str.contains(drug_name, na=False)]
        if matched.empty:
            matched = df[df["tw_e_brand"].str.lower().str.contains(drug_name, na=False)]

        enriched_matches = []
        for _, row in matched.iterrows():
            enriched_matches.append({
                "tw_id": row["tw_id"],
                "tw_c_brand": row["tw_c_brand"],
                "tw_e_brand": row["tw_e_brand"],
                "tw_form": row["tw_form"],
                "tw_company": row["tw_company"]
            })

        results.append({"fda_title": title, "taiwan_matches": enriched_matches})

    return results
