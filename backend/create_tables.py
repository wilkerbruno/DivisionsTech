#!/usr/bin/env python3
"""
create_tables.py — Cria todas as tabelas no MySQL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Execute UMA VEZ antes de iniciar o servidor:

    python create_tables.py

Banco: mysql+pymysql://...@easypanel.pontocomdesconto.com.br:3020/divisionstech
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import subprocess

# ── Instala dependências automaticamente ─────────────────────
REQUIRED = [
    "sqlalchemy==2.0.30",
    "pymysql==1.1.1",        # driver Python puro — não precisa do MySQLdb/mysqlclient
    "cryptography==42.0.8",
    "bcrypt==4.0.1",
]

def install_deps():
    print("📦 Verificando e instalando dependências...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--quiet"] + REQUIRED
    )
    print("   ✅ Dependências OK\n")

try:
    import sqlalchemy, pymysql, bcrypt
except ImportError:
    install_deps()

# ── Importações após garantir dependências ────────────────────
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Registra PyMySQL como substituto do MySQLdb (garante que o SQLAlchemy use pymysql)
import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import create_engine, text
from security import hash_password
from config import DB_URL

# Força o driver pymysql na URL caso não esteja explícito
_url = DB_URL
if _url.startswith("mysql://"):
    _url = _url.replace("mysql://", "mysql+pymysql://", 1)

engine = create_engine(_url, pool_pre_ping=True, echo=False)

# ── SQL das tabelas ───────────────────────────────────────────

SQL_ADMINS = """
CREATE TABLE IF NOT EXISTS admins (
    id         INT          NOT NULL AUTO_INCREMENT,
    username   VARCHAR(80)  NOT NULL,
    password   VARCHAR(255) NOT NULL,
    created_at DATETIME     NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    UNIQUE KEY uq_admins_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

SQL_CLIENTS = """
CREATE TABLE IF NOT EXISTS clients (
    id             INT          NOT NULL AUTO_INCREMENT,
    name           VARCHAR(200) NOT NULL,
    cpf            VARCHAR(20)      NULL DEFAULT NULL,
    email          VARCHAR(200) NOT NULL,
    phone          VARCHAR(30)      NULL DEFAULT NULL,
    plan           ENUM('standard','plus','pro') NOT NULL,
    domain         VARCHAR(255)     NULL DEFAULT NULL,
    has_domain     TINYINT(1)   NOT NULL DEFAULT 0,
    status         ENUM('pending','active','cancelled') NOT NULL DEFAULT 'pending',
    payment_id     VARCHAR(120)     NULL DEFAULT NULL,
    payment_status ENUM('pending','approved','failed','in_process','rejected')
                   NOT NULL DEFAULT 'pending',
    contracted_at  VARCHAR(30)      NULL DEFAULT NULL,
    expires_at     VARCHAR(30)      NULL DEFAULT NULL,
    created_at     DATETIME     NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    KEY idx_clients_email  (email),
    KEY idx_clients_status (status),
    KEY idx_clients_plan   (plan)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

SQL_PAYMENTS = """
CREATE TABLE IF NOT EXISTS payments (
    id            INT           NOT NULL AUTO_INCREMENT,
    client_id     INT           NOT NULL,
    mp_payment_id VARCHAR(120)      NULL DEFAULT NULL,
    plan          VARCHAR(30)       NULL DEFAULT NULL,
    amount        DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    status        VARCHAR(30)   NOT NULL DEFAULT 'pending',
    created_at    DATETIME      NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    KEY idx_payments_client    (client_id),
    KEY idx_payments_mp_pay_id (mp_payment_id),
    CONSTRAINT fk_payments_client
        FOREIGN KEY (client_id) REFERENCES clients (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

TABLES = [
    ("admins",   SQL_ADMINS),
    ("clients",  SQL_CLIENTS),
    ("payments", SQL_PAYMENTS),
]


def test_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ MySQL conectado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar no MySQL: {e}")
        return False


def create_all():
    print()
    print("=" * 54)
    print("  Divisions Tech — Criação de Tabelas MySQL")
    print("=" * 54)
    print()

    if not test_connection():
        print()
        print("❌ Não foi possível conectar ao MySQL.")
        print("   Verifique a string de conexão em config.py")
        sys.exit(1)

    with engine.begin() as conn:
        for name, sql in TABLES:
            conn.execute(text(sql))
            print(f"  ✅ Tabela `{name}` — OK")

        existing = conn.execute(
            text("SELECT id FROM admins WHERE username = 'admin' LIMIT 1")
        ).fetchone()

        if not existing:
            hashed = hash_password("admin123")
            conn.execute(
                text("INSERT INTO admins (username, password) VALUES (:u, :p)"),
                {"u": "admin", "p": hashed}
            )
            print()
            print("  👤 Admin padrão criado:")
            print("     Usuário : admin")
            print("     Senha   : admin123")
            print("     ⚠️  Troque a senha no painel após o primeiro acesso!")
        else:
            print()
            print("  👤 Admin já existe — nenhuma alteração.")

    print()
    print("✅ Banco de dados pronto para uso!")
    print()


if __name__ == "__main__":
    create_all()