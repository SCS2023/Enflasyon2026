# GEREKLİ KÜTÜPHANELER:
# pip install streamlit streamlit-option-menu pandas plotly matplotlib requests xlsxwriter python-docx

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import requests
from io import BytesIO
import base64
import time

# --- 1. AYARLAR VE TEMA ---
st.set_page_config(
    page_title="Piyasa Monitörü | Pro Analytics",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="collapsed"
)

# --- CSS MOTORU (GLASSMORPHISM & NAVIGASYON) ---
def apply_theme():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        
        :root {
            --bg-deep: #0f172a;
            --glass-bg: rgba(30, 41, 59, 0.7);
            --glass-border: rgba(255, 255, 255, 0.08);
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
            --accent: #3b82f6;
            --success: #10b981;
            --danger: #ef4444;
        }

        /* Ana Arkaplan */
        [data-testid="stAppViewContainer"] {
            background-color: var(--bg-deep);
            background-image: 
                radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
        }

        /* Navigasyon Bar Stili */
        .nav-container {
            display: flex;
            justify-content: center;
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--glass-border);
            padding: 10px 20px;
            position: sticky;
            top: 0;
            z-index: 999;
            margin-top: -60px; /* Streamlit header'ı gizlemek için */
            border-radius: 0 0 16px 16px;
        }
        
        div[data-testid="stHorizontalBlock"] button {
            background-color: transparent;
            border: 1px solid transparent;
            color: var(--text-dim);
            font-weight: 600;
            transition: all 0.3s;
            border-radius: 8px;
        }
        
        div[data-testid="stHorizontalBlock"] button:hover {
            background-color: rgba(255,255,255,0.05);
            color: #fff;
        }

        div[data-testid="stHorizontalBlock"] button:focus  {
            background-color: rgba(59, 130, 246, 0.2);
            border-color: var(--accent);
            color: #fff;
        }

        /* Kartlar */
        .info-card {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
            margin-bottom: 20px;
        }

        /* Tablolar */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--glass-border);
            border-radius: 10px;
            overflow: hidden;
        }

        h1, h2, h3 { color: #fff !important; font-weight: 800; letter-spacing: -0.5px; }
        
        .big-kpi { font-size: 32px; font-weight: 800; color: #fff; }
        .sub-kpi { font-size: 12px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; }
        .diff-pos { color: var(--success); font-weight: 600; font-size: 14px; }
        .diff-neg { color: var(--danger); font-weight: 600; font-size: 14px; }

        /* PDF Button Style */
        .pdf-btn {
            display: inline-flex; align-items: center; justify-content: center;
            background: #ef4444; color: white; padding: 10px 20px;
            border-radius: 8px; text-decoration: none; font-weight: 600;
            margin-top: 10px; transition: transform 0.2s;
        }
        .pdf-btn:hover { transform: scale(1.02); }

    </style>
    """, unsafe_allow_html=True)

apply_theme()

# --- 2. VERİ YÖNETİMİ (MOCKUP & GERÇEK KARIŞIK) ---
# Not: Gerçek GitHub entegrasyonu önceki kodunuzda vardı, 
# burada arayüzü oluşturmak için yapıyı kuruyorum. 
# "df_analiz" hesaplanmış ana veri setimizdir.

@st.cache_data
def get_mock_data():
    # Bu fonksiyon normalde GitHub'dan veriyi çekecek ve hesaplayacak.
    # Şimdilik UI'ı göstermek için dummy veri üretiyorum.
    
    dates = pd.date_range(start="2026-02-01", end="2026-02-08")
    groups = ["Gıda ve Alkolsüz İçecekler", "Giyim ve Ayakkabı", "Konut", "Ulaştırma", "Sağlık", "Eğlence ve Kültür", "Lokanta ve Oteller"]
    
    data = []
    base_price = 100
    
    for g in groups:
        for d in dates:
            daily_change = np.random.normal(0.001, 0.005) # Rastgele günlük değişim
            price = base_price * (1 + daily_change)
            
            # Alt ürünler (Her grup için 5 tane)
            for i in range(1, 6):
                item_name = f"{g} - Ürün {i}"
                item_price = price * (1 + np.random.normal(0, 0.02))
                data.append({
                    "Tarih": d,
                    "Grup": g,
                    "Madde": item_name,
                    "Fiyat": item_price,
                    "Agirlik": np.random.randint(1, 10)
                })
    
    df = pd.DataFrame(data)
    
    # Değişim Hesaplama
    df['Onceki_Fiyat'] = df.groupby('Madde')['Fiyat'].shift(1)
    df['Gunluk_Degisim'] = (df['Fiyat'] / df['Onceki_Fiyat']) - 1
    
    # Şubat başı fiyatı (Aylık değişim için baz)
    feb_start = df[df['Tarih'] == "2026-02-01"].set_index('Madde')['Fiyat'].to_dict()
    df['Aylik_Degisim'] = df.apply(lambda x: (x['Fiyat'] / feb_start.get(x['Madde'], x['Fiyat'])) - 1, axis=1)
    
    # Yıllık Değişim (Simülasyon)
    df['Yillik_Degisim'] = df['Aylik_Degisim'] + 0.35 # %35 baz enflasyon ekle
    
    return df

df_full = get_mock_data()
last_date = df_full['Tarih'].max()
df_today = df_full[df_full['Tarih'] == last_date].copy()

# --- 3. HESAPLAMA & YARDIMCI FONKSİYONLAR ---
def calculate_kpi(df):
    # Ağırlıklı Ortalama Değişimler
    total_w = df['Agirlik'].sum()
    monthly = (df['Aylik_Degisim'] * df['Agirlik']).sum() / total_w
    yearly = (df['Yillik_Degisim'] * df['Agirlik']).sum() / total_w
    daily = (df['Gunluk_Degisim'] * df['Agirlik']).sum() / total_w
    return monthly * 100, yearly * 100, daily * 100

monthly_cpi, yearly_cpi, daily_cpi = calculate_kpi(df_today)

# --- 4. NAVIGASYON ---
# Basit bir tab yapısı yerine "Sayfa" hissi veren bir yapı
menu = ["ANA SAYFA", "AĞIRLIKLAR", "TÜFE", "ANA GRUPLAR", "MADDELER", "METODOLOJİ"]
st.markdown('<div style="margin-bottom: 20px;"></div>', unsafe_allow_html=True)
selected_tab = st.radio("", menu, horizontal=True, label_visibility="collapsed")
st.markdown("---")

# --- 5. SAYFA İÇERİKLERİ ---

# ==========================================
# 1. ANA SAYFA
# ==========================================
if selected_tab == "ANA SAYFA":
    st.markdown(f"### 📅 Son Güncellenme Tarihi: {last_date.strftime('%d.%m.%Y')}")
    st.info("ℹ️ Nihai veriler her ayın 24.günü belli olmaktadır.")

    # KPI WIDGET ALANI
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="info-card">
            <div class="sub-kpi">YILLIK ENFLASYON</div>
            <div class="big-kpi">%{yearly_cpi:.2f}</div>
            <div class="diff-neg">▲ Yüksek Seyir</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        diff_color = "diff-neg" if monthly_cpi > 0 else "diff-pos"
        arrow = "▲" if monthly_cpi > 0 else "▼"
        st.markdown(f"""
        <div class="info-card">
            <div class="sub-kpi">AYLIK ENFLASYON (ŞUBAT)</div>
            <div class="big-kpi">%{monthly_cpi:.2f}</div>
            <div class="{diff_color}">{arrow} Önceki Güne Göre</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="info-card">
            <div class="sub-kpi">GÜNLÜK DEĞİŞİM</div>
            <div class="big-kpi">%{daily_cpi:.2f}</div>
            <div style="color:#aaa; font-size:14px;">Anlık Piyasa Nabzı</div>
        </div>
        """, unsafe_allow_html=True)

    # BÜLTEN KISMI
    col_bulten, col_grafik = st.columns([1, 2])
    with col_bulten:
        st.markdown("""
        <div class="info-card" style="height: 100%;">
            <h3 style="color:#3b82f6 !important;">📢 Ocak Bülteni Yayında</h3>
            <p>Piyasa Monitörü Ocak ayında %5,09 artış gösterdi.</p>
            <a href="#" class="pdf-btn">📄 Bültene Git</a>
            <br><br>
            <a href="#" style="color:#94a3b8; font-size:12px;">Aylık Değişim Oranları Nasıl Hesaplanır?</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col_grafik:
        # Mini bir trend grafiği
        daily_trend = df_full.groupby("Tarih").apply(lambda x: (x['Gunluk_Degisim'] * x['Agirlik']).sum() / x['Agirlik'].sum() * 100).reset_index(name='Degisim')
        fig_mini = px.bar(daily_trend, x='Tarih', y='Degisim', title="Günlük Piyasa Trendi", color='Degisim', color_continuous_scale="RdYlGn_r")
        fig_mini.update_layout(height=200, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#fff")
        st.plotly_chart(fig_mini, use_container_width=True)

    # ANA GRUP TABLOSU
    st.subheader("📊 Piyasa Monitörü Şubat Ayı Ana Grup Artış Oranları")
    
    # Grup bazlı özet hesapla
    group_stats = df_today.groupby("Grup").apply(
        lambda x: pd.Series({
            "Aylık %": (x['Aylik_Degisim'] * x['Agirlik']).sum() / x['Agirlik'].sum() * 100,
            "Yıllık %": (x['Yillik_Degisim'] * x['Agirlik']).sum() / x['Agirlik'].sum() * 100
        })
    ).reset_index().sort_values("Aylık %", ascending=False)
    
    st.dataframe(
        group_stats.style.format({"Aylık %": "{:.2f}%", "Yıllık %": "{:.2f}%"})
        .background_gradient(subset=["Aylık %"], cmap="Reds"),
        use_container_width=True,
        hide_index=True
    )

    # EN ÇOK ARTANLAR / AZALANLAR
    c_inc, c_dec = st.columns(2)
    with c_inc:
        st.subheader("🔥 En Çok Artanlar (Aylık)")
        top_inc = df_today.sort_values("Aylik_Degisim", ascending=False).head(5)[["Madde", "Grup", "Aylik_Degisim"]]
        top_inc["Aylik_Degisim"] = top_inc["Aylik_Degisim"] * 100
        st.dataframe(top_inc.style.format({"Aylik_Degisim": "%{:.2f}"}), hide_index=True, use_container_width=True)
        
    with c_dec:
        st.subheader("❄️ En Çok Düşenler (Aylık)")
        top_dec = df_today.sort_values("Aylik_Degisim", ascending=True).head(5)[["Madde", "Grup", "Aylik_Degisim"]]
        top_dec["Aylik_Degisim"] = top_dec["Aylik_Degisim"] * 100
        st.dataframe(top_dec.style.format({"Aylik_Degisim": "%{:.2f}"}), hide_index=True, use_container_width=True)


# ==========================================
# 2. AĞIRLIKLAR
# ==========================================
elif selected_tab == "AĞIRLIKLAR":
    st.header("⚖️ Sepet Ağırlıkları")
    st.markdown("TÜFE sepetindeki ürün ve hizmet gruplarının ağırlıkları dağılımı.")
    
    # Sunburst Chart
    fig_sun = px.sunburst(
        df_today, 
        path=['Grup', 'Madde'], 
        values='Agirlik',
        color='Grup',
        title="Enflasyon Sepeti Ağırlık Dağılımı (2026)"
    )
    fig_sun.update_layout(height=700, paper_bgcolor="rgba(0,0,0,0)", font_color="#fff")
    st.plotly_chart(fig_sun, use_container_width=True)
    
    with st.expander("Ağırlık Tablosunu Görüntüle"):
        w_table = df_today.groupby("Grup")['Agirlik'].sum().reset_index().sort_values("Agirlik", ascending=False)
        w_table['Oran'] = (w_table['Agirlik'] / w_table['Agirlik'].sum()) * 100
        st.table(w_table)

# ==========================================
# 3. TÜFE (GENEL ANALİZ)
# ==========================================
elif selected_tab == "TÜFE":
    st.header("📈 TÜFE Detay Analizi")
    
    # Seçim Kutusu
    options = ["GENEL TÜFE"] + list(df_full['Madde'].unique())
    selection = st.selectbox("Madde veya Endeks Seçin:", options)
    
    # Grafik Türü
    chart_type = st.radio("Grafik Türü:", ["Çizgi (Line)", "Sütun (Bar)"], horizontal=True)
    
    if selection == "GENEL TÜFE":
        # Genel Endeks Hesabı (Günlük)
        daily_idx = df_full.groupby("Tarih").apply(
            lambda x: (x['Fiyat'] * x['Agirlik']).sum() / x['Agirlik'].sum()
        ).reset_index(name='Deger')
        # Normalize (Başlangıç 100)
        daily_idx['Endeks'] = daily_idx['Deger'] / daily_idx['Deger'].iloc[0] * 100
        plot_data = daily_idx
        y_col = 'Endeks'
        title = "Genel TÜFE Endeks Seyri"
    else:
        plot_data = df_full[df_full['Madde'] == selection]
        y_col = 'Fiyat'
        title = f"{selection} Fiyat Seyri"

    if chart_type == "Çizgi (Line)":
        fig = px.line(plot_data, x='Tarih', y=y_col, title=title, markers=True)
    else:
        fig = px.bar(plot_data, x='Tarih', y=y_col, title=title)
        
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    
    # Neon Efekti
    fig.update_traces(line_color='#3b82f6', line_width=4)
    st.plotly_chart(fig, use_container_width=True)
    
    # İstatistikler
    if selection != "GENEL TÜFE":
        curr = plot_data.iloc[-1][y_col]
        prev = plot_data.iloc[0][y_col]
        degisim = ((curr/prev)-1)*100
        st.metric(label="Dönem İçi Değişim", value=f"{curr:.2f} TL", delta=f"%{degisim:.2f}")

# ==========================================
# 4. ANA GRUPLAR
# ==========================================
elif selected_tab == "ANA GRUPLAR":
    st.header("🏢 Ana Harcama Grupları Performansı")
    
    # Ana grupların zaman içindeki değişimi
    group_trend = df_full.groupby(["Tarih", "Grup"]).apply(
        lambda x: (x['Fiyat'] * x['Agirlik']).sum() / x['Agirlik'].sum()
    ).reset_index(name='Fiyat_Endeks')
    
    # Her grubu kendi içinde normalize et (Başlangıç=100)
    group_trend['Endeks'] = group_trend.groupby('Grup')['Fiyat_Endeks'].transform(lambda x: x / x.iloc[0] * 100)
    
    fig_groups = px.line(group_trend, x='Tarih', y='Endeks', color='Grup', title="Ana Grupların Karşılaştırmalı Endeks Gelişimi")
    fig_groups.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=600)
    st.plotly_chart(fig_groups, use_container_width=True)
    
    # Bar Chart (Aylık Değişim Karşılaştırma)
    st.subheader("Bu Ay Hangi Sektör Ne Kadar Arttı?")
    
    # Son günün aylık değişimlerini al
    latest_grp = df_today.groupby("Grup").apply(
        lambda x: (x['Aylik_Degisim'] * x['Agirlik']).sum() / x['Agirlik'].sum() * 100
    ).reset_index(name='Aylik_Degisim').sort_values('Aylik_Degisim', ascending=False)
    
    fig_bar = px.bar(latest_grp, x='Aylik_Degisim', y='Grup', orientation='h', 
                     color='Aylik_Degisim', color_continuous_scale='RdYlGn_r', text_auto='.2f')
    fig_bar.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# 5. MADDELER
# ==========================================
elif selected_tab == "MADDELER":
    st.header("📦 Madde Bazlı Analiz")
    
    selected_group = st.selectbox("Bir Ana Grup Seçiniz:", df_full['Grup'].unique())
    
    # Sadece o grubun ürünlerini filtrele
    filtered_items = df_today[df_today['Grup'] == selected_group].sort_values("Aylik_Degisim", ascending=False)
    filtered_items['Aylik_Yuzde'] = filtered_items['Aylik_Degisim'] * 100
    
    st.subheader(f"{selected_group} İçindeki Ürünlerin Aylık Değişimi")
    
    fig_items = px.bar(
        filtered_items, 
        y='Madde', 
        x='Aylik_Yuzde', 
        orientation='h',
        color='Aylik_Yuzde',
        color_continuous_scale='RdYlGn_r',
        text_auto='.2f',
        title=f"{selected_group} - Ürün Bazlı Performans"
    )
    fig_items.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=max(400, len(filtered_items)*30))
    st.plotly_chart(fig_items, use_container_width=True)

# ==========================================
# 6. METODOLOJİ
# ==========================================
elif selected_tab == "METODOLOJİ":
    # Metni Markdown olarak düzenle
    metodoloji_text = """
    # 📚 Piyasa Monitörü Metodolojisi
    ### Günlük Tüketici Fiyat Endeksi Hesaplama Yöntemi

    ---

    ## Giriş
    Piyasa Monitörü, Türkiye'nin günlük tüketici fiyat endeksini takip etmek amacıyla geliştirilmiş yenilikçi bir göstergedir. Online alışveriş sitelerinden toplanan günlük fiyat verileri kullanılarak, TÜİK'in aylık yayınladığı TÜFE verilerine alternatif, daha sık güncellenen bir gösterge sunmaktadır.

    Geleneksel enflasyon ölçüm yöntemlerinin aylık periyotlarla sınırlı kalması, hızlı değişen ekonomik koşullarda karar alıcıların ve vatandaşların güncel bilgiye erişimini kısıtlamaktadır. Piyasa Monitörü bu boşluğu doldurmak üzere, web scraping teknikleri kullanılarak 2025 yılında başlatılmıştır.

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
    1.  **Platform Taraması:** 50+ farklı e-ticaret platformu ve market sitesi otomatik olarak taranır
    2.  **Ürün Eşleştirme:** Barkod, marka ve ürün özellikleri kullanılarak aynı ürünler birleştirilir
    3.  **Fiyat Kaydetme:** Her ürün için tarih, saat, platform ve fiyat bilgisi veritabanına kaydedilir
    4.  **Anlık İşleme:** Toplanan veriler gerçek zamanlı olarak işlenir ve endeks hesaplamalarına dahil edilir

    #### 🧹 Veri Temizleme ve Kalite Kontrol:
    Ham veri toplandıktan sonra, güvenilirliği artırmak için çok katmanlı bir temizleme ve doğrulama sürecinden geçer:

    * **Aykırı Değer Tespiti:** İstatistiksel yöntemlerle (IQR, Z-score) normal dağılımdan sapan fiyatlar tespit edilir ve otomatik olarak filtrelenir
    * **Platform Karşılaştırması:** Aynı ürünün farklı platformlardaki fiyatları karşılaştırılır, %50'den fazla sapma gösteren veriler incelemeye alınır
    * **Stok Durumu:** "Stokta yok" ürünler ortalamadan çıkarılır
    * **Manuel Doğrulama:** Kritik ürün grupları (akaryakıt, gıda gibi) için haftalık manuel kontroller yapılır

    ---

    ## 2. Ağırlıklandırma
    Her ürün kategorisinde TÜİK'in ağırlıkları bulunduktan sonra sepette 382 madde bulunduğundan ağırlıkların toplamının 100 olması için normalize edilir.

    #### Ana Grup Ağırlıkları (%)
    | Grup | Ağırlık (%) |
    | :--- | :--- |
    | Gıda ve alkolsüz içecekler | **25,78%** |
    | Ulaştırma | **16,49%** |
    | Konut, su, elektrik, gaz | **10,59%** |
    | Lokantalar ve konaklama | **11,05%** |
    | Giyim ve ayakkabı | **8,06%** |
    | ... | ... |

    ---

    ## 3. Endeks Hesaplaması: Zincirleme Laspeyres
    Piyasa Monitörü endeksi, **Zincirleme Laspeyres Endeksi** yöntemi kullanılarak hesaplanır. Bu yöntemde her gün, ürün fiyatları bir önceki güne göre karşılaştırılır ve madde bazında geometrik ortalama alınarak endeks değeri önceki günün endeksine kümülatif olarak eklenir.

    ### 🔗 Zincirleme Yönteminin Mantığı
    Piyasa Monitörü, klasik Laspeyres fiyat endeksinin zincirleme (chain-linked) versiyonunu kullanır.

    1.  **Günlük Hesaplama:** Her gün, fiyatlar bir önceki güne göre karşılaştırılır ve geometrik ortalama ile endeks güncellenir.
    2.  **Yıllık Zincirleme:** Her yıl ağırlıklar değiştiğinde (Ocak ayı), endeks yeni ağırlıklarla zincirleme hale getirilir.

    #### 📐 Hesaplama Formülü (Günlük - Kümülatif)

    **1. Madde Bazında Geometrik Ortalama:**
    $$ G_{madde,t} = (\prod_{i=1}^{n} R_{i,t})^{1/n} $$

    **2. Kümülatif Endeks Hesabı:**
    $$ I_t = I_{t-1} \\times G_{madde,t} $$

    * $I_t$: t gününün endeks değeri
    * $I_{t-1}$: Bir önceki günün endeks değeri
    * $G_{madde,t}$: t günündeki madde bazında geometrik ortalama
    * $R_{i,t}$: i'inci ürünün günlük fiyat değişim oranı ($P_t / P_{t-1}$)

    #### 💡 Neden Geometrik Ortalama?
    Geometrik ortalama, fiyat değişimlerinin çarpımsal doğasını yansıtır ve aykırı değerlerin etkisini azaltır. Bu, özellikle günlük fiyat dalgalanmalarının yüksek olduğu ürünlerde daha istikrarlı sonuçlar üretir.

    ---
    *Pro Analytics - Validasyon Müdürlüğü © 2026*
    """
    
    st.markdown("""
    <div style="background: rgba(255,255,255,0.03); padding: 40px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">
    """, unsafe_allow_html=True)
    st.markdown(metodoloji_text, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # PDF İndirme Butonu (Mock)
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="📥 Tam Metodoloji Dokümanını İndir (PDF)",
        data=b"PDF Content",
        file_name="Web_TUFE_Metodoloji_2026.pdf",
        mime="application/pdf",
        key="pdf-download"
    )

# --- ALT BİLGİ ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center; color:#52525b; font-size:11px; opacity:0.6;">VALIDASYON MÜDÜRLÜĞÜ © 2026 - CONFIDENTIAL | PRO ANALYTICS</div>',
    unsafe_allow_html=True)
