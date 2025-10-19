import os
import streamlit as st
from getpass import getpass

# LangChain kütüphanelerini içe aktar
from langchain_community.vectorstores import FAISS
# DİKKAT: 0.1.x sürümüne döndüğümüz için import yolu değişti
from langchain_community.embeddings import HuggingFaceEmbeddings 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- 1. Model ve Veritabani Yükleme Fonksiyonlari ---

@st.cache_resource
def load_models_and_db():
    """
    Lokal embedding modelini ve FAISS veritabanini yükler.
    """
    print("Lokal embedding modeli yükleniyor...")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    print("FAISS veritabani yükleniyor...")
    db_path = "faiss_index"
    if not os.path.exists(db_path):
        st.error(f"HATA: 'faiss_index' klasörü bulunamadi. Lütfen önce 'process_data.py' betiğini çaliştirin.")
        return None, None
        
    vector_db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vector_db.as_retriever(search_kwargs={'k': 3})
    
    print("Modeller ve veritabani yüklendi.")
    return retriever

@st.cache_resource
def load_llm(google_api_key):
    """
    Gemini LLM modelini yükler.
    """
    print("Gemini LLM yükleniyor...")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest", # Mentörünüzün önerdiği güncel model
            google_api_key=google_api_key,
            temperature=0.3
        )
        return llm
    except Exception as e:
        st.error(f"Gemini modeli yüklenirken hata oluştu: {e}")
        return None

# --- 2. RAG Pipeline (Zincir) Oluşturma ---
def create_rag_chain(retriever, llm):
    template = """
    Sana verilen bağlami (context) kullanarak kullanici sorusunu cevapla.
    Bağlam, Evrensel gazetesinden alinan haber metinleridir.
    Cevabin sadece sana verilen bağlamdaki bilgilere dayanmalidir.
    Eğer bağlamda cevap yoksa, 'Bu konuda bilgim yok.' de.
    
    Bağlam (Context):
    {context}
    
    Soru (Question):
    {question}
    
    Cevap:
    """
    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain

# --- 3. Streamlit Arayüzü ---

st.set_page_config(page_title="Evrensel Haber Chatbot", layout="wide")
st.title("📰 Evrensel Gazetesi RAG Chatbot")
st.markdown("Evrensel gazetesinin 'Son 24 Saat' haberleri hakkinda sorular sorun.")
st.markdown("---")

# API Anahtarini al (Mentörünüzün deploy tavsiyesine uygun)
with st.sidebar:
    st.header("API Anahtari")
    st.write("Bu uygulama Gemini API kullanir. [Google AI Studio'dan](https://aistudio.google.com/app/apikey) ücretsiz anahtarinizi alabilirsiniz.")
    
    google_api_key = None
    
    try:
        # Streamlit Cloud'a deploy ettiğinizde burasi çalişir
        google_api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("API Anahtari (Secrets) başariyla yüklendi.")
    
    except: 
        # Lokal'de (bilgisayarinizda) çalişirken burasi çalişir
        st.warning("Lütfen API anahtarinizi girin. (Deploy ettiyseniz, Streamlit Cloud > Settings > Secrets bölümüne 'GOOGLE_API_KEY' olarak eklemelisiniz.)")
        google_api_key = st.text_input("Google API Anahtarinizi girin:", type="password")

    if not google_api_key:
        st.error("API anahtari bulunamadi. Lütfen bir anahtar girin.")
        st.stop()

# Ana bileşenleri yükle
retriever = load_models_and_db()
llm = load_llm(google_api_key)

if retriever and llm:
    rag_chain = create_rag_chain(retriever, llm)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Haberler hakkinda bir soru sorun..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                with st.spinner("Haberler araniyor ve cevap oluşturuluyor..."):
                    response = rag_chain.invoke(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                if "429" in str(e) and "quota" in str(e).lower():
                    st.error("HATA: Google API kotanizi (Gemini) aştiniz. Lütfen daha sonra tekrar deneyin veya planinizi kontrol edin.")
                else:
                    st.error(f"Cevap alinirken bir hata oluştu: {e}")
else:
    st.error("Uygulama başlatilamadi. Lütfen 'faiss_index' klasörünün olduğundan ve API anahtarinizin doğru olduğundan emin olun.")