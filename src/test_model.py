import os
import torch
from transformers import (
    BertTokenizer,
    BertModel,
    GPT2LMHeadModel,
    GPT2Config,
    EncoderDecoderModel
)

# Relative path ke direktori project
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load tokenizer dari lokal
tokenizer_path = os.path.join(BASE_DIR, "bert2gpt_tokenizer")
tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
tokenizer.bos_token = tokenizer.cls_token
tokenizer.eos_token = tokenizer.sep_token

# Load encoder (BERT) dari lokal
bert_path = os.path.join(BASE_DIR, "bert_encoder")
bert_model = BertModel.from_pretrained(bert_path)

# Load konfigurasi decoder GPT2 dari lokal
gpt2_config_path = os.path.join(BASE_DIR, "gpt2_config")
gpt2_config = GPT2Config.from_pretrained(gpt2_config_path, add_cross_attention=True)

# Inisialisasi decoder GPT2 dari config
gpt2_model = GPT2LMHeadModel(gpt2_config)

# Gabungkan encoder dan decoder
model = EncoderDecoderModel(encoder=bert_model, decoder=gpt2_model)

# Load weight dari file .pt lokal
weight_path = os.path.join(BASE_DIR,"model", "bert2gpt_weights_loss_0.0510.pt")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.load_state_dict(torch.load(weight_path, map_location=device))

# Contoh teks yang ingin disummarize
sample = """
JAKARTA, KOMPAS.com- Ketua Umum Dewan Pimpinan Nasional Perhimpunan Advokat Indonesia (DPNPERADI) sekaligus Wakil Menteri Koordinator Bidang Hukum, HAM, Imigrasi dan Pemasyarakatan Otto Hasibuan menegaskan bahwa hingga saat ini belum ada pengaduan etik yang masuk terkait advokat Marcella Santoso.
Marcella Santoso ditetapkan sebagai tersangka oleh Kejaksaan Agung (Kejagung) dalam dugaan suap dan gratifikasi vonis lepas (ontslag) perkara ekspor Crude Palm Oil (CPO).
...
"""

# Summarization menggunakan generate
inputs = tokenizer(sample, return_tensors="pt", padding=True, truncation=True, max_length=1024).to(device)
summary_ids = model.generate(
    inputs["input_ids"],
    max_length=100,
    min_length=30,
    length_penalty=2.0,
    num_beams=4,
    early_stopping=True
)
summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
print("Rangkuman:")
print(summary)
