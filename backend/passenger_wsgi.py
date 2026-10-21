"""
passenger_wsgi.py — Ponte entre o Passenger (cPanel, WSGI) e o FastAPI (ASGI).

No cPanel: Setup Python App
  - Application root ........ repositories/DivisionsTech/backend
  - Application startup file  passenger_wsgi.py
  - Application entry point . application
  - Application URL ......... divisionstech.com/api   (ou a raiz "/")
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("PRODUCAO", "true")

from a2wsgi import ASGIMiddleware  # noqa: E402
from main import app as fastapi_app  # noqa: E402

_asgi_app = ASGIMiddleware(fastapi_app)


def application(environ, start_response):
    # Quando o app é montado em /api, o Passenger remove esse prefixo do PATH_INFO
    # e o coloca em SCRIPT_NAME. As rotas do FastAPI já começam com /api/..., então
    # devolvemos o prefixo ao caminho. Se o app estiver na raiz, nada muda.
    script = environ.get("SCRIPT_NAME", "")
    if script:
        environ["PATH_INFO"] = script.rstrip("/") + environ.get("PATH_INFO", "")
        environ["SCRIPT_NAME"] = ""
    return _asgi_app(environ, start_response)
