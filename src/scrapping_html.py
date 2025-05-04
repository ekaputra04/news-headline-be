import requests
from bs4 import BeautifulSoup
import re

# URL target
url = 'https://www.detik.com/jateng/bisnis/d-7898444/harga-emas-hari-ini-di-semarang-4-mei-2025-mulai-dari-rp-995-ribu-ini-detailnya'

# Header untuk menghindari blokir bot
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

# Mengirim request
response = requests.get(url, headers=headers)

# Cek status
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Ambil judul dari tag <title>
    raw_title = soup.title.string if soup.title else 'detik_berita'
    
    # Bersihkan judul agar valid sebagai nama file
    clean_title = re.sub(r'[\\/*?:"<>|]', '', raw_title).strip()
    
    # Simpan ke file
    filename = f"{clean_title}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    
    print(f"HTML berhasil disimpan dalam file: {filename}")
else:
    print(f"Gagal mengambil halaman. Status code: {response.status_code}")
