
import pandas as pd
from rapidfuzz import fuzz, process

def match_drugs(fda_df, taiwan_csv_path, threshold=80):
    # 讀取台灣藥品資料
    tw_df = pd.read_csv(taiwan_csv_path)

    # 標準化欄位
    tw_df['tw_ingredient'] = tw_df['tw_ingredient'].str.upper().str.strip()

    results = []
    for _, row in fda_df.iterrows():
        fda_title = row['title'].upper()
        # 嘗試從 FDA 標題中找出藥品名稱（簡單處理，可再優化）
        matched = process.extractOne(fda_title, tw_df['tw_ingredient'], scorer=fuzz.partial_ratio)
        if matched and matched[1] >= threshold:
            tw_match = tw_df[tw_df['tw_ingredient'] == matched[0]].iloc[0]
            results.append({
                "FDA_Date": row['date'],
                "FDA_Title": row['title'],
                "FDA_Link": row['link'],
                "TW_Match": "是",
                "TW_Drug": tw_match['tw_c_brand'],
                "TW_Ingredient": tw_match['tw_ingredient'],
                "TW_Form": tw_match['tw_form'],
                "TW_Company": tw_match['tw_company']
            })
        else:
            results.append({
                "FDA_Date": row['date'],
                "FDA_Title": row['title'],
                "FDA_Link": row['link'],
                "TW_Match": "否",
                "TW_Drug": "",
                "TW_Ingredient": "",
                "TW_Form": "",
                "TW_Company": ""
            })

