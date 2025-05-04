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
    
    # Ambil konten berita
    content_div = soup.find('div', class_='detail__body itp_bodycontent_wrapper')
    if content_div:
        content_text = content_div.get_text(strip=True, separator=' ')
        # Simpan ke file atau cetak
        print(content_text)
    else:
        print("Konten berita tidak ditemukan.")
else:
    print(f"Gagal mengambil halaman. Status code: {response.status_code}")
