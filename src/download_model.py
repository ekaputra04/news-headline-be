from transformers import BertTokenizer, BertModel, GPT2Config
import os

# Path relatif ke folder 'news-headline-be' di direktori yang sama dengan skrip ini
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Pastikan folder tujuan ada
os.makedirs(BASE_DIR, exist_ok=True)

# 1. Download dan simpan Tokenizer
print("Mengunduh tokenizer...")
tokenizer = BertTokenizer.from_pretrained("cahya/bert2gpt-indonesian-summarization")
tokenizer.save_pretrained(os.path.join(BASE_DIR, "bert2gpt_tokenizer"))

# 2. Download dan simpan Encoder BERT
print("Mengunduh model encoder BERT...")
bert_model = BertModel.from_pretrained("cahya/bert-base-indonesian-1.5G")
bert_model.save_pretrained(os.path.join(BASE_DIR, "bert_encoder"))

# 3. Download dan simpan Config Decoder GPT2
print("Mengunduh konfigurasi decoder GPT2...")
gpt2_config = GPT2Config.from_pretrained("cahya/gpt2-small-indonesian-522M", add_cross_attention=True)
gpt2_config.save_pretrained(os.path.join(BASE_DIR, "gpt2_config"))

print("Semua model telah berhasil disimpan ke folder lokal:")
print(BASE_DIR)
