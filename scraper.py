import requests
from bs4 import BeautifulSoup
import json
import time
from newspaper import Article, ArticleException

# --- 1. BÖLÜM: YAPILANDIRMA ---
BASE_URL = "https://www.evrensel.net"
TARGET_URL = "https://www.evrensel.net/son-24-saat"
ARTICLE_HEADLINE_SELECTOR = "div.title"
POLITE_WAIT_TIME = 10
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- 2. BÖLÜM: YARDIMCI FONKSİYONLAR (HİBRİT YÖNTEM - DÜZELTİLDİ) ---

def get_article_details(article_url):
    """
    requests ile sayfayı indirir ve newspaper ile içeriği akıllıca çeker.
    """
    print(f"  -> Detaylar hibrit yöntemle çekiliyor: {article_url}")
    try:
        # 1. Adım: Sayfayı requests ile güvenilir bir şekilde indir.
        response = requests.get(article_url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"     Hata: Sayfa indirilemedi (Kod: {response.status_code}).")
            return None

        # 2. Adım: Article nesnesini oluştur.
        article = Article(article_url, language='tr')
        
        # 3. Adım: Kendi indirdiğimiz HTML'i newspaper'a vererek download() çağır.
        # Bu, "You must download() first" hatasını çözer.
        article.download(input_html=response.text)
        article.parse()

        # 4. Adım: İçeriği kontrol et.
        if not article.text or len(article.text) < 100:
             print(f"     Uyarı: Newspaper yeterli içerik bulamadı. Bu haber atlanacak.")
             return None

        # Tarihi al ve string formatına çevir (eğer varsa)
        date_str = "Tarih Bulunamadı"
        if article.publish_date:
            date_str = article.publish_date.strftime('%d %B %Y')

        return {"date": date_str, "content": article.text}

    except (requests.exceptions.RequestException, ArticleException) as e:
        print(f"     Hata: URL işlenirken sorun oluştu ({e}). Atlanıyor.")
        return None
    finally:
        # Sunucuya saygılı olmak için her istek sonrası bekle
        time.sleep(POLITE_WAIT_TIME)

# --- 3. BÖLÜM: ANA SCRAPING İŞLEMİ ---

def scrape_site():
    all_news_data = []
    print(f"Scraping işlemi başlıyor. Hedef: {TARGET_URL}")
    try:
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"  Hata: Ana sayfa ({TARGET_URL}) açılamadı. Durduruluyor.")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        headline_elements = soup.select(ARTICLE_HEADLINE_SELECTOR)
        
        if not headline_elements:
            print(f"  Haber başlığı bulunamadı. Seçicinizi kontrol edin.")
            return

        print(f"  {len(headline_elements)} adet haber başlığı bulundu.")
        for headline_element in headline_elements:
            headline = headline_element.get_text(strip=True)
            link_element = headline_element.find_parent('a')
            
            if not link_element or not link_element.get('href'):
                continue

            href = link_element.get('href')
            article_url = BASE_URL + href if not href.startswith('http') else href

            article_details = get_article_details(article_url)

            if article_details and article_details["content"]:
                news_item = {
                    "headline": headline,
                    "url": article_url,
                    "date": article_details["date"],
                    "content": article_details["content"]
                }
                all_news_data.append(news_item)

    except requests.exceptions.RequestException as e:
        print(f"  Ana sayfayı çekerken hata: {e}.")
    
    if all_news_data:
        output_filename = 'evrensel_son24saat.json'
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_news_data, f, ensure_ascii=False, indent=4)
        print(f"\nİşlem tamamlandı. {len(all_news_data)} geçerli haber '{output_filename}' dosyasına kaydedildi.")
    else:
        print("\nİşlem tamamlandı ancak hiç geçerli veri çekilemedi.")

if __name__ == "__main__":
    scrape_site()

