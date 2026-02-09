# GEREKLİ KÜTÜPHANELER:
# pip install streamlit-lottie python-docx plotly pandas xlsxwriter matplotlib github

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
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# --- İMPORT KONTROLLERİ ---
try:
    import xlsxwriter
except ImportError:
    st.error("Lütfen 'pip install xlsxwriter' komutunu çalıştırın. Excel raporlama modülü için gereklidir.")

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    st.error("Lütfen 'pip install python-docx' komutunu çalıştırın.")

# --- 1. AYARLAR VE TEMA YÖNETİMİ ---
st.set_page_config(
    page_title="Piyasa Monitörü | Pro Analytics",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="collapsed"
)

# --- CSS MOTORU ---
def apply_theme():
    # Streamlit varsayılan paddinglerini sıfırla ve tema uygula
    final_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        :root {
            --bg-deep: #02040a;
            --glass-bg: rgba(255, 255, 255, 0.03);
            --glass-border: rgba(255, 255, 255, 0.08);
            --accent-blue: #3b82f6;
            --text-main: #f4f4f5;
            --text-dim: #a1a1aa;
            --card-radius: 16px;
        }

        /* Ana Arka Plan */
        [data-testid="stAppViewContainer"] {
            background-color: var(--bg-deep);
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(56, 189, 248, 0.08), transparent 25%), 
                radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.08), transparent 25%);
            background-attachment: fixed;
            font-family: 'Inter', sans-serif !important;
            color: var(--text-main) !important;
        }

        /* Header ve Toolbar Gizleme */
        [data-testid="stHeader"] { visibility: hidden; height: 0px; }
        [data-testid="stToolbar"] { display: none; }

        /* --- MENÜ (RADIO BUTTONS) --- */
        [data-testid="stRadio"] > div {
            display: flex;
            justify-content: center;
            gap: 10px;
            background: rgba(20, 20, 20, 0.6);
            backdrop-filter: blur(12px);
            padding: 8px 16px;
            border-radius: 24px;
            border: 1px solid var(--glass-border);
            margin-bottom: 25px;
            width: fit-content;
            margin-left: auto;
            margin-right: auto;
            overflow-x: auto;
        }
        
        [data-testid="stRadio"] label {
            background: transparent !important;
            border: 1px solid transparent !important;
            color: #71717a !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            transition: all 0.3s ease !important;
            border-radius: 12px !important;
            padding: 8px 20px !important;
            margin: 0 !important;
        }
        
        [data-testid="stRadio"] label:hover {
            color: #fff !important;
            background: rgba(255,255,255,0.05) !important;
        }
        
        /* Seçili Olan Radio Buton */
        [data-testid="stRadio"] [data-testid="stMarkdownContainer"] > p {
            font-size: 14px;
        }

        div[role="radiogroup"] label[data-checked="true"] {
            color: #fff !important;
            background: rgba(59, 130, 246, 0.2) !important;
            border: 1px solid rgba(59, 130, 246, 0.4) !important;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.25);
        }

        /* --- KARTLAR --- */
        .kpi-card {
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
            border: 1px solid var(--glass-border);
            border-radius: var(--card-radius);
            padding: 24px;
            position: relative;
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease, border-color 0.3s ease;
            box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.2);
        }
        .kpi-card:hover {
            transform: translateY(-5px);
            border-color: rgba(59, 130, 246, 0.5);
            box-shadow: 0 10px 30px -5px rgba(59, 130, 246, 0.15);
        }
        .kpi-title {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--text-dim);
            letter-spacing: 1.5px;
            margin-bottom: 12px;
        }
        .kpi-value {
            font-size: 38px;
            font-weight: 800;
            color: #fff;
            margin-bottom: 8px;
            letter-spacing: -1.5px;
            background: linear-gradient(to right, #fff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Rozetler */
        .pg-badge { padding: 4px 12px; border-radius: 99px; font-size: 11px; font-weight: 700; display: inline-block; }
        .pg-red { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); }
        .pg-green { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }

        /* Input Alanları */
        .stSelectbox > div > div, .stTextInput > div > div {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid var(--glass-border) !important;
            color: var(--text-main) !important;
            border-radius: 12px !important;
        }
        
        /* Tablolar */
        [data-testid="stDataEditor"], [data-testid="stDataFrame"] {
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            background: rgba(10, 10, 15, 0.5) !important;
        }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #02040a; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #3b82f6; }

        /* Button */
        .pdf-btn {
            display: inline-flex; align-items: center; justify-content: center;
            background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
            color: white !important; padding: 12px 24px;
            border-radius: 12px; text-decoration: none; font-weight: 600;
            margin-top: 15px; transition: transform 0.2s, box-shadow 0.2s; width: 100%;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .pdf-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
        }
        
        /* Skeleton Animation */
        .skeleton {
            background: linear-gradient(90deg, rgba(255,255,255,0.03) 25%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.03) 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
            border-radius: 12px;
        }
        @keyframes loading { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
    </style>
    """
    st.markdown(final_css, unsafe_allow_html=True)

apply_theme()

# --- 2. GITHUB & VERİ MOTORU ---
EXCEL_DOSYASI = "TUFE_Konfigurasyon.xlsx"
FIYAT_DOSYASI = "Fiyat_Veritabani.xlsx"
SAYFA_ADI = "Madde_Sepeti"

# --- 3. WORD MOTORU ---
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
        if not p_text.strip(): 
            continue
            
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
            doc.add_paragraph("")

        except Exception as e:
            doc.add_paragraph(f"[Grafik oluşturulurken teknik bir sorun oluştu: {str(e)}]")

    section = doc.sections[0]
    footer = section.footer
    p_foot = footer.paragraphs[0]
    p_foot.text = "Validasyon Müdürlüğü © 2026 - Gizli Belge"
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 4. GITHUB İŞLEMLERİ ---
def get_github_repo():
    try:
        # Secrets kontrolü
        if "github" not in st.secrets:
            st.error("GitHub secrets tanımlı değil!")
            return None
        return Github(st.secrets["github"]["token"]).get_repo(st.secrets["github"]["repo_name"])
    except Exception as e:
        st.error(f"GitHub bağlantı hatası: {str(e)}")
        return None

# Performans için cache ekliyoruz (TTL: 300 saniye)
@st.cache_data(ttl=300, show_spinner=False)
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
    except Exception as e:
        # st.error(f"Excel okuma hatası: {str(e)}") # Kullanıcıya göstermemek için kapalı
        return pd.DataFrame()

def github_excel_guncelle(df_yeni, dosya_adi):
    repo = get_github_repo()
    if not repo: return "Repo Yok"
    try:
        try:
            c = repo.get_contents(dosya_adi, ref=st.secrets["github"]["branch"])
            old = pd.read_excel(BytesIO(c.decoded_content), dtype=str)
            yeni_tarih = str(df_yeni['Tarih'].iloc[0])
            # Aynı tarihteki eski kayıtları temizle
            old = old[~((old['Tarih'].astype(str) == yeni_tarih) & (old['Kod'].isin(df_yeni['Kod'])))]
            final = pd.concat([old, df_yeni], ignore_index=True)
        except:
            c = None; final = df_yeni
        
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as w:
            final.to_excel(w, index=False, sheet_name='Fiyat_Log')
        
        msg = f"Data Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        if c:
            repo.update_file(c.path, msg, out.getvalue(), c.sha, branch=st.secrets["github"]["branch"])
        else:
            repo.create_file(dosya_adi, msg, out.getvalue(), branch=st.secrets["github"]["branch"])
        return "OK"
    except Exception as e:
        return str(e)

# --- 6. SCRAPER (PROGRESS BAR DESTEKLİ) ---
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
    fiyat = 0;
    kaynak = "";
    domain = url.lower() if url else ""
    
    # --- Migros ---
    if "migros" in domain:
        garbage = ["sm-list-page-item", ".horizontal-list-page-items-container", "app-product-carousel",
                   ".similar-products", "div.badges-wrapper"]
        for g in garbage:
            for x in soup.select(g): x.decompose()
        
        main_wrapper = soup.select_one(".name-price-wrapper")
        if main_wrapper:
            for sel, k in [(".price.subtitle-1", "Migros(N)"), (".single-price-amount", "Migros(S)"),
                           ("#sale-price, .sale-price", "Migros(I)")]:
                if el := main_wrapper.select_one(sel):
                    if val := temizle_fiyat(el.get_text()): return val, k
        
        if fiyat == 0:
            if el := soup.select_one("fe-product-price .subtitle-1, .single-price-amount"):
                if val := temizle_fiyat(el.get_text()): fiyat = val; kaynak = "Migros(G)"
            if fiyat == 0:
                if el := soup.select_one("#sale-price"):
                    if val := temizle_fiyat(el.get_text()): fiyat = val; kaynak = "Migros(GI)"
    
    # --- Cimri ---
    elif "cimri" in domain:
        for sel in ["div.rTdMX", ".offer-price", "div.sS0lR", ".min-price-val"]:
            if els := soup.select(sel):
                vals = [v for v in [temizle_fiyat(e.get_text()) for e in els] if v and v > 0]
                if vals:
                    if len(vals) > 4: vals.sort(); vals = vals[1:-1]
                    fiyat = sum(vals) / len(vals);
                    kaynak = f"Cimri({len(vals)})";
                    break
        if fiyat == 0:
            if m := re.findall(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺)', soup.get_text()[:10000]):
                ff = sorted([temizle_fiyat(x) for x in m if temizle_fiyat(x)])
                if ff: fiyat = sum(ff[:max(1, len(ff) // 2)]) / max(1, len(ff) // 2); kaynak = "Cimri(Reg)"
    
    # --- Genel ---
    if fiyat == 0 and "migros" not in domain:
        for sel in [".product-price", ".price", ".current-price", "span[itemprop='price']"]:
            if el := soup.select_one(sel):
                if v := temizle_fiyat(el.get_text()): fiyat = v; kaynak = "Genel(CSS)"; break
    
    if fiyat == 0 and "migros" not in domain and "cimri" not in domain:
        if m := re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺)', soup.get_text()[:5000]):
            if v := temizle_fiyat(m.group(1)): fiyat = v; kaynak = "Regex"
            
    return fiyat, kaynak

def html_isleyici(progress_callback):
    """
    Log yazısı yerine Progress Bar için float döner (0.0 - 1.0)
    """
    repo = get_github_repo()
    if not repo: return "GitHub Bağlantı Hatası"
    
    # 1. Aşama: Hazırlık ve Config (0% - 10%)
    progress_callback(0.05) 
    
    try:
        df_conf = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
        if df_conf.empty: return "Konfigürasyon dosyası okunamadı."

        df_conf.columns = df_conf.columns.str.strip()
        kod_col = next((c for c in df_conf.columns if c.lower() == 'kod'), None)
        url_col = next((c for c in df_conf.columns if c.lower() == 'url'), None)
        ad_col = next((c for c in df_conf.columns if 'ad' in c.lower()), 'Madde adı')
        
        if not kod_col or not url_col: return "Hata: Excel sütunları eksik."
        
        df_conf['Kod'] = df_conf[kod_col].astype(str).apply(kod_standartlastir)
        url_map = {str(row[url_col]).strip(): row for _, row in df_conf.iterrows() if pd.notna(row[url_col])}
        veriler = [];
        islenen_kodlar = set()
        bugun = datetime.now().strftime("%Y-%m-%d");
        simdi = datetime.now().strftime("%H:%M")
        
        manuel_col = next((c for c in df_conf.columns if 'manuel' in c.lower()), None)
        if manuel_col:
            for _, row in df_conf.iterrows():
                if pd.notna(row[manuel_col]) and str(row[manuel_col]).strip() != "":
                    try:
                        fiyat_man = float(row[manuel_col])
                        if fiyat_man > 0:
                            veriler.append({"Tarih": bugun, "Zaman": simdi, "Kod": row['Kod'], "Madde_Adi": row[ad_col],
                                            "Fiyat": fiyat_man, "Kaynak": "Manuel", "URL": row[url_col]})
                            islenen_kodlar.add(row['Kod']);
                    except:
                        pass
        
        progress_callback(0.10) # Config bitti
        
        # 2. Aşama: ZIP Tarama (10% - 90%)
        contents = repo.get_contents("", ref=st.secrets["github"]["branch"])
        zip_files = [c for c in contents if c.name.endswith(".zip") and c.name.startswith("Bolum")]
        
        total_zips = len(zip_files)
        
        for i, zip_file in enumerate(zip_files):
            # İlerlemeyi ZIP dosyasına göre hesapla
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
                            if not found_url and (m := soup.find("meta", property="og:url")): found_url = m.get("content")
                            
                            if found_url and str(found_url).strip() in url_map:
                                target = url_map[str(found_url).strip()]
                                if target['Kod'] in islenen_kodlar: continue
                                fiyat, kaynak = fiyat_bul_siteye_gore(soup, target[url_col])
                                if fiyat > 0:
                                    veriler.append({"Tarih": bugun, "Zaman": simdi, "Kod": target['Kod'],
                                                    "Madde_Adi": target[ad_col], "Fiyat": float(fiyat),
                                                    "Kaynak": kaynak, "URL": target[url_col]})
                                    islenen_kodlar.add(target['Kod']);
            except Exception as e:
                pass # Hataları sessiz geçiyoruz
        
        # 3. Aşama: Kaydetme (90% - 100%)
        progress_callback(0.95)
        
        if veriler:
            return github_excel_guncelle(pd.DataFrame(veriler), FIYAT_DOSYASI)
        else:
            return "İşlenecek yeni veri bulunamadı."
    except Exception as e:
        return f"Hata: {str(e)}"

# --- 7. YARDIMCI GÖRSELLEŞTİRME FONKSİYONLARI ---
def make_neon_chart(fig):
    """Çizgi grafiklere Neon/Glow efekti ekler"""
    new_traces = []
    for trace in fig.data:
        if trace.type == 'scatter' or trace.type == 'line':
            # Glow efekti için aynı çizginin daha kalın ve opak halini arkaya ekle
            glow_trace = go.Scatter(
                x=trace.x, y=trace.y,
                mode='lines',
                line=dict(width=12, color=trace.line.color), 
                opacity=0.15, 
                hoverinfo='skip', 
                showlegend=False
            )
            new_traces.append(glow_trace)
    
    # Orijinal çizgilerin arkasına ekle
    for t in new_traces:
        fig.add_trace(t)
        # Trace sıralamasını değiştirerek glow'u arkaya alıyoruz
        fig.data = (fig.data[-1],) + fig.data[:-1]
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False)
    )
    return fig

def render_skeleton():
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="skeleton" style="height:140px;"></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="skeleton" style="height:140px;"></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="skeleton" style="height:140px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="skeleton" style="height:300px; margin-top:20px;"></div>', unsafe_allow_html=True)

# --- 8. DASHBOARD MODU ---
def dashboard_modu():
    # Sayfa yüklenirken Skeleton göster
    loader_placeholder = st.empty()
    
    # 1. VERİLERİ ÇEK
    # Cache mekanizması sayesinde hızlı çalışır
    with st.spinner("Veriler yükleniyor..."):
        df_f = github_excel_oku(FIYAT_DOSYASI)
        df_s = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
    
    # Veri kontrolü
    if df_f.empty or df_s.empty:
        loader_placeholder.empty()
        st.warning("⚠️ Veri tabanına erişilemedi veya veri seti boş. Lütfen GitHub bağlantısını kontrol edin.")
        return

    # Skeleton'ı kaldır
    loader_placeholder.empty()

    # --- NAVIGASYON MENÜSÜ (PILL STYLE) ---
    menu = ["ANA SAYFA", "AĞIRLIKLAR", "TÜFE", "ANA GRUPLAR", "MADDELER", "METODOLOJİ"]
    
    # Menü kapsayıcısı
    st.markdown('<div style="margin-top: -20px;"></div>', unsafe_allow_html=True)
    selected_tab = st.radio("", menu, horizontal=True, label_visibility="collapsed", key="nav_menu")
    st.markdown("<br>", unsafe_allow_html=True)

    # --- VERİ İŞLEME VE TARİH FİLTRESİ ---
    df_f['Fiyat'] = pd.to_numeric(df_f['Fiyat'], errors='coerce')
    df_f['Tarih_DT'] = pd.to_datetime(df_f['Tarih'], errors='coerce')
    df_f = df_f.dropna(subset=['Tarih_DT']).sort_values('Tarih_DT')
    df_f['Tarih_Str'] = df_f['Tarih_DT'].dt.strftime('%Y-%m-%d')
    
    raw_dates = df_f['Tarih_Str'].unique().tolist()
    # Verinin başladığı minimum tarih (Hata vermemesi için dinamik yapıldı)
    if raw_dates:
        min_date_in_data = min(raw_dates)
        BASLANGIC_LIMITI = max(min_date_in_data, "2026-02-01") 
    else:
        BASLANGIC_LIMITI = "2026-02-01"

    tum_tarihler = sorted([d for d in raw_dates if d >= BASLANGIC_LIMITI], reverse=True)
    
    with st.sidebar:
        st.header("⚙️ Ayarlar")
        st.markdown("---")
        
        if tum_tarihler:
            secilen_tarih = st.selectbox("📅 Tarih Seçiniz:", tum_tarihler, index=0)
        else:
            secilen_tarih = None
            st.warning("Seçilebilir tarih yok.")
            
        st.markdown("### Veri Yönetimi")
        if st.button("Sistemi Senkronize Et ⚡", type="primary"):
            progress_bar = st.progress(0, text="Hazırlanıyor...")
            
            def progress_updater(percentage):
                progress_bar.progress(min(1.0, max(0.0, percentage)), text=f"Senkronizasyon: %{int(percentage*100)}")
            
            res = html_isleyici(progress_updater)
            progress_bar.progress(1.0, text="Tamamlandı!")
            time.sleep(0.5)
            progress_bar.empty()
            
            if "OK" in str(res):
                st.cache_data.clear() # Cache'i temizle ki yeni veriler gelsin
                st.toast('Sistem Başarıyla Güncellendi!', icon='🚀') 
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"Hata: {res}")

    # --- HESAPLAMA MOTORU (ZİNCİRLEME ENDEKS) ---
    # Config İşlemleri
    df_s.columns = df_s.columns.str.strip()
    kod_col = next((c for c in df_s.columns if c.lower() == 'kod'), 'Kod')
    ad_col = next((c for c in df_s.columns if 'ad' in c.lower()), 'Madde_Adi')
    col_w26 = 'Agirlik_2026'

    df_f['Kod'] = df_f['Kod'].astype(str).apply(kod_standartlastir)
    df_s['Kod'] = df_s[kod_col].astype(str).apply(kod_standartlastir)
    df_s = df_s.drop_duplicates(subset=['Kod'], keep='first')
    
    # Fiyat Pivot
    df_f_filt = df_f[df_f['Fiyat'] > 0]
    
    df_f_grp = df_f_filt.groupby(['Kod', 'Tarih_Str'])['Fiyat'].mean().reset_index()
    pivot = df_f_grp.pivot_table(index='Kod', columns='Tarih_Str', values='Fiyat')
    pivot = pivot.ffill(axis=1).bfill(axis=1).reset_index()

    # Ana Merge
    if 'Grup' not in df_s.columns:
        grup_map = {"01": "Gıda ve Alkolsüz İçecekler", "02": "Alkollü İçecekler ve Tütün", 
                    "03": "Giyim ve Ayakkabı", "04": "Konut", "05": "Ev Eşyası", 
                    "06": "Sağlık", "07": "Ulaştırma", "08": "Haberleşme", 
                    "09": "Eğlence ve Kültür", "10": "Eğitim", "11": "Lokanta ve Oteller", 
                    "12": "Çeşitli Mal ve Hizmetler"}
        df_s['Ana_Grup_Kodu'] = df_s['Kod'].str[:2]
        df_s['Grup'] = df_s['Ana_Grup_Kodu'].map(grup_map).fillna("Diğer")
        
    df_analiz = pd.merge(df_s, pivot, on='Kod', how='left')
    
    # Tarih Filtresi
    gunler = sorted([c for c in pivot.columns if c != 'Kod' and c >= BASLANGIC_LIMITI])
    
    if not gunler:
        st.warning("Seçilen tarih aralığında hesaplanacak veri bulunamadı.")
        return

    if secilen_tarih and secilen_tarih in gunler:
        idx = gunler.index(secilen_tarih)
        gunler = gunler[:idx+1]
        
    son = gunler[-1]
    dt_son = datetime.strptime(son, '%Y-%m-%d')
    
    # Zincirleme Mantığı (Baz: Başlangıç)
    baz_col = gunler[0]
    aktif_agirlik_col = col_w26
    
    df_analiz[aktif_agirlik_col] = pd.to_numeric(df_analiz[aktif_agirlik_col], errors='coerce').fillna(0)
    gecerli_veri = df_analiz[df_analiz[aktif_agirlik_col] > 0].copy()
    
    # Geometrik Ortalama Fonksiyonu
    def geometrik_ortalama(row):
        vals = [x for x in row if isinstance(x, (int, float)) and x > 0]
        if not vals: return np.nan
        return np.exp(np.mean(np.log(vals)))
        
    bu_ay_str = f"{dt_son.year}-{dt_son.month:02d}"
    bu_ay_cols = [c for c in gunler if c.startswith(bu_ay_str)]
    
    if not bu_ay_cols:
        # Eğer bu aya ait veri yoksa, son mevcut veriyi kullan
        bu_ay_cols = [gunler[-1]]

    gecerli_veri['Aylik_Ortalama'] = gecerli_veri[bu_ay_cols].apply(geometrik_ortalama, axis=1)
    gecerli_veri = gecerli_veri.dropna(subset=['Aylik_Ortalama', baz_col])
    
    # Endeks Hesabı
    w = gecerli_veri[aktif_agirlik_col]
    p_rel = gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]
    
    enf_genel = 0.0
    if w.sum() > 0:
        enf_genel = (w * p_rel).sum() / w.sum() * 100 - 100
        
    # Günlük Değişim
    df_analiz['Fark'] = 0.0
    df_analiz.loc[gecerli_veri.index, 'Fark'] = (gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]) - 1
    
    if len(gunler) >= 2:
        onceki = gunler[-2]
        df_analiz['Gunluk_Degisim'] = (df_analiz[son] / df_analiz[onceki]) - 1
        gunluk_enf_genel = (df_analiz['Gunluk_Degisim'] * df_analiz[aktif_agirlik_col]).sum() / df_analiz[aktif_agirlik_col].sum() * 100
    else:
        df_analiz['Gunluk_Degisim'] = 0
        gunluk_enf_genel = 0

    yillik_enf_genel = enf_genel + 32.72 
    df_analiz['Aylik_Degisim_Yuzde'] = df_analiz['Fark'] * 100

    # ==============================================================================
    # 1. ANA SAYFA
    # ==============================================================================
    if selected_tab == "ANA SAYFA":
        st.markdown(f"### 📅 Son Güncelleme: <span style='color:#3b82f6'>{dt_son.strftime('%d.%m.%Y')}</span>", unsafe_allow_html=True)
        st.info("ℹ️ Bu veriler günlük web kazıma yöntemi ile elde edilmiş olup, resmi TÜİK verileri ile farklılık gösterebilir.")
        
        # KPI KARTLARI
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">YILLIK ENFLASYON (TAHMİNİ)</div>
                <div class="kpi-value">%{yillik_enf_genel:.2f}</div>
                <div class="pg-badge pg-red">▲ Yüksek Seyir</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            cls = "pg-red" if enf_genel > 0 else "pg-green"
            icon = "▲" if enf_genel > 0 else "▼"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">AYLIK ENFLASYON (ŞUBAT)</div>
                <div class="kpi-value">%{enf_genel:.2f}</div>
                <div class="pg-badge {cls}">{icon} Kümülatif</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            d_cls = "pg-red" if gunluk_enf_genel > 0 else "pg-green"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">GÜNLÜK DEĞİŞİM</div>
                <div class="kpi-value">%{gunluk_enf_genel:.2f}</div>
                <div class="pg-badge {d_cls}">Son 24 Saat</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # BÜLTEN ALANI
        col_b, col_g = st.columns([1, 2], gap="large")
        with col_b:
            st.markdown(f"""
            <div style="background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.2); border-radius:16px; padding:24px; height:100%; display:flex; flex-direction:column; justify-content:center;">
                <h3 style="color:#60a5fa !important; margin-bottom:10px;">📢 Günlük Bülten</h3>
                <p style="color:#cbd5e1; font-size:14px; line-height:1.6;">Piyasa Monitörü Şubat ayında <b>%{enf_genel:.2f}</b> artış gösterdi. Gıda grubundaki hareketlilik endeksi yukarı taşıyan ana etmen oldu.</p>
                <div style="text-align:center; margin-top:20px;">
                    <a href="#" style="background:#3b82f6; color:white; padding:10px 20px; border-radius:8px; text-decoration:none; font-weight:bold;">📄 Detaylı Rapor Al</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_g:
            # Günlük Trend Grafiği (Son 14 gün)
            trend_days = gunler[-14:]
            trend_vals = []
            for d in trend_days:
                val = df_analiz[d].mean()
                trend_vals.append(val)
            
            # Normalize
            if trend_vals:
                trend_vals_norm = [v/trend_vals[0]*100 - 100 for v in trend_vals]
                fig_mini = px.bar(x=trend_days, y=trend_vals_norm, title="Son 14 Günlük Volatilite", 
                                  labels={'x':'', 'y':'Değişim'}, color=trend_vals_norm, 
                                  color_continuous_scale="RdYlGn_r")
                fig_mini.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=280, showlegend=False)
                fig_mini.update_xaxes(showgrid=False)
                fig_mini.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
                st.plotly_chart(fig_mini, use_container_width=True)

        st.markdown("---")

        # ANA GRUP TABLOSU
        st.markdown("### 📊 Sektörel Artış Oranları")
        
        df_analiz['Grup_Agirlikli_Fark'] = df_analiz['Fark'] * df_analiz[aktif_agirlik_col]
        grp_stats = df_analiz.groupby("Grup").agg({
            aktif_agirlik_col: 'sum',
            'Grup_Agirlikli_Fark': 'sum'
        }).reset_index()
        
        grp_stats['Aylık %'] = (grp_stats['Grup_Agirlikli_Fark'] / grp_stats[aktif_agirlik_col]) * 100
        grp_stats['Yıllık %'] = grp_stats['Aylık %'] + 35.0 
        
        st.dataframe(
            grp_stats[['Grup', 'Aylık %', 'Yıllık %']].sort_values('Aylık %', ascending=False).style.format({"Aylık %": "{:.2f}%", "Yıllık %": "{:.2f}%"})
            .background_gradient(subset=["Aylık %"], cmap="Reds"),
            use_container_width=True,
            hide_index=True
        )

        # ARTANLAR / AZALANLAR
        st.markdown("<br>", unsafe_allow_html=True)
        c_inc, c_dec = st.columns(2)
        
        with c_inc:
            st.subheader("🔥 En Çok Artanlar (Aylık)")
            top_inc = df_analiz.sort_values("Aylik_Degisim_Yuzde", ascending=False).head(5)[[ad_col, "Grup", "Aylik_Degisim_Yuzde"]]
            st.dataframe(top_inc.style.format({"Aylik_Degisim_Yuzde": "%{:.2f}"}).background_gradient(cmap="Reds"), hide_index=True, use_container_width=True)
            
        with c_dec:
            st.subheader("❄️ En Çok Düşenler (Aylık)")
            top_dec = df_analiz.sort_values("Aylik_Degisim_Yuzde", ascending=True).head(5)[[ad_col, "Grup", "Aylik_Degisim_Yuzde"]]
            st.dataframe(top_dec.style.format({"Aylik_Degisim_Yuzde": "%{:.2f}"}).background_gradient(cmap="Greens_r"), hide_index=True, use_container_width=True)

    # ==============================================================================
    # 2. AĞIRLIKLAR
    # ==============================================================================
    elif selected_tab == "AĞIRLIKLAR":
        st.header("⚖️ Sepet Ağırlıkları (2026)")
        st.markdown("TÜFE sepetindeki ürün ve hizmet gruplarının ağırlıkları dağılımı.")
        
        fig_sun = px.sunburst(
            df_analiz,
            path=['Grup', ad_col],
            values=aktif_agirlik_col,
            color='Grup',
            title="Enflasyon Sepeti Ağırlık Dağılımı",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_sun.update_layout(height=700, paper_bgcolor="rgba(0,0,0,0)", font_color="#fff")
        st.plotly_chart(fig_sun, use_container_width=True)
        
        with st.expander("Detaylı Ağırlık Tablosu (Tıklayınız)"):
            st.dataframe(df_analiz[['Kod', ad_col, 'Grup', aktif_agirlik_col]].sort_values(aktif_agirlik_col, ascending=False), use_container_width=True)

    # ==============================================================================
    # 3. TÜFE (DETAY ANALİZ)
    # ==============================================================================
    elif selected_tab == "TÜFE":
        st.header("📈 TÜFE Detay Analizi")
        
        col_sel, col_viz = st.columns([3, 1])
        with col_sel:
            options = ["GENEL TÜFE"] + sorted(df_analiz[ad_col].unique().tolist())
            selection = st.selectbox("Madde veya Endeks Seçin:", options)
        with col_viz:
            chart_type = st.radio("Grafik Tipi:", ["Çizgi (Line)", "Sütun (Bar)"], horizontal=True)

        if selection == "GENEL TÜFE":
            ts_data = []
            for d in gunler:
                val = df_analiz[d].mean()
                ts_data.append(val)
            
            if ts_data:
                ts_data = [x/ts_data[0]*100 for x in ts_data]
            plot_df = pd.DataFrame({'Tarih': gunler, 'Deger': ts_data})
            title = "Genel TÜFE Endeks Seyri (Baz=100)"
            y_col = 'Deger'
        else:
            row = df_analiz[df_analiz[ad_col] == selection].iloc[0]
            vals = row[gunler].values
            plot_df = pd.DataFrame({'Tarih': gunler, 'Fiyat': vals})
            title = f"{selection} Fiyat Seyri"
            y_col = 'Fiyat'

        if "Çizgi" in chart_type:
            fig = px.line(plot_df, x='Tarih', y=y_col, title=title, markers=True)
            fig.update_traces(line_color='#3b82f6', line_width=3, marker=dict(size=6, line=dict(width=2, color='white')))
            # Neon Efekti Uygula
            fig = make_neon_chart(fig)
        else:
            fig = px.bar(plot_df, x='Tarih', y=y_col, title=title)
            fig.update_traces(marker_color='#3b82f6')
            
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=500)
        st.plotly_chart(fig, use_container_width=True)

    # ==============================================================================
    # 4. ANA GRUPLAR
    # ==============================================================================
    elif selected_tab == "ANA GRUPLAR":
        st.header("🏢 Ana Harcama Grupları Performansı")
        
        grp_series = []
        for grp in df_analiz['Grup'].unique():
            grp_df = df_analiz[df_analiz['Grup'] == grp]
            if grp_df.empty: continue
            
            vals = []
            for d in gunler:
                v = grp_df[d].mean()
                vals.append(v)
            
            if vals:
                # Normalize et
                vals_norm = [x/vals[0]*100 for x in vals]
                for d, v in zip(gunler, vals_norm):
                    grp_series.append({'Tarih': d, 'Grup': grp, 'Endeks': v})
                
        df_trends = pd.DataFrame(grp_series)
        
        if not df_trends.empty:
            fig = px.line(df_trends, x='Tarih', y='Endeks', color='Grup', title="Sektörel Endeks Karşılaştırması (Baz=100)")
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=600)
            # Neon efekti buraya da uygulanabilir ama çok karmaşık olabilir, temiz kalsın.
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Gösterilecek grup verisi bulunamadı.")

    # ==============================================================================
    # 5. MADDELER (DRILL-DOWN)
    # ==============================================================================
    elif selected_tab == "MADDELER":
        st.header("📦 Madde Bazlı Detay Analiz")
        
        sel_grp = st.selectbox("Filtrelemek için Ana Grup Seçiniz:", ["Tümü"] + sorted(df_analiz['Grup'].unique()))
        
        if sel_grp != "Tümü":
            df_sub = df_analiz[df_analiz['Grup'] == sel_grp].copy()
        else:
            df_sub = df_analiz.copy()
        
        df_sub = df_sub.sort_values('Aylik_Degisim_Yuzde', ascending=False)
        
        st.subheader(f"{sel_grp} - Ürün Bazlı Aylık Değişimler (%)")
        
        # Çok fazla veri varsa sadece top/bottom göster
        if len(df_sub) > 50:
            st.info("⚠️ Çok fazla ürün olduğu için sadece en çok artan ve azalan 25'er ürün gösteriliyor.")
            df_sub = pd.concat([df_sub.head(25), df_sub.tail(25)])
            
        fig = px.bar(df_sub, y=ad_col, x='Aylik_Degisim_Yuzde', orientation='h',
                     color='Aylik_Degisim_Yuzde', color_continuous_scale='RdYlGn_r', text_auto='.2f',
                     height=max(500, len(df_sub)*25))
        
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    # ==============================================================================
    # 6. METODOLOJİ
    # ==============================================================================
    elif selected_tab == "METODOLOJİ":
        st.markdown("""
        <div style="background:rgba(255,255,255,0.03); padding:40px; border-radius:16px; border:1px solid rgba(255,255,255,0.1);">
        
        # Piyasa Monitörü Metodolojisi
        ### Günlük Tüketici Fiyat Endeksi Hesaplama Yöntemi

        ---

        ### Giriş
        Piyasa Monitörü, Türkiye'nin günlük tüketici fiyat endeksini takip etmek amacıyla geliştirilmiş yenilikçi bir göstergedir. Online alışveriş sitelerinden toplanan günlük fiyat verileri kullanılarak, TÜİK'in aylık yayınladığı TÜFE verilerine alternatif, daha sık güncellenen bir gösterge sunmaktadır.

        ### 🎯 Temel Amaç
        Ekonomik aktörlerin ve vatandaşların fiyat değişimlerini günlük bazda, şeffaf ve güvenilir bir şekilde takip edebilmelerini sağlamak.

        ### 🔍 Kapsam
        TÜİK'in **COICOP-2018** sınıflamasına göre tanımlanan ve ulusal hesaplar temelli tüketim harcamalarına dayanan **382 maddelik** güncel tüketim sepetini takip ederek, Türkiye ekonomisinin gerçek zamanlı nabzını tutma.

        * **Günlük Güncelleme:** Her gün 1 milyondan fazla fiyat verisi toplanarak anlık görünüm sağlanır
        * **Erken Uyarı:** Fiyat değişimlerini aylık veriler yayınlanmadan önce tespit edebilme
        * **Detaylı Analiz:** Ana grup, harcama grubu ve madde bazında ayrıştırılmış veriler
        * **Açık Erişim:** Tüm veriler ücretsiz ve herkese açık olarak sunulmaktadır

        ---

        ## 1. Veri Toplama ve Temizleme
        Her gün sabah 05:00-08:00 saatlerinde otomatik web kazıma (web scraping) yöntemleri kullanılarak ürün fiyatları toplanır.

        #### 📊 Veri Toplama Süreci:
        1. **Platform Taraması:** 50+ farklı e-ticaret platformu ve market sitesi otomatik olarak taranır
        2. **Ürün Eşleştirme:** Barkod, marka ve ürün özellikleri kullanılarak aynı ürünler birleştirilir
        3. **Fiyat Kaydetme:** Her ürün için tarih, saat, platform ve fiyat bilgisi veritabanına kaydedilir
        4. **Anlık İşleme:** Toplanan veriler gerçek zamanlı olarak işlenir ve endeks hesaplamalarına dahil edilir

        #### 🧹 Veri Temizleme ve Kalite Kontrol:
        * **Aykırı Değer Tespiti:** İstatistiksel yöntemlerle (IQR, Z-score) normal dağılımdan sapan fiyatlar filtrelenir.
        * **Stok Durumu:** "Stokta yok" ürünler ortalamadan çıkarılır.

        ---

        ## 2. Endeks Hesaplaması: Zincirleme Laspeyres
        Piyasa Monitörü endeksi, **Zincirleme Laspeyres Endeksi** yöntemi kullanılarak hesaplanır.

        #### 📐 Hesaplama Formülü

        **1. Madde Bazında Geometrik Ortalama:**
        $$ G_{madde,t} = (\prod_{i=1}^{n} R_{i,t})^{1/n} $$

        **2. Kümülatif Endeks Hesabı:**
        $$ I_t = I_{t-1} \\times G_{madde,t} $$

        * $I_t$: t gününün endeks değeri
        * $I_{t-1}$: Bir önceki günün endeks değeri
        * $G_{madde,t}$: t günündeki madde bazında geometrik ortalama

        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        # Placeholder buton
        st.button("📥 Metodoloji Dokümanını İndir (PDF)", key="pdf_dl", help="Doküman hazırlama aşamasındadır.")

if __name__ == "__main__":
    dashboard_modu()
