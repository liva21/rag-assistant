import streamlit as st
import requests

# Sayfa Yapısı
st.set_page_config(page_title="Omi: Akademik Analist", layout="wide", page_icon="🎓")

# Özel CSS ile daha akademik bir görünüm
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
    .main {
        background-color: #f4f7f6;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        width: 100%;
        background-color: #2c3e50;
        color: white;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #34495e;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .source-card {
        background-color: #34495e; /* Koyu Mavi/Gri Tonu */
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 5px solid #3498db;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-size: 0.95em;
        line-height: 1.6;
        color: #ecf0f1; /* Açık Gri/Beyaz Yazı */
    }
    .source-meta {
        font-weight: 600;
        color: #bdc3c7; /* Metalik Açık Gri */
        font-size: 0.85em;
        margin-top: 12px;
        display: flex;
        justify-content: space-between;
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 10px;
    }
    .highlight {
        color: #3498db;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 Omi: Akademik Makale Analisti")
st.markdown("*Kurumsal düzeyde akademik araştırma ve döküman analiz asistanı*")
st.markdown("---")

import os
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8003")

# --- SOL PANEL: DÖKÜMAN YÖNETİMİ ---
with st.sidebar:
    st.header("📂 Makale Yükle")
    uploaded_file = st.file_uploader("PDF Formatında Makale", type=["pdf"])
    
    if uploaded_file:
        if st.button("Analize Başla"):
            with st.spinner("Makale vektör uzayına işleniyor..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                try:
                    res = requests.post(f"{BACKEND_URL}/api/upload", files=files)
                    if res.status_code == 200:
                        st.success("✅ Makale hafızaya alındı!")
                        st.session_state['doc_loaded'] = True
                    else:
                        st.error("Yükleme başarısız.")
                except Exception as e:
                    st.error(f"Bağlantı hatası: {e}")
    
    st.markdown("---")
    st.info("💡 **İpucu:** Makalenin metodolojisi, sonuçları veya belirli bir verisi hakkında soru sorabilirsiniz.")

# --- ANA PANEL: SOHBET VE KAYNAKLAR ---
col1, col2 = st.columns([1.8, 1.2])

with col1:
    st.subheader("💬 Analiz Sohbeti")
    question = st.text_input("Makale hakkında ne öğrenmek istiyorsunuz?", placeholder="Örn: Bu çalışmanın temel hipotezi nedir?")
    
    if question and st.session_state.get('doc_loaded'):
        with st.spinner("Literatür taranıyor ve cevap oluşturuluyor..."):
            try:
                payload = {"question": question}
                res = requests.post(f"{BACKEND_URL}/api/query", json=payload)
                
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "")
                    sources = data.get("source_documents", [])
                    
                    # Cevabı Göster
                    st.markdown("### 📝 Analiz Sonucu")
                    st.write(answer)
                    
                    # Kaynakları Sağ Kolona Gönder (Session State ile)
                    st.session_state['last_sources'] = sources
                    
                else:
                    st.error("Backend hatası.")
            except Exception as e:
                st.error(f"Hata: {e}")

# --- SAĞ PANEL: KANITLAR / KAYNAKÇA ---
with col2:
    st.subheader("🔍 Kaynak Kanıtları")
    if 'last_sources' in st.session_state:
        st.markdown(f"Cevap için <span class='highlight'>{len(st.session_state['last_sources'])}</span> farklı kesit incelendi:", unsafe_allow_html=True)
        
        for idx, source in enumerate(st.session_state['last_sources']):
            with st.expander(f"📌 Kanıt {idx+1} — Sayfa {source['page']}", expanded=(idx==0)):
                st.markdown(f"""
                <div class="source-card">
                    {source['content']}
                    <div class="source-meta">
                        <span>📄 Sayfa: {source['page']}</span>
                        <span>📂 {source['source']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.write("Henüz bir sorgu yapılmadı.")
