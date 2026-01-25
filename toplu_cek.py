import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import os, re

SABLON_YOLU = "sablon.png"
FONT_YOLU = "Sancreek-Regular.ttf"
CIKTI_KLASORU = "sertifikalar"

if not os.path.exists(CIKTI_KLASORU):
    os.makedirs(CIKTI_KLASORU)

def renk_getir(rozet_metni):
    renkler = {
        "Nefer": (0, 255, 132), "Bronz": (205, 127, 50), "Gümüş": (192, 192, 192),
        "Altın": (255, 215, 0), "Platin": (229, 228, 226), "Safir": (15, 82, 186),
        "Zümrüt": (4, 121, 89), "Siyah Elmas": (40, 40, 40), "1965 Efsane": (255, 165, 0)
    }
    for anahtar, deger in renkler.items():
        if anahtar.lower() in rozet_metni.lower(): return deger
    return (255, 255, 255)

def denetle():
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}
    sekmeler = ["https://bagis.sakaryaspor.org.tr/bagiscilarimiz", "https://bagis.sakaryaspor.org.tr/bagiscilarimiz?tab=corporate"]

    for base_url in sekmeler:
        sayfa_no = 1
        while True:
            url = f"{base_url}&page={sayfa_no}" if "?" in base_url else f"{base_url}?page={sayfa_no}"
            response = session.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            bagis_satirlari = soup.find_all('div', class_=re.compile(r'grid|flex'))
            gecerli_satirlar = [s for s in bagis_satirlari if s.find('div', class_='col-span-5')]
            
            if not gecerli_satirlar: break
            print(f"Sayfa {sayfa_no} işleniyor...")

            for satir in gecerli_satirlar:
                isim = satir.find('div', class_='col-span-5').get_text(strip=True)
                if not isim or "Bağışçı" in isim: continue
                
                satir_metni = satir.get_text(" ", strip=True)
                rozet = "Nefer"
                for anahtar in ["Bronz", "Gümüş", "Altın", "Platin", "Safir", "Zümrüt", "Siyah Elmas", "1965 Efsane"]:
                    if anahtar in satir_metni: rozet = anahtar; break
                
                img = Image.open(SABLON_YOLU).convert("RGB")
                draw = ImageDraw.Draw(img)
                font = ImageFont.truetype(FONT_YOLU, 50)
                
                bbox = draw.textbbox((0, 0), isim, font=font)
                x = (img.size[0] - (bbox[2] - bbox[0])) / 2
                draw.text((x+2, 594+2), isim, fill=(0, 0, 0), font=font)
                draw.text((x, 594), isim, fill=renk_getir(rozet), font=font)
                
                temiz_isim = re.sub(r'[^\w\s-]', '', isim).strip()
                img.save(f"{CIKTI_KLASORU}/{temiz_isim}.png")
            sayfa_no += 1

if __name__ == "__main__":
    denetle()
