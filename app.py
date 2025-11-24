
from fda_scraper import fetch_fda_drug_safety
from matcher import match_drugs

# 抓取 FDA 公告
fda_df = fetch_fda_drug_safety()

# 比對台灣藥品資料
result_df = match_drugs(fda_df, "data/37_2c.csv")

# 輸出 Excel
result_df.to_excel("FDA_TW_Match.xlsx", index=False)
print("比對完成，已輸出 FDA_TW_Match.xlsx")
