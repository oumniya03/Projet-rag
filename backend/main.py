from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RAG Q&A API")

# Configuration CORS pour laisser le frontend Next.js parler au backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration RAG
INDEX_PATH = "/app/data/faiss_index"
# Assurez-vous que la clé API est dans docker-compose ou .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY") 

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sources: List[str]

def get_qa_chain():
    # 1. Charger l'index FAISS existant (créé par ingest.py)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    try:
        vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    except RuntimeError:
        raise HTTPException(status_code=500, detail="Index introuvable. Avez-vous lancé './docker.sh ingest' ?")

    # 2. Configurer le LLM (Groq)
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.3, groq_api_key=GROQ_API_KEY)
    
    # 3. Créer la chaîne
    return RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever(search_kwargs={"k": 3}), return_source_documents=True
    )

@app.post("/ask", response_model=AnswerResponse)
async def ask(request: QuestionRequest):
    try:
        qa_chain = get_qa_chain()
        response = qa_chain.invoke({"query": request.question})
        
        # Extraire les sources
        sources = list(set([os.path.basename(doc.metadata.get('source', 'Inconnu')) for doc in response["source_documents"]]))
        
        return {
            "answer": response["result"],
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))