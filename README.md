# 📚 RAG Q&A Chatbot 

A full-stack Retrieval-Augmented Generation (RAG) application capable of answering questions based on uploaded PDF documents. Built with **Next.js**, **FastAPI**, **LangChain**, and **Docker**.

## 🚀 Features

- **📂 Document Ingestion**: Upload multiple PDF files via the UI.
- **🧠 Advanced RAG Pipeline**:
  - Text Chunking & Splitting (RecursiveCharacterTextSplitter).
  - Local Embeddings (HuggingFace `all-MiniLM-L6-v2`).
  - Vector Storage (FAISS).
- **🤖 LLM Integration**: Powered by **Llama-3-70b** via Groq API for lightning-fast inference.
- **💬 Modern UI**: Chat interface with markdown support, history management, and **citation sources**.
- **🔒 Secure**: API keys managed via environment variables (not exposed in code).
- **🐳 Dockerized**: Fully containerized environment managed by a custom `docker.sh` script.

## 🛠️ Architecture

```mermaid
graph TD
    subgraph Frontend [Frontend Container]
        UI[Next.js Interface]
    end

    subgraph Backend [Backend Container]
        API[FastAPI Server]
        Chain[LangChain Pipeline]
    end

    subgraph Data [Persistence]
        PDFs[Uploaded Files]
        FAISS[(Vector Index)]
    end

    User((User)) -->|Uploads PDF| UI
    UI -->|POST /upload| API
    API -->|Process & Embed| FAISS

    User -->|Asks Question| UI
    UI -->|POST /chat| API
    API -->|Retrieves Context| FAISS
    FAISS -->|Context| Chain
    Chain -->|Context + Query| Groq[Groq API]
    Groq -->|Response| UI