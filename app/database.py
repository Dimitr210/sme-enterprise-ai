from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Δημιουργία του αρχείου βάσης δεδομένων SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./sme_enterprise.db"

# connect_args={"check_same_thread": False} απαραίτητο μόνο για την SQLite στο FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Δημιουργία Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class για τα ORM models μας
Base = declarative_base()

# Dependency για να παίρνουμε DB Session σε κάθε FastAPI endpoint
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()