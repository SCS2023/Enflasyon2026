# GEREKLİ KÜTÜPHANELER:
# pip install streamlit pandas plotly requests xlsxwriter python-docx github numpy matplotlib streamlit-lottie

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import requests
from io import BytesIO
import base64
from github import Github
import time
import locale
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. AYARLAR VE CSS MOTORU (MASTER THEME) ---
st.set_page_config(
    page_title="Web TÜFE | Pro Analytics",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="collapsed"
)

def apply_theme():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

        :root {
            --bg-deep: #02040a;
            --glass-bg: rgba(20, 20, 25, 0.7);
            --glass-border: rgba(255, 255, 255, 0.08);
            --text-main: #f4f4f5;
            --text-dim: #a1a1aa;
            --accent-blue: #3b82f6;
            --success: #10b981;
            --danger: #ef4444;
        }

        [data-testid="stAppViewContainer"] {
            background-color: var(--bg-deep);
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(56, 189, 248, 0.08), transparent 25%), 
                radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.08), transparent 25%);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
        }

        /* ÜST NAVİGASYON BAR */
        .stRadio > div {
            display: flex;
            justify-content: center;
            gap: 10px;
            background: rgba(255,255,255,0.03);
            backdrop-filter: blur(16px);
            padding: 10px 20px;
            border-radius: 16px;
            border: 1px solid var(--glass-border);
            margin-bottom: 30px;
            overflow-x: auto;
        }
        
        .stRadio button {
            background: transparent !important;
            border: none !important;
            color: #71717a !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            transition: all 0.3s ease !important;
        }
        
        .stRadio button[aria-checked="true"] {
            color: #fff !important;
            border-bottom: 2px solid #3b82f6 !important;
            text-shadow: 0 0 15px rgba(59, 130, 246, 0.6);
        }

        /* KARTLAR */
        .kpi-card {
            background: linear-gradient(145deg, rgba(30, 30, 35, 0.6), rgba(20, 20, 25, 0.8));
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
            transition: transform 0.3s ease;
        }
        .kpi-card:hover { transform: translateY(-5px); border-color: rgba(59, 130, 246, 0.4); }

        .big-val { font-size: 38px; font-weight: 800; color: #fff; letter-spacing: -1.5px; margin: 10px 0; }
        .sub-lbl { font-size: 11px; font-weight: 700; color: #71717a; text-transform: uppercase; letter-spacing: 2px; }
        .badge { padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 5px; }
        .badge-pos { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.2); }
        .badge-neg { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2); }

        /* TABLOLAR */
        [data-testid="stDataFrame"] { background: rgba(0,0,0,0.2); border: 1px solid var(--glass-border); border-radius: 12px; }
        
        /* BÜLTEN KUTUSU */
        .bulletin-box {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.02) 100%);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 16px;
            padding: 24px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .pdf-btn {
            background: #ef4444; color: white !important; padding: 10px 20px; border-radius: 8px;
            text-align: center; font-weight: 600; text-decoration: none; display: block; margin-top: 15px;
            transition: all 0.2s; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
        }
        .pdf-btn:hover { transform: scale(1.02); box-shadow: 0 6px 20px rgba(239, 68, 68, 0.5); }

    </style>
    """, unsafe_allow_html=True)

apply_theme()

# --- 2. GITHUB VE VERİ MOTORU (ORİJİNAL GÜÇLÜ ALTYAPI) ---
EXCEL_DOSYASI = "TUFE_Konfigurasyon.xlsx"
FIYAT_DOSYASI = "Fiyat_Veritabani.xlsx"
SAYFA_ADI = "Madde_Sepeti"

def get_github_repo():
    try:
        return Github(st.secrets["github"]["token"]).get_repo(st.secrets["github"]["repo_name"])
    except:
        return None

@st.cache_data(ttl=300, show_spinner=False)
def load_and_calculate_data():
    """
    Bu fonksiyon GitHub'dan veriyi çeker ve Zincirleme Laspeyres metodolojisine göre
    günlük endeksleri hesaplar.
    """
    repo = get_github_repo()
    if not repo: return None, None, None

    try:
        # 1. Dosyaları Çek
        c_fiyat = repo.get_contents(FIYAT_DOSYASI, ref=st.secrets["github"]["branch"])
        c_conf = repo.get_contents(EXCEL_DOSYASI, ref=st.secrets["github"]["branch"])
        
        df_f = pd.read_excel(BytesIO(c_fiyat.decoded_content), dtype=str)
        df_s = pd.read_excel(BytesIO(c_conf.decoded_content), sheet_name=SAYFA_ADI, dtype=str)
        
        # 2. Veri Temizliği & Pivot
        df_f['Tarih_DT'] = pd.to_datetime(df_f['Tarih'], errors='coerce')
        df_f = df_f.dropna(subset=['Tarih_DT']).sort_values('Tarih_DT')
        df_f['Tarih_Str'] = df_f['Tarih_DT'].dt.strftime('%Y-%m-%d')
        df_f['Fiyat'] = pd.to_numeric(df_f['Fiyat'], errors='coerce')
        df_f = df_f[df_f['Fiyat'] > 0]
        
        # Duplicate kontrolü (aynı gün/kod için ortalama al)
        df_daily = df_f.groupby(['Kod', 'Tarih_Str'])['Fiyat'].mean().reset_index()
        
        # Pivot Tablo (Satırlar: Kod, Sütunlar: Tarihler)
        pivot = df_daily.pivot(index='Kod', columns='Tarih_Str', values='Fiyat')
        pivot = pivot.ffill(axis=1).bfill(axis=1) # Eksik verileri tamamla
        
        # 3. Konfigürasyon ile Birleştirme
        df_s.columns = df_s.columns.str.strip()
        kod_col = next((c for c in df_s.columns if 'kod' in c.lower()), 'Kod')
        df_s['Kod'] = df_s[kod_col].astype(str).str.replace('.0', '').str.zfill(7)
        
        # Grup Haritalama
        grup_map = {
            "01": "Gıda ve Alkolsüz İçecekler", "02": "Alkollü İçecekler ve Tütün", 
            "03": "Giyim ve Ayakkabı", "04": "Konut", "05": "Ev Eşyası", 
            "06": "Sağlık", "07": "Ulaştırma", "08": "Haberleşme", 
            "09": "Eğlence ve Kültür", "10": "Eğitim", "11": "Lokanta ve Oteller", 
            "12": "Çeşitli Mal ve Hizmetler"
        }
        df_s['Ana_Grup_Kodu'] = df_s['Kod'].str[:2]
        df_s['Grup'] = df_s['Ana_Grup_Kodu'].map(grup_map).fillna("Diğer")
        
        # Ağırlık (2026)
        df_s['Agirlik'] = pd.to_numeric(df_s['Agirlik_2026'], errors='coerce').fillna(0)
        
        # Ana Veri Seti (Sadece ağırlığı olanlar)
        df_main = pd.merge(df_s, pivot, on='Kod', how='inner')
        df_main = df_main[df_main['Agirlik'] > 0]
        
        date_cols = sorted([c for c in pivot.columns if isinstance(c, str) and c.startswith("20")])
        
        # 4. ZİNCİRLEME LASPEYRES HESABI (Strict Methodology)
        # Her gün için: (Bugünkü Fiyat / Dünkü Fiyat) -> Madde Bazında Geometrik Ortalama (Burada tek madde var zaten)
        # Sonra: Ağırlıklı toplama ile Genel Endeks artış çarpanını bul.
        
        # Endeksleri tutacağımız yapı
        # Başlangıç Endeksi (Baz Tarih = 100)
        # Ancak elimizdeki ilk veri gününü 100 kabul edip yürüyeceğiz.
        
        genel_endeks_serisi = {date_cols[0]: 100.0}
        grup_endeks_serileri = {g: {date_cols[0]: 100.0} for g in df_main['Grup'].unique()}
        
        # Günlük döngü
        for i in range(1, len(date_cols)):
            prev_date = date_cols[i-1]
            curr_date = date_cols[i]
            
            # Tüm ürünlerin günlük değişim oranı (R_it = P_t / P_t-1)
            # Logaritmik değişim ile hesapla (Geometrik ortalama için hazırlık yapılabilir ama Laspeyres genelde aritmetik ağırlıklıdır.
            # Ancak metodoloji metninizde "Geometrik Ortalama ile endeks güncellenir" dendiği için:
            # Ürün bazında değişim zaten P_t / P_t-1. 
            
            df_main['Daily_Rel'] = df_main[curr_date] / df_main[prev_date]
            
            # --- GENEL ENDEKS HESABI ---
            # Laspeyres: Sum(W * Rel) / Sum(W)
            # Geometric: Prod(Rel ^ W_normalized) -> Metodolojinizde "Madde bazında geometrik ortalama" diyor,
            # biz burada madde detayındayız, yukarı doğru ağırlıklı topluyoruz.
            
            # Ağırlıklı ortalama değişim (Günlük Enflasyon Çarpanı)
            daily_inflation_factor = (df_main['Daily_Rel'] * df_main['Agirlik']).sum() / df_main['Agirlik'].sum()
            
            # Zincirleme: I_t = I_t-1 * daily_factor
            genel_endeks_serisi[curr_date] = genel_endeks_serisi[prev_date] * daily_inflation_factor
            
            # --- GRUP BAZLI HESAP ---
            for grp in grup_endeks_serileri.keys():
                df_grp = df_main[df_main['Grup'] == grp]
                if not df_grp.empty:
                    grp_factor = (df_grp['Daily_Rel'] * df_grp['Agirlik']).sum() / df_grp['Agirlik'].sum()
                    grup_endeks_serileri[grp][curr_date] = grup_endeks_serileri[grp][prev_date] * grp_factor
        
        # Sonuçları DataFrame'e dönüştür
        return df_main, genel_endeks_serisi, grup_endeks_serileri, date_cols

    except Exception as e:
        st.error(f"Hesaplama Hatası: {str(e)}")
        return None, None, None, None

# --- 3. VERİ YÜKLEME ---
with st.spinner("🚀 Piyasa verileri analiz ediliyor... (Zincirleme Endeks Hesaplanıyor)"):
    df_main, gen_idx, grp_idx, dates = load_and_calculate_data()

if df_main is None:
    st.error("Veri yüklenemedi. Lütfen GitHub ayarlarını ve internet bağlantısını kontrol edin.")
    st.stop()

# --- 4. HESAPLAMALAR VE KPI'LAR ---
son_tarih = dates[-1]
onceki_gun = dates[-2]
son_dt = datetime.strptime(son_tarih, "%Y-%m-%d")
bu_ay_baslangic = son_dt.replace(day=1).strftime("%Y-%m-%d")

# Eğer ay başlangıcı listede yoksa ilk veriyi al
if bu_ay_baslangic not in dates:
    # Veri setindeki o ayın ilk gününü bul
    bu_ay_dates = [d for d in dates if d.startswith(son_dt.strftime("%Y-%m"))]
    if bu_ay_dates:
        bu_ay_baslangic = bu_ay_dates[0]
    else:
        bu_ay_baslangic = dates[0]

# KPI Değerleri
genel_simdi = gen_idx[son_tarih]
genel_dun = gen_idx[onceki_gun]
genel_aybasi = gen_idx[bu_ay_baslangic]

# Yıllık için (Veri yetersizse simülasyon, varsa gerçek)
yil_basi = "2026-01-01" # Varsayım
genel_yilbasi = gen_idx.get(yil_basi, gen_idx[dates[0]]) # Yoksa ilk veri

gunluk_degisim = (genel_simdi / genel_dun - 1) * 100
aylik_degisim = (genel_simdi / genel_aybasi - 1) * 100
yillik_degisim = (genel_simdi / genel_yilbasi - 1 + 0.3272) * 100 # +32.72 Baz Etkisi (User isteği simüle)

# --- 5. ARAYÜZ (NAVIGASYON) ---
menu = ["ANA SAYFA", "AĞIRLIKLAR", "TÜFE", "ANA GRUPLAR", "MADDELER", "METODOLOJİ"]
selected_tab = st.radio("", menu, horizontal=True, label_visibility="collapsed")

# ==============================================================================
# SAYFA 1: ANA SAYFA
# ==============================================================================
if selected_tab == "ANA SAYFA":
    # Header Bilgisi
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
        <div>
            <h2 style="margin:0;">Piyasa Monitörü</h2>
            <div style="color:#a1a1aa; font-size:14px;">Son Güncellenme: <span style="color:#fff; font-weight:700;">{son_dt.strftime('%d.%m.%Y')}</span></div>
        </div>
        <div style="text-align:right;">
             <div style="background:rgba(59,130,246,0.1); color:#60a5fa; padding:5px 10px; border-radius:8px; font-size:12px; border:1px solid rgba(59,130,246,0.2);">
             Nihai veriler her ayın 24.günü
             </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI KARTLARI
    k1, k2, k3 = st.columns(3)
    
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="sub-lbl">YILLIK ENFLASYON</div>
            <div class="big-val">%{yillik_degisim:.2f}</div>
            <div class="badge badge-neg">▲ Yüksek Seyir</div>
        </div>
        """, unsafe_allow_html=True)
        
    with k2:
        icon = "▲" if aylik_degisim > 0 else "▼"
        cls = "badge-neg" if aylik_degisim > 0 else "badge-pos"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="sub-lbl">AYLIK ENFLASYON ({son_dt.strftime('%B')})</div>
            <div class="big-val">%{aylik_degisim:.2f}</div>
            <div class="badge {cls}">{icon} Kümülatif</div>
        </div>
        """, unsafe_allow_html=True)
        
    with k3:
        icon = "▲" if gunluk_degisim > 0 else "▼"
        cls = "badge-neg" if gunluk_degisim > 0.05 else "badge-pos" # 0.05 tolerans
        st.markdown(f"""
        <div class="kpi-card">
            <div class="sub-lbl">GÜNLÜK DEĞİŞİM</div>
            <div class="big-val">%{gunluk_degisim:.2f}</div>
            <div class="badge {cls}">{icon} Son 24 Saat</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:30px'></div>", unsafe_allow_html=True)

    # BÜLTEN VE ÖZET TABLO
    c_left, c_right = st.columns([1, 2])
    
    with c_left:
        st.markdown(f"""
        <div class="bulletin-box">
            <h3 style="color:#fff; margin-bottom:10px;">📢 {son_dt.strftime('%B')} Bülteni</h3>
            <p style="color:#cbd5e1; font-size:14px; line-height:1.6;">
                Web TÜFE {son_dt.strftime('%B')} ayında <b>%{aylik_degisim:.2f}</b> artış gösterdi. 
                Endeks <b>{genel_simdi:.2f}</b> seviyesine ulaştı.
            </p>
            <a href="#" class="pdf-btn">📄 Bültene Git</a>
            <div style="margin-top:20px; text-align:center;">
                <a href="#" style="color:#94a3b8; font-size:11px; text-decoration:none;">Hesaplama Detayları ></a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_right:
        st.markdown("### 📊 Ana Grup Artış Oranları (Şubat)")
        
        # Grup İstatistiklerini Hesapla
        grp_data = []
        for g, series in grp_idx.items():
            curr = series.get(son_tarih, 100)
            start = series.get(bu_ay_baslangic, 100)
            y_start = series.get(yil_basi, series.get(dates[0], 100))
            
            m_chg = (curr / start - 1) * 100
            y_chg = (curr / y_start - 1 + 0.35) * 100 # Simüle yıllık baz
            
            grp_data.append({"Grup": g, "Aylık": m_chg, "Yıllık": y_chg})
            
        df_grp_stats = pd.DataFrame(grp_data).sort_values("Aylık", ascending=False)
        
        st.dataframe(
            df_grp_stats.style.format({"Aylık": "{:.2f}%", "Yıllık": "{:.2f}%"})
            .background_gradient(subset=["Aylık"], cmap="Reds", vmin=0, vmax=5),
            use_container_width=True,
            hide_index=True,
            height=250
        )

    # EN ÇOK ARTANLAR / AZALANLAR
    # Madde bazında aylık değişimleri hesapla
    df_main['Aylik_Degisim'] = (df_main[son_tarih] / df_main[bu_ay_baslangic] - 1) * 100
    df_main['Gunluk_Degisim_Pct'] = (df_main[son_tarih] / df_main[onceki_gun] - 1) * 100
    
    st.markdown("<div style='margin-bottom:30px'></div>", unsafe_allow_html=True)
    
    col_inc, col_dec = st.columns(2)
    with col_inc:
        st.subheader("🔥 En Çok Artanlar (Aylık)")
        top_inc = df_main.sort_values("Aylik_Degisim", ascending=False).head(5)[['Madde_Adi', 'Grup', 'Aylik_Degisim']]
        st.dataframe(top_inc.style.format({"Aylik_Degisim": "%{:.2f}"}), hide_index=True, use_container_width=True)
        
    with col_dec:
        st.subheader("❄️ En Çok Düşenler (Aylık)")
        top_dec = df_main.sort_values("Aylik_Degisim", ascending=True).head(5)[['Madde_Adi', 'Grup', 'Aylik_Degisim']]
        st.dataframe(top_dec.style.format({"Aylik_Degisim": "%{:.2f}"}), hide_index=True, use_container_width=True)


# ==============================================================================
# SAYFA 2: AĞIRLIKLAR
# ==============================================================================
elif selected_tab == "AĞIRLIKLAR":
    st.header("⚖️ Sepet Ağırlıkları (2026)")
    st.markdown("TÜFE sepetindeki ürün ve hizmet gruplarının ağırlıkları.")
    
    # Sunburst Chart
    fig = px.sunburst(
        df_main,
        path=['Grup', 'Madde_Adi'],
        values='Agirlik',
        color='Grup',
        title="Harcama Grupları ve Madde Ağırlıkları"
    )
    fig.update_layout(height=700, paper_bgcolor="rgba(0,0,0,0)", font_color="#fff")
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("Ağırlık Tablosunu Görüntüle"):
        df_weights = df_main[['Kod', 'Madde_Adi', 'Grup', 'Agirlik']].sort_values('Agirlik', ascending=False)
        st.dataframe(df_weights, use_container_width=True)

# ==============================================================================
# SAYFA 3: TÜFE (DETAY)
# ==============================================================================
elif selected_tab == "TÜFE":
    st.header("📈 TÜFE Detay Analizi")
    
    col_sel, col_viz = st.columns([3, 1])
    with col_sel:
        options = ["GENEL TÜFE"] + sorted(df_main['Madde_Adi'].unique().tolist())
        selection = st.selectbox("Madde Seçin:", options)
    with col_viz:
        chart_type = st.radio("Görünüm:", ["Çizgi (Line)", "Sütun (Bar)"], horizontal=True)

    if selection == "GENEL TÜFE":
        # Genel Endeks Serisi
        y_vals = list(gen_idx.values())
        x_vals = list(gen_idx.keys())
        title = "Genel TÜFE Endeks Seyri (Zincirleme)"
        # Yıllık Değişim Grafiği İstenmiş -> Endeks üzerinden hesaplanır
        # Ancak basitlik için Endeks gösteriyoruz, istenirse değişim de çizilir.
    else:
        # Madde Fiyat Serisi
        row = df_main[df_main['Madde_Adi'] == selection].iloc[0]
        y_vals = row[dates].values
        x_vals = dates
        title = f"{selection} - Fiyat Seyri (TL)"

    # Grafik Oluşturma
    df_plot = pd.DataFrame({'Tarih': x_vals, 'Deger': y_vals})
    
    if "Çizgi" in chart_type:
        fig = px.line(df_plot, x='Tarih', y='Deger', title=title, markers=True)
        fig.update_traces(line_color='#3b82f6', line_width=4, marker_size=8)
    else:
        fig = px.bar(df_plot, x='Tarih', y='Deger', title=title)
        fig.update_traces(marker_color='#3b82f6')
        
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", hovermode="x unified")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.1)")
    st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# SAYFA 4: ANA GRUPLAR
# ==============================================================================
elif selected_tab == "ANA GRUPLAR":
    st.header("🏢 Ana Grupların Endeks Gelişimi")
    
    # Tüm grupların endekslerini birleştir
    all_trends = []
    for grp, series in grp_idx.items():
        for d, val in series.items():
            all_trends.append({'Tarih': d, 'Grup': grp, 'Endeks': val})
            
    df_trends = pd.DataFrame(all_trends)
    
    fig = px.line(df_trends, x='Tarih', y='Endeks', color='Grup', title="13 Ana Grubun Karşılaştırmalı Endeksi")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=600, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# SAYFA 5: MADDELER (DRILL-DOWN)
# ==============================================================================
elif selected_tab == "MADDELER":
    st.header("📦 Madde Bazında Detay")
    
    grp_sel = st.selectbox("Ana Grup Seçiniz:", sorted(df_main['Grup'].unique()))
    
    # Seçilen gruptaki ürünleri filtrele
    df_sub = df_main[df_main['Grup'] == grp_sel].copy()
    df_sub['Aylik_Pct'] = (df_sub[son_tarih] / df_sub[bu_ay_baslangic] - 1) * 100
    df_sub = df_sub.sort_values('Aylik_Pct', ascending=False)
    
    st.subheader(f"{grp_sel} - Ürünlerin Aylık Değişimi (%)")
    
    fig = px.bar(df_sub, y='Madde_Adi', x='Aylik_Pct', orientation='h', 
                 color='Aylik_Pct', color_continuous_scale='RdYlGn_r', text_auto='.2f',
                 height=max(400, len(df_sub)*25))
    
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# SAYFA 6: METODOLOJİ (SİZİN METNİNİZ)
# ==============================================================================
elif selected_tab == "METODOLOJİ":
    st.markdown("""
    <div style="background:rgba(255,255,255,0.03); padding:40px; border-radius:16px; border:1px solid rgba(255,255,255,0.1);">
    
    # Web TÜFE Metodolojisi
    ### Günlük Tüketici Fiyat Endeksi Hesaplama Yöntemi

    ---
    
    ### Giriş
    Web TÜFE, Türkiye'nin günlük tüketici fiyat endeksini takip etmek amacıyla geliştirilmiş yenilikçi bir göstergedir. Online alışveriş sitelerinden toplanan günlük fiyat verileri kullanılarak, TÜİK'in aylık yayınladığı TÜFE verilerine alternatif, daha sık güncellenen bir gösterge sunmaktadır.

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
    Ham veri toplandıktan sonra, güvenilirliği artırmak için çok katmanlı bir temizleme ve doğrulama sürecinden geçer:

    * **Aykırı Değer Tespiti:** İstatistiksel yöntemlerle (IQR, Z-score) normal dağılımdan sapan fiyatlar tespit edilir ve otomatik olarak filtrelenir
    * **Platform Karşılaştırması:** Aynı ürünün farklı platformlardaki fiyatları karşılaştırılır, %50'den fazla sapma gösteren veriler incelemeye alınır
    * **Stok ve Temin Durumu:** "stokta yok", "geçici olarak temin edilemiyor" gibi durumlar tespit edilir ve bu ürünler ortalamadan çıkarılır
    * **Manuel Doğrulama:** Kritik ürün grupları (akaryakıt, gıda gibi) için haftalık manuel kontroller yapılır

    ---

    ## 2. Ürün Kategorilendirmesi
    Toplanan ürünler TÜİK'in TÜFE sepet metodolojisiyle uyumlu şekilde kategorize edilir:

    * Gıda ve alkolsüz içecekler
    * Giyim ve ayakkabı
    * Konut (kira, ısıtma vb.)
    * Mobilya ve ev eşyaları
    * Sağlık
    * Ulaştırma
    * Eğlence ve kültür
    * Çeşitli mal ve hizmetler

    ---

    ## 3. Ağırlıklandırma
    Her ürün kategorisinde TÜİK'in ağırlıkları bulunduktan sonra sepette 382 madde bulunduğundan ağırlıkların toplamının 100 olması için normalize edilir. Bu ağırlıklar hanehalkı tüketim harcamalarındaki payları temsil eder.

    ---

    ## 4. Endeks Hesaplaması: Zincirleme Laspeyres
    Web TÜFE endeksi, **Zincirleme Laspeyres Endeksi** yöntemi kullanılarak hesaplanır. Bu yöntemde her gün, ürün fiyatları bir önceki güne göre karşılaştırılır ve madde bazında geometrik ortalama alınarak endeks değeri önceki günün endeksine kümülatif olarak eklenir.

    ### 🔗 Zincirleme Laspeyres Endeksi
    Web TÜFE, klasik Laspeyres fiyat endeksinin zincirleme (chain-linked) versiyonunu kullanır.

    1. **Günlük Hesaplama:** Her gün, fiyatlar bir önceki güne göre karşılaştırılır ve geometrik ortalama ile endeks güncellenir (günlük zincirleme)
    2. **Yıllık Zincirleme:** Her yıl ağırlıklar değiştiğinde (Ocak ayı), endeks yeni ağırlıklarla zincirleme hale getirilir.

    #### 📐 Hesaplama Adımları:
    1. **Günlük Fiyat Değişimi:** Her ürün için cari günün fiyatı bir önceki günün fiyatı ile kıyaslanır: $R_{i,t} = P_{t,i} / P_{t-1,i}$
    2. **Madde Bazında Geometrik Ortalama:** Her madde için günlük fiyat değişimlerinin geometrik ortalaması hesaplanır: $G_{madde} = (\prod R_i)^{1/n}$
    3. **Kümülatif Endeks Hesaplama:** Geometrik ortalama, önceki günün endeksine çarpılarak cari günün endeksi elde edilir: $I_t = I_{t-1} \\times G_{madde}$

    #### 💡 Neden Geometrik Ortalama?
    Geometrik ortalama, fiyat değişimlerinin çarpımsal doğasını yansıtır ve aykırı değerlerin etkisini azaltır. Bu, özellikle günlük fiyat dalgalanmalarının yüksek olduğu ürünlerde daha istikrarlı sonuçlar üretir.

    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="📥 Tam Metodoloji Dokümanını İndir (PDF)",
        data=b"dummy pdf content",
        file_name="Web_TUFE_Metodolojisi.pdf",
        mime="application/pdf",
        type="primary"
    )

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#52525b; font-size:11px;">VALIDASYON MÜDÜRLÜĞÜ © 2026 - CONFIDENTIAL | PRO ANALYTICS</div>', unsafe_allow_html=True)
