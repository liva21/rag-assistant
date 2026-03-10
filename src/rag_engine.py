import os
import requests as http_requests
import uuid
from typing import Any, List, Optional
from loguru import logger
from langchain_community.document_loaders import PyPDFLoader

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from app.config import get_settings

settings = get_settings()


from huggingface_hub import InferenceClient

class HuggingFaceRouterLLM(LLM):
    """Hugging Face Router API ile doğrudan iletişim kuran özel LLM sınıfı.
    huggingface_hub InferenceClient kullanarak modern TGI modellerini (ör. Qwen) destekler."""

    model_id: str = "Qwen/Qwen2.5-7B-Instruct"
    api_token: str = ""
    temperature: float = 0.3
    max_new_tokens: int = 512

    @property
    def _llm_type(self) -> str:
        return "huggingface_router"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        
        try:
            # Hugging Face'in yeni birleşik router URL'si
            # NOT: Bu URL OpenAI uyumludur ve model ismi JSON payload içinde gönderilir.
            custom_url = "https://router.huggingface.co/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_id,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.max_new_tokens,
                "temperature": self.temperature,
                "seed": 42
            }
            
            import requests
            logger.debug(f"Router API çağrısı: {custom_url} (Model: {self.model_id})")
            
            response = requests.post(custom_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                # 404/410 gibi hataları detaylı logla
                logger.error(f"API Hatası ({response.status_code}): {response.text}")
                raise ValueError(f"HTTP {response.status_code}: {response.text}")
                
            result = response.json()
            # OpenAI formatında yanıtı al
            text = result["choices"][0]["message"]["content"]
            
            if stop:
                for s in stop:
                    if s in text:
                        text = text[: text.index(s)]
            return text

        except Exception as e:
            logger.error(f"LLM Çağrı Hatası: {e}")
            raise ValueError(f"API bağlantısı başarısız oldu: {str(e)}")




class RAGEngine:
    def __init__(self):
        logger.info("RAG Motoru başlatılıyor...")
        self._embeddings = None
        
        token = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
        self.llm = HuggingFaceRouterLLM(
            model_id="Qwen/Qwen2.5-7B-Instruct",
            api_token=token,
            temperature=0.3,
            max_new_tokens=512,
        )
        self.vector_store = None
        logger.info("RAG Motoru hazır.")

    @property
    def embeddings(self):
        if self._embeddings is None:
            logger.info("Embeddings modeli yükleniyor/indiriliyor...")
            self._embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            logger.info("Embeddings modeli yüklendi.")
        return self._embeddings

    def ingest_document(self, file_path):
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )
            texts = text_splitter.split_documents(documents)

            doc_id = str(uuid.uuid4())

            logger.info(f"{len(texts)} chunk oluşturuldu, vektör veritabanına ekleniyor...")
            
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(texts, self.embeddings)
            else:
                self.vector_store.add_documents(texts)

            logger.info("Vektör veritabanı güncellendi.")
            
            return {
                "status": "success",
                "filename": os.path.basename(file_path),
                "chunks": len(texts),
                "doc_id": doc_id,
            }
        except Exception as e:
            logger.error(f"Döküman işleme hatası: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "filename": os.path.basename(file_path),
                "doc_id": "error",
            }

    def query(self, question, top_k=4, return_sources=True):
        if self.vector_store is None:
            return {
                "answer": "Lütfen önce analiz edilecek bir makale yükleyin.",
                "source_documents": [],
            }

        template = """Sen uzman bir akademik araştırma asistanısın. 
        Aşağıdaki bağlamı (context) kullanarak soruya bilimsel ve net bir cevap ver.
        
        Bağlam: {context}
        
        Soru: {question}
        
        Cevap:"""

        QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": top_k}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
        )

        try:
            result = qa_chain.invoke({"query": question})
            sources = []
            for doc in result["source_documents"]:
                sources.append(
                    {
                        "content": doc.page_content,
                        "page": doc.metadata.get("page", 0) + 1,
                        "source": os.path.basename(
                            doc.metadata.get("source", "Bilinmiyor")
                        ),
                    }
                )
            return {"answer": result["result"], "source_documents": sources}
        except Exception as e:
            return {
                "answer": f"Bir hata oluştu: {str(e)}",
                "source_documents": [],
            }
