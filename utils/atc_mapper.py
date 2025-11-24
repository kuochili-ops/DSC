
import pandas as pd

# 載入 ATC 對應表（請建立 atc_mapping.csv）
atc_df = pd.read_csv("atc_mapping.csv")

def map_to_atc(ingredient):
    ingredient = ingredient.lower()
    match = atc_df[atc_df["ingredient"].str.lower() == ingredient]
    if not match.empty:
        return {
            "ATC_code": match.iloc[0]["ATC_code"],
            "ATC_class": match.iloc[0]["ATC_class"]
        }
    else:
        return {
            "ATC_code": "N/A",
            "ATC_class": "Unknown"
        }
