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
            msg.add_attachment(f.read(), maintype='image', subtype='png', filename=f'{isim}.png')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(MAIL_ADRESI, MAIL_SIFRESI)
            smtp.send_message(msg)
        print(f"📧 Mail gönderildi: {isim}")
    except Exception as e:
        print(f"❌ Mail hatası: {e}")

def renk_getir(rozet_metni):
    renkler = {
        "Nefer": (0, 255, 132),      # İstediğin yeni parlak yeşil kod (#00ff84)
        "Bronz": (205, 127, 50), 
        "Gümüş": (192, 192, 192),
        "Altın": (255, 215, 0), 
        "Platin": (229, 228, 226), 
        "Safir": (15, 82, 186),
        "Zümrüt": (0, 168, 107), 
        "Siyah Elmas": (60, 60, 60), 
        "1965 Efsane": (255, 165, 0)
    }
    for anahtar, deger in renkler.items():
        if anahtar.lower() in rozet_metni.lower(): return deger
    return (255, 255, 255)

def denetle():
    print("🔍 Tüm bağışçı listesi taranıyor (Sınır yok)...")
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
        sekme_adi = "Kurumsal" if "corporate" in base_url else "Bireysel"
        print(f"\n--- {sekme_adi} Listesi Başlatıldı ---")
        
        sayfa_no = 1
        while True:
            url = f"{base_url}&page={sayfa_no}" if "?" in base_url else f"{base_url}?page={sayfa_no}"
            try:
                response = session.get(url, headers=headers, timeout=15)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                bagis_satirlari = soup.find_all('div', class_=re.compile(r'grid|flex'))
                
                gecerli_satirlar = []
                for s in bagis_satirlari:
                    if s.find('div', class_='col-span-5'):
                        gecerli_satirlar.append(s)

                if not gecerli_satirlar:
                    print(f"✅ {sekme_adi} listesinin sonuna gelindi. (Toplam {sayfa_no-1} sayfa)")
                    break

                print(f"Sayfa {sayfa_no} taranıyor... ({len(gecerli_satirlar)} kişi bulundu)")

                for satir in gecerli_satirlar:
                    isim_div = satir.find('div', class_='col-span-5')
                    isim = isim_div.get_text(strip=True)
                    
                    if not isim or "Bağışçı" in isim or isim in islenenler:
                        continue
                    
                    print(f"⭐ YENİ BAĞIŞÇI: {isim}")
                    
                    satir_metni = satir.get_text(" ", strip=True)
                    rozet = "Nefer"
                    for anahtar in ["Bronz", "Gümüş", "Altın", "Platin", "Safir", "Zümrüt", "Siyah Elmas", "1965 Efsane"]:
                        if anahtar in satir_metni: rozet = anahtar; break
                    
                    # Görsel Oluşturma
                    img = Image.open(SABLON_YOLU).convert("RGB")
                    draw = ImageDraw.Draw(img)
                    try:
                        font = ImageFont.truetype(FONT_YOLU, 50)
                    except:
                        font = ImageFont.load_default()
                    
                    # Yazıyı ortala
                    bbox = draw.textbbox((0, 0), isim, font=font)
                    text_width = bbox[2] - bbox[0]
                    x = (img.size[0] - text_width) / 2
                    y = 594

                    # GÖRÜNÜRLÜK İÇİN GÖLGE EKLEME (Opsiyonel: İstemezsen bu 2 satırı silebilirsin)
                    # Yazının 2 piksel sağına ve altına siyah bir gölge atar
                    draw.text((x+2, y+2), isim, fill=(0, 0, 0), font=font)
                    
                    # Ana Metni Yaz (Yeni Yeşil Renk)
                    draw.text((x, y), isim, fill=renk_getir(rozet), font=font)
                    
                    temiz_isim = re.sub(r'[^\w\s-]', '', isim).strip()
                    kayit_adi = f"{temiz_isim}.png"
                    img.save(kayit_adi)
                    
                    mail_gonder(kayit_adi, isim)
                    
                    with open(LOG_DOSYASI, "a", encoding="utf-8") as f:
                        f.write(isim + "\n")
                    islenenler.add(isim)
                
                sayfa_no += 1 

            except Exception as e:
                print(f"⚠️ Hata oluştu (Sayfa {sayfa_no}): {e}")
                break

if __name__ == "__main__":
    denetle()
