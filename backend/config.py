"""
config.py — Configurações centralizadas Divisions Tech
Edite as variáveis abaixo antes de iniciar o servidor.
"""

import os

# ── MySQL (PyMySQL como driver — compatível com Windows/Linux/Mac) ────
DB_URL = os.getenv(
    "DATABASE_URL",
    "mysql://mysql:dg9kpr99fl4jra84qz0m@easypanel.pontocomdesconto.com.br:3021/divisionstech"
)

# ── Mercado Pago ──────────────────────────────────────────────
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN", "SEU_ACCESS_TOKEN_AQUI")
MP_PUBLIC_KEY   = os.getenv("MP_PUBLIC_KEY",   "SEU_PUBLIC_KEY_AQUI")

# URL base do seu servidor (sem barra final)
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# ── WhatsApp ──────────────────────────────────────────────────
WA_PROVIDER          = os.getenv("WA_PROVIDER",          "evolution")
WA_EVOLUTION_URL     = os.getenv("WA_EVOLUTION_URL",     "http://localhost:8080")
WA_EVOLUTION_KEY     = os.getenv("WA_EVOLUTION_KEY",     "SUA_API_KEY_EVOLUTION")
WA_INSTANCE_NAME     = os.getenv("WA_INSTANCE_NAME",     "divisions")
WA_ZAPI_INSTANCE     = os.getenv("WA_ZAPI_INSTANCE",     "SEU_INSTANCE_ZAPI")
WA_ZAPI_TOKEN        = os.getenv("WA_ZAPI_TOKEN",        "SEU_TOKEN_ZAPI")
WA_ZAPI_CLIENT_TOKEN = os.getenv("WA_ZAPI_CLIENT_TOKEN", "SEU_CLIENT_TOKEN")
ADMIN_WHATSAPP       = os.getenv("ADMIN_WHATSAPP",       "5583993654478")

# ── JWT ───────────────────────────────────────────────────────
JWT_SECRET       = os.getenv("JWT_SECRET", "TROQUE_POR_UMA_CHAVE_ALEATORIA_LONGA_32CHARS")
JWT_ALGO         = "HS256"
JWT_EXPIRE_HOURS = 12

# ── Planos de Hospedagem ──────────────────────────────────────
PLANS = {
    "standard": {"name": "Standard", "price": 39.90, "label": "R$ 39,90/mês"},
    "plus":     {"name": "Plus",     "price": 69.90, "label": "R$ 69,90/mês"},
    "pro":      {"name": "Pro",      "price": 89.90, "label": "R$ 89,90/mês"},
}