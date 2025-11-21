# streamlit_app.py
import re
import io
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st
from urllib.parse import urljoin

FDA_URL = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"

# ---------- Normalization & utilities ----------

def clean_text(s: str) -> str:
    if pd.isna(s):
        return ""
    s = str(s)
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s

def normalize_brand(s: str) -> str:
    s = clean_text(s).lower()
    # remove typical dosage/form tails
    s = re.sub(r"\b(tablets?|capsules?|injection|solution|concentrate|for infusion|pre-filled syringe|f\.?c\.?|s\.?c\.?)\b", "", s)
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# Keep only core moiety for ingredients and split multi-ingredients
SALT_WORDS = [
    "hbr", "hydrobromide", "bromide", "butylbromide", "butyl bromide", "methobromide",
    "tartrate", "maleate", "methylsulfate", "methy sulfate", "hcl", "hydrochloride",
    "acetate", "anhydrous", "monohydrate"
]

SYNONYMS = {
    # equivalence classes
    "hyoscine": "scopolamine",
    "scopolamine": "scopolamine",
    "scopolamine butylbromide": "scopolamine",
    "scopolamine butyl bromide": "scopolamine",
    "hyoscine n butylbromide": "scopolamine",
    "hyoscine butylbromide": "scopolamine",
    "n methylscopolamine": "methscopolamine",
    "methylscopolamine": "methscopolamine",
    "methscopolamine": "methscopolamine",
    "glatiramer": "glatiramer acetate",
    "glatiramer acetate": "glatiramer acetate",
    "lecanemab": "lecanemab",
    "clozapine": "clozapine",
    "cetirizine": "cetirizine",
    "levocetirizine": "levocetirizine",
    "methylphenidate": "methylphenidate",
    "amphetamine": "amphetamine",
    "dextroamphetamine": "amphetamine",
}

def normalize_ingredient_token(tok: str) -> str:
    tok = clean_text(tok).lower()
    tok = tok.replace("n-", "n ").replace("n –", "n ")
    # remove salt/descriptor words
    for w in SALT_WORDS:
        tok = re.sub(rf"\b{re.escape(w)}\b", " ", tok)
    tok = re.sub(r"[^\w\s]", " ", tok)
    tok = re.sub(r"\s+", " ", tok).strip()
    # fold synonyms
    tok = SYNONYMS.get(tok, tok)
    return tok

def split_ingredients(s: str) -> list:
    if pd.isna(s) or not str(s).strip():
        return []
    # split by common delimiters
    parts = re.split(r";|,|/| and |\+|\|", str(s), flags=re.IGNORECASE)
    normalized = []
    for p in parts:
        p = normalize_ingredient_token(p)
        if p:
            normalized.append(p)
    # dedup preserving order
    seen = set()
    out = []
    for p in normalized:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out

def ingredient_match(fda_core: list, tw_core: list) -> bool:
    # any overlap
    return bool(set(fda_core) & set(tw_core))

# ---------- FDA scraping ----------

def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text


def parse_current_list(html: str) -> list:
    """
    Parse the 'Current Drug Safety Communications' section.
    Returns list of dicts: {date, title, href}
    """
    soup = BeautifulSoup(html, "html.parser")
    current_header = soup.find(lambda tag: tag.name in ["h2", "h3"] and "Current Drug Safety Communications" in tag.get_text(strip=True))
    items = []
    if current_header:
        # Assuming following sibling contains list items or paragraphs with links and dates
        container = current_header.find_next()
        # Look for links with date prefixes in text
        for a in container.find_all("a", href=True):
            txt = a.get_text(" ", strip=True)
            # Dates may be like "08-28-2025 ..." or "12-12-2024 ..." or "11/28/2023 ..."
            m = re.match(r"(\d{2}[-/]\d{2}[-/]\d{4})\s+(.*)", txt)
            if m:
                date = m.group(1).replace("/", "-")
                title = m.group(2)
                href = urljoin(FDA_URL, a["href"])
                items.append({"date": date, "title": title, "href": href})
    return items

def extract_fields_from_title(title: str) -> dict:
    """
    Heuristic to get product and ingredient from the title.
    """
    t = clean_text(title)
    # Ingredient in parentheses like "(lecanemab)" or "(scopolamine transdermal system)"
    ingr = None
    pm = re.search(r"\(([^)]+)\)", t)
    if pm:
        cand = pm.group(1)
        # remove trailing qualifiers like "transdermal system"
        cand = re.sub(r"\b(transdermal system|patch|system)\b", "", cand, flags=re.I)
        ingr = cand.strip()
    # Product names: before parentheses or brand words inside
    # e.g., "Leqembi", "Transderm Scōp", "Copaxone", "Clozapine" (class/program)
    # Try to capture a capitalized token before parentheses
    product = None
    if pm:
        before = t[:pm.start()].strip()
        # take last capitalized word group
        m2 = re.search(r"([A-Z][A-Za-z0-9’'\- ]+)$", before)
        if m2:
            product = m2.group(1).strip()
    # If not, search for known brands in title
    known_brands = ["Leqembi", "Clozapine", "Transderm Scōp", "Zyrtec", "Xyzal", "Copaxone", "Glatopa"]
    for kb in known_brands:
        if kb.lower() in t.lower():
            product = kb
            break
    return {
        "product": product,
        "ingredient_raw": ingr
    }

