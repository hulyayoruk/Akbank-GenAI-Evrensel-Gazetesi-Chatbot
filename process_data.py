import os
import json

# LangChain kütüphanelerini içe aktar
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import JSONLoader
# DİKKAT: 0.1.x sürümüne döndüğümüz için import yolu değişti
from langchain_community.embeddings import HuggingFaceEmbeddings 

# --- 1. API Anahtari Ayarlama (ARTIK GEREKLİ DEĞİL) ---
print("Lokal embedding modeli kullanilacak, API anahtari gerekmiyor.")

# --- 2. Veri Yükleme (JSON) ---
JSON_FILE_PATH = 'evrensel_son24saat.json'
JSON_LOADER_SCHEMA = '.[] | {"page_content": .content, "metadata": {"source": .url, "title": .headline, "date": .date}}'

print(f"'{JSON_FILE_PATH}' dosyasi yükleniyor...")
try:
    loader = JSONLoader(
        file_path=JSON_FILE_PATH,
        jq_schema=JSON_LOADER_SCHEMA,
        text_content=False
    )
    data = loader.load()
    if not data:
        print("JSON dosyasindan hiç doküman yüklenemedi. Dosya boş veya şema yanliş olabilir.")
        exit()
    print(f"Başariyla {len(data)} adet haber dokümani yüklendi.")
except Exception as e:
    print(f"JSON dosyasi yüklenirken hata oluştu: {e}")
    exit()

# --- 3. Metinleri Parçalama (Chunking) ---
print("Metinler parçalara (chunks) ayriliyor...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
documents = text_splitter.split_documents(data)
print(f"Toplam {len(documents)} adet metin parçasi (chunk) oluşturuldu.")

# --- 4. Embedding Modeli ve Vektör Veritabani (GÜNCELLENDİ) ---
print("Lokal Embedding modeli (HuggingFace) yükleniyor...")
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)
print("FAISS vektör veritabani oluşturuluyor ve veriler yükleniyor...")
try:
    vector_db = FAISS.from_documents(documents, embeddings)
    DB_SAVE_PATH = "faiss_index"
    vector_db.save_local(DB_SAVE_PATH)
    print("\nİşlem tamamlandi!")
    print(f"Vektör veritabani başariyla '{DB_SAVE_PATH}' klasörüne kaydedildi.")
except Exception as e:
    print(f"Vektör veritabani oluşturulurken bir hata oluştu: {e}")