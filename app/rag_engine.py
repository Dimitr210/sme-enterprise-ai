import os
import chromadb
from google import genai
from dotenv import load_dotenv

# Φόρτωση μεταβλητών περιβάλλοντος από το .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Αρχικοποίηση Google GenAI Client
ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Αρχικοποίηση ChromaDB Persistent Client (Τοπική Αποθήκευση)
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="company_policies")


def add_policy_document(doc_id: str, text: str, metadata: dict = None):
    """
    Προσθέτει ένα έγγραφο πολιτικής στην ChromaDB.
    """
    collection.add(
        documents=[text],
        metadatas=[metadata] if metadata else [{"source": "manual"}],
        ids=[doc_id]
    )
    return {"status": "success", "message": f"Document {doc_id} added to ChromaDB."}


def query_rag_system(user_query: str) -> str:
    """
    Αναζητά τα πιο σχετικά έγγραφα στην ChromaDB και παράγει απάντηση με το Gemini API.
    """
    if not ai_client:
        return "Σφάλμα: Το GEMINI_API_KEY δεν έχει ρυθμιστεί στο .env αρχείο."

    # 1. Retrieval: Αναζήτηση των 2 πιο σχετικών αποσπασμάτων
    results = collection.query(
        query_texts=[user_query],
        n_results=2
    )

    retrieved_docs = results.get("documents", [[]])[0]
    context = "\n---\n".join(retrieved_docs) if retrieved_docs else "Δεν βρέθηκαν σχετικές πληροφορίες."

    # 2. Generation: Σύνθεση απάντησης με το Gemini
    prompt = f"""
Είσαι ο Ψηφιακός Βοηθός Εξυπηρέτησης της εταιρείας SME Enterprise.
Απάντησε στην ερώτηση του χρήστη βασιζόμενος ΑΠΟΚΛΕΙΣΤΙΚΑ στο παρακάτω πλαίσιο πληροφοριών (Context).
Αν η απάντηση δεν βρίσκεται στο Context, πες ευγενικά ότι δεν διαθέτεις αυτή την πληροφορία.

=== CONTEXT ===
{context}

=== ΕΡΩΤΗΣΗ ΧΡΗΣΤΗ ===
{user_query}

=== ΑΠΑΝΤΗΣΗ ===
"""

    response = ai_client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )

    return response.text