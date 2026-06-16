"""
Divisions Tech — Backend Principal
FastAPI + MySQL + Mercado Pago + WhatsApp + Portfólio
Serve o frontend estático automaticamente.
"""

import pymysql
pymysql.install_as_MySQLdb()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
import sys, os, threading, time

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR    = os.path.abspath(os.path.join(BACKEND_DIR, ".."))

sys.path.insert(0, BACKEND_DIR)

from routers import auth, clients, payments, webhooks, admin, portfolio
from database import test_connection

# Garante que a pasta de uploads existe (importante em deploys novos)
os.makedirs(os.path.join(BACKEND_DIR, "uploads", "portfolio"), exist_ok=True)


def abrir_navegador():
    if os.getenv("PRODUCAO") or os.getenv("DOCKER"):
        return
    time.sleep(1.5)
    try:
        import webbrowser
        webbrowser.open("http://localhost:8000")
    except Exception:
        pass


def testar_db_em_background():
    """Testa a conexão MySQL sem bloquear o startup do servidor."""
    ok = test_connection()
    if not ok:
        print("⚠️  ATENÇÃO: MySQL indisponível. Verifique config.py / variáveis de ambiente")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print()
    print("=" * 45)
    print("  Divisions Tech API — iniciando...")
    print("=" * 45)

    # Testa o MySQL em background — não bloqueia o startup do servidor HTTP
    threading.Thread(target=testar_db_em_background, daemon=True).start()
    threading.Thread(target=abrir_navegador, daemon=True).start()

    print()
    print(f"  ✅ Servidor rodando!")
    print(f"  📌 Site:       http://localhost:8000")
    print(f"  📌 Admin:      http://localhost:8000/admin")
    print(f"  📌 Hospedagem: http://localhost:8000/pages/hospedagem.html")
    print(f"  📌 API Docs:   http://localhost:8000/api/docs")
    print()

    yield

    print("\n  Sistema encerrado.\n")


app = FastAPI(
    title="Divisions Tech API",
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,      prefix="/api/auth",      tags=["Auth"])
app.include_router(clients.router,   prefix="/api/clients",   tags=["Clientes"])
app.include_router(payments.router,  prefix="/api/payments",  tags=["Pagamentos"])
app.include_router(webhooks.router,  prefix="/api/webhooks",  tags=["Webhooks"])
app.include_router(admin.router,     prefix="/api/admin",     tags=["Admin"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfólio"])


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Divisions Tech API", "version": "2.1.0"}


@app.get("/healthz")
def healthz():
    """Health check super leve, sem tocar no banco — usado por proxies/EasyPanel."""
    return {"ok": True}


@app.get("/admin")
def admin_redirect():
    return RedirectResponse(url="/admin/index.html")


# Frontend estático — SEMPRE por último
app.mount("/", StaticFiles(directory=ROOT_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="warning",
    )