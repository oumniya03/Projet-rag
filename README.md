📚 RAG Q&A Chatbot (Coding Challenge)

A full-stack Retrieval-Augmented Generation (RAG) application capable of answering questions based on uploaded PDF documents. Built with Next.js, FastAPI, LangChain, and Docker.

🚀 Features

📂 Document Ingestion: Upload multiple PDF files via the UI.

🧠 Advanced RAG Pipeline:

Text Chunking & Splitting (RecursiveCharacterTextSplitter).

Local Embeddings (HuggingFace all-MiniLM-L6-v2).

Vector Storage (FAISS).

🤖 LLM Integration: Powered by Llama-3-70b via Groq API for lightning-fast inference.

💬 Modern UI: Chat interface with markdown support, history management, and citation sources.

🔒 Secure: API keys managed via environment variables (not exposed in code).

🐳 Dockerized: Fully containerized environment managed by a custom docker.sh script.

🛠️ Architecture

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


📦 Prerequisites

Docker & Docker Compose installed on your machine.

Git.

⚡ Quick Start Guide

Follow these steps to run the application locally.

1. Clone the repository

git clone [https://github.com/oumniya03/Projet-rag.git](https://github.com/oumniya03/Projet-rag.git)
cd Projet-rag


2. Configure Environment Variables

For security reasons, API keys are not stored in the repository. You must create a .env file at the root of the project.

Create a file named .env and add your Groq API Key:

GROQ_API_KEY=gsk_your_groq_api_key_here


3. Run with Docker Script

The project includes a helper script docker.sh as requested in the challenge requirements.

Start the application:

chmod +x docker.sh  # Only needed the first time (Linux/Mac/GitBash)
./docker.sh up


Note: The first launch may take a few minutes to build the images and download the embedding model.

4. Access the Application

Frontend (Chat UI): http://localhost:3000

Backend (API Docs): http://localhost:8000/docs

🔧 Management Commands (docker.sh)

Command

Description

./docker.sh up

Builds and starts the containers in the background.

./docker.sh down

Stops and removes containers and networks.

./docker.sh build

Rebuilds the images (useful after code changes).

./docker.sh logs

Displays real-time logs from backend and frontend.

🧪 Evaluation & Testing

API Endpoint (/ask)

Per the challenge requirements, a compliant endpoint is available:

curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is Cloud Computing?"}'


Self-Evaluation Script (LLM-as-a-Judge)

An automated evaluation script is included to test Faithfulness and Answer Relevance using Llama-3 as a judge.

# Requires local python environment
pip install python-dotenv langchain-groq langchain
python evaluate.py


📂 Project Structure

├── backend/
│   ├── main.py            # FastAPI Application & RAG Logic
│   ├── Dockerfile         # Backend Container Config
│   └── requirements.txt   # Python Dependencies
├── frontend/
│   ├── app/page.tsx       # Main Chat Interface (React/Next.js)
│   ├── Dockerfile         # Frontend Container Config
│   └── tailwind.config.ts # Styling Configuration
├── data/                  # Persisted data (Indices & Uploads)
├── docker-compose.yml     # Docker Orchestration
├── docker.sh              # Management Script
└── evaluate.py            # Quality Assessment Script


Author: Oumniya

Submission for: Quorium Coding Challenge
