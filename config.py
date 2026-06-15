"""
config.py — Configurações centralizadas Divisions Tech
"""

import os

# ── MySQL ────────────────────────────────────────────────────
DB_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://mysql:0h5j6srwidut7rpv3uwz@easypanel.pontocomdesconto.com.br:3020/divisionstech"
)

# ── Mercado Pago ─────────────────────────────────────────────
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN", "SEU_ACCESS_TOKEN_AQUI")
MP_PUBLIC_KEY   = os.getenv("MP_PUBLIC_KEY",   "SEU_PUBLIC_KEY_AQUI")

# URL base do servidor (sem barra final)
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# ── WhatsApp ─────────────────────────────────────────────────
# Provedor: "evolution" ou "zapi"
WA_PROVIDER       = os.getenv("WA_PROVIDER", "evolution")

# Evolution API
WA_EVOLUTION_URL  = os.getenv("WA_EVOLUTION_URL",  "http://localhost:8080")
WA_EVOLUTION_KEY  = os.getenv("WA_EVOLUTION_KEY",  "SUA_API_KEY_EVOLUTION")
WA_INSTANCE_NAME  = os.getenv("WA_INSTANCE_NAME",  "divisions")

# Z-API
WA_ZAPI_INSTANCE     = os.getenv("WA_ZAPI_INSTANCE",     "SEU_INSTANCE_ZAPI")
WA_ZAPI_TOKEN        = os.getenv("WA_ZAPI_TOKEN",        "SEU_TOKEN_ZAPI")
WA_ZAPI_CLIENT_TOKEN = os.getenv("WA_ZAPI_CLIENT_TOKEN", "SEU_CLIENT_TOKEN")

# Número do admin (DDI + DDD + número, sem +)
ADMIN_WHATSAPP = os.getenv("ADMIN_WHATSAPP", "5583993654478")

# ── JWT ──────────────────────────────────────────────────────
JWT_SECRET       = os.getenv("JWT_SECRET", "TROQUE_POR_CHAVE_SEGURA_ALEATORIA_32CHARS")
JWT_ALGO         = "HS256"
JWT_EXPIRE_HOURS = 12

# ── Planos ───────────────────────────────────────────────────
PLANS = {
    "standard": {"name": "Standard", "price": 39.90, "label": "R$ 39,90/mês"},
    "plus":     {"name": "Plus",     "price": 69.90, "label": "R$ 69,90/mês"},
    "pro":      {"name": "Pro",      "price": 89.90, "label": "R$ 89,90/mês"},
}