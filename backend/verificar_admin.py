#!/usr/bin/env python3
"""
verificar_admin.py — Mostra os admins cadastrados no banco
Útil para diagnosticar problemas de login.

Execute: python verificar_admin.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import create_engine, text
from config import DB_URL

_url = DB_URL
if _url.startswith("mysql://"):
    _url = _url.replace("mysql://", "mysql+pymysql://", 1)

print()
print("=" * 54)
print("  Divisions Tech — Verificar Admins")
print("=" * 54)
print()

try:
    masked = _url.split("@")[1] if "@" in _url else _url
    print(f"🔌 Conectando em: {masked}")
except Exception:
    pass

engine = create_engine(_url, pool_pre_ping=True, echo=False)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ Conexão OK\n")
except Exception as e:
    print(f"❌ Erro de conexão: {e}")
    sys.exit(1)

# Verifica se a tabela existe
with engine.connect() as conn:
    try:
        tables = conn.execute(text("SHOW TABLES")).fetchall()
        table_names = [t[0] for t in tables]
        print(f"📋 Tabelas encontradas: {table_names}\n")

        if "admins" not in table_names:
            print("❌ A tabela 'admins' NÃO existe neste banco!")
            print("   Rode: python create_tables.py")
            sys.exit(1)

        admins = conn.execute(text("SELECT id, username, password, created_at FROM admins")).fetchall()

        if not admins:
            print("❌ A tabela 'admins' existe mas está VAZIA!")
            print("   Rode: python resetar_admin.py")
        else:
            print(f"👤 Admins cadastrados ({len(admins)}):")
            for a in admins:
                print(f"   ID: {a[0]} | Usuário: {a[1]} | Hash: {a[2][:30]}... | Criado: {a[3]}")

    except Exception as e:
        print(f"❌ Erro ao consultar: {e}")
        sys.exit(1)

print()