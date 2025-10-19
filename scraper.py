import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import re

# --- 1. BÖLÜM: YAPILANDIRMA (SİZİN GÖNDERDİĞİNİZ KODA GÖRE GÜNCELLENDİ) ---

# Ana sayfa URL'si (linkleri birleştirmek için)
BASE_URL = "https://www.evrensel.net"

# Veri çekeceğimiz hedef sayfa
TARGET_URL = "https://www.evrensel.net/son-24-saat"

# SİTEYE ÖZEL CSS SEÇİCİLERİ (GÜNCELLENDİ)

# 1. "son-24-saat" listesindeki her bir haberin BAŞLIĞINI içeren etiket.
#    Döngü için ana giriş noktamiz bu olacak.
ARTICLE_HEADLINE_SELECTOR = "div.title" 

# 2. Haberin detay sayfasindaki ana içerik metni.
#    (Bunu koruyoruz, muhtemelen doğrudur. Değilse, bir sonraki adimda bunu da "İncele" ile buluruz)
ARTICLE_CONTENT_SELECTOR = "div.haber-metni"

# 3. Haberin detay sayfasindaki tarih bilgisi.
#    (Bunu da koruyoruz)
ARTICLE_DATE_SELECTOR = "div.tarih-bolumu time"


# Sunucuyu yormamak için her istek arasi bekleme süresi (ÇOK ÖNEMLİ)
# robots.txt 'Crawl-delay: 10' istiyor. Buna UYMALISINIZ.
POLITE_WAIT_TIME = 10

# Tarayici taklidi yapmak için User-Agent bilgisi
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- 2. BÖLÜM: YARDIMCI FONKSİYONLAR (Değişiklik yok) ---

def get_article_details(article_url):
    """
    Tek bir haberin URL'sini alir, sayfaya istek atar
    ve haberin başliğini, tarihini, içeriğini döndürür.
    """
    print(f"  -> Detaylar çekiliyor: {article_url}")
    try:
        response = requests.get(article_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"     Hata: Detay sayfasi açilamadi (Kod: {response.status_code})")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # İçerik Metni
        content_element = soup.select_one(ARTICLE_CONTENT_SELECTOR)
        if content_element:
            paragraphs = content_element.find_all('p')
            content = "\n".join([p.get_text(strip=True) for p in paragraphs])
            if not content:
                content = content_element.get_text(strip=True)
        else:
            content = "İçerik Metni Bulunamadi"
            
        # Tarih Bilgisi
        date_element = soup.select_one(ARTICLE_DATE_SELECTOR)
        date_str = date_element.get_text(strip=True) if date_element else "Tarih Bulunamadi"

        return {
            "date": date_str,
            "content": content
        }

    except requests.exceptions.RequestException as e:
        print(f"     Hata: {e}")
        return None
    finally:
        # Sunucuya saygili olmak için her detay isteği sonrasi bekle
        time.sleep(POLITE_WAIT_TIME)


# --- 3. BÖLÜM: ANA SCRAPING İŞLEMİ (GÜNCELLENDİ) ---

def scrape_site():
    """
    Ana scraping fonksiyonu. "son-24-saat" sayfasini çeker ve verileri toplar.
    """
    all_news_data = []
    
    print(f"Scraping işlemi başliyor. Hedef: {TARGET_URL}")

    try:
        # 1. Liste Sayfasini Çek (Sadece 1 kez)
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"  Hata: Ana sayfa ({TARGET_URL}) açilamadi (Kod: {response.status_code}). Durduruluyor.")
            return

        soup = BeautifulSoup(response.content, 'html.parser')

        # 2. Liste Sayfasindaki Tüm Haber BAŞLIĞI Elementlerini Bul
        headline_elements = soup.select(ARTICLE_HEADLINE_SELECTOR)
        
        if not headline_elements:
            print(f"  Haber başliği bulunamadi (Seçici: {ARTICLE_HEADLINE_SELECTOR}).")
            print(f"  Lütfen {TARGET_URL} adresini 'İncele' ile tekrar kontrol edin.")
            print(f"  'Sayfa Kaynağini Görüntüle' diyerek 'div class=\"title\"' ifadesini aratin.")
            return

        print(f"  {len(headline_elements)} adet haber başliği bulundu.")

        # 3. Her Haber Başliğini İşle
        for headline_element in headline_elements:
            
            # Başliği doğrudan elementten al
            headline = headline_element.get_text(strip=True)
            
            # Linki (href) almak için başliğin "parent" (ebeveyn) elementine (<a> etiketi) git
            link_element = headline_element.find_parent('a')
            
            if link_element:
                href = link_element.get('href')
            else:
                print(f"  Hata: '{headline}' başliği için link (<a>) bulunamadi. Atlaniyor.")
                continue # Link yoksa atla

            # Link tam URL değilse (örn: /gundem/...), BASE_URL ile birleştir
            if href and not href.startswith('http'):
                article_url = BASE_URL + href
            elif href:
                article_url = href
            else:
                print(f"  Hata: '{headline}' başliği için 'href' attribute boş. Atlaniyor.")
                continue 

            # 4. Haberin Detay Sayfasini Çek (Yardimci fonksiyonu kullanarak)
            article_details = get_article_details(article_url)

            if article_details:
                news_item = {
                    "headline": headline,
                    "url": article_url,
                    "date": article_details["date"],
                    "content": article_details["content"]
                }
                all_news_data.append(news_item)
        
        print(f"\nİşlem tamamlandi. Toplam {len(all_news_data)} haber çekildi.")

    except requests.exceptions.RequestException as e:
        print(f"  Ana sayfayi çekerken hata: {e}.")
    
    # 5. Tüm Verileri JSON Dosyasina Kaydet
    if all_news_data:
        output_filename = 'evrensel_son24saat.json'
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_news_data, f, ensure_ascii=False, indent=4)
        print(f"\nİşlem tamamlandi. {len(all_news_data)} haber '{output_filename}' dosyasina kaydedildi.")
    else:
        print("\nİşlem tamamlandi ancak hiç veri çekilemedi. Lütfen CSS seçicilerinizi (1. Bölüm) kontrol edin.")

# --- 4. BÖLÜM: BETİĞİ ÇALIŞTIR (Değişiklik yok) ---

if __name__ == "__main__":
    scrape_site()