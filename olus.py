import requests
from bs4 import BeautifulSoup
import os
import re

LOG_DOSYASI = "paylasilanlar.txt"

def hafiza_olustur():
    print("🧹 Eski bağışçılar hafızaya alınıyor (Mail gönderilmeyecek)...")
    islenenler = set()
    
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for sayfa_no in range(1, 40): # 550+ bağışçı için 40 sayfa yeterli
        print(f"📄 Sayfa {sayfa_no} taranıyor...")
        url = f"https://bagis.sakaryaspor.org.tr/bagiscilarimiz?page={sayfa_no}"
        
        try:
            response = session.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            bagis_satirlari = soup.find_all('div', class_=re.compile(r'grid|flex'))
            
            if not bagis_satirlari: break

            for satir in bagis_satirlari:
                isim_div = satir.find('div', class_='col-span-5')
                if isim_div:
                    isim = isim_div.get_text(strip=True)
                    if isim and "Bağışçı" not in isim:
                        islenenler.add(isim)
        except:
            break

    # Tüm isimleri tek seferde dosyaya yaz
    with open(LOG_DOSYASI, "w", encoding="utf-8") as f:
        for isim in islenenler:
            f.write(isim + "\n")
    
    print(f"✅ Toplam {len(islenenler)} bağışçı hafızaya alındı. Artık temiz bir sayfa açıldı.")

if __name__ == "__main__":
    hafiza_olustur()
