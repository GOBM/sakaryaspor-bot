import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import os
import re
import smtplib
from email.message import EmailMessage

# --- GITHUB SECRETS ---
MAIL_ADRESI = os.getenv("MAIL_ADRESI")
MAIL_SIFRESI = os.getenv("MAIL_SIFRESI")
ALICI_MAIL = os.getenv("ALICI_MAIL")

# --- AYARLAR ---
LOG_DOSYASI = "paylasilanlar.txt"
SABLON_YOLU = "sablon.png"
FONT_YOLU = "Sancreek-Regular.ttf"

def mail_gonder(gorsel_yolu, isim):
    try:
        msg = EmailMessage()
        msg['Subject'] = f'Yeni Sakaryaspor Bağışçısı: {isim}'
        msg['From'] = MAIL_ADRESI
        msg['To'] = ALICI_MAIL
        msg.set_content(f'Yeni bir bağışçı yakalandı: {isim}\n\nGörsel ektedir.')

        with open(gorsel_yolu, 'rb') as f:
            msg.add_attachment(f.read(), maintype='image', subtype='png', filename=os.path.basename(gorsel_yolu))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(MAIL_ADRESI, MAIL_SIFRESI)
            smtp.send_message(msg)
        print(f"📧 Mail gönderildi: {isim}")
    except Exception as e:
        print(f"❌ Mail hatası: {e}")

def renk_getir(rozet_metni):
    renkler = {
        "Nefer": (0, 255, 132),       # Parlak Yeşil
        "Bronz": (205, 127, 50),  
        "Gümüş": (192, 192, 192),
        "Altın": (255, 215, 0),  
        "Platin": (229, 228, 226),  
        "Safir": (15, 82, 186),
        "Zümrüt": (4, 121, 89),       # Koyu Zümrüt Yeşili
        "Siyah Elmas": (40, 40, 40),  
        "1965 Efsane": (255, 165, 0)
    }
    for anahtar, deger in renkler.items():
        if anahtar.lower() in rozet_metni.lower(): return deger
    return (255, 255, 255)

def denetle():
    print("🔍 Bağışçı listesi taranıyor...")
    
    # Tekrar eden isimleri takip etmek için sayaç
    isim_sayaclari = {}
    
    # İşlenenleri küme olarak tut (Zaten paylaşılanları atlamak için)
    if os.path.exists(LOG_DOSYASI):
        with open(LOG_DOSYASI, "r", encoding="utf-8") as f:
            islenenler = set(f.read().splitlines())
    else:
        islenenler = set()

    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    sekmeler = [
        "https://bagis.sakaryaspor.org.tr/bagiscilarimiz", 
        "https://bagis.sakaryaspor.org.tr/bagiscilarimiz?tab=corporate"
    ]

    for base_url in sekmeler:
        sayfa_no = 1
        while True:
            url = f"{base_url}&page={sayfa_no}" if "?" in base_url else f"{base_url}?page={sayfa_no}"
            try:
                response = session.get(url, headers=headers, timeout=15)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                bagis_satirlari = soup.find_all('div', class_=re.compile(r'grid|flex'))
                gecerli_satirlar = [s for s in bagis_satirlari if s.find('div', class_='col-span-5')]

                if not gecerli_satirlar:
                    break

                for satir in gecerli_satirlar:
                    isim_div = satir.find('div', class_='col-span-5')
                    isim = isim_div.get_text(strip=True)
                    
                    # Gizli bağışçıları veya zaten işlenenleri atla
                    if not isim or "Bağışçı" in isim or isim in islenenler:
                        continue
                    
                    # Rozet tespiti
                    satir_metni = satir.get_text(" ", strip=True)
                    rozet = "Nefer"
                    for anahtar in ["Bronz", "Gümüş", "Altın", "Platin", "Safir", "Zümrüt", "Siyah Elmas", "1965 Efsane"]:
                        if anahtar in satir_metni: rozet = anahtar; break
                    
                    # BENZERSİZ DOSYA ADI OLUŞTURMA (Eksik sertifika sorununu çözer)
                    temiz_isim = re.sub(r'[^\w\s-]', '', isim).strip()
                    if temiz_isim in isim_sayaclari:
                        isim_sayaclari[temiz_isim] += 1
                        kayit_adi = f"{temiz_isim}-{isim_sayaclari[temiz_isim]}.png"
                    else:
                        isim_sayaclari[temiz_isim] = 1
                        kayit_adi = f"{temiz_isim}.png"

                    # Görsel Oluşturma
                    img = Image.open(SABLON_YOLU).convert("RGB")
                    draw = ImageDraw.Draw(img)
                    try:
                        font = ImageFont.truetype(FONT_YOLU, 50)
                    except:
                        font = ImageFont.load_default()
                    
                    bbox = draw.textbbox((0, 0), isim, font=font)
                    x = (img.size[0] - (bbox[2] - bbox[0])) / 2
                    
                    # Yazı (Gölge ve Ana Renk)
                    draw.text((x+2, 594+2), isim, fill=(0, 0, 0), font=font)
                    draw.text((x, 594), isim, fill=renk_getir(rozet), font=font)
                    
                    img.save(kayit_adi)
                    mail_gonder(kayit_adi, isim)
                    
                    # Kayıt Defterine Ekle
                    with open(LOG_DOSYASI, "a", encoding="utf-8") as f:
                        f.write(isim + "\n")
                    islenenler.add(isim)
                
                sayfa_no += 1 

            except Exception as e:
                print(f"⚠️ Hata: {e}")
                break

if __name__ == "__main__":
    denetle()
