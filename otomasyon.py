from playwright.sync_api import sync_playwright
import time
from datetime import datetime, timedelta

# BURAYA KENDİ SİTENİZİN LİNKİNİ YAPIŞTIRIN
URL = "https://enflasyon.streamlit.app/" 

def baslat():
    with sync_playwright() as p:
        print("🤖 Sanal asistan uyandırılıyor...")
        browser = p.chromium.launch(headless=True) # Ekransız arka plan tarayıcısı
        page = browser.new_page()
        
        print(f"🌍 {URL} adresine gidiliyor...")
        page.goto(URL, timeout=120000)
        
        # Site uyku modundaysa uyanmasını ve butonun görünmesini bekle (Maks 3 dakika)
        page.wait_for_selector("text=SİSTEMİ SENKRONİZE ET ⚡", timeout=180000)
        
        # --- 1. İŞLEM: TSİ 08:56 / 20:56 ---
        print("⚡ SİSTEMİ SENKRONİZE ET butonuna tıklanıyor...")
        page.locator("text=SİSTEMİ SENKRONİZE ET ⚡").click()
        
        # Senkronizasyonun bitmesini bekle
        print("⏳ Senkronizasyon işlemi bekleniyor...")
        page.wait_for_selector("text=Sistem Senkronize Edildi", timeout=300000)
        print("✅ Senkronizasyon başarıyla bitti!")
        
        # Sayfa otomatik yenilendiği için sistemin oturmasını 5 saniye bekle
        time.sleep(5)
        
        # --- 2. İŞLEM: TAM SAATİ BEKLE (09:00 / 21:00) ---
        print("⏱️ E-Tabloya aktarmak için tam saatin (00) gelmesi bekleniyor...")
        while True:
            simdi = datetime.utcnow() + timedelta(hours=3) # Türkiye Saati
            if simdi.minute == 0: # Dakika tam 00 olduğunda (Yani 09:00 veya 21:00)
                break
            time.sleep(10) # 10 saniyede bir saati kontrol et
            
        print(f"⏰ Saat tam {simdi.strftime('%H:%M')}! E-Tabloya Aktar butonuna tıklanıyor...")
        page.locator("text=📊 Verileri E-Tabloya Aktar").click()
        
        # Aktarımın bitmesini bekle
        page.wait_for_selector("text=Google Sheets başarıyla güncellendi!", timeout=120000)
        print("🎉 Tüm görevler başarıyla tamamlandı. Kapatılıyor...")
        
        browser.close()

if __name__ == "__main__":
    baslat()
