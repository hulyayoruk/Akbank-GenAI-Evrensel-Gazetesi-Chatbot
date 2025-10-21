🗞️ Proje: Evrensel.net Habercisi - RAG Tabanlı Chatbot

Bu proje, Akbank GenAI Bootcamp (GAIH) kapsamında geliştirilmiştir. Projenin amacı, Evrensel.net haber sitesinin “Son 24 Saat” kategorisindeki güncel içerikleri toplayarak, kullanıcıların bu haberlerle ilgili doğal dilde sorular sorabileceği bir RAG (Retrieval-Augmented Generation) tabanlı chatbot oluşturmaktır.

Chatbot, harici bilgi kaynaklarına başvurmadan, yalnızca toplanan haber verilerini kullanarak yanıt üretir ve bağlam dışı cevaplardan (halüsinasyonlardan) kaçınarak güvenilir bilgi sunmayı hedefler.

🗂️ Veri Seti ve Metodoloji

Bu proje için hazır bir veri seti kullanılmamıştır. Veri seti, proje içinde geliştirilen bir scraper betiği ile dinamik olarak toplanmıştır.

Veri Kaynağı: https://www.evrensel.net/son-24-saat

Toplama Yöntemi: scraper.py betiği, Python'un requests ve newspaper3k kütüphanelerini kullanarak hedef URL'deki haber başlıklarını, bağlantılarını, içeriklerini ve tarihlerini çeker.

Kayıt Formatı: Toplanan tüm haberler, JSON formatında evrensel_son24saat.json dosyasına kaydedilir.

Ortalama Veri Miktarı: Her çalıştırmada yaklaşık 90–140 arası güncel haber makalesi toplanır.

🧠 Çözüm Mimarisi ve Kullanılan Teknolojiler

Proje, LangChain altyapısı üzerinde oluşturulmuş bir RAG (Retrieve + Generate) mimarisi kullanır.

Veri Yükleme (Load): evrensel_son24saat.json dosyası, JSONLoader ile LangChain dokümanlarına dönüştürülür.

Metin Parçalama (Split): Haber metinleri (Başlık + İçerik), RecursiveCharacterTextSplitter ile anlamsal bütünlüğü koruyacak şekilde ~1000 karakterlik bölümlere (chunks) ayrılır.

Vektörleştirme (Embedding):

Model: all-MiniLM-L6-v2 (Lokal Hugging Face modeli)

Amaç: Google API kota sınırlamalarından bağımsız, tamamen yerel ve ücretsiz bir embedding süreci sağlamak.

Veri Depolama (Store):

Veritabanı: FAISS

Süreç: Oluşturulan vektörler, hızlı "similarity search" (anlamsal arama) yapabilmek için faiss_index klasörüne kaydedilir.

Sorgu İşleme (Retrieve):

Süreç: Kullanıcının sorusu, FAISS veritabanında anlamsal olarak en alakalı 7 metin parçası ile eşleştirilir.

Cevap Üretimi (Generate):

Model: Google Gemini (gemini-flash-latest)

Süreç: Bulunan 7 metin parçası (context) ve kullanıcının sorusu, bir sistem prompt'u ile birleştirilerek nihai cevabı üretmesi için Gemini API'ye gönderilir.

Arayüz (Frontend):

Framework: Streamlit

Özellikler: Sohbet geçmişini destekleyen, sade ve kullanıcı dostu bir web arayüzü sunar.

🚀 Elde Edilen Sonuçlar

Proje sonucunda, Streamlit arayüzü üzerinden sunulan, Evrensel gazetesinin güncel haberleri hakkında soruları yanıtlayabilen bir chatbot başarıyla geliştirilmiştir. Chatbot, RAG mimarisi sayesinde yalnızca sağlanan haber verilerini kullanarak cevap üretir, cevabının sonunda kullandığı kaynakları belirtir ve bağlam dışı sorularda “Bu konuda bilgim yok.” şeklinde yanıt vererek halüsinasyondan kaçınır.

💻 Kurulum ve Yerel Çalıştırma Kılavuzu

Projeyi Klonlayın:

git clone [https://github.com/hulyayoruk/Akbank-GenAI-Evrensel-Gazetesi-Chatbot.git](https://github.com/hulyayoruk/Akbank-GenAI-Evrensel-Gazetesi-Chatbot.git)
cd Akbank-GenAI-Evrensel-Gazetesi-Chatbot


Sanal Ortamı Oluşturun ve Aktifleştirin:

python -m venv venv
.\venv\Scripts\activate


Gerekli Kütüphaneleri Yükleyin:

pip install -r requirements.txt


.env Dosyası Oluşturun: Proje ana klasöründe .env adında bir dosya oluşturun. İçine, kendi Google Gemini API anahtarınızı aşağıdaki formatta ekleyin:

GOOGLE_API_KEY="AIzaSy...SİZİN_ANAHTARINIZ"


Veri Toplama ve İşleme: Sırasıyla aşağıdaki komutları çalıştırarak haber verilerini çekin ve vektör veritabanını oluşturun.

python scraper.py
python process_data.py


Uygulamayı Başlatın:

streamlit run app.py


🌐 Web Arayüzü ve Product Kılavuzu

Uygulamanın Streamlit Cloud'a deploy edilmiş, çalışan haline aşağıdaki linkten ulaşılabilir.

🔗 https://hulyayoruk-akbank-genai-evrensel-gazetesi-chatbot-app-5cd4ib.streamlit.app/
