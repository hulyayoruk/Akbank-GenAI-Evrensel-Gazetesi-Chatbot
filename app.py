import os
import streamlit as st
from dotenv import load_dotenv # .env dosyasn okumak için

# --- YENİ: .env dosyasn yükle ---
# Bu satr, projenin başndaki .env dosyasn arar ve içindeki değişkenleri yükler.
load_dotenv()

# LangChain kütüphanelerini içe aktar
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings # 0.2.x+ sürümü için doğru import
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- 1. Model ve Veritaban Yükleme Fonksiyonlar ---

@st.cache_resource
def load_models_and_db():
    """
    Lokal embedding modelini ve FAISS veritabann yükler.
    """
    print("Lokal embedding modeli yükleniyor...")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    print("FAISS veritaban yükleniyor...")
    db_path = "faiss_index"
    vector_db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vector_db.as_retriever(search_kwargs={'k': 3})
    if not os.path.exists(db_path):
        st.error(f"HATA: 'faiss_index' klasörü bulunamad. Lütfen önce 'process_data.py' betiğini çalştrn.")
        return None, None
        
    
    
    print("Modeller ve veritaban yüklendi.")
    return retriever

@st.cache_resource
def load_llm(google_api_key):
    """
    Gemini LLM modelini yükler.
    """
    print("Gemini LLM yükleniyor...")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest", # GitHub'da bulduğunuz doğru model ad
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
    Sana verilen bağlam (context) kullanarak kullanc sorusunu cevapla.
    Bağlam, Evrensel gazetesinden alnan haber metinleridir.
    Cevabn sadece sana verilen bağlamdaki bilgilere dayanmaldr.
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
st.markdown("Evrensel gazetesinin 'Son 24 Saat' haberleri hakknda sorular sorun.")
st.markdown("---")

# --- YENİ: API ANAHTARINI .env DOSYASINDAN OKUMA ---
# Arayüzden istemek yerine, .env dosyasndan yüklenen anahtar alyoruz.
google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    st.error("HATA: Google API Anahtar bulunamad!")
    st.error("Lütfen proje ana klasöründe '.env' adnda bir dosya oluşturun ve içine 'GOOGLE_API_KEY=\"AIza...\"' şeklinde anahtarnz ekleyin.")
    st.stop() # Anahtar yoksa uygulamay durdur

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
    if prompt := st.chat_input("Haberler hakknda bir soru sorun..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                with st.spinner("Haberler aranyor ve cevap oluşturuluyor..."):
                    response = rag_chain.invoke(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                if "429" in str(e) and "quota" in str(e).lower():
                    st.error("HATA: Google API kotanz (Gemini) aştnz. Lütfen daha sonra tekrar deneyin veya plannz kontrol edin.")
                else:
                    st.error(f"Cevap alnrken bir hata oluştu: {e}")
else:
    st.error("Uygulama başlatlamad. Lütfen 'faiss_index' klasörünün olduğundan ve API anahtarnzn doğru olduğundan emin olun.")