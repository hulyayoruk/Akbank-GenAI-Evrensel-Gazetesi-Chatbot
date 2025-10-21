from datetime import datetime
import subprocess
import os
import streamlit as st
from dotenv import load_dotenv

st.sidebar.title("🔧 Veri Güncelleme")
# Güncelleme butonu
if st.sidebar.button("🔄 Haberleri Güncelle"):
    with st.spinner("Haberler güncelleniyor... Lütfen bekleyin ⏳"):
        try:
            # scraper.py ve process_data.py'yi çalıştır
            subprocess.run(["python", "scraper.py"], check=True)
            subprocess.run(["python", "process_data.py"], check=True)

            # Son güncelleme zamanını yaz
            now = datetime.now().strftime("%d.%m.%Y %H:%M")
            with open("last_update.txt", "w", encoding="utf-8") as f:
                f.write(now)

            st.success(f"✅ Güncelleme tamamlandı ({now})")
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Güncelleme sırasında hata oluştu: {e}")

# Son güncelleme zamanını göster
if os.path.exists("last_update.txt"):
    with open("last_update.txt", "r", encoding="utf-8") as f:
        last_update = f.read().strip()
else:
    last_update = "Henüz güncelleme yapılmadı."

st.sidebar.markdown(f"🕒 **Son güncelleme:** {last_update}")

load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

# --- 1. Model ve Veritabanı Yükleme Fonksiyonları ---

@st.cache_resource
def load_models_and_db():
    print("Lokal embedding modeli yükleniyor...")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    print("FAISS veritabanı yükleniyor...")
    db_path = "faiss_index"
    if not os.path.exists(db_path):
        st.error(f"HATA: 'faiss_index' klasörü bulunamadı.")
        return None
        
    vector_db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    
    # --- YENİ VE GÜÇLENDİRİLMİŞ RETRIEVER ---
    # Arama sonuç sayısını 3'ten 7'ye çıkararak ilgili haberi bulma olasılığını artırıyoruz.
    retriever = vector_db.as_retriever(search_type="mmr", search_kwargs={'k': 10, 'fetch_k': 30})

    
    print("Modeller ve veritabanı yüklendi.")
    return retriever

@st.cache_resource
def load_llm(google_api_key):
    print("Gemini LLM yükleniyor...")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=google_api_key,
            temperature=0.3
        )
        return llm
    except Exception as e:
        st.error(f"Gemini modeli yüklenirken hata oluştu: {e}")
        return None

# --- 2. RAG Pipeline (Zincir) Oluşturma (GÜNCELLENDİ) ---

def create_rag_chain(retriever, llm):
    system_prompt = (
        "Sen Evrensel gazetesinin haberleri hakkında bilgi veren bir asistansın. "
        "Kullanıcı sorusunu anlamaya çalış ve sadece bağlamda (context) geçen haberleri temel alarak cevap ver. "
        "Bağlamdaki bilgiyi anlam olarak da değerlendir, yani isim, olay veya kişi eşleşmelerini semantik olarak ara. "
        "Cevabın sonunda kullandığın haberlerin kaynak linklerini 'Kaynak:' başlığı altında listele. "
        "Bağlamda hiçbir bilgi yoksa 'Bu konuda bilgim yok.' de."
    )

    human_prompt = (
        "Bağlam (Context):\n{context}\n\n"
        "Soru (Question):\n{question}"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", human_prompt),
        ]
    )
    
    def format_docs(docs):
        formatted_strings = []
        for doc in docs:
            source = doc.metadata.get('source', 'Kaynak Bulunamadı')
            formatted_strings.append(f"Kaynak: {source}\n{doc.page_content}")
        return "\n\n---\n\n".join(formatted_strings)

    # --- YENİ VE DOĞRU ZİNCİR YAPISI ---
    # Bu yeni yapı, hem cevabı (answer) hem de kaynakları (sources) paralel olarak çalıştırır.
    
    # Sadece cevap üretmek için kullanılan ana zincir
    answer_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Cevap zincirini ve kaynakları getiren zinciri birleştiren son yapı
    rag_chain = RunnableParallel(
        answer=answer_chain,
        sources=retriever,
    )

    return rag_chain

# --- 3. Streamlit Arayüzü ---

st.set_page_config(page_title="Evrensel Haber Chatbot", layout="wide")
st.title("📰 Evrensel Gazetesi RAG Chatbot")
st.markdown("Evrensel gazetesinin 'Son 24 Saat' haberleri hakkında sorular sorun.")
st.markdown("---")

google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    st.error("HATA: Google API Anahtarı bulunamadı!")
    st.stop()

retriever = load_models_and_db()
llm = load_llm(google_api_key)

if retriever and llm:
    # Değişken adını basitleştirelim.
    rag_chain = create_rag_chain(retriever, llm)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Haberler hakkında bir soru sorun..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                with st.spinner("Haberler aranıyor ve cevap oluşturuluyor..."):
                    # Zincir artık bir sözlük döndürüyor: {'answer': ..., 'sources': ...}
                    response = rag_chain.invoke(prompt)
                
                # Cevabı ve debug bilgisini ekrana yazdır
                answer = response['answer']
                sources = response['sources']
                
                st.markdown(answer)
                
                
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Cevap alınırken bir hata oluştu: {e}")
else:
    st.error("Uygulama başlatılamadı.")

