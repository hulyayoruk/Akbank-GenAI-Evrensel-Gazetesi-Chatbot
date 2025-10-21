import os
import json

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import JSONLoader
from langchain_huggingface import HuggingFaceEmbeddings

print("Lokal embedding modeli kullanılacak, API anahtarı gerekmiyor.")

JSON_FILE_PATH = 'evrensel_son24saat.json'

# --- YENİ VE GÜÇLENDİRİLMİŞ ŞEMA ---
# Artık page_content, "Başlık: [başlık]\n\nİçerik: [içerik]" formatında olacak.
# Bu, anlamsal aramanın hem başlığı hem de içeriği dikkate almasını sağlar.
JSON_LOADER_SCHEMA = '.[] | {"page_content": "Başlık: " + .headline + "\n\n" + "İçerik: " + .content, "metadata": {"source": .url, "title": .headline, "date": .date}}'

print(f"'{JSON_FILE_PATH}' dosyası yükleniyor...")

try:
    loader = JSONLoader(
        file_path=JSON_FILE_PATH,
        jq_schema=JSON_LOADER_SCHEMA,
        text_content=False
    )
    data = loader.load()
    if not data:
        print("JSON dosyasından hiç doküman yüklenemedi.")
        exit()
    print(f"Başarıyla {len(data)} adet haber dokümanı yüklendi.")
except Exception as e:
    print(f"JSON dosyası yüklenirken hata oluştu: {e}")
    exit()

print("Metinler parçalara (chunks) ayrılıyor...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
documents = text_splitter.split_documents(data)
print(f"Toplam {len(documents)} adet metin parçası (chunk) oluşturuldu.")

print("Lokal Embedding modeli (HuggingFace) yükleniyor...")
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

print("FAISS vektör veritabanı oluşturuluyor ve veriler yükleniyor...")
try:
    vector_db = FAISS.from_documents(documents, embeddings)
    DB_SAVE_PATH = "faiss_index"
    vector_db.save_local(DB_SAVE_PATH)
    print("\nİşlem tamamlandı!")
    print(f"Vektör veritabanı başarıyla '{DB_SAVE_PATH}' klasörüne kaydedildi.")
except Exception as e:
    print(f"Vektör veritabanı oluşturulurken bir hata oluştu: {e}")
    
import shutil

DB_SAVE_PATH = "faiss_index"
if os.path.exists(DB_SAVE_PATH):
    shutil.rmtree(DB_SAVE_PATH)
