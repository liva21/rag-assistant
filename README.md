# 🎓 Omi: Akademik Makale Analisti (RAG Assistant)

Omi, PDF formatındaki akademik makaleleri derinlemesine analiz eden ve döküman içeriğine dayalı soruları yanıtlayan gelişmiş bir RAG (Retrieval-Augmented Generation) asistanıdır.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B?style=for-the-badge&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker)

## 🚀 Öne Çıkan Özellikler

- **Gelişmiş LLM Bağlantısı:** Hugging Face **Qwen2.5-7B-Instruct** modeli ile OpenAI uyumlu, düşük gecikmeli çıkarım.
- **Akıllı Geri Çağırma (RAG):** **FAISS** vektör veritabanı ve **Sentence Transformers** (`all-MiniLM-L6-v2`) ile yüksek doğruluklu metin eşleme.
- **Modern Akademik Arayüz:** Streamlit tabanlı, Inter yazı tipiyle optimize edilmiş, kaynak odaklı karanlık mod destekli kullanıcı deneyimi.
- **Kanıt Gösterimi:** Cevabın hangi sayfadan ve hangi bağlamdan alındığını gösteren interaktif "Kaynak Kanıtları" paneli.
- **Dockerize Edilmiş Yapı:** Tek komutla ayağa kalkan frontend ve backend servisleri.

## 🛠️ Teknoloji Yığını

- **Backend:** FastAPI, LangChain, Hugging Face Inference API.
- **Vektör Veritabanı:** FAISS (Facebook AI Similarity Search).
- **Frontend:** Streamlit, Custom CSS/HTML.
- **Model:** Qwen/Qwen2.5-7B-Instruct (LLM) & all-MiniLM-L6-v2 (Embeddings).

## 📥 Kurulum ve Çalıştırma

### Docker ile (Önerilen)

1. Projeyi klonlayın:
   ```bash
   git clone <repo-url>
   cd rag-assistant
   ```

2. `.env` dosyasını oluşturun ve Hugging Face token'ınızı ekleyin:
   ```env
   HUGGINGFACEHUB_API_TOKEN=hf_your_token_here
   ```

3. Docker servislerini başlatın:
   ```bash
   docker-compose up -d
   ```

4. Uygulamaya erişin:
   - **Frontend:** `http://localhost:8503`
   - **Backend API:** `http://localhost:8003`

### Yerel Geliştirme (Docker Olmadan)

```bash
# Sanal ortam oluşturun
python -m venv venv
source venv/bin/activate # Windows için: venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Backend'i başlatın (Port 8003)
uvicorn app.main:app --host 0.0.0.0 --port 8003

# Frontend'i başlatın (Port 8503)
streamlit run frontend/app.py --server.port 8503
```

## 📖 Kullanım Kılavuzu

1. Sol paneldeki **"Makale Yükle"** bölümünden bir PDF dökümanı seçin.
2. **"Analize Başla"** butonuna basın (İlk yüklemede model indirme işlemi nedeniyle 10-20 sn sürebilir).
3. "Analiz Sohbeti" kısmına makale ile ilgili sorularınızı sorun.
4. Sağ paneldeki **"Kaynak Kanıtları"** kutucuklarını genişleterek cevabın döküman içindeki tam yerini doğrulayın.

## 📄 Lisans

Bu proje MIT lisansı ile lisanslanmıştır.

---
*Geliştiren: [Liva Karanfil](https://github.com/Liva21)*
# rag-assistant görseli


<img width="2992" height="1654" alt="image" src="https://github.com/user-attachments/assets/aa326fda-e76f-4c90-8308-0bdc57315e43" />

