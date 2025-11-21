import streamlit as st
import pandas as pd
import requests
import re
import os
from bs4 import BeautifulSoup

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
        ul = header.find_next("ul")
        for li in ul.find_all("li"):
            a = li.find("a", href=True)
            if not a:
                continue
            li_text = li.get_text(" ", strip=True)
            m_date = re.match(r"^\s*(\d{2}-\d{2}-\d{4})\b", li_text)
            date = m_date.group(1) if m_date else ""
            title = a.get("title") or a.get_text(strip=True)
            href = a["href"]
            if href.startswith("/"):
                href = "https://www.fda.gov" + href
            items.append({"date": date, "title": title, "href": href})
    return items

EXCLUDE_TOKENS = {"rems", "program", "strategy", "risk", "evaluation", "mitigation", "warning", "labeling"}
KNOWN_INGREDIENTS = set(SYNONYMS.keys())

def extract_fields(title):
    t = title.lower()
    paren = re.findall(r"\(([^)]+)\)", t)
    if paren:
        ing_raw = paren[-1]
        ing_list = split_ingredients(ing_raw)
        ing_list = [tok for tok in ing_list if tok not in EXCLUDE_TOKENS]
    else:
        tokens = re.findall(r"[a-zA-Z][a-zA-Z\-]+", t)
        norm_tokens = [normalize_ingredient_token(x) for x in tokens]
        ing_list = sorted({tok for tok in norm_tokens if tok in KNOWN_INGREDIENTS and tok not in EXCLUDE_TOKENS})
    if paren:
        product = title.split("(")[0].strip()
    else:
        product = ""
        for k in KNOWN_INGREDIENTS:
            if re.search(rf"\b{k}\b", t):
                m = re.search(rf"\b({k})\b", t)
                if m:
                    product = m.group(1)
                    break
        if not product:
            product = title.split(":")[0].split("–")[0].split("-")[0].strip()
    return {"product": product, "ingredient_list": ing_list}

def build_fda_df(items):
    if not items:
        return pd.DataFrame(columns=["日期","品名","主成分","安全議題","用藥族群","注意事項與對策","source_title","source_url"])
    rows = []
    for it in items:
        fields = extract_fields(it["title"])
        rows.append({
            "日期": it["date"],
            "品名": fields["product"],
            "主成分": ", ".join(fields["ingredient_list"]),
            "安全議題": "",
            "用藥族群": "",
            "注意事項與對策": "",
            "source_title": it["title"],
            "source_url": it["href"]
        })
    return pd.DataFrame(rows)

def fallback_seed():
    return pd.DataFrame([
        {"日期":"2025-08-28","品名":"Leqembi","主成分":"lecanemab","安全議題":"建議更早 MRI 監測","用藥族群":"阿茲海默症患者","注意事項與對策":"調整 MRI 頻率","source_title":"Leqembi (lecanemab)","source_url":"https://www.fda.gov/drugs/drug-safety-and-availability/fda-recommend-additional-earlier-mri-monitoring-patients-alzheimers-disease-taking-leqembi-lecanemab"},
        {"日期":"2025-08-27","品名":"Clozapine","主成分":"clozapine","安全議題":"移除 REMS 計畫","用藥族群":"精神分裂症患者","注意事項與對策":"依新標示調整監測","source_title":"Clozapine","source_url":"https://www.fda.gov/drugs/drug-safety-and-availability/fda-removes-risk-evaluation-and-mitigation-strategy-rems-program-antipsychotic-drug-clozapine"},
        {"日期":"2025-01-22","品名":"Copaxone","主成分":"glatiramer acetate","安全議題":"過敏性休克警示","用藥族群":"多發性硬化症患者","注意事項與對策":"出現過敏徵兆立即停藥","source_title":"Copaxone (glatiramer acetate)","source_url":"https://www.fda.gov/drugs/drug-safety-and-availability/fda-adds-boxed-warning-about-rare-serious-allergic-reaction-called-anaphylaxis-multiple-sclerosis"},
        {"日期":"2025-06-18","品名":"Transderm Scōp","主成分":"scopolamine","安全議題":"高溫併發症風險","用藥族群":"使用抗暈貼片者","注意事項與對策":"高溫環境慎用","source_title":"Transderm Scōp (scopolamine)","source_url":"https://www.fda.gov/drugs/drug-safety-and-availability/fda-adds-warning-about-serious-risk-heat-related-complications-antinausea-patch-transderm-scop"},
    ])

@st.cache_data
def load_tw_data():
    path = os.path.join(os.path.dirname(__file__), "37_2c.csv")
    df = pd.read_csv(path)
    df["tw_e_brand_norm"] = df["tw_e_brand"].apply(normalize_brand)
    df["tw_ing_list"] = df["tw_ingredient"].apply(split_ingredients)
    return df

def match_tw_products(fda_df, tw_df):
    matches = []
    for _, row in fda_df.iterrows():
        fda_brand = normalize_brand(row["品名"])

        # 只做品牌比對
        brand_hits = tw_df[tw_df["tw_e_brand_norm"] == fda_brand]
        for _, tw in brand_hits.iterrows():
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
                "比對方式": "品牌命中"
            })
    return pd.DataFrame(matches)
