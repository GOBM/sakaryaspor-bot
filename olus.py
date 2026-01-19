import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import os
import re
import smtplib
from email.message import EmailMessage
import sys

# --- GITHUB SECRETS'DAN GELEN BILGILER ---
MAIL_ADRESI = os.getenv("MAIL_ADRESI")
MAIL_SIFRESI = os.getenv("MAIL_SIFRESI")
ALICI_MAIL = os.getenv("ALICI_MAIL")

# --- AYARLAR (GitHub Sunucuları İçin Kesin Çözüm) ---
LOG_DOSYASI = "paylasilanlar.txt"
SABLON_YOLU = "sablon.png"
FONT_YOLU = "Sancreek-Regular.ttf"

def mail_gonder(gorsel_yolu, isim):
    try:
        msg = EmailMessage()
        msg['Subject'] = f'Yeni Sakaryaspor Bağışçısı: {isim}'
        msg['From'] = MAIL_ADRESI
        msg['To'] = ALICI_MAIL
        msg.set_content(f'Yeni bağışçı için görsel oluşturuldu: {isim}\n\nEkten görseli indirip paylaşabilirsiniz.')

        with open(gorsel_yolu, 'rb') as f:
            file_data = f.read()
            msg.add_attachment(file_data, maintype='image', subtype='png', filename=f'{isim}.png')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(MAIL_ADRESI, MAIL_SIFRESI)
            smtp.send_message(msg)
        print(f"📧 Mail başarıyla gönderildi: {isim}")
    except Exception as e:
        print(f"❌ Mail gönderme hatası: {e}")

def renk_getir(rozet_metni):
    renkler = {
        "Nefer": (76, 175, 80), "Bronz": (205, 127, 50), "Gümüş": (192, 192, 192),
        "Altın": (255, 215, 0), "Platin": (229, 228, 226), "Safir": (15, 82, 186),
        "Zümrüt": (0, 168, 107), "Siyah Elmas": (60, 60, 60), "1965 Efsane": (255, 165, 0)
    }
    for anahtar, deger in renkler.items():
        if anahtar.lower() in rozet_metni.lower(): return deger
    return (255, 255, 255)

def denetle():
    print("🔍 Yeni bağışçılar kontrol ediliyor...")
    
    # paylasilanlar.txt dosyasını kontrol et
    if os.path.exists(LOG_DOSYASI):
        with open(LOG_DOSYASI, "r", encoding="utf-8") as f:
            islenenler = f.read().splitlines()
    else:
        islenenler = []

    url = "https://bagis.sakaryaspor.org.tr/bagiscilarimiz"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        bagis_satirlari = soup.find_all('div', class_=re.compile(r'grid|flex'))
        
        found_new = False
        for satir in bagis_satirlari:
            isim_div = satir.find('div', class_='col-span-5')
            if isim_div:
                isim = isim_div.get_text(strip=True)
                if not isim or "Bağışçı" in isim or isim in islenenler: 
                    continue
                
                print(f"✅ Yeni bağışçı bulundu: {isim}")
                found_new = True
                satir_metni = satir.get_text(" ", strip=True)
                rozet = "Nefer"
                for anahtar in ["Bronz", "Gümüş", "Altın", "Platin", "Safir", "Zümrüt", "Siyah Elmas", "1965 Efsane"]:
                    if anahtar in satir_metni: rozet = anahtar; break
                
                # --- GÖRSEL OLUŞTURMA ---
                try:
                    # Dosya var mı kontrolü
                    if not os.path.exists(SABLON_YOLU):
                        print(f"❌ HATA: {SABLON_YOLU} bulunamadı!")
                        continue

                    img = Image.open(SABLON_YOLU).convert("RGB")
                    draw = ImageDraw.Draw(img)
                    
                    try:
                        font = ImageFont.truetype(FONT_YOLU, 50)
                    except:
                        print("⚠️ Font yüklenemedi, varsayılan kullanılıyor.")
                        font = ImageFont.load_default()
                        
                    bbox = draw.textbbox((0, 0), isim, font=font)
                    draw.text(((img.size[0] - (bbox[2]-bbox[0])) / 2, 594), isim, fill=renk_getir(rozet), font=font)
                    
                    kayit_adi = f"{re.sub(r'[^\w\s-]', '', isim).strip()}.png"
                    img.save(kayit_adi)
                    
                    # Mail Gönder
                    mail_gonder(kayit_adi, isim)
                    
                    with open(LOG_DOSYASI, "a", encoding="utf-8") as f:
                        f.write(isim + "\n")
                    
                    break # Şimdilik sadece en sonuncuyu alıyoruz
                except Exception as e:
                    print(f"❌ Görsel oluşturma hatası ({isim}): {e}")

        if not found_new:
            print("ℹ️ Yeni bağışçı yok.")

    except Exception as e:
        print(f"❌ Site tarama hatası: {e}")

if __name__ == "__main__":
    denetle()
