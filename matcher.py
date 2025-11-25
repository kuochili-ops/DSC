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
    if "title" not in fda_df.columns:
        raise ValueError("FDA 公告需要 'title' 欄位")
    if "商品名" not in tw_df.columns:
        raise ValueError("台灣藥品需要 '商品名' 欄位")

    results = []
    for _, fda_row in fda_df.iterrows():
        fda_title = str(fda_row["title"]).lower()

        # 模糊比對：公告標題只要包含藥品名稱就算匹配
        matched = tw_df[tw_df["商品名"].astype(str).str.lower().apply(lambda x: x in fda_title)]

        if not matched.empty:
            for _, tw_row in matched.iterrows():
                results.append({
                    "date": fda_row.get("date", ""),
                    "fda_title": fda_row["title"],
                    "fda_url": fda_row.get("url", ""),
                    "tw_drug": tw_row["商品名"],
                    "tw_license": tw_row.get("許可證字號", "")
                })
        else:
            results.append({
                "date": fda_row.get("date", ""),
                "fda_title": fda_row["title"],
                "fda_url": fda_row.get("url", ""),
                "tw_drug": "",
                "tw_license": ""
            })

    return pd.DataFrame(results)
