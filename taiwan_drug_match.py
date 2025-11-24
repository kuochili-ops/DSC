
import pandas as pd

def match_taiwan_drugs(fda_data, csv_path):
    df = pd.read_csv(csv_path)
    results = []

    for item in fda_data:
        drug_name = item["drug_name"].lower()
        matched = df[df["tw_ingredient"].str.lower().str.contains(drug_name)]
        results.append({
            "fda_drug": item["drug_name"],
            "taiwan_matches": matched.to_dict(orient="records")
        })
    return results
