from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import os
import torch
from transformers import (
    BertTokenizer,
    BertModel,
    GPT2LMHeadModel,
    GPT2Config,
    EncoderDecoderModel
)

app = Flask(__name__)

# === Load Model Sekali Saat Startup ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load tokenizer
tokenizer_path = os.path.join(BASE_DIR, "bert2gpt_tokenizer")
tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
tokenizer.bos_token = tokenizer.cls_token
tokenizer.eos_token = tokenizer.sep_token

# Load encoder BERT
bert_path = os.path.join(BASE_DIR, "bert_encoder")
bert_model = BertModel.from_pretrained(bert_path)

# Load config decoder GPT2
gpt2_config_path = os.path.join(BASE_DIR, "gpt2_config")
gpt2_config = GPT2Config.from_pretrained(gpt2_config_path, add_cross_attention=True)

# Inisialisasi GPT2 decoder dan EncoderDecoderModel
gpt2_model = GPT2LMHeadModel(gpt2_config)
model = EncoderDecoderModel(encoder=bert_model, decoder=gpt2_model)

# Load weight dari file lokal
weight_path = os.path.join(BASE_DIR, "model", "bert2gpt_weights_loss_0.0510.pt")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.load_state_dict(torch.load(weight_path, map_location=device))
model.eval()

# === Headers untuk scraping ===
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

def extract_kompas_content(soup):
    content_div = soup.find("div", class_="read__content")
    if not content_div:
        return None, "Konten artikel Kompas tidak ditemukan."

    for tag in content_div.find_all(["iframe", "span", "div", "strong", "a"]):
        tag.unwrap()

    paragraphs = content_div.find_all("p")
    clean_text = []

    for p in paragraphs:
        text = p.get_text(strip=True)
        if not text.lower().startswith("baca juga:"):
            text = re.sub(r'Baca juga:[^\n\.!?]*[\.!?]?', '', text, flags=re.IGNORECASE)
            if text:
                clean_text.append(text)

    final_text = " ".join(clean_text)
    return final_text, None

def extract_detik_content(soup):
    content_div = soup.find('div', class_='detail__body itp_bodycontent_wrapper')
    if not content_div:
        return None, "Konten artikel Detik tidak ditemukan."

    content_text = content_div.get_text(strip=True, separator=' ')
    return content_text, None

def summarize(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=1024).to(device)
    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=100,
        min_length=30,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

@app.route('/extract-news', methods=['POST'])
def extract_news():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "Parameter 'url' diperlukan."}), 400

    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    if not (domain.endswith("kompas.com") or domain.endswith("detik.com")):
        return jsonify({"error": "URL tidak valid. Hanya diperbolehkan dari kompas.com atau detik.com"}), 400

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return jsonify({"error": f"Gagal mengambil halaman. Status code: {response.status_code}"}), 400

        soup = BeautifulSoup(response.text, 'html.parser')

        if "kompas.com" in domain:
            content, error = extract_kompas_content(soup)
        elif "detik.com" in domain:
            content, error = extract_detik_content(soup)
        else:
            return jsonify({"error": "Domain tidak dikenali."}), 400

        if error:
            return jsonify({"error": error}), 400

        summary = summarize(content)

        return jsonify({
            "content": content,
            "summary": summary
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
