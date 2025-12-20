import os
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Charger la clé API
load_dotenv()

# Configuration du "Juge" (Votre IA)
llm_judge = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0
)

# Fonction pour noter la réponse
def evaluate_answer(question, context, answer):
    prompt = f"""
    Tu es un juge impartial évaluant un système RAG.
    
    Données :
    - Question utilisateur : "{question}"
    - Contexte récupéré (Source) : "{context}"
    - Réponse générée par l'IA : "{answer}"
    
    Tâche :
    1. Évalue la "Fidélité" (Faithfulness) : La réponse est-elle uniquement basée sur le contexte fourni ? (Note 1-5)
    2. Évalue la "Pertinence" (Relevance) : La réponse répond-elle bien à la question ? (Note 1-5)
    
    Format de réponse attendu :
    Fidélité: X/5
    Pertinence: Y/5
    Commentaire: Court commentaire expliquant la note.
    """
    
    evaluation = llm_judge.invoke(prompt).content
    return evaluation

# --- TEST ---
# 1. On définit une question test (Assurez-vous d'avoir uploadé le PDF correspondant dans l'app avant !)
API_URL = "http://localhost:8000"

print("--- 🧪 DÉBUT DE L'ÉVALUATION AUTOMATISÉE ---")

# Créer une session temporaire pour le test
session_id = requests.post(f"{API_URL}/sessions/new").json()["session_id"]
print(f"Session de test créée : {session_id}")

# ATTENTION : Pour que ce test marche, il faut idéalement que vous ayez déjà des docs chargés
# Ou alors on teste une question générale si le LLM répond sans doc.
question_test = "Quels sont les avantages du Cloud Computing ?" 

print(f"Question posée : {question_test}")

# Interroger votre API
payload = {"prompt": question_test}
response = requests.post(f"{API_URL}/chat/{session_id}", json=payload).json()

answer_generated = response["answer"] if "answer" in response else response["response"]
sources = response.get("sources", [])

# Construire le contexte texte à partir des sources (Simulation)
context_text = " ".join([src['name'] for src in sources]) if sources else "Aucun contexte (Chat pur)"

print(f"\n🤖 Réponse de votre RAG : {answer_generated[:100]}...")

# Lancer le Juge
print("\n⚖️  Le Juge Llama-3 analyse la qualité...")
resultat = evaluate_answer(question_test, context_text, answer_generated)

print("\n" + "="*30)
print("RÉSULTAT DE L'ÉVALUATION")
print("="*30)
print(resultat)