def parse_dsc_page(url: str) -> dict:
    """
    Fetch the DSC page and try to extract issue, population, guidance.
    Best-effort heuristics; returns empty strings if not found.
    """
    try:
        html = fetch_html(url)
    except Exception:
        return {"issue": "", "population": "", "guidance": ""}
    soup = BeautifulSoup(html, "html.parser")
    # Collect paragraphs
    paras = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    text = " ".join(paras)

    # Issue: look for phrases like "adds warning", "Boxed Warning", "requires", "recommends"
    m_issue = re.search(
        r"(adds Boxed Warning|adds warning|Boxed Warning|requires(?: expanded)? labeling|recommends .* MRI monitoring|removes REMS|requiring .* update|added .* warning|warning about .*|risk of .*|serious .* side effects)",
        text, flags=re.I)
    issue = m_issue.group(0) if m_issue else ""

    # Population: look for "patients" phrases
    m_pop = re.search(r"(patients? [^\.]{0,120})\.", text, flags=re.I)
    population = m_pop.group(1) if m_pop else ""

    # Guidance: look for sentences starting with "Patients should", "Health care professionals should", "Do not", "Monitor"
    m_guid = re.search(
        r"((Patients|Health care professionals) should[^\.]{0,200}\.|Monitor[^\.]{0,200}\.|Do not[^\.]{0,200}\.)",
        text, flags=re.I)
    guidance = m_guid.group(1) if m_guid else ""

    return {
        "issue": issue.strip(),
        "population": population.strip(),
        "guidance": guidance.strip()
    }

# ---------- Matching pipeline ----------

def build_fda_summary(items: list, seed_2025: bool = False) -> pd.DataFrame:
    rows = []
    for it in items:
        fields = extract_fields_from_title(it["title"])
        dsc = parse_dsc_page(it["href"])
        fda_ingrs = split_ingredients(fields["ingredient_raw"] or "")
        rows.append({
            "日期": it["date"],
            "品名": fields["product"] or "",
            "主成分": ", ".join(fda_ingrs),
            "安全議題": dsc["issue"],
            "用藥族群": dsc["population"],
            "注意事項與對策": dsc["guidance"],
            "source_title": it["title"],
            "source_url": it["href"],
        })
    df = pd.DataFrame(rows)

    # Optional seed: if Current list is unexpectedly short, inject known 2025 items (title-only)
    if seed_2025 and (len(df) == 0 or df["日期"].max() < "2025-01-01"):
        seeds = [
            ("2025-08-28", "FDA to recommend additional, earlier MRI monitoring for patients with Alzheimer’s disease taking Leqembi (lecanemab)"),
            ("2025-08-27", "FDA removes risk evaluation and mitigation strategy (REMS) program for the antipsychotic drug Clozapine"),
            ("2025-08-25", "FDA is requiring opioid pain medicine manufacturers to update prescribing information for oral opioids"),
            ("2025-08-21", "FDA requires expanded labeling about risk of serious mental health side effects for 6 years taking extended-release stimulants for ADHD"),
            ("2025-08-18", "Boxed warning about serious risk of heat-related complications added to the antipsychotic patch Transderm Scōp (scopolamine transdermal system)"),
            ("2025-08-14", "FDA requires warning about rare but severe itching after stopping long-term use of oral allergy medicines cetirizine or levocetirizine (Zyrtec, Xyzal, and other trade names)"),
            ("2025-08-11", "FDA adds Boxed Warning and medication guide about allergic reaction called anaphylaxis with the multiple sclerosis medicine glatiramer acetate (Copaxone, Glatopa)"),
        ]
        extra = []
        for dt, title in seeds:
            fields = extract_fields_from_title(title)
            fda_ingrs = split_ingredients(fields["ingredient_raw"] or "")
            extra.append({
                "日期": dt,
                "品名": fields["product"] or "",
                "主成分": ", ".join(fda_ingrs),
                "安全議題": "",
                "用藥族群": "",
                "注意事項與對策": "",
                "source_title": title,
                "source_url": FDA_URL,
            })
        df = pd.concat([df, pd.DataFrame(extra)], ignore_index=True)
    return df

