"""
database.py — Conexão MySQL via SQLAlchemy (PyMySQL driver)
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from config import DB_URL

# ── Engine ───────────────────────────────────────────────────
engine = create_engine(
    DB_URL,
    pool_pre_ping=True,       # testa conexão antes de usar
    pool_recycle=3600,        # recicla conexões a cada 1h
    pool_size=10,
    max_overflow=20,
    echo=False,               # True para debug SQL
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# ── Dependency (FastAPI) ─────────────────────────────────────
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Context manager (uso direto) ─────────────────────────────
@contextmanager
def get_conn():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def test_connection():
    """Verifica conectividade com o banco."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ MySQL conectado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar no MySQL: {e}")
        return False