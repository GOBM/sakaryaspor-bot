import requests
from bs4 import BeautifulSoup
import os
import re

# --- AYARLAR ---
# Sonuçlar bu dosyaya kaydedilecek
VERI_DOSYASI = "tum_bagiscilar_listesi.txt"

def tum_veriyi_cek():
    print("🚀 Tüm bağışçı verileri çekiliyor (Bireysel + Kurumsal)...")
    bagis_verileri = []
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # Taratılacak sekmeler
    sekmeler = [
        {"url": "https://bagis.sakaryaspor.org.tr/bagiscilarimiz", "tip": "Bireysel"},
        {"url": "https://bagis.sakaryaspor.org.tr/bagiscilarimiz?tab=corporate", "tip": "Kurumsal"}
    ]

    for sekme in sekmeler:
        print(f"📂 {sekme['tip']} sekmesi taranıyor...")
        # 550+ kişi için yaklaşık 40 sayfa yeterlidir
        for sayfa_no in range(1, 41):
            base_url = sekme['url']
            url = f"{base_url}&page={sayfa_no}" if "?" in base_url else f"{base_url}?page={sayfa_no}"
            
            try:
                response = session.get(url, headers=headers, timeout=15)
                soup = BeautifulSoup(response.text, 'html.parser')
                bagis_satirlari = soup.find_all('div', class_=re.compile(r'grid|flex'))
                
                if not bagis_satirlari or len(bagis_satirlari) < 5:
                    break

                for satir in bagis_satirlari:
                    isim_div = satir.find('div', class_='col-span-5')
                    if isim_div:
                        isim = isim_div.get_text(strip=True)
                        if not isim or "Bağışçı" in isim: continue
                        
                        # Kategori/Renk belirleme
                        satir_metni = satir.get_text(" ", strip=True)
                        kategori = "Nefer"
                        for anahtar in ["Bronz", "Gümüş", "Altın", "Platin", "Safir", "Zümrüt", "Siyah Elmas", "1965 Efsane"]:
                            if anahtar in satir_metni:
                                kategori = anahtar
                                break
                        
                        bagis_verileri.append(f"{isim} | {kategori} | {sekme['tip']}")
                
                print(f"   📄 Sayfa {sayfa_no} tamamlandı.")
            except Exception as e:
                print(f"   ❌ Sayfa {sayfa_no} hatası: {e}")
                break

    # Verileri dosyaya kaydet
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        f.write("İSİM | KATEGORİ | TİP\n")
        f.write("-" * 30 + "\n")
        for veri in bagis_verileri:
            f.write(veri + "\n")
    
    print(f"✅ İşlem tamam! Toplam {len(bagis_verileri)} bağışçı {VERI_DOSYASI} dosyasına kaydedildi.")

if __name__ == "__main__":
    tum_veriyi_cek()
