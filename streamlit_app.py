### 📦 完整 `streamlit_app.py`

```python
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import os

FDA_URL = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"

# ---------- 資料清理與正規化 ----------

def clean_text(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()

def normalize_brand(s):
    s = clean_text(s)
    s = re.sub(r"\b(tablets?|capsules?|injection|solution|concentrate|for infusion|pre-filled syringe)\b", "", s)
    return re.sub(r"[^\w\s]", "", s).strip()

SYNONYMS = {
    "hyoscine": "scopolamine",
    "scopolamine butylbromide": "scopolamine",
    "hyoscine n butylbromide": "scopolamine",
    "glatiramer": "glatiramer acetate",
    "lecanemab": "lecanemab",
    "clozapine": "clozapine",
    "cetirizine": "cetirizine",
    "levocetirizine": "levocetirizine",
    "methylphenidate": "methylphenidate",
    "amphetamine": "amphetamine",
}

def normalize_ingredient_token(tok):
    tok = clean_text(tok)
    for salt in ["hbr", "bromide", "acetate", "tartrate", "hcl", "maleate", "methylsulfate"]:
        tok = tok.replace(salt, "")
    tok = re.sub(r"[^\w\s]", "", tok).strip()
    return SYNONYMS.get(tok, tok)

def split_ingredients(s):
    parts = re.split(r";|,|/| and |\+|\|", str(s))
    return list({normalize_ingredient_token(p) for p in parts if p.strip()})

def ingredient_match(fda_list, tw_list):
    return bool(set(fda_list) & set(tw_list))

# ---------- FDA 抓取與解析 ----------

def fetch_html(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text

def parse_current_list(html):
    soup = BeautifulSoup(html, "html.parser")
    header = soup.find(lambda tag: tag.name in ["h2", "h3"] and "Current Drug Safety Communications" in tag.text)
    items = []
    if header:
        for a in header.find_next().find_all("a", href=True):
            txt = a.get_text(strip=True)
            m = re.match(r"(\d{2}[-/]\d{2}[-/]\d{4})\s+(.*)", txt)
            if m:
                date = m.group(1).replace("/", "-")
                title = m.group(2)
                href = a["href"]
                items.append({"date": date, "title": title, "href": href})
    return items

def extract_fields(title):
    t = title.lower()
    ingr = re.findall(r"\(([^)]+)\)", t)
    product = re.split(r"\(|-", title)[0].strip()
    return {
        "product": product,
        "ingredient_raw": ingr[0] if ingr else ""
    }

def build_fda_df(items):
    if not items:
        return pd.DataFrame(columns=["日期","品名","主成分","安全議題","用藥族群","注意事項與對策","source_title","source_url"])
    rows = []
    for it in items:
        fields = extract_fields(it["title"])
        ingr_list = split_ingredients(fields["ingredient_raw"])
        rows.append({
            "日期": it["date"],
            "品名": fields["product"],
            "主成分": ", ".join(ingr_list),
            "安全議題": "",
            "用藥族群": "",
            "注意事項與對策": "",
            "source_title": it["title"],
            "source_url": it["href"]
        })
    return pd.DataFrame(rows)

def fallback_seed():
    return pd.DataFrame([
        {"日期":"2025-08-28","品名":"Leqembi","主成分":"lecanemab","安全議題":"建議更早 MRI 監測","用藥族群":"阿茲海默症患者","注意事項與對策":"調整 MRI 頻率","source_title":"Leqembi (lecanemab)","source_url":FDA_URL},
        {"日期":"2025-08-27","品名":"Clozapine","主成分":"clozapine","安全議題":"移除 REMS 計畫","用藥族群":"精神分裂症患者","注意事項與對策":"依新標示調整監測","source_title":"Clozapine","source_url":FDA_URL},
        {"日期":"2025-08-11","品名":"Copaxone","主成分":"glatiramer acetate","安全議題":"過敏性休克警示","用藥族群":"多發性硬化症患者","注意事項與對策":"出現過敏徵兆立即停藥","source_title":"Copaxone (glatiramer acetate)","source_url":FDA_URL},
        {"日期":"2025-08-18","品名":"Transderm Scōp","主成分":"scopolamine","安全議題":"高溫併發症風險","用藥族群":"使用抗暈貼片者","注意事項與對策":"高溫環境慎用","source_title":"Transderm Scōp (scopolamine)","source_url":FDA_URL},
    ])

# ---------- 台灣 CSV 載入 ----------

@st.cache_data
def load_tw_data():
    path = os.path.join(os.path.dirname(__file__), "37_2c.csv")
    df = pd.read_csv(path)
    df["tw_e_brand_norm"] = df["tw_e_brand"].apply(normalize_brand)
    df["tw_ing_list"] = df["tw_ingredient"].apply(split_ingredients)
    return df

# ---------- 比對邏輯 ----------

def match_tw_products(fda_df, tw_df):
    matches = []
    for _, row in fda_df.iterrows():
        fda_brand = normalize_brand(row["品名"])
        fda_ing = split_ingredients(row["主成分"])
        brand_hits = tw_df[tw_df["tw_e_brand_norm"] == fda_brand]
        ing_hits = tw_df[tw_df["tw_ing_list"].apply(lambda lst: ingredient_match(fda_ing, lst))]
        hit_df = pd.concat([brand_hits, ing_hits]).drop_duplicates(subset=["tw_id"])
        for _, tw in hit_df.iterrows():
            matches.append({
                "日期": row["日期"],
                "FDA_品名": row["品名"],
                "FDA_主成分": row["主成分"],
                "藥證號碼": tw["tw_id"],
                "中文品名": tw["tw_c_brand"],
                "英文品名": tw["tw_e_brand"],
                "劑型": tw["tw_form"],
                "主成分": tw["tw_ingredient"],
                "藥商": tw["tw_company"],
            })
    return pd.DataFrame(matches)

# ---------- Streamlit UI ----------

st.set_page_config(page_title="FDA 通報解析與台灣品項比對", layout="wide")
st.title("💊 FDA 藥品安全通報解析與台灣品項比對")

st.info("正在抓取 FDA 通報資料…")
try:
    html = fetch_html(FDA_URL)
    items = parse_current_list(html)
    fda_df = build_fda_df(items)
    if fda_df.empty:
        st.warning("⚠️ FDA 網頁解析失敗，已載入 2025 種子資料。")
        fda_df = fallback_seed()
    else:
        st.success(f"已解析 FDA 通報 {len(fda_df)} 筆")
except Exception as e:
    st.error(f"FDA 網頁抓取失敗：{e}")
    fda_df = fallback_seed()

st.subheader("FDA Current Drug Safety Communications")
cols = [c for c in ["日期","品名","主成分","source_title"] if c in fda_df.columns]
st.dataframe(fda_df[cols], use_container_width=True)

st.info("正在載入台灣品項資料…")
try:
    tw_df = load_tw_data()
    st.success(f"已載入台灣品項 {len(tw_df)} 筆")
except Exception as e:
    st.error(f"CSV 載入失敗：{e}")
    tw_df = pd.DataFrame()

if not fda_df.empty and not tw_df.empty:
    match_df = match_tw_products(fda_df, tw_df)
    st.subheader(f"✅ 成功比對結果（{len(match_df)} 筆）")
    st.dataframe(match_df[
        ["日期","FDA_品名","FDA_主成分","藥證號碼","中文品名","英文品名","劑型","主成分","藥商"]
    ], use_container_width=True)

    matched_keys = set(zip(match_df["日期"], match_df["FDA_品名"], match_df["FDA_主成分"]))
    unmatched = fda_df[~fda_df.apply(lambda r: (r["日期"], r["品名"], r["主成分"]) in matched_keys, axis=1)]
    st.subheader(f"⚠️ 未匹配 FDA 通報（{len(unmatched)} 筆）")
    st.dataframe(unmatched[["日期","品名","主成分","source_title"]], use_container_width=True)

    relevant_tokens = set()
    for ing in fda_df["主成分"].dropna():
        relevant_tokens.update(split_ingredients(ing))
    cand_tw = tw_df[tw_df["tw_ing_list"].apply(lambda lst: bool(set(lst) & relevant_tokens))]
    st.subheader(f"🔍 可能相關台灣品項（{len(cand_tw)} 筆）")
    st.dataframe(cand_tw[
        ["tw_id","tw_c_brand","tw_e_brand","tw_form","tw_ingredient","tw_company"]
    ], use_container_width=True)