def match_tw_products(fda_df: pd.DataFrame, tw_df: pd.DataFrame) -> pd.DataFrame:
    # Prepare TW columns
    tw_df = tw_df.rename(columns={
        "tw_id": "tw_id", "tw_c_brand": "tw_c_brand", "tw_e_brand": "tw_e_brand",
        "tw_form": "tw_form", "tw_ingredient": "tw_ingredient", "tw_company": "tw_company"
    })
    tw_df["tw_e_brand_norm"] = tw_df["tw_e_brand"].apply(normalize_brand)
    tw_df["tw_ing_list"] = tw_df["tw_ingredient"].apply(split_ingredients)

    matches = []
    for _, row in fda_df.iterrows():
        fda_brand_norm = normalize_brand(row.get("品名", ""))
        fda_ing_list = split_ingredients(row.get("主成分", ""))

        # Brand match
        brand_hits = tw_df[tw_df["tw_e_brand_norm"] == fda_brand_norm]

        # Ingredient match (any overlap)
        ing_hits = tw_df[tw_df["tw_ing_list"].apply(lambda lst: ingredient_match(fda_ing_list, lst))]

        hit_df = pd.concat([brand_hits, ing_hits]).drop_duplicates(subset=["tw_id"])
        for _, tw in hit_df.iterrows():
            matches.append({
                "日期": row["日期"],
                "FDA_品名": row["品名"],
                "FDA_主成分": row["主成分"],
                "FDA_安全議題": row["安全議題"],
                "FDA_用藥族群": row["用藥族群"],
                "FDA_注意事項與對策": row["注意事項與對策"],
                "tw_id": tw["tw_id"],
                "tw_c_brand": tw["tw_c_brand"],
                "tw_e_brand": tw["tw_e_brand"],
                "tw_form": tw["tw_form"],
                "tw_ingredient": tw["tw_ingredient"],
                "tw_company": tw["tw_company"],
            })

    return pd.DataFrame(matches)

# ---------- Streamlit UI ----------

st.set_page_config(page_title="FDA DSC Parser & TW Matching", layout="wide")
st.title("FDA Drug Safety Communications 解析與台灣品項比對")

with st.expander("設定與說明", expanded=True):
    st.markdown("- **資料來源：** FDA Drug Safety Communications（Current 區段）")
    st.markdown("- **輸出：** 日期、品名、主成分、安全議題、用藥族群、注意事項與對策；以及台灣品項匹配欄位")
    seed = st.checkbox("若當前頁未列出 2025，加入 2025 標題種子（依你提供的清單）", value=True)

# Fetch FDA page
st.subheader("FDA Current Drug Safety Communications")
status_placeholder = st.empty()
try:
    status_placeholder.info("抓取 FDA 頁面中…")
    html = fetch_html(FDA_URL)
    items = parse_current_list(html)
    fda_df = build_fda_summary(items, seed_2025=seed)
    status_placeholder.success(f"已解析 {len(items)} 條當前通報；總列出 {len(fda_df)} 條（含種子）")
except Exception as e:
    st.error(f"無法抓取或解析 FDA 頁面：{e}")
    fda_df = pd.DataFrame(columns=["日期","品名","主成分","安全議題","用藥族群","注意事項與對策","source_title","source_url"])

# Show FDA table
st.dataframe(fda_df[["日期","品名","主成分","安全議題","用藥族群","注意事項與對策","source_title"]], use_container_width=True)

# Upload TW CSV (37_2c.csv)
st.subheader("上傳台灣上市品 CSV（37_2c.csv）")
uploaded = st.file_uploader("選擇 CSV 檔（需含欄位：tw_id, tw_c_brand, tw_e_brand, tw_form, tw_ingredient, tw_company）", type=["csv"])

if uploaded:
    try:
        tw_df = pd.read_csv(uploaded)
        st.success(f"已載入台灣品項 {len(tw_df)} 筆")
        # Matching
        with st.spinner("比對中…"):
            match_df = match_tw_products(fda_df, tw_df)
            st.subheader(f"匹配結果（{len(match_df)} 筆）")
            st.dataframe(match_df[
                ["日期","FDA_品名","FDA_主成分","FDA_安全議題","FDA_用藥族群","FDA_注意事項與對策",
                 "tw_id","tw_c_brand","tw_e_brand","tw_form","tw_ingredient","tw_company"]
            ], use_container_width=True)

            # Diagnostics: FDA entries with zero matches
            matched_keys = set(zip(match_df["日期"], match_df["FDA_品名"], match_df["FDA_主成分"]))
            unmatched = []
            for _, r in fda_df.iterrows():
                key = (r["日期"], r["品名"], r["主成分"])
                if key not in matched_keys:
                    unmatched.append(r)
            unmatched_df = pd.DataFrame(unmatched)
            st.subheader(f"未匹配 FDA 通報（{len(unmatched_df)} 條）")
            st.dataframe(unmatched_df[["日期","品名","主成分","source_title","source_url"]], use_container_width=True)

            # Diagnostics: TW candidates containing relevant ingredients (optional)
            relevant_tokens = set()
            for ing in fda_df["主成分"].dropna():
                relevant_tokens.update(split_ingredients(ing))
            if relevant_tokens:
                cand_tw = tw_df[tw_df["tw_ing_list"].apply(lambda lst: bool(set(lst) & relevant_tokens))]
                st.subheader(f"相關台灣品項（依主成分交集，{len(cand_tw)} 筆）")
                st.dataframe(cand_tw[
                    ["tw_id","tw_c_brand","tw_e_brand","tw_form","tw_ingredient","tw_company"]
                ], use_container_width=True)
    except Exception as e:
        st.error(f"CSV 解析錯誤：{e}")
else:
    st.info("請上傳 37_2c.csv 以進行比對。")

st.caption("提示：若特定欄位解析困難（例如安全議題或用藥族群），會以空白顯示。你可在後續版本加入更精細的規則。")

