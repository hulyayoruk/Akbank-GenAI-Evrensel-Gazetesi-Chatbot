##🗞️ Proje: Evrensel.net Habercisi - RAG Tabanlı Chatbot

Bu proje, Akbank GenAI Bootcamp (GAIH) kapsamında geliştirilmiştir.
Amaç, Evrensel.net haber sitesinin “Son 24 Saat” kategorisindeki güncel içerikleri toplayarak, kullanıcıların bu haberlerle ilgili doğal dilde sorular sorabileceği bir RAG (Retrieval-Augmented Generation) tabanlı chatbot oluşturmaktır.

Chatbot, yalnızca toplanan haber verilerini kullanarak yanıt üretir ve bağlam dışı cevaplardan (halüsinasyonlardan) kaçınır.

##🎯 Projenin Amacı

Kullanıcıya güncel haberler hakkında hızlı, güvenilir ve bağlam temelli bilgi sunan bir sohbet arayüzü geliştirmek.
Model, dış veri kaynaklarına başvurmadan yalnızca topladığı haberleri temel alır.

##🗂️ Veri Seti

Hazır bir veri seti kullanılmamıştır. Veriler, proje içinde geliştirilen bir scraper betiği ile dinamik olarak toplanır.

Kaynak: https://www.evrensel.net/son-24-saat

Toplama Yöntemi: scraper.py, requests ve BeautifulSoup kullanarak haber başlıklarını, bağlantılarını, içeriklerini ve tarihlerini çeker.

Kayıt Formatı: Tüm haberler JSON formatında evrensel_son24saat.json dosyasına kaydedilir.

Ortalama Veri: Yaklaşık 90–100 güncel haber.

##🧠 Mimarinin Genel Yapısı

Proje, LangChain altyapısı üzerinde oluşturulmuş bir RAG (Retrieve + Generate) mimarisi kullanır.

1-Veri Yükleme:
evrensel_son24saat.json, JSONLoader ile içeri aktarılır.

2-Metin Parçalama:
Haber metinleri, RecursiveCharacterTextSplitter ile 1000 karakterlik bölümlere ayrılır.

3-Vektörleştirme (Embedding):

Model: all-MiniLM-L6-v2 (yerel HuggingFace modeli)

Amaç: Google API kota sınırlamalarından bağımsız, yerel embedding süreci

4-Veri Depolama (FAISS):

Vektörler faiss_index klasörüne kaydedilir.

Hızlı “similarity search” desteği sağlar.

5-Sorgu İşleme (Retrieval):

Kullanıcının sorusu FAISS veritabanında en alakalı 3 parça ile eşleştirilir.

6-Cevap Üretimi (Generation):

Model: gemini-flash-latest

Prompt, seçilen 3 bağlamla birleştirilerek modele gönderilir.

7-Arayüz (Frontend):

Framework: Streamlit

Özellikler: Sohbet geçmişi, sade kullanıcı deneyimi

##🚀 Sonuç

Sonuçta, streamlit arayüzü üzerinden çalışan bir haber tabanlı chatbot geliştirilmiştir.
Chatbot yalnızca sağlanan haber verilerini kullanarak cevap üretir, bağlam dışı sorularda “Bu konuda bilgim yok.” şeklinde yanıt verir.

##⚙️ Kurulum ve Çalıştırma

 1-projeyi klonlayın
 ```bash
    git clone [https://github.com/hulyayoruk/Akbank-GenAI-Evrensel-Gazetesi-Chatbot.git](https://github.com/hulyayoruk/Akbank-GenAI-Evrensel-Gazetesi-Chatbot.git)
    cd Akbank-GenAI-Evrensel-Gazetesi-Chatbot
    ```

   
2.  Bir sanal ortam (virtual environment) oluşturun ve aktifleştirin:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  Gerekli tüm kütüphaneleri `requirements.txt` dosyasından yükleyin:
    ```bash
    pip install -r requirements.txt
    ```

4.  **`.env` Dosyası Oluşturun:** Proje ana klasöründe `.env` adında bir dosya oluşturun. İçine, kendi Google Gemini API anahtarınızı aşağıdaki formatta ekleyin:
    ```
    GOOGLE_API_KEY="AIzaSy...SİZİN_ANAHTARINIZ"
    ```

5.  Haber verilerini çekmek için `scraper.py` betiğini çalıştırın (Bu, `evrensel_son24saat.json` dosyasını oluşturur):
    ```bash
    python scraper.py
    ```

6.  Vektör veritabanını oluşturmak için `process_data.py` betiğini çalıştırın (Bu, `faiss_index` klasörünü oluşturur):
    ```bash
    python process_data.py
    ```

7.  Streamlit uygulamasını başlatın. Arayüzde API anahtarı sormayacaktır.
    ```bash
    streamlit run app.py
    ```
##☁️ Streamlit Deploy Bilgisi

Proje, Streamlit Cloud'a deploy edildiğinde, `GOOGLE_API_KEY`'in Streamlit'in "Secrets" bölümüne eklenmesi gerekir.

Sonrasında uygulama bağlantınız aktif olacaktır:
##🔗 https://hulyayoruk-akbank-genai-evrensel-gazetesi-chatbot-app-5cd4ib.streamlit.app/