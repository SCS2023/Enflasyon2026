# GEREKLİ KÜTÜPHANELER:
# pip install streamlit-lottie python-docx plotly pandas xlsxwriter matplotlib requests

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
import matplotlib.pyplot as plt
import matplotlib
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from streamlit_lottie import st_lottie

# --- 1. AYARLAR VE TEMA YÖNETİMİ ---
st.set_page_config(
    page_title="Piyasa Monitörü | Pro Analytics",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="expanded"
)

# --- CSS MOTORU (DÜZELTİLDİ: f-string kaldırıldı) ---
def apply_theme():
    if 'plotly_template' not in st.session_state:
        st.session_state.plotly_template = "plotly_dark"

    # BURADAKİ 'f' HARFİ KALDIRILDI, ARTIK DÜZ STRING
    final_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

        :root {
            --bg-dark: #09090b;
            --bg-card: rgba(24, 24, 27, 0.6);
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-primary: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.5);
            --text-primary: #f4f4f5;
            --text-secondary: #a1a1aa;
            --success: #10b981;
            --danger: #ef4444;
        }

        /* Genel Sayfa Yapısı */
        .stApp {
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.08), transparent 40%),
                radial-gradient(circle at 0% 50%, rgba(16, 185, 129, 0.05), transparent 40%);
            font-family: 'Inter', sans-serif;
        }

        /* Header Gizleme */
        header {visibility: hidden;}
        [data-testid="stHeader"] { visibility: hidden; height: 0px; }
        
        /* Sidebar Özelleştirme */
        section[data-testid="stSidebar"] {
            background-color: #0c0c0e !important;
            border-right: 1px solid var(--border-color);
        }
        
        /* --- MODERN TAB MENU (Radio Butonu Dönüştürme) --- */
        [data-testid="stRadio"] > div {
            display: flex;
            flex-wrap: wrap;
            background: #18181b;
            padding: 6px;
            border-radius: 16px;
            border: 1px solid var(--border-color);
            gap: 4px;
            justify-content: center;
        }

        [data-testid="stRadio"] label {
            flex: 1;
            min-width: 100px;
            background: transparent;
            color: var(--text-secondary) !important;
            border: 1px solid transparent;
            border-radius: 12px;
            padding: 8px 16px;
            text-align: center;
            font-weight: 500;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        [data-testid="stRadio"] label:hover {
            color: #fff !important;
            background: rgba(255,255,255,0.05);
        }

        [data-testid="stRadio"] label[data-checked="true"] {
            background: #27272a;
            color: #fff !important;
            border: 1px solid #3f3f46;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            font-weight: 600;
        }

        [data-testid="stRadio"] div[role="radiogroup"] > :first-child {
            display: none;
        }

        /* --- KART TASARIMLARI (Glassmorphism) --- */
        .kpi-card {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .kpi-card:hover {
            border-color: rgba(255,255,255,0.15);
            box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
            transform: translateY(-2px);
        }

        .kpi-title {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: var(--text-secondary);
            font-weight: 600;
            margin-bottom: 8px;
        }

        .kpi-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 32px;
            font-weight: 700;
            color: #fff;
            letter-spacing: -1px;
            margin-bottom: 4px;
        }
        
        .kpi-sub {
            font-size: 12px;
            font-weight: 500;
            padding: 4px 8px;
            border-radius: 6px;
            width: fit-content;
            background: rgba(255,255,255,0.03);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* --- TICKER BANDI --- */
        .ticker-wrap {
            width: 100%;
            overflow: hidden;
            background: #0f1014;
            border-y: 1px solid var(--border-color);
            padding: 10px 0;
            white-space: nowrap;
            margin-bottom: 30px;
        }
        .ticker-move {
            display: inline-block;
            white-space: nowrap;
            padding-right: 100%;
            animation: marquee 40s linear infinite;
        }
        .ticker-item {
            display: inline-block;
            padding: 0 2rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
        }
        @keyframes marquee {
            0% { transform: translate3d(0, 0, 0); }
            100% { transform: translate3d(-100%, 0, 0); }
        }

        /* --- FİYAT KARTLARI (Grid) --- */
        .pg-card {
            background: rgba(30, 30, 35, 0.4);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.2s;
        }
        .pg-card:hover {
            background: rgba(40, 40, 45, 0.6);
            border-color: var(--accent-primary);
        }
        .pg-name {
            font-size: 13px;
            color: #e4e4e7;
            font-weight: 500;
            line-height: 1.4;
            margin-bottom: 8px;
            overflow: hidden; 
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }
        .pg-price {
            font-family: 'JetBrains Mono', monospace;
            font-size: 18px;
            font-weight: 700;
            color: #fff;
        }
        .pg-badge {
            font-size: 11px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 99px;
            width: fit-content;
            margin-top: 8px;
        }
        .pg-red { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.2); }
        .pg-green { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.2); }
        .pg-yellow { background: rgba(234, 179, 8, 0.15); color: #fde047; border: 1px solid rgba(234, 179, 8, 0.2); }

        /* Butonlar */
        div.stButton > button {
            background: linear-gradient(180deg, #27272a 0%, #18181b 100%);
            border: 1px solid #3f3f46;
            color: #fff;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s;
            padding: 0.5rem 1rem;
        }
        div.stButton > button:hover {
            border-color: var(--accent-primary);
            color: var(--accent-primary);
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
        }
        
        /* Selectbox & Input */
        div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
            background-color: #18181b;
            border-color: #3f3f46;
            color: white;
            border-radius: 8px;
        }
    </style>
    """
    st.markdown(final_css, unsafe_allow_html=True)

apply_theme()

# --- 2. GITHUB & VERİ MOTORU ---
EXCEL_DOSYASI = "TUFE_Konfigurasyon.xlsx"
FIYAT_DOSYASI = "Fiyat_Veritabani.xlsx"
SAYFA_ADI = "Madde_Sepeti"

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# --- 3. RAPOR MOTORU ---
def create_word_report(text_content, tarih, df_analiz=None):
    try:
        doc = Document()
        matplotlib.use('Agg')
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(11)
        head = doc.add_heading(f'PİYASA GÖRÜNÜM RAPORU', 0)
        head.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subhead = doc.add_paragraph(f'Rapor Tarihi: {tarih}')
        subhead.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        doc.add_paragraph("")
        paragraphs = text_content.split('\n')
        for p_text in paragraphs:
            if not p_text.strip(): continue
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            parts = p_text.split('**')
            for i, part in enumerate(parts):
                run = p.add_run(part)
                if i % 2 == 1: 
                    run.bold = True
                    run.font.color.rgb = RGBColor(0, 50, 100) 
        if df_analiz is not None and not df_analiz.empty:
            doc.add_page_break()
            doc.add_heading('EKLER: GÖRSEL ANALİZLER', 1)
            doc.add_paragraph("")
            try:
                if 'Fark' in df_analiz.columns:
                    data = pd.to_numeric(df_analiz['Fark'], errors='coerce').dropna() * 100
                    if not data.empty:
                        fig, ax = plt.subplots(figsize=(6, 4))
                        ax.hist(data, bins=20, color='#3b82f6', edgecolor='white', alpha=0.7)
                        ax.set_title(f"Fiyat Değişim Dağılımı (%) - {tarih}", fontsize=12, fontweight='bold')
                        memfile = BytesIO()
                        plt.savefig(memfile, format='png', dpi=100)
                        plt.close(fig)
                        doc.add_picture(memfile, width=Inches(5.5))
                        memfile.close()
                        doc.add_paragraph("Grafik 1: Ürünlerin fiyat değişim oranlarına göre dağılımı.")
            except Exception:
                pass
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        return BytesIO()

# --- 4. GITHUB İŞLEMLERİ ---
@st.cache_resource
def get_github_connection():
    try:
        return Github(st.secrets["github"]["token"])
    except:
        return None

def get_github_repo():
    g = get_github_connection()
    if g:
        return g.get_repo(st.secrets["github"]["repo_name"])
    return None

@st.cache_data(ttl=600, show_spinner=False)
def github_excel_oku(dosya_adi, sayfa_adi=None):
    repo = get_github_repo()
    if not repo: return pd.DataFrame()
    try:
        c = repo.get_contents(dosya_adi, ref=st.secrets["github"]["branch"])
        if sayfa_adi:
            df = pd.read_excel(BytesIO(c.decoded_content), sheet_name=sayfa_adi, dtype=str)
        else:
            df = pd.read_excel(BytesIO(c.decoded_content), dtype=str)
        return df
    except:
        return pd.DataFrame()

def github_excel_guncelle(df_yeni, dosya_adi):
    repo = get_github_repo()
    if not repo: return "Repo Yok"
    try:
        try:
            c = repo.get_contents(dosya_adi, ref=st.secrets["github"]["branch"])
            old = pd.read_excel(BytesIO(c.decoded_content), dtype=str)
            yeni_tarih = str(df_yeni['Tarih'].iloc[0])
            old = old[~((old['Tarih'].astype(str) == yeni_tarih) & (old['Kod'].isin(df_yeni['Kod'])))]
            final = pd.concat([old, df_yeni], ignore_index=True)
        except:
            c = None; final = df_yeni
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as w:
            final.to_excel(w, index=False, sheet_name='Fiyat_Log')
        msg = f"Data Update"
        if c:
            repo.update_file(c.path, msg, out.getvalue(), c.sha, branch=st.secrets["github"]["branch"])
        else:
            repo.create_file(dosya_adi, msg, out.getvalue(), branch=st.secrets["github"]["branch"])
        return "OK"
    except Exception as e:
        return str(e)

# --- 5. RESMİ ENFLASYON (CACHED) ---
@st.cache_data(ttl=3600, show_spinner=False)
def get_official_inflation():
    api_key = st.secrets.get("evds", {}).get("api_key")
    if not api_key: return None, "API Key Yok"
    start_date = (datetime.now() - timedelta(days=365)).strftime("%d-%m-%Y")
    end_date = datetime.now().strftime("%d-%m-%Y")
    url = f"https://evds2.tcmb.gov.tr/service/evds/series=TP.FG.J0&startDate={start_date}&endDate={end_date}&type=json"
    headers = {'User-Agent': 'Mozilla/5.0', 'key': api_key, 'Accept': 'application/json'}
    try:
        url_with_key = f"{url}&key={api_key}"
        res = requests.get(url_with_key, headers=headers, timeout=10, verify=False)
        if res.status_code == 200:
            data = res.json()
            if "items" in data:
                df_evds = pd.DataFrame(data["items"])
                df_evds = df_evds[['Tarih', 'TP_FG_J0']]
                df_evds.columns = ['Tarih', 'Resmi_TUFE']
                df_evds['Tarih'] = pd.to_datetime(df_evds['Tarih'] + "-01", format="%Y-%m-%d")
                df_evds['Resmi_TUFE'] = pd.to_numeric(df_evds['Resmi_TUFE'], errors='coerce')
                return df_evds, "OK"
        return None, "Hata"
    except Exception as e:
        return None, str(e)

# --- 6. SCRAPER YARDIMCILARI ---
def temizle_fiyat(t):
    if not t: return None
    t = str(t).replace('TL', '').replace('₺', '').strip()
    t = t.replace('.', '').replace(',', '.') if ',' in t and '.' in t else t.replace(',', '.')
    try:
        return float(re.sub(r'[^\d.]', '', t))
    except:
        return None

def kod_standartlastir(k): return str(k).replace('.0', '').strip().zfill(7)

def fiyat_bul_siteye_gore(soup, url):
    fiyat = 0; kaynak = ""; domain = url.lower() if url else ""
    # Basit Regex ve CSS arama
    if m := re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺)', soup.get_text()[:5000]):
        if v := temizle_fiyat(m.group(1)): fiyat = v; kaynak = "Regex"
    return fiyat, kaynak

def html_isleyici(progress_callback):
    repo = get_github_repo()
    if not repo: return "GitHub Bağlantı Hatası"
    progress_callback(0.05) 
    try:
        df_conf = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
        df_conf.columns = df_conf.columns.str.strip()
        kod_col = next((c for c in df_conf.columns if c.lower() == 'kod'), None)
        url_col = next((c for c in df_conf.columns if c.lower() == 'url'), None)
        ad_col = next((c for c in df_conf.columns if 'ad' in c.lower()), 'Madde adı')
        if not kod_col or not url_col: return "Hata: Excel sütunları eksik."
        df_conf['Kod'] = df_conf[kod_col].astype(str).apply(kod_standartlastir)
        url_map = {str(row[url_col]).strip(): row for _, row in df_conf.iterrows() if pd.notna(row[url_col])}
        veriler = []
        islenen_kodlar = set()
        bugun = datetime.now().strftime("%Y-%m-%d")
        simdi = datetime.now().strftime("%H:%M")
        
        progress_callback(0.10)
        contents = repo.get_contents("", ref=st.secrets["github"]["branch"])
        zip_files = [c for c in contents if c.name.endswith(".zip") and c.name.startswith("Bolum")]
        total_zips = len(zip_files)
        
        for i, zip_file in enumerate(zip_files):
            current_progress = 0.10 + (0.80 * ((i + 1) / max(1, total_zips)))
            progress_callback(current_progress)
            try:
                blob = repo.get_git_blob(zip_file.sha)
                zip_data = base64.b64decode(blob.content)
                with zipfile.ZipFile(BytesIO(zip_data)) as z:
                    for file_name in z.namelist():
                        if not file_name.endswith(('.html', '.htm')): continue
                        with z.open(file_name) as f:
                            raw = f.read().decode("utf-8", errors="ignore")
                            soup = BeautifulSoup(raw, 'html.parser')
                            found_url = None
                            if c := soup.find("link", rel="canonical"): found_url = c.get("href")
                            if found_url and str(found_url).strip() in url_map:
                                target = url_map[str(found_url).strip()]
                                if target['Kod'] in islenen_kodlar: continue
                                fiyat, kaynak = fiyat_bul_siteye_gore(soup, target[url_col])
                                if fiyat > 0:
                                    veriler.append({"Tarih": bugun, "Zaman": simdi, "Kod": target['Kod'],
                                                    "Madde_Adi": target[ad_col], "Fiyat": float(fiyat),
                                                    "Kaynak": kaynak, "URL": target[url_col]})
                                    islenen_kodlar.add(target['Kod'])
            except: pass
        
        progress_callback(0.95)
        if veriler:
            return github_excel_guncelle(pd.DataFrame(veriler), FIYAT_DOSYASI)
        else:
            return "Veri bulunamadı."
    except Exception as e:
        return f"Hata: {str(e)}"

# --- 7. STATİK ANALİZ MOTORU ---
def generate_detailed_static_report(df_analiz, tarih, enf_genel, enf_gida, gun_farki, tahmin, ad_col, agirlik_col):
    df_clean = df_analiz.dropna(subset=['Fark'])
    toplam_urun = len(df_clean)
    artanlar = df_clean[df_clean['Fark'] > 0]
    dusenler = df_clean[df_clean['Fark'] < 0]
    sabitler = df_clean[df_clean['Fark'] == 0]
    artan_sayisi = len(artanlar)
    yayilim_orani = (artan_sayisi / toplam_urun) * 100 if toplam_urun > 0 else 0
    inc = df_clean.sort_values('Fark', ascending=False).head(5)
    dec = df_clean.sort_values('Fark', ascending=True).head(5)
    inc_str = "\n".join([f"   🔴 %{row['Fark']*100:5.2f} | {row[ad_col]}" for _, row in inc.iterrows()])
    dec_str = "\n".join([f"   🟢 %{abs(row['Fark']*100):5.2f} | {row[ad_col]}" for _, row in dec.iterrows()])

    text = f"""
**PİYASA GÖRÜNÜM RAPORU**
**Tarih:** {tarih}

**1. 📊 ANA GÖSTERGELER**
-----------------------------------------
**GENEL ENFLASYON** : **%{enf_genel:.2f}**
**GIDA ENFLASYONU** : **%{enf_gida:.2f}**
**AY SONU TAHMİNİ** : **%{tahmin:.2f}**
-----------------------------------------

**2. 🔎 PİYASA RÖNTGENİ**
**Fiyat Hareketleri:**
   🔺 **Zamlanan Ürün:** {artan_sayisi} adet
   🔻 **İndirimli Ürün:** {len(dusenler)} adet
   ➖ **Fiyatı Değişmeyen:** {len(sabitler)} adet

**Sepet Yayılımı:**
   Her 100 üründen **{int(yayilim_orani)}** tanesinde fiyat artışı tespit edilmiştir.

**3. ⚡ DİKKAT ÇEKEN ÜRÜNLER**

**▲ Yüksek Artışlar (Cep Yakanlar)**
{inc_str}

**▼ Fiyat Düşüşleri (Fırsatlar)**
{dec_str}

**4. 💡 SONUÇ**
Tahmin modelimiz, ay sonu kapanışının **%{tahmin:.2f}** bandında olacağını öngörmektedir.

---
*Otomatik Rapor Sistemi | Validasyon Müdürlüğü*
"""
    return text.strip()

# --- YENİ YARDIMCI FONKSİYONLAR ---
def make_neon_chart(fig):
    # Ana çizgiye glow efekti ve kalınlık ver
    fig.update_traces(line=dict(width=3, color='#3b82f6')) # Neon mavi ana renk
    
    # Glow efekti için aynı çizgiyi opak ve kalın olarak arkaya ekle
    new_traces = []
    for trace in fig.data:
        if trace.type == 'scatter' or trace.type == 'line':
            glow_trace = go.Scatter(
                x=trace.x, y=trace.y, mode='lines',
                line=dict(width=10, color=trace.line.color), opacity=0.2, 
                hoverinfo='skip', showlegend=False
            )
            new_traces.append(glow_trace)
    
    # Sıralamayı ayarla: glow arkada, ana çizgi önde
    fig.data = tuple(new_traces) + fig.data
    
    return fig

def style_chart(fig, is_pdf=False, is_sunburst=False):
    if is_pdf:
        fig.update_layout(template="plotly_white", font=dict(family="Arial", size=14, color="black"))
    else:
        # Minimalist "Clean Dark" Tema
        layout_args = dict(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#a1a1aa", size=12),
            margin=dict(l=0, r=0, t=40, b=0),
            hoverlabel=dict(bgcolor="#18181b", bordercolor="#3b82f6", font=dict(family="JetBrains Mono", color="#fff"))
        )
        if not is_sunburst:
            layout_args.update(dict(
                xaxis=dict(
                    showgrid=False, 
                    zeroline=False, 
                    showline=True, 
                    linecolor="#3f3f46", 
                    tickfont=dict(color="#71717a"),
                    dtick="M1"
                ),
                yaxis=dict(
                    showgrid=True, 
                    gridcolor="rgba(255,255,255,0.05)", 
                    zeroline=False, 
                    gridwidth=1,
                    tickfont=dict(color="#71717a")
                )
            ))
        fig.update_layout(**layout_args)
    return fig

# --- 9. VERİ VE HESAPLAMA MOTORLARI (CACHE) ---

# 1. VERİ GETİR
@st.cache_data(ttl=600, show_spinner=False)
def verileri_getir_cache():
    df_f = github_excel_oku(FIYAT_DOSYASI)
    df_s = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
    if df_f.empty or df_s.empty: return None, None, None

    df_f['Tarih_DT'] = pd.to_datetime(df_f['Tarih'], errors='coerce')
    df_f = df_f.dropna(subset=['Tarih_DT']).sort_values('Tarih_DT')
    df_f['Tarih_Str'] = df_f['Tarih_DT'].dt.strftime('%Y-%m-%d')
    raw_dates = df_f['Tarih_Str'].unique().tolist()

    df_s.columns = df_s.columns.str.strip()
    kod_col = next((c for c in df_s.columns if c.lower() == 'kod'), 'Kod')
    ad_col = next((c for c in df_s.columns if 'ad' in c.lower()), 'Madde_Adi')
    df_f['Kod'] = df_f['Kod'].astype(str).apply(kod_standartlastir)
    df_s['Kod'] = df_s[kod_col].astype(str).apply(kod_standartlastir)
    df_s = df_s.drop_duplicates(subset=['Kod'], keep='first')
    df_f['Fiyat'] = pd.to_numeric(df_f['Fiyat'], errors='coerce')
    df_f = df_f[df_f['Fiyat'] > 0]
    
    pivot = df_f.pivot_table(index='Kod', columns='Tarih_Str', values='Fiyat', aggfunc='mean')
    pivot = pivot.ffill(axis=1).bfill(axis=1).reset_index()
    if pivot.empty: return None, None, None

    if 'Grup' not in df_s.columns:
        grup_map = {"01": "Gıda", "02": "Alkol-Tütün", "03": "Giyim", "04": "Konut"}
        df_s['Grup'] = df_s['Kod'].str[:2].map(grup_map).fillna("Diğer")

    df_analiz_base = pd.merge(df_s, pivot, on='Kod', how='left')
    return df_analiz_base, raw_dates, ad_col

# 2. HESAPLAMA YAP (CACHED)
@st.cache_data(show_spinner=False)
def hesapla_metrikler(df_analiz_base, secilen_tarih, gunler, tum_gunler_sirali, ad_col, agirlik_col, baz_col, aktif_agirlik_col, son):
    df_analiz = df_analiz_base.copy()
    for col in gunler: df_analiz[col] = pd.to_numeric(df_analiz[col], errors='coerce')
    dt_son = datetime.strptime(son, '%Y-%m-%d')
    if baz_col in df_analiz.columns: df_analiz[baz_col] = df_analiz[baz_col].fillna(df_analiz[son])
    df_analiz[aktif_agirlik_col] = pd.to_numeric(df_analiz.get(aktif_agirlik_col, 0), errors='coerce').fillna(0)
    gecerli_veri = df_analiz[df_analiz[aktif_agirlik_col] > 0].copy()
    
    def geo_mean(row):
        vals = [x for x in row if isinstance(x, (int, float)) and x > 0]
        return np.exp(np.mean(np.log(vals))) if vals else np.nan

    bu_ay_str = f"{dt_son.year}-{dt_son.month:02d}"
    bu_ay_cols = [c for c in gunler if c.startswith(bu_ay_str)]
    if not bu_ay_cols: bu_ay_cols = [son]
    
    gecerli_veri['Aylik_Ortalama'] = gecerli_veri[bu_ay_cols].apply(geo_mean, axis=1)
    gecerli_veri = gecerli_veri.dropna(subset=['Aylik_Ortalama', baz_col])

    enf_genel = 0.0; enf_gida = 0.0
    if not gecerli_veri.empty:
        w = gecerli_veri[aktif_agirlik_col]
        p_rel = gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]
        if w.sum() > 0: enf_genel = (w * p_rel).sum() / w.sum() * 100 - 100
        
        gida_df = gecerli_veri[gecerli_veri['Kod'].astype(str).str.startswith("01")]
        if not gida_df.empty and gida_df[aktif_agirlik_col].sum() > 0:
            enf_gida = ((gida_df[aktif_agirlik_col] * (gida_df['Aylik_Ortalama']/gida_df[baz_col])).sum() / gida_df[aktif_agirlik_col].sum() * 100) - 100
            
        df_analiz['Fark'] = 0.0
        df_analiz.loc[gecerli_veri.index, 'Fark'] = (gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]) - 1
        df_analiz['Fark_Yuzde'] = df_analiz['Fark'] * 100
    
    gun_farki = 0
    if len(gunler) >= 2:
        onceki_gun = gunler[-2]
        df_analiz['Gunluk_Degisim'] = (df_analiz[son] / df_analiz[onceki_gun].replace(0, np.nan)) - 1
    else:
        df_analiz['Gunluk_Degisim'] = 0
        onceki_gun = son

    month_end_forecast = 0.0
    target_fixed = f"{dt_son.year}-{dt_son.month:02d}-31"
    fixed_cols = [c for c in tum_gunler_sirali if c.startswith(bu_ay_str) and c <= target_fixed]
    if fixed_cols and not gecerli_veri.empty:
        gecerli_veri['Fixed_Ort'] = gecerli_veri[fixed_cols].apply(geo_mean, axis=1)
        gecerli_t = gecerli_veri.dropna(subset=['Fixed_Ort'])
        if not gecerli_t.empty and gecerli_t[aktif_agirlik_col].sum() > 0:
             month_end_forecast = ((gecerli_t[aktif_agirlik_col] * (gecerli_t['Fixed_Ort']/gecerli_t[baz_col])).sum() / gecerli_t[aktif_agirlik_col].sum() * 100) - 100

    resmi_aylik_degisim = 0.0
    try:
        df_resmi, _ = get_official_inflation()
        if df_resmi is not None and not df_resmi.empty:
             df_resmi = df_resmi.sort_values('Tarih')
             if len(df_resmi) >= 2:
                 son_endeks = df_resmi.iloc[-1]['Resmi_TUFE']
                 onceki_endeks = df_resmi.iloc[-2]['Resmi_TUFE']
                 resmi_aylik_degisim = ((son_endeks / onceki_endeks) - 1) * 100
    except:
        resmi_aylik_degisim = 0.0

    return {
        "df_analiz": df_analiz, "enf_genel": enf_genel, "enf_gida": enf_gida,
        "tahmin": month_end_forecast, "resmi_aylik_degisim": resmi_aylik_degisim,
        "son": son, "onceki_gun": onceki_gun, "gunler": gunler,
        "ad_col": ad_col, "agirlik_col": aktif_agirlik_col, "baz_col": baz_col, "gun_farki": gun_farki,
        "stats_urun": len(df_analiz), "stats_kategori": df_analiz['Grup'].nunique(),
        "stats_veri_noktasi": len(df_analiz) * len(tum_gunler_sirali)
    }

# 3. SIDEBAR UI (CONTEXT_HAZIRLA YERİNE)
def ui_sidebar_ve_veri_hazirlama(df_analiz_base, raw_dates, ad_col):
    if df_analiz_base is None: return None
    st.sidebar.markdown("### ⚙️ Veri Ayarları")
    
    # Lottie
    lottie_url = "https://lottie.host/98606416-297c-4a37-9b2a-714013063529/5D6o8k8fW0.json"
    try:
        lottie_json = load_lottieurl(lottie_url)
        with st.sidebar:
             if lottie_json: st_lottie(lottie_json, height=120, key="nav_anim")
    except: pass

    BASLANGIC_LIMITI = "2026-02-04"
    tum_tarihler = sorted([d for d in raw_dates if d >= BASLANGIC_LIMITI], reverse=True)
    if not tum_tarihler:
        st.sidebar.warning("Veri henüz oluşmadı.")
        return None
    secilen_tarih = st.sidebar.selectbox("Rapor Tarihi:", options=tum_tarihler, index=0)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌍 Piyasalar")
    symbols = [ {"s": "FX_IDC:USDTRY", "d": "Dolar / TL"}, {"s": "FX_IDC:EURTRY", "d": "Euro / TL"}, {"s": "FX_IDC:XAUTRYG", "d": "Gram Altın"}, {"s": "TVC:UKOIL", "d": "Brent Petrol"}, {"s": "BINANCE:BTCUSDT", "d": "Bitcoin ($)"} ]
    for sym in symbols:
        widget_code = f"""<div class="tradingview-widget-container" style="border-radius:12px; overflow:hidden; margin-bottom:10px;"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>{{ "symbol": "{sym['s']}", "width": "100%", "height": 80, "locale": "tr", "dateRange": "1D", "colorTheme": "dark", "isTransparent": true, "autosize": true, "largeChartUrl": "" }}</script></div>"""
        with st.sidebar: components.html(widget_code, height=90)
    
    tum_gunler_sirali = sorted([c for c in df_analiz_base.columns if re.match(r'\d{4}-\d{2}-\d{2}', str(c)) and c >= BASLANGIC_LIMITI])
    if secilen_tarih in tum_gunler_sirali:
        idx = tum_gunler_sirali.index(secilen_tarih)
        gunler = tum_gunler_sirali[:idx+1]
    else: gunler = tum_gunler_sirali
    if not gunler: return None
    son = gunler[-1]; dt_son = datetime.strptime(son, '%Y-%m-%d')
    col_w25, col_w26 = 'Agirlik_2025', 'Agirlik_2026'
    ZINCIR_TARIHI = datetime(2026, 2, 4)
    if dt_son >= ZINCIR_TARIHI:
        aktif_agirlik_col = col_w26
        gunler_2026 = [c for c in tum_gunler_sirali if c >= "2026-01-01"]
        baz_col = gunler_2026[0] if gunler_2026 else gunler[0]
    else:
        aktif_agirlik_col = col_w25; baz_col = gunler[0]

    ctx = hesapla_metrikler(df_analiz_base, secilen_tarih, gunler, tum_gunler_sirali, ad_col, agirlik_col=None, baz_col=baz_col, aktif_agirlik_col=aktif_agirlik_col, son=son)
    return ctx

# --- SAYFA FONKSİYONLARI ---
def sayfa_ana_sayfa(ctx):
    urun_sayisi = ctx["stats_urun"] if ctx else "..."
    kategori_sayisi = ctx["stats_kategori"] if ctx else "..."
    veri_noktasi = ctx["stats_veri_noktasi"] if ctx else "..."
    
    # Hero Section - Daha Modern Tipografi
    st.markdown(f"""
    <div style="text-align:center; padding: 60px 20px;">
        <h1 style="font-size: 64px; font-weight: 800; letter-spacing: -2px; margin-bottom: 20px; 
            background: linear-gradient(135deg, #fff 30%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Enflasyonun Gerçek Yüzü
        </h1>
        <p style="font-size: 18px; color: #a1a1aa; max-width: 700px; margin: 0 auto 40px auto; line-height: 1.6;">
            Türkiye'nin en gelişmiş yapay zeka destekli fiyat takip sistemi. 
            <span style="color:#fff; font-weight:600;">{kategori_sayisi}</span> kategoride 
            <span style="color:#fff; font-weight:600;">{urun_sayisi}</span> ürünü anlık simüle ediyor, resmi verilerle kıyaslıyoruz.
        </p>
        
        <div style="display:flex; justify-content:center; gap:24px; flex-wrap:wrap;">
            <div class="kpi-card" style="width:240px; text-align:center; align-items:center;">
                <div style="color:#3b82f6; font-size:32px; margin-bottom:10px;">📦</div>
                <div style="font-size:36px; font-weight:800; color:#fff; font-family:'JetBrains Mono';">{urun_sayisi}</div>
                <div style="color:#71717a; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:1px;">Ürün Takipte</div>
            </div>
            <div class="kpi-card" style="width:240px; text-align:center; align-items:center;">
                <div style="color:#10b981; font-size:32px; margin-bottom:10px;">📊</div>
                <div style="font-size:36px; font-weight:800; color:#fff; font-family:'JetBrains Mono';">{kategori_sayisi}</div>
                <div style="color:#71717a; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:1px;">Alt Sektör</div>
            </div>
            <div class="kpi-card" style="width:240px; text-align:center; align-items:center;">
                <div style="color:#f59e0b; font-size:32px; margin-bottom:10px;">⚡</div>
                <div style="font-size:36px; font-weight:800; color:#fff; font-family:'JetBrains Mono';">{veri_noktasi}+</div>
                <div style="color:#71717a; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:1px;">Veri Noktası</div>
            </div>
        </div>

        <div style="margin-top:50px;">
            <div style="background: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.2); 
                 padding: 12px 24px; border-radius: 99px; display: inline-flex; align-items:center; gap:10px;">
                <span style="display:block; width:8px; height:8px; background:#10b981; border-radius:50%; box-shadow:0 0 10px #10b981;"></span>
                <span style="color: #93c5fd; font-size:14px; font-weight: 500;">
                    Sistem Botları Aktif • Son Güncelleme: <span style="color:#fff; font-family:'JetBrains Mono';">{datetime.now().strftime('%H:%M')}</span>
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def sayfa_piyasa_ozeti(ctx):
    # Ana KPI'lar - Flex Grid ile
    st.markdown("### ⚡ Piyasa Nabzı")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-title">GENEL ENFLASYON</div><div class="kpi-value">%{ctx["enf_genel"]:.2f}</div><div class="kpi-sub" style="color:#ef4444; background:rgba(239,68,68,0.1)">▲ Aylık Değişim</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-title">GIDA ENFLASYONU</div><div class="kpi-value">%{ctx["enf_gida"]:.2f}</div><div class="kpi-sub" style="color:#fca5a5; background:rgba(252,165,165,0.1)">🍲 Mutfak Sepeti</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-title">AY SONU BEKLENTİ</div><div class="kpi-value">%{ctx["tahmin"]:.2f}</div><div class="kpi-sub" style="color:#a78bfa; background:rgba(167,139,250,0.1)">🤖 AI Projeksiyonu</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi-card"><div class="kpi-title">RESMİ (TÜİK) VERİSİ</div><div class="kpi-value">%{ctx["resmi_aylik_degisim"]:.2f}</div><div class="kpi-sub" style="color:#fbbf24; background:rgba(251,191,36,0.1)">🏛️ Son Açıklanan</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Ticker
    df = ctx["df_analiz"]
    inc = df.sort_values('Gunluk_Degisim', ascending=False).head(5)
    dec = df.sort_values('Gunluk_Degisim', ascending=True).head(5)
    items = []
    for _, r in inc.iterrows():
        if r['Gunluk_Degisim'] > 0: items.append(f"<span class='ticker-item' style='color:#f87171'>▲ {r[ctx['ad_col']]} %{r['Gunluk_Degisim']*100:.1f}</span>")
    for _, r in dec.iterrows():
        if r['Gunluk_Degisim'] < 0: items.append(f"<span class='ticker-item' style='color:#34d399'>▼ {r[ctx['ad_col']]} %{r['Gunluk_Degisim']*100:.1f}</span>")
    st.markdown(f"""<div class="ticker-wrap"><div class="ticker-move">{"".join(items)}</div></div>""", unsafe_allow_html=True)
    
    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        st.markdown("#### Fiyat Değişim Dağılımı")
        fig_hist = px.histogram(df, x="Fark_Yuzde", nbins=25, color_discrete_sequence=["#3b82f6"])
        fig_hist.update_traces(marker_line_width=0, opacity=0.8)
        fig_hist.update_layout(bargap=0.1, margin=dict(t=10))
        fig_hist.update_xaxes(title_text=None, showticklabels=True, gridcolor='rgba(255,255,255,0.05)')
        fig_hist.update_yaxes(visible=False)
        st.plotly_chart(style_chart(fig_hist), use_container_width=True)
        
    with col_g2:
        st.markdown("#### Hareket Özeti")
        st.markdown(f"""
        <div style="background:var(--bg-card); border-radius:16px; padding:20px; border:1px solid var(--border-color);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:10px;">
                <span style="font-size:13px; color:#a1a1aa;">YÜKSELENLER</span>
                <span style="font-size:18px; color:#ef4444; font-weight:700; font-family:'JetBrains Mono';">{len(df[df['Fark'] > 0])}</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:10px;">
                <span style="font-size:13px; color:#a1a1aa;">DÜŞENLER</span>
                <span style="font-size:18px; color:#10b981; font-weight:700; font-family:'JetBrains Mono';">{len(df[df['Fark'] < 0])}</span>
            </div>
             <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:13px; color:#a1a1aa;">SABİT</span>
                <span style="font-size:18px; color:#fbbf24; font-weight:700; font-family:'JetBrains Mono';">{len(df[df['Fark'] == 0])}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("#### Sektörel Isı Haritası")
    fig_tree = px.treemap(df, path=[px.Constant("Piyasa"), 'Grup', ctx['ad_col']], values=ctx['agirlik_col'], color='Fark', color_continuous_scale='RdYlGn_r')
    st.plotly_chart(style_chart(fig_tree, is_sunburst=True), use_container_width=True)

def sayfa_kategori_detay(ctx):
    df = ctx["df_analiz"]
    st.markdown("### 🔍 Detaylı Fiyat Takibi")
    col_sel, col_src = st.columns([1, 2])
    kategoriler = ["Tümü"] + sorted(df['Grup'].unique().tolist())
    secilen_kat = col_sel.selectbox("Kategori Filtresi", kategoriler)
    arama = col_src.text_input("Ürün Arama", placeholder="Örn: Süt, Yumurta...")
    
    df_show = df.copy()
    if secilen_kat != "Tümü": df_show = df_show[df_show['Grup'] == secilen_kat]
    if arama: df_show = df_show[df_show[ctx['ad_col']].astype(str).str.contains(arama, case=False, na=False)]
    
    if not df_show.empty:
        items_per_page = 16
        # Pagination UI
        total_pages = max(1, len(df_show)//items_per_page + 1)
        col_p1, col_p2 = st.columns([1, 6])
        page_num = col_p1.number_input("Sayfa", min_value=1, max_value=total_pages, step=1)
        
        batch = df_show.iloc[(page_num - 1) * items_per_page : (page_num - 1) * items_per_page + items_per_page]
        cols = st.columns(4)
        for idx, row in enumerate(batch.to_dict('records')):
            fiyat = row[ctx['son']]; fark = row.get('Gunluk_Degisim', 0) * 100
            cls = "pg-red" if fark > 0 else ("pg-green" if fark < 0 else "pg-yellow")
            icon = "▲" if fark > 0 else ("▼" if fark < 0 else "•")
            with cols[idx % 4]:
                st.markdown(f"""
                <div class="pg-card">
                    <div>
                        <div class="pg-name" title="{row[ctx['ad_col']]}">{row[ctx['ad_col']]}</div>
                        <div class="pg-price">{fiyat:.2f} ₺</div>
                    </div>
                    <div class="pg-badge {cls}">{icon} %{abs(fark):.2f}</div>
                </div>
                <div style="margin-bottom:20px;"></div>
                """, unsafe_allow_html=True)
    else: st.info("Kriterlere uygun ürün bulunamadı.")

def sayfa_tam_liste(ctx):
    st.markdown("### 📋 Ham Veri Seti")
    df = ctx["df_analiz"]
    def fix_sparkline(row):
        vals = row.tolist(); 
        if vals and min(vals) == max(vals): vals[-1] += 0.00001
        return vals
    df['Fiyat_Trendi'] = df[ctx['gunler']].apply(fix_sparkline, axis=1)
    cols_show = ['Grup', ctx['ad_col'], 'Fiyat_Trendi', ctx['baz_col'], 'Gunluk_Degisim']
    if ctx['baz_col'] != ctx['son']: cols_show.insert(3, ctx['son'])
    cfg = {
        "Fiyat_Trendi": st.column_config.LineChartColumn("Trend", width="small", y_min=0), 
        ctx['ad_col']: "Ürün Adı", 
        "Gunluk_Degisim": st.column_config.ProgressColumn("Değişim", format="%.2f%%", min_value=-0.5, max_value=0.5), 
        ctx['baz_col']: st.column_config.NumberColumn(f"Baz Fiyat", format="%.2f ₺"), 
        ctx['son']: st.column_config.NumberColumn(f"Son Fiyat", format="%.2f ₺")
    }
    st.data_editor(df[cols_show], column_config=cfg, hide_index=True, use_container_width=True, height=600)
    output = BytesIO(); 
    with pd.ExcelWriter(output) as writer: df.to_excel(writer, index=False)
    st.download_button("📥 Excel Olarak İndir", data=output.getvalue(), file_name="Veri_Seti.xlsx")

def sayfa_raporlama(ctx):
    st.markdown("### 📝 Stratejik Pazar Raporu")
    col_l, col_r = st.columns([2, 1])
    with col_l:
        rap_text = generate_detailed_static_report(ctx["df_analiz"], ctx["son"], ctx["enf_genel"], ctx["enf_gida"], ctx["gun_farki"], ctx["tahmin"], ctx["ad_col"], ctx["agirlik_col"])
        st.markdown(f"""<div style="background:#18181b; padding:40px; border-radius:12px; border:1px solid #27272a; font-family:'Inter'; line-height:1.8; font-size:15px; box-shadow:0 10px 30px rgba(0,0,0,0.2);">{rap_text.replace(chr(10), '<br>').replace('**', '<b>').replace('**', '</b>')}</div>""", unsafe_allow_html=True)
    with col_r:
        st.markdown("#### İşlemler")
        word_buffer = create_word_report(rap_text, ctx["son"], ctx["df_analiz"])
        st.download_button(label="📥 Word Raporu İndir", data=word_buffer, file_name="Strateji_Raporu.docx", type="primary", use_container_width=True)
        st.info("Bu rapor, yapay zeka algoritmaları tarafından oluşturulmuş olup resmi yatırım tavsiyesi niteliği taşımaz.")

def sayfa_maddeler(ctx):
    df = ctx["df_analiz"]
    st.markdown("### 📦 Madde Bazlı Değişim Analizi")
    st.markdown("<p style='color:#a1a1aa; font-size:14px; margin-bottom:20px;'>Seçilen kategorideki ürünlerin, baz alınan tarihe göre kümülatif değişim oranları.</p>", unsafe_allow_html=True)
    kategoriler = sorted(df['Grup'].unique().tolist())
    col1, col2 = st.columns([1, 3])
    with col1: secilen_kat = st.selectbox("Kategori:", options=kategoriler, index=0)
    df_sub = df[df['Grup'] == secilen_kat].copy().sort_values('Fark_Yuzde', ascending=True)
    if not df_sub.empty:
        colors = ['#10b981' if x < 0 else '#ef4444' for x in df_sub['Fark_Yuzde']]
        fig = go.Figure(go.Bar(x=df_sub['Fark_Yuzde'], y=df_sub[ctx['ad_col']], orientation='h', marker_color=colors, text=df_sub['Fark_Yuzde'].apply(lambda x: f"%{x:.2f}"), textposition='outside', hovertemplate='<b>%{y}</b><br>Değişim: %%{x:.2f}<extra></extra>'))
        fig.update_layout(height=max(500, len(df_sub) * 35), title="", xaxis_title="Değişim Oranı (%)", margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else: st.warning("Bu kategoride veri bulunamadı.")

def sayfa_trend_analizi(ctx):
    st.markdown("### 📈 Zaman Serisi ve Enflasyon Trendleri")
    df = ctx["df_analiz"]; gunler = ctx["gunler"]; agirlik_col = ctx["agirlik_col"]
    endeks_verisi = []
    for gun in gunler:
        temp_df = df.dropna(subset=[gun, agirlik_col])
        if not temp_df.empty and temp_df[agirlik_col].sum() > 0:
            index_val = (temp_df[gun] * temp_df[agirlik_col]).sum() / temp_df[agirlik_col].sum()
            endeks_verisi.append({"Tarih": gun, "Deger": index_val})
    df_endeks = pd.DataFrame(endeks_verisi)
    if not df_endeks.empty:
        df_endeks['Kümülatif_Degisim'] = ((df_endeks['Deger'] / df_endeks.iloc[0]['Deger']) - 1) * 100
        fig_genel = make_neon_chart(px.line(df_endeks, x='Tarih', y='Kümülatif_Degisim', title="GENEL ENFLASYON TRENDİ", markers=True))
        st.plotly_chart(style_chart(fig_genel), use_container_width=True)
        st.info(f"ℹ️ Grafik, {gunler[0]} tarihini baz alarak hesaplanan kümülatif sepet değişimini gösterir.")
    
    st.markdown("---")
    st.subheader("Ürün Kıyaslama")
    seçilen_urunler = st.multiselect("Grafiğe eklenecek ürünler:", options=df[ctx['ad_col']].unique(), default=df.sort_values('Fark_Yuzde', ascending=False).head(3)[ctx['ad_col']].tolist())
    if seçilen_urunler:
        df_melted = df[df[ctx['ad_col']].isin(seçilen_urunler)][[ctx['ad_col']] + gunler].melt(id_vars=[ctx['ad_col']], var_name='Tarih', value_name='Fiyat')
        base_prices = df_melted[df_melted['Tarih'] == gunler[0]].set_index(ctx['ad_col'])['Fiyat'].to_dict()
        df_melted['Yuzde_Degisim'] = df_melted.apply(lambda row: ((row['Fiyat']/base_prices.get(row[ctx['ad_col']], 1)) - 1)*100 if base_prices.get(row[ctx['ad_col']], 0) > 0 else 0, axis=1)
        st.plotly_chart(style_chart(px.line(df_melted, x='Tarih', y='Yuzde_Degisim', color=ctx['ad_col'], title="", markers=True)), use_container_width=True)

def sayfa_metodoloji(ctx=None):
    html_content = """
    <style>.method-card { background: #18181b; border: 1px solid #27272a; border-radius: 16px; padding: 25px; margin-bottom: 20px; }</style>
    <h3 style="margin-bottom:30px;">Metodoloji ve Akademik Çerçeve</h3>
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
        <div class="method-card">
            <h4 style="color:#3b82f6; margin-top:0;">1. Veri Toplama (Web Scraping)</h4>
            <p style="color:#a1a1aa; font-size:14px; line-height:1.6;">User-Agent rotasyonu ve Rate Limiting ile güvenli veri çekimi. IP bazlı anomali tespiti ve veri boşluklarının yönetimi.</p>
        </div>
        <div class="method-card">
            <h4 style="color:#10b981; margin-top:0;">2. Endeks Hesaplama</h4>
            <p style="color:#a1a1aa; font-size:14px; line-height:1.6;">Fiyat endeksi hesaplamasında zincirleme Laspeyres yaklaşımı benimsenmiştir.</p>
            <code style="background:#000; padding:5px; border-radius:4px; color:#fff;">I(t) = Σ ( P(i,t) / P(i,0) ) × W(i)</code>
        </div>
        <div class="method-card" style="grid-column: span 2;">
            <h4 style="color:#f59e0b; margin-top:0;">3. Ağırlıklandırma</h4>
            <p style="color:#a1a1aa; font-size:14px;">Ürün ağırlıkları, TÜİK Hanehalkı Bütçe Anketi (HBA) harcama payları temel alınarak 2024 yılı bazlı simüle edilmiştir.</p>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

# --- ANA MAIN ---
def main():
    # --- 1. MODERN HEADER ---
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"""
        <div style="padding:10px 0;">
            <div style="font-weight:900; font-size:28px; color:#fff; letter-spacing:-1px;">
                Piyasa Monitörü <span style="color:#3b82f6;">PRO</span>
            </div>
            <div style="font-size:14px; color:#71717a; display:flex; gap:10px; align-items:center;">
                <span>Yapay Zeka Destekli Enflasyon Analiz Platformu</span>
                <span style="background:rgba(16,185,129,0.1); color:#10b981; font-size:10px; padding:2px 8px; border-radius:4px;">CANLI</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_h2:
        st.markdown(f"""
        <div style="text-align:right; padding:10px 0;">
            <div style="font-size:11px; color:#52525b; font-weight:700; letter-spacing:1px;">İSTANBUL</div>
            <div style="font-size:24px; font-weight:700; color:#e4e4e7; font-family:'JetBrains Mono';">{datetime.now().strftime("%d.%m.%Y")}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1px; background:linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent); margin-bottom:20px;'></div>", unsafe_allow_html=True)

    # --- 2. ÜST MENÜ VE AKSİYON ---
    c_nav, c_act = st.columns([5, 1])
    
    with c_nav:
        menu_items = {
            "🏠 Ana Sayfa": "Ana Sayfa",
            "⚡ Özet": "Piyasa Özeti",
            "📈 Trend": "Trendler",
            "📦 Ürünler": "Maddeler",
            "🔍 Detay": "Kategori Detay",
            "💾 Veri": "Tam Liste",
            "📝 Rapor": "Raporlama",
            "ℹ️ Bilgi": "Metodoloji"
        }
        secilen_etiket = st.radio("Navigasyon", options=list(menu_items.keys()), label_visibility="collapsed", key="nav_radio", horizontal=True)
        secim = menu_items[secilen_etiket]

    with c_act:
        if st.button("🔄 Senkronize Et", use_container_width=True):
            progress_bar = st.progress(0, text="Veri akışı sağlanıyor...")
            res = html_isleyici(lambda p: progress_bar.progress(min(1.0, max(0.0, p)), text="Senkronizasyon sürüyor..."))
            progress_bar.progress(1.0, text="Tamamlandı!"); time.sleep(0.5); progress_bar.empty()
            if "OK" in res:
                st.cache_data.clear(); st.toast('Sistem Senkronize Edildi!', icon='🚀'); time.sleep(1); st.rerun()
            elif "Veri bulunamadı" in res: st.warning("⚠️ Yeni veri akışı yok.")
            else: st.error(res)

    # --- 3. VERİ YÜKLEME ---
    with st.spinner("Veri tabanına bağlanılıyor..."):
        df_base, r_dates, col_name = verileri_getir_cache()
    
    if df_base is not None:
        ctx = ui_sidebar_ve_veri_hazirlama(df_base, r_dates, col_name)
    else:
        ctx = None

    # --- 4. İÇERİK YÖNETİMİ ---
    if ctx:
        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        if secim == "Ana Sayfa": sayfa_ana_sayfa(ctx)
        elif secim == "Piyasa Özeti": sayfa_piyasa_ozeti(ctx)
        elif secim == "Trendler": sayfa_trend_analizi(ctx)
        elif secim == "Maddeler": sayfa_maddeler(ctx)
        elif secim == "Kategori Detay": sayfa_kategori_detay(ctx)
        elif secim == "Tam Liste": sayfa_tam_liste(ctx)
        elif secim == "Raporlama": sayfa_raporlama(ctx)
        elif secim == "Metodoloji": sayfa_metodoloji(ctx)
    else:
        if secim == "Metodoloji": sayfa_metodoloji()
        else:
            st.error("Veri seti yüklenemedi. Lütfen internet bağlantınızı kontrol edin veya GitHub yapılandırmasını doğrulayın.")

    # --- FOOTER ---
    st.markdown('<div style="text-align:center; color:#52525b; font-size:11px; margin-top:60px; padding-top:20px; border-top:1px solid rgba(255,255,255,0.05);">VALIDASYON MUDURLUGU © 2026 - CONFIDENTIAL ANALYTICS SUITE</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
