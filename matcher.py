import pandas as pd

def match_drugs(fda_df, tw_df):
    """
    比對 FDA 公告與台灣藥品資料
    fda_df: DataFrame (FDA 公告)
    tw_df: DataFrame 或 CSV 檔案路徑 (台灣藥品)
    """

    # 如果 tw_df 是檔案路徑，就讀檔；如果已經是 DataFrame，就直接用
    if isinstance(tw_df, (str, bytes)):
        tw_df = pd.read_csv(tw_df)

    # 確保欄位存在
    required_cols = ["tw_id", "tw_c_brand", "tw_e_brand", "tw_form", "tw_ingredient", "tw_company"]
    for col in required_cols:
        if col not in tw_df.columns:
            raise ValueError(f"台灣藥品資料缺少必要欄位：{col}")

    if "title" not in fda_df.columns:
        raise ValueError("FDA 公告需要 'title' 欄位")

    results = []
    for _, fda_row in fda_df.iterrows():
        fda_title = str(fda_row["title"]).lower()

        # 先比對主成分
        matched = tw_df[tw_df["tw_ingredient"].astype(str).str.lower().apply(lambda x: x in fda_title)]

        # 如果主成分沒找到，再比對英文品名
        if matched.empty:
            matched = tw_df[tw_df["tw_e_brand"].astype(str).str.lower().apply(lambda x: x in fda_title)]

        if not matched.empty:
            for _, tw_row in matched.iterrows():
                results.append({
                    "date": fda_row.get("date", ""),
                    "fda_title": fda_row["title"],
                    "fda_url": fda_row.get("url", ""),
                    "tw_id": tw_row["tw_id"],
                    "tw_c_brand": tw_row["tw_c_brand"],
                    "tw_e_brand": tw_row["tw_e_brand"],
                    "tw_ingredient": tw_row["tw_ingredient"],
                    "tw_company": tw_row["tw_company"]
                })
        else:
            results.append({
                "date": fda_row.get("date", ""),
                "fda_title": fda_row["title"],
                "fda_url": fda_row.get("url", ""),
                "tw_id": "",
                "tw_c_brand": "",
                "tw_e_brand": "",
                "tw_ingredient": "",
                "tw_company": ""
            })

    return pd.DataFrame(results)
