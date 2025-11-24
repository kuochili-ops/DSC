
import pandas as pd

def match_taiwan_drugs(fda_data, csv_path="37_2c.csv"):
    df = pd.read_csv(csv_path)
    df["tw_ingredient"] = df["tw_ingredient"].fillna("").astype(str)

    results = []
    for item in fda_data:
        ingredient = item.get("ingredient", "").lower().strip()
        if not ingredient:
            results.append({"fda_title": item.get("title", ""), "matches": []})
            continue

        matched = df[df["tw_ingredient"].str.lower().str.contains(ingredient, na=False)]

        enriched_matches = []
        for _, row in matched.iterrows():
            enriched_matches.append({
                "tw_id": row["tw_id"],
                "tw_c_brand": row["tw_c_brand"],
                "tw_e_brand": row["tw_e_brand"],
                "tw_form": row["tw_form"],
                "tw_company": row["tw_company"]
            })

        results.append({
            "fda_title": item.get("title", ""),
            "ingredient": ingredient,
            "matches": enriched_matches
        })

    return results
