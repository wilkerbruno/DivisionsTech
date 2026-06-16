#!/usr/bin/env python3
"""
resetar_admin.py — Recria ou redefine a senha do usuário admin
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Execute: python resetar_admin.py

Vai apagar o admin "admin" existente (se houver) e criar um novo
com usuário "admin" e senha "admin123".
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import create_engine, text
from security import hash_password
from config import DB_URL

_url = DB_URL
if _url.startswith("mysql://"):
    _url = _url.replace("mysql://", "mysql+pymysql://", 1)

engine = create_engine(_url, pool_pre_ping=True, echo=False)

NOVO_USUARIO = "admin"
NOVA_SENHA   = "admin123"


def resetar():
    print()
    print("=" * 54)
    print("  Divisions Tech — Resetar Admin")
    print("=" * 54)
    print()

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ MySQL conectado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao conectar no MySQL: {e}")
        sys.exit(1)

    with engine.begin() as conn:
        # Remove admin existente com esse username
        conn.execute(
            text("DELETE FROM admins WHERE username = :u"),
            {"u": NOVO_USUARIO}
        )
        print(f"  🗑️  Admin antigo removido (se existia)")

        # Cria novo admin
        hashed = hash_password(NOVA_SENHA)
        conn.execute(
            text("INSERT INTO admins (username, password) VALUES (:u, :p)"),
            {"u": NOVO_USUARIO, "p": hashed}
        )
        print(f"  👤 Novo admin criado com sucesso!")

    print()
    print(f"  Usuário : {NOVO_USUARIO}")
    print(f"  Senha   : {NOVA_SENHA}")
    print()
    print("  ⚠️  Troque a senha no painel após o login!")
    print()


if __name__ == "__main__":
    resetar()