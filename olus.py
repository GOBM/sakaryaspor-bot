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

LOG_DOSYASI = "paylasilanlar.txt"
SABLON_YOLU = "sablon.png"
FONT_YOLU = "Sancreek-Regular.ttf"

def mail_gonder(gorsel_yolu, isim):
    try:
        msg = EmailMessage()
        msg['Subject'] = f'Yeni Sakaryaspor Bağışçısı: {isim}'
        msg['From'] = MAIL_ADRESI
        msg['To'] = ALICI_MAIL
        msg.set_content(f'Yeni bir bağışçı tespit edildi: {isim}')

        with open(gorsel_yolu, 'rb') as f:
            msg.add_attachment(f.read(), maintype='image', subtype='png', filename=f'{isim}.png')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(MAIL_ADRESI, MAIL_SIFRESI)
            smtp.send_message(msg)
        print(f"📧 Mail gönderildi: {isim}")
    except Exception as e:
        print(f"❌ Mail hatası: {e}")

def denetle():
    print("🔍 Yeni bağışçılar taranıyor...")
    if os.path.exists(LOG_DOSYASI):
        with open(LOG_DOSYASI, "r", encoding="utf-8") as f:
            islenenler = set(f.read().splitlines())
    else:
        islenenler = set()

    session = requests.Session()
    # Tek seferde çok fazla mail gelirse diye limit (Opsiyonel)
    gonderilen_bu_tur = 0 

    for sayfa_no in range(1, 11): # Genellikle yeni bağışlar ilk 10 sayfaya düşer
        url = f"https://bagis.sakaryaspor.org.tr/bagiscilarimiz?page={sayfa_no}"
        response = session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        bagis_satirlari = soup.find_all('div', class_=re.compile(r'grid|flex'))
        
        for satir in bagis_satirlari:
            isim_div = satir.find('div', class_='col-span-5')
            if isim_div:
                isim = isim_div.get_text(strip=True)
                if not isim or "Bağışçı" in isim or isim in islenenler:
                    continue
                
                print(f"⭐ YENİ BAĞIŞÇI: {isim}")
                
                # Görsel oluşturma ve mail atma işlemleri buraya gelecek...
                # (Daha önceki mail atma kodlarını buraya ekleyebilirsin)
                
                with open(LOG_DOSYASI, "a", encoding="utf-8") as f:
                    f.write(isim + "\n")
                islenenler.add(isim)
                gonderilen_bu_tur += 1

    if gonderilen_bu_tur == 0:
        print("ℹ️ Yeni bağışçı bulunamadı.")

if __name__ == "__main__":
    denetle()
