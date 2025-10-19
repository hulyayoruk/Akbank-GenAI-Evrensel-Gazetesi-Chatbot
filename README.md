# Proje: Evrensel.net Habercisi - RAG Tabanlı Chatbot

[cite_start]GAIH (Akbank GenAI Bootcamp) projesi [cite: 1] [cite_start]kapsamında geliştirilmiş, RAG (Retrieval-Augmented Generation) [cite: 2] mimarisini kullanan bir haber chatbot'udur.

## 1. Projenin Amacı

[cite_start]Bu projenin amacı [cite: 9][cite_start], `evrensel.net` haber sitesinin "Son 24 Saat" kategorisindeki güncel haberleri kullanarak, kullanıcıların bu haberler hakkında doğal dilde sorular sormasına olanak tanıyan bir RAG tabanlı chatbot [cite: 2] geliştirmektir. Chatbot, sadece sağlanan haber metinlerini (bağlamı) kullanarak cevaplar üretir ve halüsinasyonu en aza indirmeyi hedefler.

## 2. Veri Seti Hakkında Bilgi

[cite_start]Bu proje için hazır bir veri seti kullanılmamıştır[cite: 17]. [cite_start]Veri seti, proje gereksinimlerine uygun olarak "toplama/hazırlanış metodolojisi" [cite: 17] ile anlık olarak oluşturulmuştur.

* **Veri Kaynağı:** `https://www.evrensel.net/son-24-saat`
* **Toplama Yöntemi:** `scraper.py` betiği, Python'un `requests` ve `BeautifulSoup` kütüphanelerini kullanarak hedef URL'deki haber başlıklarını ve linklerini çeker.
* **İçerik Çıkarımı:** Betik, toplanan her bir haber linkini ziyaret ederek haberin ana metnini (`div.haber-metni`) ve tarihini (`div.tarih-bolumu time`) ayıklar.
* [cite_start]**Sonuç:** Bu işlem sonucunda, o an sitede bulunan (yaklaşık 90-100 adet) haberin başlığı, URL'si, tarihi ve içeriği `evrensel_son24saat.json` dosyasına kaydedilir[cite: 10].

## 3. Kullanılan Yöntemler ve Çözüm Mimarisi

[cite_start]Proje, LangChain kütüphanesi [cite: 44] [cite_start]üzerine kurulu bir RAG mimarisi [cite: 23] kullanır:

1.  **Veri Yükleme (Load):** `evrensel_son24saat.json` dosyası `JSONLoader` ile okunur.
2.  **Parçalama (Split):** Haber metinleri, `RecursiveCharacterTextSplitter` ile 1000 karakterlik, birbiriyle kesişen parçalara (chunks) ayrılır.
3.  **Vektörleştirme (Embedding):**
    * [cite_start]**Model:** `langchain-huggingface` (`all-MiniLM-L6-v2`) [cite: 43]
    * **Süreç:** Tüm metin parçaları, Google API kotalarından kaçınmak için lokal (yerel) bir embedding modeli kullanılarak vektörlere dönüştürülür.
4.  **Depolama (Store):**
    * [cite_start]**Veritabanı:** `FAISS` [cite: 43]
    * **Süreç:** Oluşturulan vektörler, hızlı arama (similarity search) yapabilmek için bir `faiss_index` klasörüne kaydedilir.
5.  **Geri Getirme (Retrieve):** Kullanıcının sorusu, `FAISS` veritabanında en ilgili 3 metin parçasını (context) bulmak için kullanılır.
6.  **Üretim (Generate):**
    * [cite_start]**Model:** Google Gemini (`gemini-flash-latest`) [cite: 42]
    * **Süreç:** Bulunan 3 metin parçası (context) ve kullanıcının sorusu, bir prompt şablonu ile birleştirilerek cevap üretmesi için Gemini API'ye gönderilir.
7.  **Arayüz:**
    * **Teknoloji:** `Streamlit`
    * [cite_start]**Özellik:** Sohbet geçmişini destekleyen bir web arayüzü sunar[cite: 2, 25].

## 4. Elde Edilen Sonuçlar

[cite_start]Proje sonucunda, `streamlit` arayüzü üzerinden sunulan, Evrensel gazetesinin güncel haberleri hakkında soruları yanıtlayabilen bir chatbot başarıyla geliştirilmiştir[cite: 12]. Chatbot, RAG mimarisi sayesinde sadece sağlanan veriye dayalı cevaplar vermekte ve bağlam dışı sorulduğunda "Bu konuda bilgim yok" diyerek halüsinasyondan kaçınmaktadır.

## 5. Çalışma Kılavuzu

[cite_start]Projenin yerel makinede çalıştırılabilmesi için gerekenler[cite: 20]:

1.  Bu repoyu klonlayın:
    ```bash
    git clone [REPO_URL]
    cd [REPO_ADI]
    ```

2.  [cite_start]Bir sanal ortam (virtual environment) oluşturun ve aktifleştirin[cite: 21]:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  [cite_start]Gerekli tüm kütüphaneleri `requirements.txt` dosyasından yükleyin[cite: 21]:
    ```bash
    pip install -r requirements.txt
    ```

4.  Haber verilerini çekmek için `scraper.py` betiğini çalıştırın (Bu, `evrensel_son24saat.json` dosyasını oluşturur):
    ```bash
    python scraper.py
    ```

5.  Vektör veritabanını oluşturmak için `process_data.py` betiğini çalıştırın (Bu, `faiss_index` klasörünü oluşturur):
    ```bash
    python process_data.py
    ```

6.  [cite_start]Streamlit uygulamasını başlatın[cite: 21]:
    ```bash
    streamlit run app.py
    ```

7.  [cite_start]Açılan web arayüzünde, sol taraftaki bölüme Google Gemini API anahtarınızı girerek chatbot'u kullanmaya başlayın[cite: 25].

## 6. Web Arayüzü Linki

[cite_start]Proje, Streamlit Cloud'a deploy edildikten sonra web linki buraya eklenecektir[cite: 13, 25].

`[DEPLOY LINKI BURAYA]`