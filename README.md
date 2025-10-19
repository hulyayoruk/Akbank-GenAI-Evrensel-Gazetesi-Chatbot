# Proje: Evrensel.net Habercisi - RAG Tabanlı Chatbot

GAIH (Akbank GenAI Bootcamp) projesi kapsamında geliştirilmiş, RAG (Retrieval-Augmented Generation) mimarisini kullanan bir haber chatbot'udur.

## 1. Projenin Amacı

Bu projenin amacı, `evrensel.net` haber sitesinin "Son 24 Saat" kategorisindeki güncel haberleri kullanarak, kullanıcıların bu haberler hakkında doğal dilde sorular sormasına olanak tanıyan bir RAG tabanlı chatbot geliştirmektir. Chatbot, sadece sağlanan haber metinlerini (bağlamı) kullanarak cevaplar üretir ve halüsinasyonu en aza indirmeyi hedefler.

## 2. Veri Seti Hakkında Bilgi

Bu proje için hazır bir veri seti kullanılmamıştır. Veri seti, proje gereksinimlerine uygun olarak "toplama/hazırlanış metodolojisi" ile anlık olarak oluşturulmuştur.

* **Veri Kaynağı:** `https://www.evrensel.net/son-24-saat`
* **Toplama Yöntemi:** `scraper.py` betiği, Python'un `requests` ve `BeautifulSoup` kütüphanelerini kullanarak hedef URL'deki haber başlıklarını ve linklerini çeker.
* **İçerik Çıkarımı:** Betik, toplanan her bir haber linkini ziyaret ederek haberin ana metnini (`div.haber-metni`) ve tarihini (`div.tarih-bolumu time`) ayıklar.
* **Sonuç:** Bu işlem sonucunda, o an sitede bulunan (yaklaşık 90-100 adet) haberin başlığı, URL'si, tarihi ve içeriği `evrensel_son24saat.json` dosyasına kaydedilir.

## 3. Kullanılan Yöntemler ve Çözüm Mimarisi

Proje, LangChain kütüphanesi üzerine kurulu bir RAG mimarisi kullanır:

1.  **Veri Yükleme (Load):** `evrensel_son24saat.json` dosyası `JSONLoader` ile okunur.
2.  **Parçalama (Split):** Haber metinleri, `RecursiveCharacterTextSplitter` ile 1000 karakterlik, birbiriyle kesişen parçalara (chunks) ayrılır.
3.  **Vektörleştirme (Embedding):**
    * **Model:** `langchain-huggingface` (`all-MiniLM-L6-v2`)
    * **Süreç:** Tüm metin parçaları, Google API kotalarından kaçınmak için lokal (yerel) bir embedding modeli kullanılarak vektörlere dönüştürülür.
4.  **Depolama (Store):**
    * **Veritabanı:** `FAISS`
    * **Süreç:** Oluşturulan vektörler, hızlı arama (similarity search) yapabilmek için bir `faiss_index` klasörüne kaydedilir.
5.  **Geri Getirme (Retrieve):** Kullanıcının sorusu, `FAISS` veritabanında en ilgili 3 metin parçasını (context) bulmak için kullanılır.
6.  **Üretim (Generate):**
    * **Model:** Google Gemini (`gemini-flash-latest`)
    * **Süreç:** Bulunan 3 metin parçası (context) ve kullanıcının sorusu, bir prompt şablonu ile birleştirilerek cevap üretmesi için Gemini API'ye gönderilir.
7.  **Arayüz:**
    * **Teknolojisi:** `Streamlit`
    * **Özellik:** Sohbet geçmişini destekleyen bir web arayüzü sunar.

## 4. Elde Edilen Sonuçlar

Proje sonucunda, `streamlit` arayüzü üzerinden sunulan, Evrensel gazetesinin güncel haberleri hakkında soruları yanıtlayabilen bir chatbot başarıyla geliştirilmiştir. Chatbot, RAG mimarisi sayesinde sadece sağlanan veriye dayalı cevaplar vermekte ve bağlam dışı sorulduğunda "Bu konuda bilgim yok" diyerek halüsinasyondan kaçınmaktadır.

## 5. Çalışma Kılavuzu (GÜNCELLENDİ)

Projenin yerel makinede çalıştırılabilmesi için gerekenler:

1.  Bu repoyu klonlayın:
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

## 6. Web Arayüzü Linki

Proje, Streamlit Cloud'a deploy edildiğinde, `GOOGLE_API_KEY`'in Streamlit'in "Secrets" bölümüne eklenmesi gerekir.

`[DEPLOY LINKI BURAYA]`