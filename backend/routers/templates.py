"""templates.py — CRUD de temas de modelos (landing pages de exemplo) com upload de capa"""

import json
import os
import sys
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import engine, get_db
from routers.auth import get_current_admin

router = APIRouter()

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(BACKEND_DIR, "uploads", "templates")
PAGES_DIR   = os.path.join(UPLOADS_DIR, "pages")
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(PAGES_DIR, exist_ok=True)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 8 * 1024 * 1024  # 8MB
MAX_LINKS = 4

ALLOWED_PAGE_EXT = {".html", ".htm"}
MAX_PAGE_SIZE = 10 * 1024 * 1024  # 10MB (página exportada com imagens embutidas pode pesar)


def _ensure_schema():
    """Cria as tabelas se ainda não existirem (deploy novo que não rodou create_tables.py)."""
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS template_themes (
                    id             INT          NOT NULL AUTO_INCREMENT,
                    title          VARCHAR(200) NOT NULL,
                    description    TEXT         NOT NULL,
                    image_filename VARCHAR(255)     NULL DEFAULT NULL,
                    is_published   TINYINT(1)   NOT NULL DEFAULT 1,
                    sort_order     INT          NOT NULL DEFAULT 0,
                    created_at     DATETIME     NOT NULL DEFAULT NOW(),
                    updated_at     DATETIME     NOT NULL DEFAULT NOW() ON UPDATE NOW(),
                    PRIMARY KEY (id),
                    KEY idx_template_themes_published (is_published)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS template_links (
                    id         INT          NOT NULL AUTO_INCREMENT,
                    theme_id   INT          NOT NULL,
                    label      VARCHAR(100) NOT NULL,
                    url        VARCHAR(500) NOT NULL,
                    sort_order INT          NOT NULL DEFAULT 0,
                    PRIMARY KEY (id),
                    KEY idx_template_links_theme (theme_id),
                    CONSTRAINT fk_template_links_theme
                        FOREIGN KEY (theme_id) REFERENCES template_themes (id)
                        ON DELETE CASCADE ON UPDATE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
    except Exception as e:
        print(f"[templates] aviso na migração: {e}")


_ensure_schema()


def _parse_links(raw: str) -> list[dict]:
    """Valida o JSON de links vindo do admin: no máx. 4, label+url obrigatórios."""
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Links em formato inválido")
    if not isinstance(data, list):
        raise HTTPException(status_code=400, detail="Links em formato inválido")

    out = []
    for item in data[:MAX_LINKS]:
        label = str(item.get("label", "")).strip()[:100]
        url = str(item.get("url", "")).strip()[:500]
        if not label or not url:
            continue
        if not (url.lower().startswith(("http://", "https://")) or url.startswith("/")):
            raise HTTPException(status_code=400, detail=f"Link '{label}' deve ser uma URL (http://...) ou um arquivo enviado")
        out.append({"label": label, "url": url})
    return out


def _save_image(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"Formato não suportado: {ext}")

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOADS_DIR, filename)

    with open(filepath, "wb") as buffer:
        import shutil
        shutil.copyfileobj(file.file, buffer)

    if os.path.getsize(filepath) > MAX_FILE_SIZE:
        os.remove(filepath)
        raise HTTPException(status_code=400, detail="Imagem muito grande (máx 8MB)")

    return filename


def _attach_links(db, themes: list[dict]):
    for t in themes:
        rows = db.execute(
            text("SELECT label, url FROM template_links WHERE theme_id = :id ORDER BY sort_order ASC"),
            {"id": t["id"]}
        ).fetchall()
        t["links"] = [dict(r._mapping) for r in rows]


# ════════════════════════════════════════════════════════════
#  ROTAS PÚBLICAS
# ════════════════════════════════════════════════════════════

@router.get("/public")
def list_public_themes(db=Depends(get_db)):
    rows = db.execute(text("""
        SELECT * FROM template_themes
        WHERE is_published = 1
        ORDER BY sort_order ASC, created_at DESC
    """)).fetchall()

    themes = [dict(r._mapping) for r in rows]
    for t in themes:
        t["image"] = f"/api/templates/image/{t['image_filename']}" if t["image_filename"] else None
    _attach_links(db, themes)
    return themes


@router.get("/image/{filename}")
def get_image(filename: str):
    filepath = os.path.join(UPLOADS_DIR, filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    return FileResponse(filepath)


@router.get("/page/{filename}")
def get_page(filename: str):
    """Serve uma página HTML enviada pelo admin como exemplo (sem precisar de link externo)."""
    safe_name = os.path.basename(filename)
    filepath = os.path.join(PAGES_DIR, safe_name)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Página não encontrada")
    return FileResponse(filepath, media_type="text/html")


@router.post("/upload-page")
async def upload_page(file: UploadFile = File(...), _: str = Depends(get_current_admin)):
    """Admin envia um .html pronto; vira o link de exemplo do tema, sem precisar hospedar em outro lugar."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_PAGE_EXT:
        raise HTTPException(status_code=400, detail="Envie um arquivo .html")

    filename = f"{uuid.uuid4().hex}.html"
    filepath = os.path.join(PAGES_DIR, filename)

    import shutil
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if os.path.getsize(filepath) > MAX_PAGE_SIZE:
        os.remove(filepath)
        raise HTTPException(status_code=400, detail="Arquivo muito grande (máx 10MB)")

    return {"ok": True, "url": f"/api/templates/page/{filename}"}


# ════════════════════════════════════════════════════════════
#  ROTAS ADMIN
# ════════════════════════════════════════════════════════════

@router.get("/")
def list_all_themes(db=Depends(get_db), _: str = Depends(get_current_admin)):
    rows = db.execute(text(
        "SELECT * FROM template_themes ORDER BY sort_order ASC, created_at DESC"
    )).fetchall()
    themes = [dict(r._mapping) for r in rows]
    _attach_links(db, themes)
    return themes


@router.get("/{theme_id}")
def get_theme(theme_id: int, db=Depends(get_db), _: str = Depends(get_current_admin)):
    row = db.execute(text("SELECT * FROM template_themes WHERE id = :id"), {"id": theme_id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Tema não encontrado")
    theme = dict(row._mapping)
    _attach_links(db, [theme])
    return theme


@router.post("/")
async def create_theme(
    title: str = Form(...),
    description: str = Form(...),
    is_published: bool = Form(True),
    links: str = Form("[]"),
    file: UploadFile | None = File(None),
    db=Depends(get_db),
    _: str = Depends(get_current_admin),
):
    parsed_links = _parse_links(links)
    filename = _save_image(file) if (file and file.filename) else None

    result = db.execute(
        text("""
            INSERT INTO template_themes (title, description, image_filename, is_published)
            VALUES (:title, :description, :image, :published)
        """),
        {"title": title, "description": description, "image": filename,
         "published": 1 if is_published else 0}
    )
    db.commit()
    theme_id = result.lastrowid

    for idx, link in enumerate(parsed_links):
        db.execute(
            text("INSERT INTO template_links (theme_id, label, url, sort_order) VALUES (:tid, :label, :url, :order)"),
            {"tid": theme_id, "label": link["label"], "url": link["url"], "order": idx}
        )
    db.commit()

    return {"ok": True, "id": theme_id}


@router.put("/{theme_id}")
async def update_theme(
    theme_id: int,
    title: str = Form(...),
    description: str = Form(...),
    is_published: bool = Form(True),
    links: str = Form("[]"),
    file: UploadFile | None = File(None),
    db=Depends(get_db),
    _: str = Depends(get_current_admin),
):
    existing = db.execute(
        text("SELECT image_filename FROM template_themes WHERE id = :id"), {"id": theme_id}
    ).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Tema não encontrado")

    parsed_links = _parse_links(links)

    params = {
        "title": title, "description": description,
        "published": 1 if is_published else 0, "id": theme_id,
    }

    if file and file.filename:
        new_filename = _save_image(file)
        old_filename = existing.image_filename
        db.execute(
            text("""
                UPDATE template_themes
                SET title = :title, description = :description,
                    image_filename = :image, is_published = :published
                WHERE id = :id
            """),
            {**params, "image": new_filename}
        )
        db.commit()
        if old_filename:
            old_path = os.path.join(UPLOADS_DIR, old_filename)
            if os.path.isfile(old_path):
                os.remove(old_path)
    else:
        db.execute(
            text("""
                UPDATE template_themes
                SET title = :title, description = :description, is_published = :published
                WHERE id = :id
            """),
            params
        )
        db.commit()

    # Substitui os links (no máx. 4)
    db.execute(text("DELETE FROM template_links WHERE theme_id = :id"), {"id": theme_id})
    for idx, link in enumerate(parsed_links):
        db.execute(
            text("INSERT INTO template_links (theme_id, label, url, sort_order) VALUES (:tid, :label, :url, :order)"),
            {"tid": theme_id, "label": link["label"], "url": link["url"], "order": idx}
        )
    db.commit()

    return {"ok": True}


@router.delete("/{theme_id}")
def delete_theme(theme_id: int, db=Depends(get_db), _: str = Depends(get_current_admin)):
    row = db.execute(
        text("SELECT image_filename FROM template_themes WHERE id = :id"), {"id": theme_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Tema não encontrado")

    if row.image_filename:
        path = os.path.join(UPLOADS_DIR, row.image_filename)
        if os.path.isfile(path):
            os.remove(path)

    db.execute(text("DELETE FROM template_themes WHERE id = :id"), {"id": theme_id})
    db.commit()
    return {"ok": True}
