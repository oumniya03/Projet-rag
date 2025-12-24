# 📚 RAG Q&A Chatbot 
**Candidate : Oumniya Moutaouakil**

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
## 🤖 Interface
<img width="914" height="416" alt="image" src="https://github.com/user-attachments/assets/e69331f2-a84f-4e08-85e7-884a6d8d87bf" />

## 🐳Docker Image
<img width="953" height="479" alt="image" src="https://github.com/user-attachments/assets/86536f1d-576c-4f7d-a495-daa74bc60c3b" />

## 🛠️ Architecture

<img width="1096" height="684" alt="diagram-export-20-12-2025-18_22_19" src="https://github.com/user-attachments/assets/8b180a65-355d-495b-a80f-76fe597c0a79" />




## 📦 Prerequisites

Before you begin, ensure you have the following installed on your machine:

* **Docker** & **Docker Compose** - [Install Docker](https://docs.docker.com/get-docker/)
* **Git** - [Install Git](https://git-scm.com/downloads)

## ⚡ Quick Start Guide

Follow these steps to run the application locally.

### 1. Clone the Repository

```bash
git clone https://github.com/oumniya03/Projet-rag.git
cd Projet-rag
```

### 2. Configure Environment Variables

For security reasons, API keys are not stored in the repository. You must create a `.env` file at the root of the project.

Create a file named `.env` and add your Groq API Key:

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

> **Note:** You can obtain a Groq API key from [https://console.groq.com](https://console.groq.com)

### 3. Run with Docker Script

The project includes a helper script `docker.sh` as requested in the challenge requirements.

**Start the application:**

```bash
chmod +x docker.sh  # Only needed the first time (Linux/Mac/GitBash)
./docker.sh up
```

> **Note:** The first launch may take a few minutes to build the images and download the embedding model.

### 4. Access the Application

Once the containers are running, you can access:

* **Frontend (Chat UI):** [http://localhost:3000](http://localhost:3000)
* **Backend (API Docs):** [http://localhost:8000/docs](http://localhost:8000/docs)

## 🔧 Management Commands (docker.sh)

| Command | Description |
|---------|-------------|
| `./docker.sh up` | Builds and starts the containers in the background |
| `./docker.sh down` | Stops and removes containers and networks |
| `./docker.sh build` | Rebuilds the images (useful after code changes) |
| `./docker.sh logs` | Displays real-time logs from backend and frontend |


## 📂 Project Structure

```
Projet-rag/
├── backend/
│   ├── main.py              # FastAPI Application & RAG Logic
│   ├── Dockerfile           # Backend Container Configuration
│   └── requirements.txt     # Python Dependencies
├── frontend/
│   ├── app/
│   │   └── page.tsx         # Main Chat Interface (React/Next.js)
│   ├── Dockerfile           # Frontend Container Configuration
│   └── tailwind.config.ts   # Styling Configuration
├── data/                    # Persisted Data (Indices & Uploads)
├── docker-compose.yml       # Docker Orchestration
├── docker.sh                # Management Script
├── .env                     # Environment Variables (create this)
└── README.md                # This file
```



## 📝 Usage Guide

### Uploading Documents

1. Navigate to [http://localhost:3000](http://localhost:3000)
2. Use the upload interface to add your documents
3. Wait for the processing confirmation

### Asking Questions

1. Type your question in the chat interface
2. Press Enter or click Send
3. View the AI-generated answer with source references

### API Integration

You can integrate the backend API into your own applications:

```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={"question": "Your question here"}
)

answer = response.json()["answer"]
sources = response.json()["sources"]
```

## 🔍 Troubleshooting

### Port Already in Use

If ports 3000 or 8000 are already in use:

```bash
# Modify docker-compose.yml to use different ports
# Change "3000:3000" to "3001:3000" for frontend
# Change "8000:8000" to "8001:8000" for backend
```

### Container Build Failures

```bash
./docker.sh down
docker system prune -a
./docker.sh build
./docker.sh up
```

### Missing Environment Variables

Ensure your `.env` file exists and contains:
```env
GROQ_API_KEY=your_actual_key_here
```

## 🤝 Contributing

This is a challenge submission project. For questions or feedback, please contact the author.


## 👤 Author

**Oumniya**

- GitHub: [@oumniya03](https://github.com/oumniya03)
- Project: [Projet-rag](https://github.com/oumniya03/Projet-rag)

## 🎯 Challenge Requirements Met

- ✅ Dockerized application with `docker.sh` script
- ✅ RAG implementation with document retrieval
- ✅ `/ask` endpoint with proper response format
- ✅ Evaluation script for quality assessment
- ✅ Modern, responsive frontend interface
- ✅ Complete documentation

---



*Built  using FastAPI, Next.js, and Docker*

