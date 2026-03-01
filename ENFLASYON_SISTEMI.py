# GEREKLİ KÜTÜPHANELER:
# pip install streamlit streamlit-lottie python-docx plotly pandas openpyxl xlsxwriter matplotlib requests PyGithub gspread google-auth beautifulsoup4

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import json
from github import Github
from io import BytesIO
import zipfile
import base64
import requests
import streamlit.components.v1 as components
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

# streamlit-lottie opsiyonel — yoksa sessizce atla
try:
    from streamlit_lottie import st_lottie
    LOTTIE_OK = True
except ImportError:
    LOTTIE_OK = False


# ─────────────────────────────────────────────
# 1. AYARLAR VE TEMA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Enflasyon Monitörü | Pro Analytics",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="expanded"
)

def apply_theme():
    if 'plotly_template' not in st.session_state:
        st.session_state.plotly_template = "plotly_dark"

    final_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');

        header {visibility: hidden;}
        [data-testid="stHeader"] { visibility: hidden; height: 0px; }
        [data-testid="stToolbar"] { display: none; }
        .main .block-container { padding-top: 1rem; }

        .stApp, p, h1, h2, h3, h4, h5, h6, label,
        .stMarkdown, .stDataFrame div, .stDataFrame span {
            color: #ffffff;
        }

        @keyframes gradientBG {
            0%   { background-position: 0%   50%; }
            50%  { background-position: 100% 50%; }
            100% { background-position: 0%   50%; }
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translate3d(0, 30px, 0); }
            to   { opacity: 1; transform: translate3d(0,  0,  0); }
        }
        @keyframes marquee {
            0%   { transform: translateX(0);    }
            100% { transform: translateX(-50%); }
        }
        @keyframes textShine {
            to { background-position: 200% center; }
        }
        @keyframes pulseGlow {
            0%   { box-shadow: 0 0  0  0   rgba(59,130,246,0.4); }
            70%  { box-shadow: 0 0  0  10px rgba(59,130,246,0);   }
            100% { box-shadow: 0 0  0  0   rgba(59,130,246,0);   }
        }

        :root {
            --card-bg:      rgba(20,24,33,0.65);
            --border:       rgba(255,255,255,0.08);
            --accent:       #3b82f6;
            --glass-shadow: 0 8px 32px 0 rgba(0,0,0,0.37);
        }

        .stApp {
            background: linear-gradient(-45deg, #0a0f1c, #131b2f, #0f172a, #050811);
            background-size: 400% 400%;
            animation: gradientBG 20s ease infinite;
            font-family: 'Inter', sans-serif;
        }

        section[data-testid="stSidebar"] {
            background-color: rgba(9,10,12,0.8) !important;
            backdrop-filter: blur(15px);
            border-right: 1px solid var(--border);
        }

        .gradient-text {
            background: linear-gradient(to right,#60a5fa,#a78bfa,#f472b6,#60a5fa);
            background-size: 200% auto;
            color: transparent !important;
            -webkit-background-clip: text;
            background-clip: text;
            animation: textShine 4s linear infinite;
        }

        /* NAV RADIO */
        [data-testid="stRadio"] > label { display: none !important; }
        [data-testid="stRadio"] > div {
            display: flex; flex-direction: row; flex-wrap: nowrap !important;
            overflow-x: auto; justify-content: center; align-items: center; gap: 10px;
            background: rgba(30,33,40,0.3); padding: 10px; border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.05); margin-top: -20px;
            white-space: nowrap; backdrop-filter: blur(10px);
            box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
        }
        [data-testid="stRadio"] > div::-webkit-scrollbar { height: 4px; }
        [data-testid="stRadio"] > div::-webkit-scrollbar-thumb {
            background: rgba(59,130,246,0.5); border-radius: 4px;
        }
        [data-testid="stRadio"] label {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
            padding: 10px 16px; border-radius: 12px; cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
            font-family: 'Inter', sans-serif; font-weight: 600; font-size: 13px;
            color: #ffffff !important;
            display: flex; justify-content: center; align-items: center;
        }
        [data-testid="stRadio"] label p { color: inherit !important; margin: 0; }
        [data-testid="stRadio"] label:hover {
            background: rgba(59,130,246,0.15);
            border-color: rgba(59,130,246,0.4);
            transform: translateY(-3px);
            box-shadow: 0 10px 20px -10px rgba(59,130,246,0.5);
        }
        [data-testid="stRadio"] label[data-checked="true"] {
            background: linear-gradient(135deg,#3b82f6 0%,#1d4ed8 100%);
            border-color: #60a5fa; color: #ffffff !important; font-weight: 800;
            box-shadow: 0 8px 16px rgba(37,99,235,0.4), inset 0 2px 4px rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }

        /* KPI KARTLARI */
        .kpi-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px; padding: 24px;
            backdrop-filter: blur(12px);
            box-shadow: var(--glass-shadow);
            animation: fadeInUp 0.6s ease-out both;
            transition: all 0.4s cubic-bezier(0.175,0.885,0.32,1.275);
            position: relative; overflow: hidden;
        }
        .kpi-card::before {
            content: ''; position: absolute; top: 0; left: -100%;
            width: 50%; height: 100%;
            background: linear-gradient(to right,transparent,rgba(255,255,255,0.03),transparent);
            transform: skewX(-25deg); transition: 0.5s;
        }
        .kpi-card:hover::before { left: 150%; }
        .kpi-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 30px -10px rgba(0,0,0,0.5), 0 0 20px rgba(59,130,246,0.2);
            border-color: rgba(59,130,246,0.4);
        }
        .kpi-title  { font-size:11px; text-transform:uppercase; letter-spacing:1.5px; color:#94a3b8 !important; font-weight:700; margin-bottom:8px; }
        .kpi-value  { font-family:'JetBrains Mono',monospace; font-size:34px; font-weight:800; color:#ffffff !important; text-shadow:0 0 20px rgba(59,130,246,0.4); }

        /* TICKER */
        .ticker-wrap {
            width:100%; overflow:hidden;
            background: linear-gradient(90deg,rgba(15,23,42,0) 0%,rgba(30,41,59,0.5) 50%,rgba(15,23,42,0) 100%);
            border-top:1px solid rgba(255,255,255,0.05);
            border-bottom:1px solid rgba(255,255,255,0.05);
            padding:12px 0; margin-bottom:25px;
            white-space:nowrap; position:relative;
            box-shadow:0 5px 15px rgba(0,0,0,0.2);
        }
        .ticker-move { display:inline-block; white-space:nowrap; animation:marquee 40s linear infinite; }

        /* ÜRÜN KARTLARI */
        .pg-card {
            background: linear-gradient(145deg,rgba(30,33,40,0.6),rgba(15,18,25,0.8));
            border:1px solid var(--border); border-radius:14px; padding:18px;
            animation:fadeInUp 0.5s ease-out both; transition:all 0.4s ease;
            height:100%; backdrop-filter:blur(8px);
        }
        .pg-card:hover {
            transform:translateY(-5px) scale(1.03);
            border-color:var(--accent);
            box-shadow:0 10px 25px rgba(59,130,246,0.25);
        }
        .pg-name   { font-size:13px; font-weight:600; color:#e2e8f0 !important; margin-bottom:8px; height:36px; overflow:hidden; }
        .pg-price  { font-family:'JetBrains Mono'; font-size:19px; font-weight:800; color:#ffffff !important; }
        .pg-badge  { font-size:11px; font-weight:800; padding:4px 10px; border-radius:8px; margin-top:10px; display:inline-block; letter-spacing:0.5px; }
        .pg-red    { background:rgba(239,68,68,0.15);   color:#fca5a5 !important; border:1px solid rgba(239,68,68,0.3);   box-shadow:0 0 10px rgba(239,68,68,0.1); }
        .pg-green  { background:rgba(16,185,129,0.15);  color:#6ee7b7 !important; border:1px solid rgba(16,185,129,0.3);  box-shadow:0 0 10px rgba(16,185,129,0.1); }
        .pg-yellow { background:rgba(234,179,8,0.15);   color:#fde047 !important; border:1px solid rgba(234,179,8,0.3); }

        /* BUTONLAR */
        div.stButton > button {
            background: linear-gradient(90deg,#2563eb,#3b82f6,#2563eb);
            background-size: 200% auto;
            color: white !important; font-weight:700; letter-spacing:0.5px;
            border:1px solid rgba(255,255,255,0.1); border-radius:10px;
            padding:0.6rem 1.2rem;
            transition: all 0.4s cubic-bezier(0.175,0.885,0.32,1.275);
            animation: textShine 3s linear infinite, pulseGlow 2.5s infinite;
        }
        div.stButton > button:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 10px 25px rgba(59,130,246,0.5);
            border-color: #93c5fd; background-position: right center;
        }

        [data-testid="stDataFrame"] {
            border-radius:12px; overflow:hidden;
            border:1px solid rgba(255,255,255,0.05);
        }
    </style>
    """
    st.markdown(final_css, unsafe_allow_html=True)

apply_theme()


# ─────────────────────────────────────────────
# 2. SABİTLER
# ─────────────────────────────────────────────
EXCEL_DOSYASI = "TUFE_Konfigurasyon.xlsx"
FIYAT_DOSYASI = "Fiyat_Veritabani.xlsx"
SAYFA_ADI     = "Madde_Sepeti"


# ─────────────────────────────────────────────
# 3. YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def get_github_connection():
    try:
        return Github(st.secrets["github"]["token"])
    except Exception:
        return None


def get_github_repo():
    g = get_github_connection()
    return g.get_repo(st.secrets["github"]["repo_name"]) if g else None


def temizle_fiyat(t):
    if not t:
        return None
    t = str(t).replace('TL', '').replace('₺', '').strip()
    if ',' in t and '.' in t:
        t = t.replace('.', '').replace(',', '.')
    elif ',' in t:
        t = t.replace(',', '.')
    try:
        return float(re.sub(r'[^\d.]', '', t))
    except Exception:
        return None


def kod_standartlastir(k):
    return str(k).replace('.0', '').strip().zfill(7)


# ─────────────────────────────────────────────
# 4. GITHUB EXCEL GÜNCELLE
# ─────────────────────────────────────────────
def github_excel_guncelle(df_yeni, dosya_adi):
    repo = get_github_repo()
    if not repo:
        return "Repo Yok"
    try:
        branch = st.secrets["github"]["branch"]
        sha = None
        try:
            c = repo.get_contents(dosya_adi, ref=branch)
            sha = c.sha
            old = pd.read_excel(BytesIO(c.decoded_content), dtype=str)
            yeni_tarih = str(df_yeni['Tarih'].iloc[0])
            old = old[~(
                (old['Tarih'].astype(str) == yeni_tarih) &
                (old['Kod'].isin(df_yeni['Kod']))
            )]
            final = pd.concat([old, df_yeni], ignore_index=True)
        except Exception as e:
            if "404" in str(e):
                final = df_yeni
            else:
                return f"Dosya Okuma Hatası: {e}"

        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as w:
            final.to_excel(w, index=False, sheet_name='Fiyat_Log')

        if sha:
            repo.update_file(dosya_adi, "Data Update", out.getvalue(), sha, branch=branch)
        else:
            repo.create_file(dosya_adi, "Data Update", out.getvalue(), branch=branch)
        return "OK"
    except Exception as e:
        return str(e)


# ─────────────────────────────────────────────
# 5. SCRAPER
# ─────────────────────────────────────────────
def fiyat_bul_siteye_gore(soup, kaynak_tipi):
    kaynak_tipi = str(kaynak_tipi).lower()
    try:
        if "migros" in kaynak_tipi:
            for cop in [
                "sm-list-page-item", ".horizontal-list-page-items-container",
                "app-product-carousel", ".similar-products", "div.badges-wrapper",
                "mat-tab-body", ".mat-mdc-tab-body-wrapper"
            ]:
                for el in soup.select(cop):
                    el.decompose()

            main_wrapper = soup.select_one(".name-price-wrapper")
            if main_wrapper:
                for css, _ in [
                    (".money-discount-label-wrapper .sale-price", ""),
                    (".single-price-amount", ""),
                    (".price.subtitle-1", ""),
                    ("#sale-price", ""),
                ]:
                    el = main_wrapper.select_one(css)
                    if el:
                        val = temizle_fiyat(el.get_text())
                        if val and val > 0:
                            return val

            match = re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺)', soup.get_text())
            if match:
                return temizle_fiyat(match.group(1))

        elif "carrefour" in kaynak_tipi:
            for cop in [".product-carousel", ".category-tabs", ".tabs", ".pl-component", ".similar-products"]:
                for el in soup.select(cop):
                    el.decompose()
            tag = soup.select_one(".item-price") or soup.select_one(".priceLineThrough")
            if tag:
                return temizle_fiyat(tag.get_text())

        elif "cimri" in kaynak_tipi:
            tag = soup.select_one("span.yEvpr")
            if tag:
                return temizle_fiyat(tag.get_text())

    except Exception as e:
        print(f"Parser Hatası ({kaynak_tipi}): {e}")
    return 0


# ─────────────────────────────────────────────
# 6. ANA İŞLEYİCİ
# ─────────────────────────────────────────────
def html_isleyici(progress_callback):
    repo = get_github_repo()
    if not repo:
        return "GitHub Bağlantı Hatası"

    progress_callback(0.05)
    try:
        branch = st.secrets["github"]["branch"]

        c = repo.get_contents(EXCEL_DOSYASI, ref=branch)
        df_conf = pd.read_excel(BytesIO(c.decoded_content), sheet_name=SAYFA_ADI, dtype=str)
        df_conf.columns = df_conf.columns.str.strip()

        kod_col    = next((x for x in df_conf.columns if x.lower() == 'kod'), 'Kod')
        ad_col     = next((x for x in df_conf.columns if 'ad'     in x.lower()), 'Madde_Adi')
        manuel_col = next((x for x in df_conf.columns if 'manuel' in x.lower() and 'fiyat' in x.lower()), None)

        urun_isimleri = pd.Series(
            df_conf[ad_col].values,
            index=df_conf[kod_col].astype(str).apply(kod_standartlastir)
        ).to_dict()

        veri_havuzu: dict = {}

        if manuel_col:
            for _, row in df_conf.iterrows():
                try:
                    kod  = kod_standartlastir(row[kod_col])
                    fiyat = temizle_fiyat(row[manuel_col])
                    if fiyat and fiyat > 0:
                        veri_havuzu.setdefault(kod, []).append(fiyat)
                except Exception:
                    continue

        contents  = repo.get_contents("", ref=branch)
        zip_files = [f for f in contents if f.name.endswith(".zip") and f.name.startswith("Bolum")]
        total     = len(zip_files)

        for i, zf in enumerate(zip_files):
            progress_callback(0.10 + 0.80 * ((i + 1) / max(1, total)))
            try:
                blob     = repo.get_git_blob(zf.sha)
                zip_data = base64.b64decode(blob.content)
                with zipfile.ZipFile(BytesIO(zip_data)) as z:
                    for fname in z.namelist():
                        if not fname.endswith(('.html', '.htm')):
                            continue
                        fl = fname.lower()
                        if "migros" not in fl and "cimri" not in fl:
                            continue

                        dosya_kodu = kod_standartlastir(fname.split('_')[0])
                        if dosya_kodu not in urun_isimleri:
                            continue

                        with z.open(fname) as f:
                            raw     = f.read().decode("utf-8", errors="ignore")
                            kaynak  = "migros" if "migros" in fl else "cimri"
                            soup    = BeautifulSoup(raw, 'html.parser')
                            fiyat   = fiyat_bul_siteye_gore(soup, kaynak)
                            if fiyat > 0:
                                veri_havuzu.setdefault(dosya_kodu, []).append(fiyat)
            except Exception:
                continue

        tr_saati = datetime.utcnow() + timedelta(hours=3)
        bugun    = tr_saati.strftime("%Y-%m-%d")
        simdi    = tr_saati.strftime("%H:%M")

        final_list = []
        for kod, fiyatlar in veri_havuzu.items():
            clean_vals = [p for p in fiyatlar if p > 0]
            if not clean_vals:
                continue
            if len(clean_vals) > 1:
                final_fiyat = float(max(clean_vals))
                kaynak_str  = f"Max ({len(clean_vals)} Kaynak)"
            else:
                final_fiyat = clean_vals[0]
                kaynak_str  = "Single Source"

            final_list.append({
                "Tarih":     bugun,
                "Zaman":     simdi,
                "Kod":       kod,
                "Madde_Adi": urun_isimleri.get(kod, "Bilinmeyen Ürün"),
                "Fiyat":     final_fiyat,
                "Kaynak":    kaynak_str,
                "URL":       "ZIP_ARCHIVE"
            })

        progress_callback(0.95)
        if final_list:
            return github_excel_guncelle(pd.DataFrame(final_list), FIYAT_DOSYASI)
        return "Veri bulunamadı (Manuel veya Web)."

    except Exception as e:
        return f"Genel Hata: {e}"


# ─────────────────────────────────────────────
# 7. GRAFİK STİLİ
# ─────────────────────────────────────────────
def style_chart(fig, is_pdf=False, is_sunburst=False):
    if is_pdf:
        fig.update_layout(template="plotly_white", font=dict(family="Arial", size=14, color="black"))
    else:
        layout_args = dict(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#a1a1aa", size=12),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        if not is_sunburst:
            layout_args.update(dict(
                xaxis=dict(
                    showgrid=False, zeroline=False, showline=True,
                    linecolor="rgba(255,255,255,0.1)",
                    gridcolor='rgba(255,255,255,0.05)',
                    # dtick="M1"  ← kaldırıldı: tarih ekseni değilse hata verir
                ),
                yaxis=dict(
                    showgrid=True, gridcolor="rgba(255,255,255,0.03)",
                    zeroline=False, gridwidth=1
                )
            ))
        fig.update_layout(**layout_args)
    return fig


# ─────────────────────────────────────────────
# 8. VERİ ÇEKME (ÖNBELLEKLI)
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def verileri_getir_cache():
    try:
        repo = get_github_repo()
        if not repo:
            return None, None, None, "Repo bağlantısı kurulamadı."

        branch      = st.secrets["github"]["branch"]
        last_commit = repo.get_branch(branch).commit
        tree        = repo.get_git_tree(last_commit.sha, recursive=True)

        fiyat_sha = conf_sha = None
        for item in tree.tree:
            if item.path == FIYAT_DOSYASI:  fiyat_sha = item.sha
            elif item.path == EXCEL_DOSYASI: conf_sha  = item.sha

        if not fiyat_sha:
            return None, None, None, f"{FIYAT_DOSYASI} repoda bulunamadı!"

        fiyat_blob = repo.get_git_blob(fiyat_sha)
        df_f = pd.read_excel(BytesIO(base64.b64decode(fiyat_blob.content)), dtype=str)

        if conf_sha:
            conf_blob = repo.get_git_blob(conf_sha)
            df_s = pd.read_excel(BytesIO(base64.b64decode(conf_blob.content)), sheet_name=SAYFA_ADI, dtype=str)
        else:
            df_s = pd.DataFrame()

        if df_f.empty or df_s.empty:
            return None, None, None, "Excel dosyaları boş."

        def zorla_tarih(t):
            try:
                temiz = str(t).strip().split(' ')[0]
                temiz = ''.join(c for c in temiz if c.isdigit() or c in '-./') 
                return pd.to_datetime(temiz, dayfirst=('.' in temiz))
            except Exception:
                return pd.NaT

        df_f['Tarih_DT']  = df_f['Tarih'].apply(zorla_tarih)
        df_f              = df_f.dropna(subset=['Tarih_DT']).sort_values('Tarih_DT')
        df_f['Tarih_Str'] = df_f['Tarih_DT'].dt.strftime('%Y-%m-%d')
        raw_dates         = df_f['Tarih_Str'].unique().tolist()

        df_s.columns = df_s.columns.str.strip()
        kod_col = next((c for c in df_s.columns if c.lower() == 'kod'), 'Kod')
        ad_col  = next((c for c in df_s.columns if 'ad' in c.lower()), 'Madde_Adi')

        df_f['Kod'] = df_f['Kod'].astype(str).apply(kod_standartlastir)
        df_s['Kod'] = df_s[kod_col].astype(str).apply(kod_standartlastir)
        df_s        = df_s.drop_duplicates(subset=['Kod'], keep='first')

        df_f['Fiyat'] = pd.to_numeric(
            df_f['Fiyat'].astype(str).str.replace(',', '.').str.strip(),
            errors='coerce'
        )
        df_f = df_f[df_f['Fiyat'] > 0]

        pivot = df_f.pivot_table(index='Kod', columns='Tarih_Str', values='Fiyat', aggfunc='mean')
        pivot = pivot.ffill(axis=1).bfill(axis=1).reset_index()

        if pivot.empty:
            return None, None, None, "Pivot tablo oluşturulamadı."

        if 'Grup' not in df_s.columns:
            grup_map = {"01": "Gıda", "02": "Alkol-Tütün", "03": "Giyim", "04": "Konut"}
            df_s['Grup'] = df_s['Kod'].str[:2].map(grup_map).fillna("Diğer")

        df_analiz_base = pd.merge(df_s, pivot, on='Kod', how='left')
        return df_analiz_base, raw_dates, ad_col, None

    except Exception as e:
        return None, None, None, f"Veri Çekme Hatası: {e}"


# ─────────────────────────────────────────────
# 9. HESAPLAMA
# ─────────────────────────────────────────────
def hesapla_metrikler(df_analiz_base, secilen_tarih, gunler,
                      tum_gunler_sirali, ad_col, agirlik_col,
                      baz_col, aktif_agirlik_col, son):

    BEKLENEN_AYLIK_ORT = 3.03

    df_analiz = df_analiz_base.copy()

    # Sayısal dönüşümler
    for col in gunler:
        if col in df_analiz.columns:
            df_analiz[col] = pd.to_numeric(df_analiz[col], errors='coerce')

    if baz_col not in df_analiz.columns:
        df_analiz[baz_col] = np.nan
    if aktif_agirlik_col not in df_analiz.columns:
        df_analiz[aktif_agirlik_col] = 0

    df_analiz[baz_col]          = pd.to_numeric(df_analiz[baz_col], errors='coerce').fillna(0)
    df_analiz[aktif_agirlik_col] = pd.to_numeric(df_analiz[aktif_agirlik_col], errors='coerce').fillna(0)

    # Aylık ortalama (mevcut ay günlerinin geometrik ortalaması)
    ay_prefix    = son[:7]
    bu_ay_gunler = [g for g in gunler if g.startswith(ay_prefix)]
    if bu_ay_gunler:
        vals = df_analiz[bu_ay_gunler].replace(0, np.nan)
        df_analiz['Aylik_Ortalama'] = np.exp(np.log(vals).mean(axis=1))
    else:
        df_analiz['Aylik_Ortalama'] = df_analiz[son]

    df_analiz['Aylik_Ortalama'] = pd.to_numeric(df_analiz['Aylik_Ortalama'], errors='coerce')

    mask = (
        (df_analiz[aktif_agirlik_col] > 0) &
        (df_analiz[son] > 0) &
        (df_analiz[baz_col] > 0)
    )
    gecerli = df_analiz[mask].copy()

    enf_genel = enf_gida = yillik_enf = 0.0

    if not gecerli.empty:
        gecerli['oran'] = gecerli['Aylik_Ortalama'] / gecerli[baz_col]
        gecerli['oran'] = gecerli['oran'].replace([np.inf, -np.inf], np.nan).fillna(1)

        w          = gecerli[aktif_agirlik_col]
        toplam_w   = w.sum()
        enf_genel  = ((gecerli['oran'] * w).sum() / toplam_w - 1) * 100 if toplam_w > 0 else 0

        gida_mask  = gecerli['Kod'].astype(str).str.startswith("01")
        if gida_mask.any():
            gdf       = gecerli[gida_mask]
            gw        = gdf[aktif_agirlik_col].sum()
            enf_gida  = ((gdf['oran'] * gdf[aktif_agirlik_col]).sum() / gw - 1) * 100 if gw > 0 else 0

        if enf_genel > 0:
            yillik_enf = ((1 + enf_genel / 100) * (1 + BEKLENEN_AYLIK_ORT / 100) ** 11 - 1) * 100

        df_analiz.loc[gecerli.index, 'Simule_Fiyat'] = gecerli[baz_col] * gecerli['oran']
    else:
        df_analiz['Simule_Fiyat'] = df_analiz[son]

    # Fark hesabı
    df_analiz['Fark'] = 0.0
    valid_idx = df_analiz.index[
        (df_analiz[baz_col] > 0) &
        df_analiz['Simule_Fiyat'].notna()
    ]
    df_analiz.loc[valid_idx, 'Fark'] = (
        df_analiz.loc[valid_idx, 'Simule_Fiyat'] /
        df_analiz.loc[valid_idx, baz_col]
    ) - 1
    df_analiz['Fark_Yuzde'] = df_analiz['Fark'] * 100

    # Günlük değişim
    if len(gunler) >= 2:
        onceki_gun = gunler[-2]
        df_analiz['Gunluk_Degisim'] = (
            df_analiz[son] /
            df_analiz[onceki_gun].replace(0, np.nan)
        ) - 1
    else:
        onceki_gun = son
        df_analiz['Gunluk_Degisim'] = 0.0

    df_analiz['Gunluk_Degisim'] = df_analiz['Gunluk_Degisim'].replace([np.inf, -np.inf], 0).fillna(0)

    return {
        "df_analiz":            df_analiz,
        "enf_genel":            enf_genel,
        "enf_gida":             enf_gida,
        "yillik_enf":           yillik_enf,
        "resmi_aylik_degisim":  4.84,
        "son":                  son,
        "onceki_gun":           onceki_gun,
        "gunler":               gunler,
        "ad_col":               ad_col,
        "agirlik_col":          aktif_agirlik_col,
        "baz_col":              baz_col,
        "gun_farki":            0,
        "tahmin":               enf_genel,
    }


# ─────────────────────────────────────────────
# 10. SIDEBAR
# ─────────────────────────────────────────────
def ui_sidebar_ve_veri_hazirlama(df_analiz_base, raw_dates, ad_col):
    if df_analiz_base is None:
        return None

    with st.sidebar.expander("🛠️ Sistem Radarı", expanded=False):
        st.caption("Veritabanına İşlenen Son Günler:")
        st.write(raw_dates[-3:] if len(raw_dates) > 2 else raw_dates)

    ai_container = st.sidebar.container()
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Veri Ayarları")

    # Lottie animasyonu (opsiyonel)
    if LOTTIE_OK:
        try:
            lottie_json = load_lottieurl(
                "https://lottie.host/98606416-297c-4a37-9b2a-714013063529/5D6o8k8fW0.json"
            )
            if lottie_json:
                with st.sidebar:
                    st_lottie(lottie_json, height=100, key="nav_anim")
        except Exception:
            pass

    BASLANGIC_LIMITI = "2026-02-04"
    tum_tarihler     = sorted(
        [d for d in raw_dates if d >= BASLANGIC_LIMITI], reverse=True
    )
    if not tum_tarihler:
        st.sidebar.warning("Veri henüz oluşmadı.")
        return None

    secilen_tarih = st.sidebar.selectbox(
        "Rapor Tarihi:", options=tum_tarihler, index=0,
        key=f"tarih_secici_{tum_tarihler[0]}"
    )

    tum_gunler_sirali = sorted([
        c for c in df_analiz_base.columns
        if re.match(r'\d{4}-\d{2}-\d{2}', str(c)) and c >= BASLANGIC_LIMITI
    ])

    if secilen_tarih in tum_gunler_sirali:
        idx   = tum_gunler_sirali.index(secilen_tarih)
        gunler = tum_gunler_sirali[: idx + 1]
    else:
        gunler = tum_gunler_sirali

    if not gunler:
        return None

    son      = gunler[-1]
    dt_son   = datetime.strptime(son, '%Y-%m-%d')
    col_w25  = 'Agirlik_2025'
    col_w26  = 'Agirlik_2026'
    ZINCIR   = datetime(2026, 2, 4)

    if dt_son >= ZINCIR:
        aktif_agirlik_col = col_w26
        onceki_ay_gunleri = [
            c for c in tum_gunler_sirali
            if c < f"{dt_son.year}-{dt_son.month:02d}-01"
        ]
        baz_col = onceki_ay_gunleri[-1] if onceki_ay_gunleri else gunler[0]
        if baz_col not in gunler:
            gunler = [baz_col] + gunler
    else:
        aktif_agirlik_col = col_w25
        baz_col           = gunler[0]

    ctx = hesapla_metrikler(
        df_analiz_base, secilen_tarih, gunler,
        tum_gunler_sirali, ad_col,
        agirlik_col=None, baz_col=baz_col,
        aktif_agirlik_col=aktif_agirlik_col, son=son
    )

    # AI görüşü
    with ai_container:
        st.markdown("### 🧠 AI Görüşü")
        genel = ctx["enf_genel"]
        gida  = ctx["enf_gida"]

        if genel > 5:
            durum, renk, yorum = "KRİTİK", "#ef4444", "Enflasyon ivmesi çok yüksek. Harcama disiplini şart."
        elif genel > 2:
            durum, renk, yorum = "YÜKSEK", "#f59e0b", "Fiyatlar artış trendinde. Lüks harcamalar ertelenmeli."
        else:
            durum, renk, yorum = "STABİL", "#10b981", "Piyasa dengeli görünüyor. Ani şok beklenmiyor."

        ek_not = ""
        if gida > (genel * 1.2):
            ek_not = "<br><span style='font-size:10px;color:#fca5a5;'>⚠️ Mutfak enflasyonu ortalamadan yüksek!</span>"

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05);padding:12px;border-radius:8px;
            border-left:3px solid {renk};margin-bottom:10px;box-shadow:0 4px 15px rgba(0,0,0,0.2);">
            <div style="color:{renk};font-weight:800;font-size:13px;letter-spacing:1px;">{durum}</div>
            <div style="font-size:11px;margin-top:4px;opacity:0.9;">{yorum}</div>
            {ek_not}
        </div>
        """, unsafe_allow_html=True)

    # TradingView widget'ları
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌍 Piyasalar")
    symbols = [
        {"s": "FX_IDC:USDTRY",    "d": "Dolar"},
        {"s": "FX_IDC:EURTRY",    "d": "Euro"},
        {"s": "FX_IDC:XAUTRYG",   "d": "Gram Altın"},
        {"s": "TVC:UKOIL",        "d": "Brent Petrol"},
        {"s": "BINANCE:BTCUSDT",  "d": "Bitcoin"},
    ]
    for sym in symbols:
        widget_code = (
            f'<div class="tradingview-widget-container" '
            f'style="border-radius:12px;overflow:hidden;margin-bottom:10px;box-shadow:0 4px 10px rgba(0,0,0,0.3);">'
            f'<div class="tradingview-widget-container__widget"></div>'
            f'<script type="text/javascript" '
            f'src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>'
            f'{{ "symbol": "{sym["s"]}", "width": "100%", "height": 100, '
            f'"locale": "tr", "dateRange": "1D", "colorTheme": "dark", '
            f'"isTransparent": true, "autosize": true, "largeChartUrl": "" }}'
            f'</script></div>'
        )
        with st.sidebar:
            components.html(widget_code, height=100)

    return ctx


# ─────────────────────────────────────────────
# 11. TOP-10 YARDIMCILARI
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _hesapla_top10_tablolari(df_analiz_json: str, son_col, ad_col, baz_col):
    """df_analiz'i JSON string olarak alır (cache uyumlu)."""
    df = pd.read_json(df_analiz_json)
    df_fark = df.dropna(subset=['Fark', son_col, ad_col, baz_col]).copy()
    artan  = df_fark[df_fark['Fark'] > 0].sort_values('Fark', ascending=False).head(10)
    azalan = df_fark[df_fark['Fark'] < 0].sort_values('Fark', ascending=True).head(10)
    return artan, azalan


def sabit_kademeli_top10_hazirla(ctx):
    try:
        df_json = ctx["df_analiz"].to_json()
        a, b = _hesapla_top10_tablolari(df_json, ctx['son'], ctx['ad_col'], ctx['baz_col'])
        return a.copy(), b.copy()
    except Exception:
        df = ctx["df_analiz"]
        df_fark = df.dropna(subset=['Fark']).copy()
        artan  = df_fark[df_fark['Fark'] > 0].sort_values('Fark', ascending=False).head(10)
        azalan = df_fark[df_fark['Fark'] < 0].sort_values('Fark', ascending=True).head(10)
        return artan, azalan


# ─────────────────────────────────────────────
# 12. SAYFA: ENFLASYONa ÖZETİ
# ─────────────────────────────────────────────
def sayfa_piyasa_ozeti(ctx):
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "GENEL ENFLASYON",   f"%{ctx['enf_genel']:.2f}", "#ef4444",  "Aylık Değişim (Simüle)"),
        (c2, "GIDA ENFLASYONU",   f"%{ctx['enf_gida']:.2f}",  "#fca5a5",  "Mutfak Sepeti"),
        (c3, "YILLIK PROJ.",      "%31.47",                   "#a78bfa",  "Yıllık Projeksiyon"),
        (c4, "RESMİ (TÜİK)",     f"%{ctx['resmi_aylik_degisim']:.2f}", "#fbbf24", "Sabit Veri"),
    ]
    for col, title, val, color, sub in cards:
        with col:
            st.markdown(
                f'<div class="kpi-card">'
                f'<div class="kpi-title">{title}</div>'
                f'<div class="kpi-value">{val}</div>'
                f'<div style="color:{color};font-size:12px;font-weight:600;margin-top:5px;">{sub}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    df      = ctx["df_analiz"]
    ad_col  = ctx['ad_col']
    inc     = df.sort_values('Gunluk_Degisim', ascending=False).head(15)
    dec     = df.sort_values('Gunluk_Degisim', ascending=True).head(15)

    items = []
    for _, r in inc.iterrows():
        val = r['Gunluk_Degisim']
        if val > 0:
            items.append(
                f"<span style='color:#ef4444;font-weight:800;text-shadow:0 0 10px rgba(239,68,68,0.4);'>"
                f"▲ {r[ad_col]} %{val*100:.1f}</span>"
            )
    for _, r in dec.iterrows():
        val = r['Gunluk_Degisim']
        if val < 0:
            items.append(
                f"<span style='color:#22c55e;font-weight:800;text-shadow:0 0 10px rgba(34,197,94,0.4);'>"
                f"▼ {r[ad_col]} %{abs(val)*100:.1f}</span>"
            )

    sep        = " &nbsp;&nbsp;&nbsp; • &nbsp;&nbsp;&nbsp; "
    ticker_str = sep.join(items) if items else "Veri bekleniyor..."
    st.markdown(
        f'<div class="ticker-wrap"><div class="ticker-move">'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:14px;">'
        f'{ticker_str}{sep}{ticker_str}'
        f'</span></div></div>',
        unsafe_allow_html=True
    )

    col_g1, col_g2 = st.columns([2, 1])

    with col_g1:
        df_ana        = ctx["df_analiz"].copy()
        df_ana        = df_ana.loc[:, ~df_ana.columns.duplicated()]
        baz_col       = ctx["baz_col"]
        agirlik_col   = ctx["agirlik_col"]
        gunler        = ctx["gunler"]
        son_gun       = ctx["son"]

        df_ana[agirlik_col] = pd.to_numeric(df_ana[agirlik_col], errors='coerce').fillna(0)
        df_ana = df_ana[df_ana[agirlik_col] > 0]
        df_ana[baz_col] = pd.to_numeric(df_ana[baz_col], errors='coerce').fillna(0)
        df_ana = df_ana[df_ana[baz_col] > 0]

        hedef_ay        = son_gun[:7]
        bu_ayin_gunleri = [g for g in gunler if g.startswith(hedef_ay) and g <= son_gun]
        trend_verisi    = []

        for gun in bu_ayin_gunleri:
            gecerli_k = [g for g in bu_ayin_gunleri if g <= gun]
            if not gecerli_k:
                continue
            mevcut = [g for g in gecerli_k if g in df_ana.columns]
            if not mevcut:
                continue

            vals = df_ana[mevcut].replace(0, np.nan)
            df_ana['_ort'] = np.exp(np.log(vals).mean(axis=1))
            temp = df_ana.dropna(subset=['_ort'])
            if temp.empty:
                continue

            w  = temp[agirlik_col]
            if w.sum() == 0:
                continue
            p_rel = temp['_ort'] / temp[baz_col]
            enf   = ((w * p_rel).sum() / w.sum() * 100) - 100
            trend_verisi.append({"Tarih": gun, "Deger": enf})

        df_ana.drop(columns=['_ort'], errors='ignore', inplace=True)
        df_trend = pd.DataFrame(trend_verisi)

        if not df_trend.empty:
            df_trend = df_trend.sort_values('Tarih').reset_index(drop=True)
            # Simüle değeri ile son noktayı hizala
            raw_son    = df_trend.iloc[-1]['Deger']
            simule_son = ctx["enf_genel"]
            fark       = simule_son - raw_son
            max_idx    = max(1, len(df_trend) - 1)
            df_trend['Deger'] += fark * (df_trend.index / max_idx)

            son_deger = df_trend.iloc[-1]['Deger']
            y_max     = max(5,  df_trend['Deger'].max() + 0.5)
            y_min     = min(-5, df_trend['Deger'].min() - 0.5)

            fig_trend = px.line(
                df_trend, x='Tarih', y='Deger',
                title=f"GENEL ENFLASYON TRENDİ (Güncel: %{son_deger:.2f})",
                markers=True
            )
            fig_trend.update_traces(
                line_color='#3b82f6', line_width=4, marker_size=8,
                hovertemplate='Tarih: %{x}<br>Enflasyon: %%{y:.2f}<extra></extra>'
            )
            fig_trend.update_layout(yaxis_range=[y_min, y_max])
            st.plotly_chart(style_chart(fig_trend), use_container_width=True)
        else:
            st.warning("Grafik verisi hesaplanamadı.")

    with col_g2:
        st.markdown(
            f'<div class="kpi-card" style="height:100%;display:flex;flex-direction:column;justify-content:center;">'
            f'<div style="font-size:13px;color:#94a3b8;font-weight:800;letter-spacing:1px;">YÜKSELENLER</div>'
            f'<div style="font-size:32px;color:#ef4444;font-weight:800;text-shadow:0 0 15px rgba(239,68,68,0.3);">'
            f'{len(df[df["Fark"] > 0])} Ürün</div>'
            f'<div style="margin:25px 0;border-top:1px solid rgba(255,255,255,0.1)"></div>'
            f'<div style="font-size:13px;color:#94a3b8;font-weight:800;letter-spacing:1px;">DÜŞENLER</div>'
            f'<div style="font-size:32px;color:#22c55e;font-weight:800;text-shadow:0 0 15px rgba(34,197,94,0.3);">'
            f'{len(df[df["Fark"] < 0])} Ürün</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("### 🔥 Fiyatı En Çok Değişenler (Top 10)")
    c_art, c_az = st.columns(2)
    artan_10, azalan_10 = sabit_kademeli_top10_hazirla(ctx)

    for col_widget, df10, title, color, col_config_sign in [
        (c_art, artan_10, "🔺 EN ÇOK ARTAN 10 ÜRÜN",  "#ef4444", "+%.2f %%"),
        (c_az,  azalan_10,"🔻 EN ÇOK DÜŞEN 10 ÜRÜN",  "#22c55e", "%.2f %%"),
    ]:
        with col_widget:
            st.markdown(
                f"<div style='color:{color};font-weight:800;font-size:16px;"
                f"margin-bottom:15px;text-shadow:0 0 10px rgba(0,0,0,0.2);'>{title}</div>",
                unsafe_allow_html=True
            )
            if not df10.empty:
                # baz_col ve son sütunlarının varlığını kontrol et
                cols_to_show = [ctx['ad_col']]
                if ctx['baz_col'] in df10.columns: cols_to_show.append(ctx['baz_col'])
                if ctx['son'] in df10.columns:     cols_to_show.append(ctx['son'])
                disp = df10[cols_to_show].copy()
                disp['Değişim'] = df10['Fark'] * 100

                col_cfg = {ctx['ad_col']: "Ürün Adı", "Değişim": st.column_config.NumberColumn("% Değişim", format=col_config_sign)}
                if ctx['baz_col'] in disp.columns:
                    col_cfg[ctx['baz_col']] = st.column_config.NumberColumn("İlk Fiyat", format="%.2f ₺")
                if ctx['son'] in disp.columns:
                    col_cfg[ctx['son']] = st.column_config.NumberColumn("Son Fiyat", format="%.2f ₺")

                st.dataframe(disp, column_config=col_cfg, hide_index=True, use_container_width=True)
            else:
                st.info("Fiyatı değişen ürün tespit edilmedi.")

    st.markdown("---")
    st.subheader("Sektörel Isı Haritası")
    ag = ctx['agirlik_col']
    df_tree = df[df[ag].notna()].copy()
    df_tree[ag] = pd.to_numeric(df_tree[ag], errors='coerce').fillna(0)
    df_tree = df_tree[df_tree[ag] > 0]

    if not df_tree.empty:
        fig_tree = px.treemap(
            df_tree,
            path=[px.Constant("Enflasyon Sepeti"), 'Grup', ctx['ad_col']],
            values=ag,
            color='Fark',
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(style_chart(fig_tree, is_sunburst=True), use_container_width=True)


# ─────────────────────────────────────────────
# 13. SAYFA: KATEGORİ DETAY
# ─────────────────────────────────────────────
def sayfa_kategori_detay(ctx):
    df     = ctx["df_analiz"].dropna(subset=[ctx['son'], ctx['ad_col']])
    st.markdown("### 🔍 Kategori Bazlı Fiyat Takibi")

    col_sel, col_src = st.columns([1, 2])
    kategoriler  = ["Tümü"] + sorted(df['Grup'].unique().tolist())
    secilen_kat  = col_sel.selectbox("Kategori Seç:", kategoriler)
    arama        = col_src.text_input("Ürün Ara:", placeholder="Örn: Süt...")

    df_show = df.copy()
    if secilen_kat != "Tümü":
        df_show = df_show[df_show['Grup'] == secilen_kat]
    if arama:
        df_show = df_show[df_show[ctx['ad_col']].astype(str).str.contains(arama, case=False, na=False)]

    if not df_show.empty:
        items_per_page = 16
        max_pages      = max(1, (len(df_show) - 1) // items_per_page + 1)
        page_num       = st.number_input("Sayfa", min_value=1, max_value=max_pages, step=1)
        batch          = df_show.iloc[
            (page_num - 1) * items_per_page: page_num * items_per_page
        ]
        cols = st.columns(4)
        for idx, row in enumerate(batch.to_dict('records')):
            fiyat = row[ctx['son']]
            fark  = row.get('Gunluk_Degisim', 0) * 100
            if abs(fark) < 0.01:
                cls, icon = "pg-yellow", "-"
            elif fark > 0:
                cls, icon = "pg-red",   "▲"
            else:
                cls, icon = "pg-green", "▼"
            with cols[idx % 4]:
                st.markdown(
                    f'<div class="pg-card">'
                    f'<div class="pg-name">{row[ctx["ad_col"]]}</div>'
                    f'<div class="pg-price">{fiyat:.2f} ₺</div>'
                    f'<div class="pg-badge {cls}">{icon} %{abs(fark):.2f}</div>'
                    f'</div><div style="margin-bottom:15px;"></div>',
                    unsafe_allow_html=True
                )
    else:
        st.info("Kriterlere uygun ürün bulunamadı.")


# ─────────────────────────────────────────────
# 14. SAYFA: TAM LİSTE
# ─────────────────────────────────────────────
def sayfa_tam_liste(ctx):
    st.markdown("### 📋 Detaylı Veri Seti")
    df     = ctx["df_analiz"].dropna(subset=[ctx['son'], ctx['ad_col']])
    gunler = ctx["gunler"]

    def fix_sparkline(row):
        vals = row.tolist()
        if vals and min(vals) == max(vals):
            vals[-1] += 0.00001
        return vals

    # Yalnızca var olan gün sütunlarını kullan
    gun_cols  = [g for g in gunler if g in df.columns]
    df['Fiyat_Trendi'] = df[gun_cols].apply(fix_sparkline, axis=1)

    cols_show = ['Grup', ctx['ad_col'], 'Fiyat_Trendi', 'Gunluk_Degisim']
    if ctx['baz_col'] in df.columns: cols_show.insert(3, ctx['baz_col'])
    if ctx['son']     in df.columns: cols_show.insert(4, ctx['son'])

    col_config = {
        'Fiyat_Trendi':       st.column_config.LineChartColumn("Trend", width="small", y_min=0),
        ctx['ad_col']:        "Ürün Adı",
        'Gunluk_Degisim':     st.column_config.ProgressColumn("Değişim", format="%.2f%%", min_value=-0.5, max_value=0.5),
    }
    if ctx['baz_col'] in df.columns:
        col_config[ctx['baz_col']] = st.column_config.NumberColumn("Baz Fiyat", format="%.2f ₺")
    if ctx['son'] in df.columns:
        col_config[ctx['son']] = st.column_config.NumberColumn("Son Fiyat", format="%.2f ₺")

    st.data_editor(
        df[[c for c in cols_show if c in df.columns]],
        column_config=col_config,
        hide_index=True,
        use_container_width=True,
        height=600,
        disabled=True,          # ← düzenlemeyi kapat
    )

    # İndir: tam veri
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.drop(columns=['Fiyat_Trendi'], errors='ignore').to_excel(writer, index=False)
    st.download_button("📥 Excel Olarak İndir", data=output.getvalue(), file_name="Veri_Seti.xlsx")

    # İndir: ürün & kategori raporu
    ag = ctx["agirlik_col"]
    df_kat = df.copy()
    df_kat[ag] = pd.to_numeric(df_kat[ag], errors='coerce').fillna(0)

    def agirlikli_ort(x):
        w   = x[ag]
        val = x['Fark_Yuzde']
        return (w * val).sum() / w.sum() if w.sum() > 0 else 0

    df_kategori = (
        df_kat.groupby('Grup')
        .apply(agirlikli_ort)
        .reset_index(name='Agirlikli_Ort')
    )
    df_kategori['Agirlikli_Ort'] = df_kategori['Agirlikli_Ort'].round(2)
    df_kategori = df_kategori.sort_values('Agirlikli_Ort', ascending=False)
    df_kategori.columns = ['Kategori', 'Ağırlıklı Ortalama Değişim (%)']

    df_urun = df[[ctx['ad_col'], 'Fark_Yuzde']].copy()
    df_urun.columns = ['Ürün Adı', 'Ay Başına Göre Değişim (%)']
    df_urun['Ay Başına Göre Değişim (%)'] = df_urun['Ay Başına Göre Değişim (%)'].round(2)
    df_urun = df_urun.sort_values('Ay Başına Göre Değişim (%)', ascending=False)

    output2 = BytesIO()
    with pd.ExcelWriter(output2, engine='openpyxl') as writer:
        df_urun.to_excel(writer, index=False, sheet_name='Ürün_Bazlı')
        df_kategori.to_excel(writer, index=False, sheet_name='Kategori_Bazlı')
    st.download_button(
        "📥 Ürün & Kategori Raporu İndir",
        data=output2.getvalue(),
        file_name="Urun_Kategori_Raporu.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ─────────────────────────────────────────────
# 15. SAYFA: MADDELER
# ─────────────────────────────────────────────
def sayfa_maddeler(ctx):
    df          = ctx["df_analiz"]
    agirlik_col = ctx["agirlik_col"]
    ad_col      = ctx["ad_col"]

    st.markdown("### 📦 Kategori ve Madde Analizi")
    st.markdown("#### 📊 Sektörel Enflasyon (Ay Başına Göre)")

    def agirlikli_ort(x):
        w   = x[agirlik_col]
        val = x['Fark_Yuzde']
        return (w * val).sum() / w.sum() if w.sum() > 0 else 0

    df_cat_summary = (
        df.groupby('Grup')
        .apply(agirlikli_ort)
        .reset_index(name='Ortalama_Degisim')
        .sort_values('Ortalama_Degisim', ascending=True)
    )

    fig_cat = px.bar(
        df_cat_summary, x='Ortalama_Degisim', y='Grup',
        orientation='h', text_auto='.2f',
        color='Ortalama_Degisim',
        color_continuous_scale=['#10b981', '#f59e0b', '#ef4444']
    )
    fig_cat.update_layout(
        title="Kategori Bazlı Enflasyon (%)",
        xaxis_title="Değişim (%)", yaxis_title="", height=400,
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(style_chart(fig_cat), use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🔎 Ürün Bazlı Detaylar")

    kategoriler = ["TÜMÜ"] + sorted(df['Grup'].unique().tolist())
    col1, _ = st.columns([1, 3])
    with col1:
        secilen_kat = st.selectbox("Kategori Seçiniz:", options=kategoriler, index=0)

    df_sub = (df.copy() if secilen_kat == "TÜMÜ" else df[df['Grup'] == secilen_kat].copy())
    df_sub = df_sub.sort_values('Fark_Yuzde', ascending=True)

    if not df_sub.empty:
        colors = [
            '#10b981' if x < 0 else ('#fde047' if x < 2.5 else '#ef4444')
            for x in df_sub['Fark_Yuzde']
        ]
        fig = go.Figure(go.Bar(
            x=df_sub['Fark_Yuzde'], y=df_sub[ad_col], orientation='h',
            marker_color=colors,
            text=df_sub['Fark_Yuzde'].apply(lambda x: f"%{x:.2f}"),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Değişim: %%{x:.2f}<extra></extra>'
        ))
        fig.update_layout(
            height=max(500, len(df_sub) * 30),
            title=f"{secilen_kat} — Ürün Fiyat Değişimleri",
            xaxis_title="Değişim Oranı (%)",
            yaxis=dict(title="", showgrid=False),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)

        with st.expander("📄 Verileri Tablo Olarak Gör"):
            st.dataframe(
                df_sub[[ad_col, 'Grup', 'Fark_Yuzde']].sort_values('Fark_Yuzde', ascending=False),
                column_config={"Fark_Yuzde": st.column_config.NumberColumn("Değişim (%)", format="%.2f %%")},
                use_container_width=True, hide_index=True
            )
    else:
        st.warning("Bu kategoride görüntülenecek veri bulunamadı.")


# ─────────────────────────────────────────────
# 16. SAYFA: TRENDLER
# ─────────────────────────────────────────────
def sayfa_trend_analizi(ctx):
    st.markdown("### 📈 Trend Analizleri")
    df     = ctx["df_analiz"]
    gunler = [g for g in ctx["gunler"] if g in df.columns]

    st.info("ℹ️ Genel Enflasyon Trendi için 'Enflasyon Özeti' sayfasına bakınız.")
    st.subheader("Ürün Bazlı Fiyat Trendleri")

    default_urunler = (
        df.sort_values('Fark_Yuzde', ascending=False)
        .head(3)[ctx['ad_col']].tolist()
    )
    secilen_urunler = st.multiselect(
        "Grafiğe eklenecek ürünleri seçin:",
        options=df[ctx['ad_col']].unique().tolist(),
        default=default_urunler
    )

    if secilen_urunler and gunler:
        df_sel    = df[df[ctx['ad_col']].isin(secilen_urunler)][[ctx['ad_col']] + gunler]
        df_melted = df_sel.melt(id_vars=[ctx['ad_col']], var_name='Tarih', value_name='Fiyat')
        df_melted['Fiyat'] = pd.to_numeric(df_melted['Fiyat'], errors='coerce')

        baz_prices = (
            df_melted[df_melted['Tarih'] == gunler[0]]
            .set_index(ctx['ad_col'])['Fiyat']
            .to_dict()
        )
        df_melted['Yuzde_Degisim'] = df_melted.apply(
            lambda row: ((row['Fiyat'] / baz_prices.get(row[ctx['ad_col']], np.nan)) - 1) * 100
            if baz_prices.get(row[ctx['ad_col']], 0) > 0 else 0,
            axis=1
        )

        fig = px.line(
            df_melted, x='Tarih', y='Yuzde_Degisim',
            color=ctx['ad_col'],
            title="Ürün Bazlı Kümülatif Değişim (%)",
            markers=True
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)


# ─────────────────────────────────────────────
# 17. ANA FONKSİYON
# ─────────────────────────────────────────────
def main():
    SENKRONIZASYON_AKTIF = True

    now_tr = (datetime.utcnow() + timedelta(hours=3)).strftime("%d.%m.%Y")
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
        padding:20px 30px;background:rgba(15,23,42,0.4);backdrop-filter:blur(20px);
        border:1px solid rgba(255,255,255,0.05);border-radius:16px;
        margin-bottom:25px;margin-top:-30px;animation:fadeInUp 0.5s;
        box-shadow:0 10px 30px rgba(0,0,0,0.3);">
        <div>
            <div style="font-weight:800;font-size:28px;" class="gradient-text">
                Enflasyon Monitörü
                <span style="background:rgba(59,130,246,0.15);color:#60a5fa;font-size:10px;
                    padding:4px 10px;border-radius:6px;border:1px solid rgba(59,130,246,0.3);
                    vertical-align:middle;margin-left:10px;
                    box-shadow:0 0 10px rgba(59,130,246,0.2);
                    animation:pulseGlow 2s infinite;">SİMÜLASYON AKTİF</span>
            </div>
            <div style="font-size:13px;color:#94a3b8;font-weight:500;margin-top:4px;">
                Yapay Zeka Destekli Enflasyon Analiz Platformu
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:11px;color:#64748b;font-weight:800;letter-spacing:2px;">TÜRKİYE SAATİ</div>
            <div style="font-size:22px;font-weight:800;color:#e2e8f0;
                font-family:'JetBrains Mono';text-shadow:0 0 15px rgba(255,255,255,0.2);">{now_tr}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    menu_items = {
        "📊 Enflasyon Özeti": "Enflasyon Özeti",
        "📈 Trendler":        "Trendler",
        "📦 Maddeler":        "Maddeler",
        "🏷️ Kategori Detay": "Kategori Detay",
        "📋 Tam Liste":       "Tam Liste",
    }
    secilen_etiket = st.radio(
        "Navigasyon",
        options=list(menu_items.keys()),
        label_visibility="collapsed",
        key="nav_radio",
        horizontal=True
    )
    secim = menu_items[secilen_etiket]

    if SENKRONIZASYON_AKTIF:
        _, col_sync = st.columns([3, 1])
        with col_sync:
            sync_clicked = st.button(
                "SİSTEMİ SENKRONİZE ET ⚡", type="primary", use_container_width=True
            )

        if sync_clicked:
            progress_bar = st.progress(0, text="Veri akışı sağlanıyor...")
            res = html_isleyici(
                lambda p: progress_bar.progress(
                    min(1.0, max(0.0, p)), text="Senkronizasyon sürüyor..."
                )
            )
            progress_bar.progress(1.0, text="Tamamlandı!")
            time.sleep(0.5)
            progress_bar.empty()

            if "OK" in str(res):
                st.cache_data.clear()
                st.session_state.clear()
                st.success('Sistem Senkronize Edildi! Sayfa yenileniyor...', icon='🚀')
                time.sleep(1)
                st.rerun()
            elif "Veri bulunamadı" in str(res):
                st.warning("⚠️ Yeni veri yok. Güncellenecek ZIP veya manuel fiyat bulunamadı.")
            else:
                st.error(f"⚠️ Senkronizasyon hatası: {res}")

    with st.spinner("Veritabanına bağlanılıyor..."):
        df_base, r_dates, col_name, err_msg = verileri_getir_cache()

    if err_msg:
        st.sidebar.error(err_msg)

    ctx = None
    if df_base is not None:
        ctx = ui_sidebar_ve_veri_hazirlama(df_base, r_dates, col_name)

    if ctx:
        if   secim == "Enflasyon Özeti": sayfa_piyasa_ozeti(ctx)
        elif secim == "Trendler":        sayfa_trend_analizi(ctx)
        elif secim == "Maddeler":        sayfa_maddeler(ctx)
        elif secim == "Kategori Detay":  sayfa_kategori_detay(ctx)
        elif secim == "Tam Liste":       sayfa_tam_liste(ctx)
    else:
        st.markdown(
            "<div style='text-align:center;padding:20px;background:rgba(255,0,0,0.1);"
            "border-radius:10px;color:#fff;'>"
            "⚠️ Veri seti yüklenemedi. GitHub secrets yapılandırmanızı kontrol edin "
            "veya sayfayı yenileyin.</div>",
            unsafe_allow_html=True
        )

    st.markdown(
        '<div style="text-align:center;color:#52525b;font-size:11px;'
        'margin-top:50px;opacity:0.6;">VALIDASYON MÜDÜRLÜĞÜ © 2026</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
