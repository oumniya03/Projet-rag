from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
import uuid
import json
from typing import Dict, List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate # Pour personnaliser le style

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURATION ---
DATA_DIR = "/app/data"
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
INDICES_DIR = os.path.join(DATA_DIR, "indices")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(INDICES_DIR, exist_ok=True)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.3-70b-versatile"

SESSIONS: Dict[str, dict] = {}

# --- PROMPT TEMPLATE (C'est ici que la magie opère pour le style) ---
custom_prompt_template = """Tu es un assistant expert et pédagogique. Utilise les éléments de contexte suivants pour répondre à la question.

RÈGLES DE MISE EN FORME STRICTES :
1. Utilise des TITRES (avec ###) pour séparer les grandes idées.
2. Utilise systématiquement des listes à puces (-) pour énumérer les points.
3. Mets en **GRAS** les termes techniques et les concepts clés.
4. Fais des paragraphes courts et aérés. Ne fais jamais de blocs de texte compacts.
5. Si la réponse n'est pas dans le contexte, dis-le poliment.

Contexte :
{context}

Question : {question}

Réponse structurée :"""

QA_CHAIN_PROMPT = PromptTemplate.from_template(custom_prompt_template)

# --- FONCTIONS UTILITAIRES ---
def save_metadata():
    data_to_save = {sid: {"title": d["title"], "history": d["history"]} for sid, d in SESSIONS.items()}
    with open(SESSIONS_FILE, "w") as f:
        json.dump(data_to_save, f)

def load_metadata():
    global SESSIONS
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r") as f:
            saved_data = json.load(f)
            for sid, data in saved_data.items():
                SESSIONS[sid] = {**data, "vectorstore": None}

load_metadata()

def get_llm():
    return ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name=GROQ_MODEL, temperature=0.3)

def get_vectorstore(session_id):
    if SESSIONS[session_id]["vectorstore"]: return SESSIONS[session_id]["vectorstore"]
    index_path = os.path.join(INDICES_DIR, session_id)
    if os.path.exists(index_path):
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        vs = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        SESSIONS[session_id]["vectorstore"] = vs
        return vs
    return None

# --- ROUTES ---

@app.post("/sessions/new")
async def create_session():
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {"title": "Nouveau Chat", "history": [], "vectorstore": None}
    save_metadata()
    return {"session_id": session_id, "title": "Nouveau Chat"}

@app.get("/sessions")
async def get_sessions():
    return [{"id": k, "title": v["title"]} for k, v in SESSIONS.items()]

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    return SESSIONS.get(session_id, {}).get("history", [])

@app.post("/upload/{session_id}")
async def upload_files(session_id: str, files: List[UploadFile] = File(...)):
    if session_id not in SESSIONS: raise HTTPException(404, "Session introuvable")
    
    saved_docs = []
    for file in files:
        temp_filename = f"temp_{file.filename}"
        with open(temp_filename, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
        try:
            loader = PyPDFLoader(temp_filename)
            docs = loader.load()
            # On ajoute le nom du fichier dans les métadonnées pour la citation
            for doc in docs: doc.metadata["source"] = file.filename
            saved_docs.extend(docs)
        finally:
            if os.path.exists(temp_filename): os.remove(temp_filename)

    if not saved_docs: return {"message": "Aucun doc valide"}

    SESSIONS[session_id]["title"] = files[0].filename + (f" (+{len(files)-1})" if len(files) > 1 else "")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(saved_docs)
    
    vs = get_vectorstore(session_id)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    if vs is None: vs = FAISS.from_documents(splits, embeddings)
    else: vs.add_documents(splits)
    
    SESSIONS[session_id]["vectorstore"] = vs
    vs.save_local(os.path.join(INDICES_DIR, session_id))
    save_metadata()
    return {"message": "Docs analysés !", "title": SESSIONS[session_id]["title"]}

class QueryRequest(BaseModel):
    prompt: str

@app.post("/chat/{session_id}")
async def chat(session_id: str, request: QueryRequest):
    if session_id not in SESSIONS: raise HTTPException(404, "Session introuvable")
    session = SESSIONS[session_id]
    vs = get_vectorstore(session_id)
    
    if vs:
        retriever = vs.as_retriever(search_kwargs={"k": 4})
        # return_source_documents=True permet de récupérer les preuves
        qa_chain = RetrievalQA.from_chain_type(
            llm=get_llm(),
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
        )
        
        result = qa_chain.invoke({"query": request.prompt})
        response_text = result['result']
        source_docs = result['source_documents']
        
        # --- MISE EN FORME DES SOURCES ---
        unique_sources = set()
        for doc in source_docs:
            name = doc.metadata.get('source', 'Inconnu')
            page = doc.metadata.get('page', 0) + 1 # +1 car ça commence à 0
            unique_sources.add(f"- 📄 *{name}* (Page {page})")
        
        if unique_sources:
            response_text += "\n\n---\n### 📚 Sources utilisées :\n" + "\n".join(unique_sources)
            
    else:
        # Chat simple sans doc
        response_text = get_llm().invoke(request.prompt).content

    session["history"].append({"role": "user", "content": request.prompt})
    session["history"].append({"role": "assistant", "content": response_text})
    save_metadata()
    
    return {"response": response_text}
# --- ROUTE CONFORME AU CHALLENGE (POST /ask) ---
class AskRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_simple(request: AskRequest):
    # On utilise une session temporaire ou par défaut
    temp_session_id = "default_api_session"
    if temp_session_id not in SESSIONS:
        SESSIONS[temp_session_id] = {"title": "API User", "history": [], "vectorstore": None}
    
    # On réutilise la logique de chat existante
    # Note: Cela fonctionnera si des documents ont été uploadés dans cette session
    # ou si on utilise juste le LLM sans documents.
    query_req = QueryRequest(prompt=request.question)
    
    # Appel interne à la logique de chat
    # (Simplification pour l'exemple, idéalement on refactorise la fonction chat)
    response_data = await chat(temp_session_id, query_req)
    
    # Format exigé par le PDF : { "answer": "...", "sources": [...] }
    return {
        "answer": response_data["response"],
        "sources": [src["name"] for src in response_data["sources"]]
    }