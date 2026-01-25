import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import os
import re
import zipfile

# --- AYARLAR ---
SABLON_YOLU = "sablon.png"
FONT_YOLU = "Sancreek-Regular.ttf"
ZIP_DOSYA_ADI = "Sakaryaspor_Tum_Sertifikalar.zip"
GECICI_KLASOR = "sertifikalar"

def renk_getir(rozet_metni):
    renkler = {
        "Nefer": (76, 175, 80), "Bronz": (205, 127, 50), "Gümüş": (192, 192, 192),
        "Altın": (255, 215, 0), "Platin": (229, 228, 226), "Safir": (15, 82, 186),
        "Zümrüt": (0, 168, 107), "Siyah Elmas": (60, 60, 60), "1965 Efsane": (255, 165, 0)
    }
    for anahtar, deger in renkler.items():
        if anahtar.lower() in rozet_metni.lower(): return deger
    return (255, 255, 255)

def temiz_dosya_adi(isim):
    # Hata veren kisim burada duzeltildi
    return re.sub(r'[^\w\s-]', '', isim).strip() + ".png"

def toplu_islem():
    if not os.path.exists(GECICI_KLASOR): os.makedirs(GECICI_KLASOR)
    print("🚀 Tüm bağışçılar taranıyor...")
    
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}
    sekmeler = [
        "https://bagis.sakaryaspor.org.tr/bagiscilarimiz",
        "https://bagis.sakaryaspor.org.tr/bagiscilarimiz?tab=corporate"
    ]

    with zipfile.ZipFile(ZIP_DOSYA_ADI, 'w') as zipf:
        for base_url in sekmeler:
            for sayfa_no in range(1, 41):
                url = f"{base_url}&page={sayfa_no}" if "?" in base_url else f"{base_url}?page={sayfa_no}"
                try:
                    response = session.get(url, headers=headers, timeout=15)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    bagis_satirlari = soup.find_all('div', class_=re.compile(r'grid|flex'))
                    
                    if not bagis_satirlari or len(bagis_satirlari) < 3: break

                    for satir in bagis_satirlari:
                        isim_div = satir.find('div', class_='col-span-5')
                        if isim_div:
                            isim = isim_div.get_text(strip=True)
                            if not isim or "Bağışçı" in isim: continue
                            
                            img = Image.open(SABLON_YOLU).convert("RGB")
                            draw = ImageDraw.Draw(img)
                            try:
                                font = ImageFont.truetype(FONT_YOLU, 50)
                            except:
                                font = ImageFont.load_default()
                            
                            satir_metni = satir.get_text(" ", strip=True)
                            rozet = "Nefer"
                            for anahtar in ["Bronz", "Gümüş", "Altın", "Platin", "Safir", "Zümrüt", "Siyah Elmas", "1965 Efsane"]:
                                if anahtar in satir_metni: rozet = anahtar; break
                                
                            bbox = draw.textbbox((0, 0), isim, font=font)
                            draw.text(((img.size[0] - (bbox[2]-bbox[0])) / 2, 594), isim, fill=renk_getir(rozet), font=font)
                            
                            dosya_adi = temiz_dosya_adi(isim)
                            dosya_yolu = os.path.join(GECICI_KLASOR, dosya_adi)
                            img.save(dosya_yolu)
                            zipf.write(dosya_yolu, dosya_adi)
                            os.remove(dosya_yolu)
                    print(f"📄 Sayfa {sayfa_no} tamamlandı.")
                except: break
    print(f"✅ Bitti! {ZIP_DOSYA_ADI} hazır.")

if __name__ == "__main__":
    toplu_islem()
