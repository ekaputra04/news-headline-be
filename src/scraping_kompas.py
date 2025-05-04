import requests
from bs4 import BeautifulSoup
import re

# URL target
url = input("Masukkan URL berita: ")

# Header untuk menghindari pemblokiran bot
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

# Kirim permintaan HTTP
response = requests.get(url, headers=headers)

# Cek status berhasil
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Ambil judul dari tag <title> sebagai nama file
    raw_title = soup.title.string if soup.title else 'kompas_berita'
    clean_title = re.sub(r'[\\/*?:"<>|]', '', raw_title).strip()

    # Cari konten utama artikel
    content_div = soup.find("div", class_="read__content")

    if content_div:
        # Bersihkan tag yang tidak diperlukan tetapi simpan teksnya
        for tag in content_div.find_all(["iframe", "span", "div", "strong", "a"]):
            tag.unwrap()

        # Ambil semua teks dari tag <p>
        paragraphs = content_div.find_all("p")
        clean_text = []

        for p in paragraphs:
            text = p.get_text(strip=True)

            # Hapus kalimat yang diawali dengan "Baca juga:"
            if not text.lower().startswith("baca juga:"):
                # Juga hapus frasa "Baca juga: ..." di dalam kalimat jika ada
                text = re.sub(r'Baca juga:[^\n\.!?]*[\.!?]?', '', text, flags=re.IGNORECASE)
                if text:
                    clean_text.append(text)

        final_text = "\n\n".join(clean_text)

        # Simpan ke file .txt
        filename = f"{clean_title}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_text)

        print(f"Teks berita berhasil disimpan dalam file: {filename}")
    else:
        print("Konten artikel tidak ditemukan.")
else:
    print(f"Gagal mengambil halaman. Status code: {response.status_code}")
