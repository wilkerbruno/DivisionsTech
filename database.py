"""
database.py — Conexão MySQL via SQLAlchemy + PyMySQL
"""

import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_URL

# Garante prefixo correto
_url = DB_URL
if _url.startswith("mysql://"):
    _url = _url.replace("mysql://", "mysql+pymysql://", 1)

engine = create_engine(
    _url,
    connect_args={
        "connect_timeout": 8,
        "read_timeout":    30,
        "write_timeout":   30,
        "charset":         "utf8mb4",
    },
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,
    max_overflow=10,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


def test_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ MySQL conectado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar no MySQL: {e}")
        return False