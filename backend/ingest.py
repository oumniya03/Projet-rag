import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Chemins vers les données [cite: 40]
DATA_PATH = "/app/data" 
INDEX_PATH = "/app/data/faiss_index"

def run_ingestion():
    print("🚀 Ingestion des PDF en cours...")
    # Charger tous les PDF du dossier data [cite: 7, 15]
    loader = DirectoryLoader(DATA_PATH, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    
    # Découper en morceaux (Chunks) [cite: 16]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    # Créer les Embeddings et l'index FAISS [cite: 17, 18]
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(texts, embeddings)
    
    # Sauvegarder localement dans le volume partagé
    vectorstore.save_local(INDEX_PATH)
    print(f"✅ Terminé ! Index sauvegardé dans {INDEX_PATH}")

if __name__ == "__main__":
    run_ingestion()