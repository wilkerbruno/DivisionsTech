"""
Divisions Tech — Backend Principal
FastAPI + MySQL + Mercado Pago + WhatsApp
Serve o frontend estático e abre o navegador automaticamente.
"""

# IMPORTANTE: registra pymysql ANTES de qualquer import do SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
import sys, os, webbrowser, threading, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routers import auth, clients, payments, webhooks, admin
from database import test_connection

# Pasta raiz do projeto (um nível acima do backend)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def abrir_navegador():
    """Abre o navegador após 1.5s para o servidor ter tempo de subir."""
    time.sleep(1.5)
    print()
    print("  🌐 Abrindo o sistema no navegador...")
    print("  📌 Se não abrir automaticamente, acesse: http://localhost:8000")
    print()
    webbrowser.open("http://localhost:8000")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print()
    print("=" * 45)
    print("  Divisions Tech API — iniciando...")
    print("=" * 45)
    ok = test_connection()
    if not ok:
        print("⚠️  ATENÇÃO: MySQL indisponível. Verifique config.py")

    # Abre navegador em thread separada
    t = threading.Thread(target=abrir_navegador, daemon=True)
    t.start()

    print()
    print("  ✅ Servidor rodando!")
    print("  📌 Site:          http://localhost:8000")
    print("  📌 Admin:         http://localhost:8000/admin")
    print("  📌 Hospedagem:    http://localhost:8000/pages/hospedagem.html")
    print("  📌 API Docs:      http://localhost:8000/api/docs")
    print()
    print("  Pressione CTRL+C para encerrar.")
    print()

    yield

    # Shutdown
    print()
    print("  Sistema encerrado.")


app = FastAPI(
    title="Divisions Tech API",
    version="2.0.0",
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

# Routers da API
app.include_router(auth.router,      prefix="/api/auth",     tags=["Auth"])
app.include_router(clients.router,   prefix="/api/clients",  tags=["Clientes"])
app.include_router(payments.router,  prefix="/api/payments", tags=["Pagamentos"])
app.include_router(webhooks.router,  prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(admin.router,     prefix="/api/admin",    tags=["Admin"])

# Health check
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Divisions Tech API", "version": "2.0.0"}

# Redireciona /admin para /admin/index.html
@app.get("/admin")
def admin_redirect():
    return RedirectResponse(url="/admin/index.html")

# Serve os arquivos estáticos do frontend (deve ser o ÚLTIMO)
app.mount("/", StaticFiles(directory=ROOT_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,   # reload=False para funcionar com o mount estático
        log_level="warning",  # menos verboso no terminal
    )