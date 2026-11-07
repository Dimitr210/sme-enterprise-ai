from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import models
from app.ai_agent import run_sme_agent
from app.rag_engine import add_policy_document

# Δημιουργία πινάκων αν χρειαστούν
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SME Enterprise AI Ecosystem",
    description="Κεντρικό Σύστημα Αυτοματοποίησης Μικρομεσαίας Επιχείρησης (ERP Integrations + RAG Engine)",
    version="2.0.0"
)

class AgentRequest(BaseModel):
    prompt: str

class PolicyDocCreate(BaseModel):
    doc_id: str
    text: str


@app.get("/")
def read_root():
    return {"status": "online", "system": "SME Enterprise Master Agent Ready"}


# --- CENTRAL MASTER AGENT ENDPOINT ---
@app.post("/api/v1/chat", tags=["Master AI Agent"])
def chat_with_master_agent(req: AgentRequest, db: Session = Depends(get_db)):
    """
    Κεντρικό σημείο επικοινωνίας. Ο Master Agent δέχεται φυσική γλώσσα
    και δρομολογεί αυτόματα το αίτημα στο ERP API ή στο RAG Engine.
    """
    response_text = run_sme_agent(user_prompt=req.prompt, db=db)
    return {"prompt": req.prompt, "response": response_text}


# --- RAG POLICY INGESTION ENDPOINT ---
@app.post("/api/v1/policies/add", tags=["Knowledge Base (RAG)"])
def add_policy(doc: PolicyDocCreate):
    """Προσθήκη νέου εγγράφου πολιτικής στη διανυσματική βάση ChromaDB."""
    return add_policy_document(doc_id=doc.doc_id, text=doc.text)