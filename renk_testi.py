from PIL import Image, ImageDraw, ImageFont

# --- BURAYI DEĞİŞTİREREK DENE ---
TEST_ISIM = "SAKARYASPOR"
DENEME_RGB = (0, 255, 132) # Nefer Yeşili
# ------------------------------

try:
    img = Image.open("sablon.png").convert("RGB")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Sancreek-Regular.ttf", 60)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), TEST_ISIM, font=font)
    x = (img.size[0] - (bbox[2] - bbox[0])) / 2
    y = 594

    draw.text((x+2, y+2), TEST_ISIM, fill=(0, 0, 0), font=font)
    draw.text((x, y), TEST_ISIM, fill=DENEME_RGB, font=font)

    img.save("deneme_sonuc.png")
    print("Görsel başarıyla oluşturuldu.")
except Exception as e:
    print(f"Hata: {e}")
