import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import os
import re

# --- YOLLAR ---
SABLON_YOLU = r"C:\Users\user\Desktop\sablon.png"
CIKTI_KLASORU = r"C:\Users\user\Desktoptesekkur_postlari"

def font_bul():
    """Sistemdeki Sancreek font dosyasını farklı konumlarda arar."""
    kullanici_adi = os.getlogin()
    olasi_yollar = [
        r"C:\Windows\Fonts\Sancreek-Regular.ttf",
        r"C:\Windows\Fonts\Sancreek.ttf",
        f"C:\\Users\\{kullanici_adi}\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Sancreek-Regular.ttf",
        f"C:\\Users\\{kullanici_adi}\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Sancreek.ttf",
        r"C:\Users\LENOVO\Desktop\Sancreek-Regular.ttf"
    ]
    
    for yol in olasi_yollar:
        if os.path.exists(yol):
            return yol
    return None

def renk_getir(rozet_metni):
    # Sitedeki rozet isimlerine göre renk kodları
    renkler = {
        "Nefer": (76, 175, 80), "Bronz": (205, 127, 50), "Gümüş": (192, 192, 192),
        "Altın": (255, 215, 0), "Platin": (229, 228, 226), "Safir": (15, 82, 186),
        "Zümrüt": (0, 168, 107), "Siyah Elmas": (60, 60, 60), "1965 Efsane": (255, 165, 0)
    }
    for anahtar, deger in renkler.items():
        if anahtar.lower() in rozet_metni.lower():
            return deger
    return (255, 255, 255)

def post_hazirla(isim, kategori):
    try:
        img = Image.open(SABLON_YOLU).convert("RGB")
        draw = ImageDraw.Draw(img)
        
        # Font Ayarı: 37.6 punto yaklaşık 50 piksele denk gelir
        font_yolu = font_bul()
        font_boyutu = 85 
        
        if font_yolu:
            font = ImageFont.truetype(font_yolu, font_boyutu)
        else:
            print(f"⚠️ Sancreek font dosyası bulunamadı, Arial Bold ile devam ediliyor.")
            font = ImageFont.truetype("arialbd.ttf", font_boyutu)

        yazi_rengi = renk_getir(kategori)
        img_genislik = img.size[0]
        y_koordinati = 594 # Yeni Paint görselindeki koordinatın

        # Metni Ortala
        left, top, right, bottom = draw.textbbox((0, 0), isim, font=font)
        w = right - left
        x_koordinati = (img_genislik - w) / 2
        
        draw.text((x_koordinati, y_koordinati), isim, fill=yazi_rengi, font=font)
        
        if not os.path.exists(CIKTI_KLASORU):
            os.makedirs(CIKTI_KLASORU)
            
        dosya_adi = "".join([c for c in isim if c.isalnum() or c in (' ', '_')]).strip().replace(' ', '_')
        img.save(os.path.join(CIKTI_KLASORU, f"{dosya_adi}.png"))
        print(f"✅ Görsel Hazırlandı: {isim} ({kategori})")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

def verileri_cek_ve_baslat():
    print("Bağışçılar ve rozetler taranıyor...")
    url = "https://bagis.sakaryaspor.org.tr/bagiscilarimiz"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # HTML içindeki rozetleri (Gümüş, Bronz vb.) ve isimleri bulur
        bagis_satirlari = soup.find_all('div', class_=re.compile(r'grid|flex')) 
        anahtar_kelimeler = ["Nefer", "Bronz", "Gümüş", "Altın", "Platin", "Safir", "Zümrüt", "Siyah Elmas", "1965 Efsane"]
        
        count = 0
        for satir in bagis_satirlari:
            if count >= 5: break
            isim_div = satir.find('div', class_='col-span-5')
            if isim_div:
                isim = isim_div.get_text(strip=True)
                if not isim or "Bağışçı" in isim: continue
                
                satir_metni = satir.get_text(" ", strip=True)
                bulunan_rozet = "Nefer"
                for anahtar in anahtar_kelimeler:
                    if anahtar in satir_metni:
                        bulunan_rozet = anahtar
                        break
                post_hazirla(isim, bulunan_rozet)
                count += 1
    except Exception as e:
        print(f"Bağlantı Hatası: {e}")

if __name__ == "__main__":
    verileri_cek_ve_baslat()
