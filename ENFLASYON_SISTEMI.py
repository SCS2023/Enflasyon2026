# GEREKLİ KÜTÜPHANELER:
# pip install streamlit-lottie python-docx plotly pandas xlsxwriter matplotlib github beautifulsoup4

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from bs4 import BeautifulSoup
import re
import calendar
from datetime import datetime, timedelta
import time
import json
from github import Github
from io import BytesIO
import zipfile
import base64
import requests
import streamlit.components.v1 as components
import tempfile
import os
import math
import random
import html
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import unicodedata

# --- İMPORT KONTROLLERİ ---
try:
    import xlsxwriter
except ImportError:
    st.error("Lütfen 'pip install xlsxwriter' komutunu çalıştırın.")

try:
    from streamlit_lottie import st_lottie
except ImportError:
    pass

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    st.error("Lütfen 'pip install python-docx' komutunu çalıştırın.")

# --- 1. AYARLAR VE TEMA YÖNETİMİ (PREMIUM UI) ---
st.set_page_config(
    page_title="PRO ANALYTICS | Piyasa Monitörü",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="expanded"
)

def apply_theme():
    st.session_state.plotly_template = "plotly_dark"

    final_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;700&display=swap');

        :root {
            --bg-deep: #050505;
            --bg-card: rgba(20, 20, 25, 0.7);
            --neon-blue: #00f2ff;
            --neon-purple: #bd00ff;
            --neon-green: #0aff68;
            --text-main: #e0e0e0;
            --text-dim: #858585;
            --glass-border: 1px solid rgba(255, 255, 255, 0.08);
        }

        /* Ana Yapı */
        [data-testid="stAppViewContainer"] {
            background-color: var(--bg-deep);
            background-image: 
                radial-gradient(circle at 0% 0%, rgba(0, 242, 255, 0.05) 0%, transparent 40%), 
                radial-gradient(circle at 100% 100%, rgba(189, 0, 255, 0.05) 0%, transparent 40%),
                linear-gradient(180deg, rgba(5,5,5,0) 0%, rgba(5,5,5,1) 100%);
            font-family: 'Outfit', sans-serif !important;
            color: var(--text-main);
        }

        /* Sidebar Özelleştirme */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(10,10,15,0.95) 0%, rgba(5,5,5,1) 100%);
            border-right: var(--glass-border);
            backdrop-filter: blur(20px);
        }
        
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: 1px;
        }

        /* Header Gizleme */
        [data-testid="stHeader"] { visibility: hidden; height: 0px; }
        
        /* Premium Kartlar (Glassmorphism) */
        .glass-card {
            background: var(--bg-card);
            border: var(--glass-border);
            border-radius: 24px;
            padding: 25px;
            backdrop-filter: blur(16px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            margin-bottom: 20px;
        }
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 rgba(0, 242, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
        }

        /* KPI Stilleri */
        .kpi-title {
            font-size: 12px; text-transform: uppercase; color: var(--text-dim); letter-spacing: 2px; font-weight: 700;
        }
        .kpi-value {
            font-size: 42px; font-weight: 800; background: -webkit-linear-gradient(0deg, #fff, #a5a5a5); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin: 5px 0; font-family: 'JetBrains Mono', monospace;
        }
        .kpi-badge {
            display: inline-block; padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: 600;
        }
        
        /* Ticker Animation */
        .ticker-container {
            width: 100%; overflow: hidden; white-space: nowrap;
            background: rgba(255,255,255,0.02); border-y: var(--glass-border);
            padding: 10px 0; margin: 20px 0;
        }
        .ticker-content {
            display: inline-block; padding-left: 100%; animation: scroll 60s linear infinite;
            font-family: 'JetBrains Mono', monospace; font-size: 13px;
        }
        @keyframes scroll { 0% { transform: translateX(0); } 100% { transform: translateX(-100%); } }

        /* Custom Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px; border-bottom: none;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255,255,255,0.03); border-radius: 12px; border: none; color: #888; padding: 10px 20px;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(255,255,255,0.08); color: #fff;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(0, 242, 255, 0.2), rgba(189, 0, 255, 0.2)) !important;
            color: #fff !important; border: 1px solid rgba(255,255,255,0.2) !important;
        }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #050505; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--neon-blue); }
    </style>
    """
    st.markdown(final_css, unsafe_allow_html=True)

apply_theme()

# --- 2. GITHUB & VERİ MOTORU (DEĞİŞTİRİLMEDİ) ---
EXCEL_DOSYASI = "TUFE_Konfigurasyon.xlsx"
FIYAT_DOSYASI = "Fiyat_Veritabani.xlsx"
SAYFA_ADI = "Madde_Sepeti"

def get_github_repo():
    try:
        if "github" not in st.secrets: return None
        return Github(st.secrets["github"]["token"]).get_repo(st.secrets["github"]["repo_name"])
    except: return None

@st.cache_data(ttl=300, show_spinner=False)
def github_excel_oku(dosya_adi, sayfa_adi=None):
    repo = get_github_repo()
    if not repo: return pd.DataFrame()
    try:
        c = repo.get_contents(dosya_adi, ref=st.secrets["github"]["branch"])
        if sayfa_adi: df = pd.read_excel(BytesIO(c.decoded_content), sheet_name=sayfa_adi, dtype=str)
        else: df = pd.read_excel(BytesIO(c.decoded_content), dtype=str)
        return df
    except: return pd.DataFrame()

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
        except: c = None; final = df_yeni
        
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as w: final.to_excel(w, index=False, sheet_name='Fiyat_Log')
        msg = f"Data Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        if c: repo.update_file(c.path, msg, out.getvalue(), c.sha, branch=st.secrets["github"]["branch"])
        else: repo.create_file(dosya_adi, msg, out.getvalue(), branch=st.secrets["github"]["branch"])
        return "OK"
    except Exception as e: return str(e)

# --- 3. RAPORLAMA MOTORU (WORD - DEĞİŞTİRİLMEDİ) ---
def create_word_report(text_content, tarih, df_analiz=None):
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
            fig, ax = plt.subplots(figsize=(6, 4))
            data = df_analiz['Fark'].dropna() * 100
            ax.hist(data, bins=20, color='#3b82f6', edgecolor='white', alpha=0.7)
            ax.set_title(f"Fiyat Değişim Dağılımı (%) - {tarih}", fontsize=12, fontweight='bold')
            ax.set_xlabel("Değişim Oranı (%)")
            ax.set_ylabel("Ürün Sayısı")
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            memfile = BytesIO()
            plt.savefig(memfile, format='png', dpi=100)
            doc.add_picture(memfile, width=Inches(5.5))
            memfile.close()
            plt.close()
            doc.add_paragraph("Grafik 1: Ürünlerin fiyat değişim oranlarına göre dağılımı.")
        except: pass
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def generate_detailed_static_report(df_analiz, tarih, enf_genel, enf_gida, gun_farki, tahmin, ad_col, agirlik_col):
    df_clean = df_analiz.dropna(subset=['Fark'])
    ortalama_fark = df_clean['Fark'].mean()
    medyan_fark = df_clean['Fark'].median()
    piyasa_yorumu = "Genele Yayılım (Fiyat Artışı Homojen)"
    if ortalama_fark > (medyan_fark * 1.2): piyasa_yorumu = "Lokal Şoklar (Belirli Ürünler Endeksi Yükseltiyor)"
    elif ortalama_fark < (medyan_fark * 0.8): piyasa_yorumu = "İndirim Ağırlıklı (Kampanyalar Etkili)"
    artanlar = df_clean[df_clean['Fark'] > 0]
    inc_str = "\n".join([f"   🔴 %{row['Fark']*100:5.2f} | {row[ad_col]}" for _, row in df_clean.sort_values('Fark', ascending=False).head(5).iterrows()])
    dec_str = "\n".join([f"   🟢 %{abs(row['Fark']*100):5.2f} | {row[ad_col]}" for _, row in df_clean.sort_values('Fark', ascending=True).head(5).iterrows()])
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
**Durum:** {piyasa_yorumu}
**Yükselen Ürün Sayısı:** {len(artanlar)}

**3. ⚡ DİKKAT ÇEKENLER**
**▲ Yüksek Artışlar**
{inc_str}

**▼ Fiyat Düşüşleri**
{dec_str}

**4. 💡 SONUÇ**
Piyasa verileri, fiyat istikrarının henüz tam sağlanamadığını göstermektedir. Tahmin modelimiz, ay sonu kapanışının **%{tahmin:.2f}** bandında olacağını öngörmektedir.
"""
    return text.strip()

# --- 4. SCRAPER & UPDATE (DEĞİŞTİRİLMEDİ) ---
def temizle_fiyat(t):
    if not t: return None
    t = str(t).replace('TL', '').replace('₺', '').strip()
    t = t.replace('.', '').replace(',', '.') if ',' in t and '.' in t else t.replace(',', '.')
    try: return float(re.sub(r'[^\d.]', '', t))
    except: return None

def kod_standartlastir(k): return str(k).replace('.0', '').strip().zfill(7)

def fiyat_bul_siteye_gore(soup, url):
    fiyat = 0; kaynak = "Regex"
    if m := re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺)', soup.get_text()[:5000]):
        if v := temizle_fiyat(m.group(1)): fiyat = v
    return fiyat, kaynak

def html_isleyici(progress_callback):
    repo = get_github_repo()
    if not repo: return "GitHub Bağlantı Hatası"
    progress_callback(0.1)
    try:
        df_conf = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
        if df_conf.empty: return "Konfigürasyon Hatası"
        df_conf.columns = df_conf.columns.str.strip()
        kod_col = next((c for c in df_conf.columns if c.lower() == 'kod'), None)
        url_col = next((c for c in df_conf.columns if c.lower() == 'url'), None)
        ad_col = next((c for c in df_conf.columns if 'ad' in c.lower()), 'Madde adı')
        df_conf['Kod'] = df_conf[kod_col].astype(str).apply(kod_standartlastir)
        url_map = {str(row[url_col]).strip(): row for _, row in df_conf.iterrows() if pd.notna(row[url_col])}
        veriler = []
        islenen = set()
        contents = repo.get_contents("", ref=st.secrets["github"]["branch"])
        zip_files = [c for c in contents if c.name.endswith(".zip") and c.name.startswith("Bolum")]
        for i, zip_file in enumerate(zip_files):
            progress_callback(0.1 + (0.8 * ((i + 1) / len(zip_files))))
            try:
                blob = repo.get_git_blob(zip_file.sha)
                with zipfile.ZipFile(BytesIO(base64.b64decode(blob.content))) as z:
                    for fn in z.namelist():
                        if not fn.endswith(('.html', '.htm')): continue
                        with z.open(fn) as f:
                            soup = BeautifulSoup(f.read().decode("utf-8", errors="ignore"), 'html.parser')
                            found = None
                            if c := soup.find("link", rel="canonical"): found = c.get("href")
                            if found and str(found).strip() in url_map:
                                t = url_map[str(found).strip()]
                                if t['Kod'] in islenen: continue
                                f_val, src = fiyat_bul_siteye_gore(soup, t[url_col])
                                if f_val > 0:
                                    veriler.append({
                                        "Tarih": datetime.now().strftime("%Y-%m-%d"),
                                        "Zaman": datetime.now().strftime("%H:%M"),
                                        "Kod": t['Kod'], "Madde_Adi": t[ad_col],
                                        "Fiyat": float(f_val), "Kaynak": src, "URL": t[url_col]
                                    })
                                    islenen.add(t['Kod'])
            except: pass
        progress_callback(0.95)
        if veriler: return github_excel_guncelle(pd.DataFrame(veriler), FIYAT_DOSYASI)
        else: return "Yeni veri bulunamadı."
    except Exception as e: return f"Hata: {str(e)}"

# --- 5. YARDIMCI GÖRSELLEŞTİRME ---
def make_neon_chart(fig):
    new_traces = []
    for trace in fig.data:
        if trace.type in ['scatter', 'line']:
            # Neon Glow Efekti
            glow = go.Scatter(x=trace.x, y=trace.y, mode='lines',
                              line=dict(width=12, color=trace.line.color),
                              opacity=0.15, hoverinfo='skip', showlegend=False)
            new_traces.append(glow)
            glow2 = go.Scatter(x=trace.x, y=trace.y, mode='lines',
                              line=dict(width=6, color=trace.line.color),
                              opacity=0.3, hoverinfo='skip', showlegend=False)
            new_traces.append(glow2)
    fig.add_traces(new_traces)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                      xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'))
    return fig

def render_skeleton():
    st.markdown("""
    <div style="display: flex; gap: 20px;">
        <div class="glass-card" style="width: 25%; height: 120px; animation: pulse 1.5s infinite;"></div>
        <div class="glass-card" style="width: 25%; height: 120px; animation: pulse 1.5s infinite; animation-delay: 0.1s;"></div>
        <div class="glass-card" style="width: 25%; height: 120px; animation: pulse 1.5s infinite; animation-delay: 0.2s;"></div>
        <div class="glass-card" style="width: 25%; height: 120px; animation: pulse 1.5s infinite; animation-delay: 0.3s;"></div>
    </div>
    <div class="glass-card" style="height: 400px; width: 100%; margin-top: 20px; animation: pulse 1.5s infinite;"></div>
    <style>@keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }</style>
    """, unsafe_allow_html=True)

def style_chart(fig, is_sunburst=False):
    layout_args = dict(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Outfit, sans-serif", color="#e0e0e0", size=12), margin=dict(l=0, r=0, t=40, b=0))
    if not is_sunburst:
        layout_args.update(dict(xaxis=dict(showgrid=False, linecolor="rgba(255,255,255,0.1)"),
                                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)")))
    fig.update_layout(**layout_args)
    return fig

# --- 6. MAIN APPLICATION (REVISED UI) ---
def main():
    # --- YÜKLEME EKRANI ---
    loader_placeholder = st.empty()
    
    # --- VERİ ÇEKME ---
    df_f = github_excel_oku(FIYAT_DOSYASI)
    df_s = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
    
    if df_f.empty or df_s.empty:
        loader_placeholder.empty()
        st.warning("⚠️ Veri tabanına erişilemedi. Lütfen GitHub bağlantısını kontrol edin.")
        return
    
    with loader_placeholder.container():
        render_skeleton()

    # --- VERİ İŞLEME VE TARİH FİLTRESİ ---
    df_f['Tarih_DT'] = pd.to_datetime(df_f['Tarih'], errors='coerce')
    df_f = df_f.dropna(subset=['Tarih_DT']).sort_values('Tarih_DT')
    df_f['Tarih_Str'] = df_f['Tarih_DT'].dt.strftime('%Y-%m-%d')
    
    BASLANGIC_LIMITI = "2026-02-04"
    raw_dates = df_f['Tarih_Str'].unique().tolist()
    tum_tarihler = sorted([d for d in raw_dates if d >= BASLANGIC_LIMITI], reverse=True)
    
    # --- SIDEBAR (YENİLENMİŞ) ---
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; margin-bottom: 20px;">
            <div style="font-size: 50px;">💎</div>
            <h2 style="color:#fff; margin:0;">PRO ANALYTICS</h2>
            <p style="color:#666; font-size:12px;">Piyasa İzleme Sistemi v3.0</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ⚙️ KONTROL PANELİ")
        
        if tum_tarihler:
            secilen_tarih = st.selectbox("Geçmiş Veri Görüntüle", tum_tarihler, index=0)
        else:
            secilen_tarih = None
            st.warning("2026-02-04 sonrası veri yok.")

        st.markdown("---")
        st.info("Veriler GitHub üzerinden günlük olarak senkronize edilmektedir.")
        
        if st.button("🔄 SİSTEMİ GÜNCELLE", type="primary", use_container_width=True):
            pbar = st.progress(0, text="GitHub Bağlantısı Kuruluyor...")
            res = html_isleyici(lambda x: pbar.progress(min(1.0, max(0.0, x))))
            pbar.empty()
            if "OK" in res:
                st.success("Veritabanı Güncellendi!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(res)

    # --- HESAPLAMA MOTORU (DOKUNULMADI) ---
    df_s.columns = df_s.columns.str.strip()
    kod_col = next((c for c in df_s.columns if c.lower() == 'kod'), 'Kod')
    ad_col = next((c for c in df_s.columns if 'ad' in c.lower()), 'Madde_Adi')
    col_w26 = 'Agirlik_2026'
    
    df_f['Kod'] = df_f['Kod'].astype(str).apply(kod_standartlastir)
    df_s['Kod'] = df_s[kod_col].astype(str).apply(kod_standartlastir)
    df_s = df_s.drop_duplicates(subset=['Kod'])
    
    df_f['Fiyat'] = pd.to_numeric(df_f['Fiyat'], errors='coerce')
    df_f = df_f.dropna(subset=['Fiyat'])
    df_f = df_f[df_f['Fiyat'] > 0]
    
    df_f_grp = df_f.groupby(['Kod', 'Tarih_Str'])['Fiyat'].mean().reset_index()
    pivot = df_f_grp.pivot_table(index='Kod', columns='Tarih_Str', values='Fiyat').ffill(axis=1).bfill(axis=1).reset_index()
    
    if 'Grup' not in df_s.columns:
        grup_map = {"01": "Gıda", "02": "Alkol-Tütün", "03": "Giyim", "04": "Konut", "05": "Ev Eşyası", "06": "Sağlık", "07": "Ulaşım", "08": "Haberleşme", "09": "Eğlence", "10": "Eğitim", "11": "Lokanta", "12": "Çeşitli"}
        df_s['Grup'] = df_s['Kod'].str[:2].map(grup_map).fillna("Diğer")
        
    df_analiz = pd.merge(df_s, pivot, on='Kod', how='left')
    
    tum_gunler = sorted([c for c in pivot.columns if c != 'Kod' and c >= BASLANGIC_LIMITI])
    if secilen_tarih and secilen_tarih in tum_gunler:
        gunler = tum_gunler[:tum_gunler.index(secilen_tarih)+1]
    else:
        gunler = tum_gunler
        
    if not gunler:
        loader_placeholder.empty(); st.error("Veri seti oluşturulamadı."); return

    son = gunler[-1]
    dt_son = datetime.strptime(son, '%Y-%m-%d')
    ZINCIR_TARIHI = datetime(2026, 2, 4)
    aktif_agirlik_col = col_w26
    
    gunler_2026 = [c for c in tum_gunler if c >= "2026-01-01"]
    baz_col = gunler_2026[0] if gunler_2026 else gunler[0]
    
    if aktif_agirlik_col in df_analiz.columns:
        df_analiz[aktif_agirlik_col] = pd.to_numeric(df_analiz[aktif_agirlik_col], errors='coerce').fillna(0)
    else:
        df_analiz[aktif_agirlik_col] = 0
        
    def geo_mean(row):
        vals = [x for x in row if isinstance(x, (int, float)) and x > 0]
        return np.exp(np.mean(np.log(vals))) if vals else np.nan

    bu_ay_str = f"{dt_son.year}-{dt_son.month:02d}"
    bu_ay_cols = [c for c in gunler if c.startswith(bu_ay_str)]
    if not bu_ay_cols: bu_ay_cols = [son]
    
    gecerli_veri = df_analiz[df_analiz[aktif_agirlik_col] > 0].copy()
    gecerli_veri['Aylik_Ortalama'] = gecerli_veri[bu_ay_cols].apply(geo_mean, axis=1)
    gecerli_veri = gecerli_veri.dropna(subset=['Aylik_Ortalama', baz_col])
    
    enf_genel = 0.0
    if not gecerli_veri.empty:
        w = gecerli_veri[aktif_agirlik_col]
        p_rel = gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]
        if w.sum() > 0: enf_genel = (w * p_rel).sum() / w.sum() * 100 - 100
        
    df_analiz['Fark'] = 0.0
    if not gecerli_veri.empty:
        df_analiz.loc[gecerli_veri.index, 'Fark'] = (gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]) - 1

    if len(gunler) >= 2:
        prev = gunler[-2]
        df_analiz['Gunluk_Degisim'] = (df_analiz[son] / df_analiz[prev]) - 1
    else:
        df_analiz['Gunluk_Degisim'] = 0
        
    gida_enf = 0
    gida_df = gecerli_veri[gecerli_veri['Kod'].astype(str).str.startswith("01")]
    if not gida_df.empty:
        wg = gida_df[aktif_agirlik_col]
        if wg.sum() > 0: gida_enf = ((wg * (gida_df['Aylik_Ortalama']/gida_df[baz_col])).sum()/wg.sum()*100)-100

    # --- UI RENDERING (PREMIUM ASYMMETRICAL LAYOUT) ---
    loader_placeholder.empty()

    # 1. HERO SECTION & TICKER
    c_hero_L, c_hero_R = st.columns([3, 1])
    with c_hero_L:
        st.markdown(f"""
        <div style="padding-top:10px;">
            <h1 style="font-size: 56px; font-weight: 900; background: -webkit-linear-gradient(0deg, #fff, #888); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin:0;">PİYASA MONİTÖRÜ</h1>
            <p style="font-size: 16px; color: #888; letter-spacing: 1px;">YAPAY ZEKA DESTEKLİ ENFLASYON ANALİZ MODÜLÜ</p>
        </div>
        """, unsafe_allow_html=True)
    with c_hero_R:
        st.markdown(f"""
        <div style="text-align: right; background: rgba(0,242,255,0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(0,242,255,0.2);">
            <div style="font-size: 12px; color: #00f2ff; font-weight: 700;">SON GÜNCELLEME</div>
            <div style="font-size: 24px; font-weight: 800; color: #fff;">{dt_son.strftime('%d.%m.%Y')}</div>
        </div>
        """, unsafe_allow_html=True)

    # Ticker HTML Generator
    inc = df_analiz.sort_values('Gunluk_Degisim', ascending=False).head(8)
    dec = df_analiz.sort_values('Gunluk_Degisim', ascending=True).head(8)
    items = []
    for _, r in inc.iterrows(): 
        if r['Gunluk_Degisim'] > 0: items.append(f"<span style='color:#ff4b4b;'>▲ {r[ad_col]} %{r['Gunluk_Degisim']*100:.1f}</span>")
    for _, r in dec.iterrows():
        if r['Gunluk_Degisim'] < 0: items.append(f"<span style='color:#0aff68;'>▼ {r[ad_col]} %{r['Gunluk_Degisim']*100:.1f}</span>")
    
    ticker_html = " &nbsp;&nbsp;&nbsp;&nbsp; ".join(items) if items else "Piyasada yatay seyir."
    st.markdown(f'<div class="ticker-container"><div class="ticker-content">{ticker_html}</div></div>', unsafe_allow_html=True)

    # 2. ANA TABS
    tab_dash, tab_detay, tab_data, tab_rapor = st.tabs(["🚀 PANORAMA", "📈 DETAY ANALİZ", "🗂 VERİ SETİ", "📑 RAPORLAMA"])

    with tab_dash:
        # A. KPI ALANI (4'lü Grid)
        col1, col2, col3, col4 = st.columns(4)
        def kpi_card(col, title, val, badge_txt, badge_color):
            with col:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title">{title}</div>
                    <div class="kpi-value">{val}</div>
                    <div class="kpi-badge" style="color:{badge_color}; background:{badge_color}22; border:1px solid {badge_color}44;">{badge_txt}</div>
                </div>
                """, unsafe_allow_html=True)

        kpi_card(col1, "GENEL TÜFE", f"%{enf_genel:.2f}", "Baz: Şubat", "#ff4b4b")
        kpi_card(col2, "GIDA ENFLASYONU", f"%{gida_enf:.2f}", "Mutfak", "#ffa500")
        kpi_card(col3, "GÜNLÜK VOLATİLİTE", f"%{df_analiz['Gunluk_Degisim'].mean()*100:.2f}", "Ortalama", "#00f2ff")
        kpi_card(col4, "TAKİP EDİLEN", f"{len(gecerli_veri)}", "Ürün Adedi", "#0aff68")

        # B. ASİMETRİK GRAFİK ALANI
        st.markdown("<br>", unsafe_allow_html=True)
        col_main, col_side = st.columns([2, 1]) # 2:1 Oranı
        
        with col_main:
            st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
            st.markdown('<h3 style="margin-top:0;">Sektörel Isı Haritası</h3>', unsafe_allow_html=True)
            df_analiz['Grup_Fark'] = df_analiz['Fark'] * df_analiz[aktif_agirlik_col]
            grp = df_analiz.groupby('Grup').agg({'Grup_Fark':'sum', aktif_agirlik_col:'sum'}).reset_index()
            grp['Etki'] = (grp['Grup_Fark'] / grp[aktif_agirlik_col]) * 100
            
            fig = px.treemap(grp, path=[px.Constant("Piyasa"), 'Grup'], values=aktif_agirlik_col, color='Etki',
                             color_continuous_scale='RdYlGn_r')
            st.plotly_chart(style_chart(fig, True), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_side:
            st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
            st.markdown('<h3 style="margin-top:0;">Günün Hareketlileri</h3>', unsafe_allow_html=True)
            
            # Custom HTML Table for elegance
            top_risers = df_analiz.sort_values('Gunluk_Degisim', ascending=False).head(6)
            table_html = "<table style='width:100%; border-collapse: collapse;'>"
            for _, r in top_risers.iterrows():
                val = r['Gunluk_Degisim']*100
                color = "#ff4b4b" if val > 0 else "#0aff68"
                table_html += f"""
                <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                    <td style="padding:12px 0; color:#ccc;">{r[ad_col]}</td>
                    <td style="text-align:right; color:{color}; font-weight:bold;">%{val:.2f}</td>
                </tr>
                """
            table_html += "</table>"
            st.markdown(table_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_detay:
        # Asimetrik: Sol (Kontrol) Dar - Sağ (Grafik) Geniş
        c_sel, c_chart = st.columns([1, 3])
        
        with c_sel:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            opt = ["GENEL TÜFE"] + sorted(df_analiz[ad_col].unique().tolist())
            sel = st.selectbox("Analiz Edilecek Varlık:", opt)
            st.caption("Seçilen varlığın zaman serisi analizi sağ tarafta görüntülenecektir.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Sunburst Grafiğini buraya küçük olarak alalım
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            fig_sun = px.sunburst(df_analiz, path=['Grup', ad_col], values=aktif_agirlik_col, color='Grup', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_sun.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(style_chart(fig_sun, True), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c_chart:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            if sel == "GENEL TÜFE":
                ts_data = [df_analiz[d].mean() for d in gunler]
                plot_df = pd.DataFrame({'Tarih': gunler, 'Deger': [x/ts_data[0]*100 for x in ts_data]})
                fig = px.line(plot_df, x='Tarih', y='Deger', title="Genel Endeks Seyri (Baz=100)")
                line_col = "#00f2ff"
            else:
                row = df_analiz[df_analiz[ad_col] == sel].iloc[0]
                plot_df = pd.DataFrame({'Tarih': gunler, 'Fiyat': row[gunler].values})
                fig = px.line(plot_df, x='Tarih', y='Fiyat', title=f"{sel} Fiyat Analizi")
                line_col = "#bd00ff"
            
            fig.update_traces(line_color=line_col, line_width=4)
            st.plotly_chart(make_neon_chart(style_chart(fig)), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_data:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col_cfg = {
            ad_col: "Ürün", "Grup": "Kategori",
            "Gunluk_Degisim": st.column_config.ProgressColumn("Günlük Trend", format="%.2f%%", min_value=-0.5, max_value=0.5),
            son: st.column_config.NumberColumn("Son Fiyat", format="%.2f ₺")
        }
        st.data_editor(
            df_analiz[['Grup', ad_col, son, 'Gunluk_Degisim']].sort_values('Gunluk_Degisim', ascending=False),
            column_config=col_cfg, use_container_width=True, height=600
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_rapor:
        c_rap1, c_rap2 = st.columns([2, 1])
        with c_rap1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            tahmin = enf_genel * 1.05
            rap_text = generate_detailed_static_report(df_analiz, son, enf_genel, gida_enf, 0, tahmin, ad_col, aktif_agirlik_col)
            st.markdown(f'<div style="font-family:monospace; white-space: pre-line; line-height: 1.6;">{rap_text}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with c_rap2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 📥 Dışa Aktar")
            st.markdown("Raporları indirerek çevrimdışı inceleyebilirsiniz.")
            
            out = BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as w: df_analiz.to_excel(w, index=False)
            st.download_button("📊 Excel Verisi", out.getvalue(), f"Data_{son}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            w_out = create_word_report(rap_text, son, df_analiz)
            st.download_button("📄 Word Raporu", w_out, f"Rapor_{son}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
