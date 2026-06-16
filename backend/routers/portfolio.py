"""portfolio.py — CRUD de projetos do portfólio com upload de imagens"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy import text
from typing import List, Optional
import os, sys, uuid, shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import get_db
from routers.auth import get_current_admin

router = APIRouter()

BACKEND_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR  = os.path.join(BACKEND_DIR, "uploads", "portfolio")
os.makedirs(UPLOADS_DIR, exist_ok=True)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 8 * 1024 * 1024  # 8MB por imagem


def _save_image(file: UploadFile) -> str:
    """Salva uma imagem no disco e retorna o nome do arquivo gerado."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"Formato não suportado: {ext}")

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOADS_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Verifica tamanho após salvar
    if os.path.getsize(filepath) > MAX_FILE_SIZE:
        os.remove(filepath)
        raise HTTPException(status_code=400, detail="Imagem muito grande (máx 8MB)")

    return filename


# ════════════════════════════════════════════════════════════
#  ROTAS PÚBLICAS (sem autenticação) — usadas na página do site
# ════════════════════════════════════════════════════════════

@router.get("/public")
def list_public_projects(category: str = "", db=Depends(get_db)):
    """Lista projetos publicados para exibir no site."""
    q = """
        SELECT * FROM portfolio_projects
        WHERE is_published = 1
    """
    params = {}
    if category and category != "all":
        q += " AND category = :cat"
        params["cat"] = category
    q += " ORDER BY sort_order ASC, created_at DESC"

    projects = db.execute(text(q), params).fetchall()
    result = []

    for p in projects:
        proj = dict(p._mapping)
        images = db.execute(
            text("""
                SELECT filename, is_cover FROM portfolio_images
                WHERE project_id = :pid
                ORDER BY is_cover DESC, sort_order ASC
            """),
            {"pid": proj["id"]}
        ).fetchall()
        proj["images"] = [f"/api/portfolio/image/{img.filename}" for img in images]
        proj["tags_list"] = [t.strip() for t in (proj["tags"] or "").split(",") if t.strip()]
        result.append(proj)

    return result


@router.get("/image/{filename}")
def get_image(filename: str):
    """Serve uma imagem do portfólio."""
    filepath = os.path.join(UPLOADS_DIR, filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    return FileResponse(filepath)


# ════════════════════════════════════════════════════════════
#  ROTAS ADMIN (requer login)
# ════════════════════════════════════════════════════════════

@router.get("/")
def list_all_projects(db=Depends(get_db), _: str = Depends(get_current_admin)):
    """Lista todos os projetos (incluindo não publicados) para o admin."""
    projects = db.execute(
        text("SELECT * FROM portfolio_projects ORDER BY sort_order ASC, created_at DESC")
    ).fetchall()

    result = []
    for p in projects:
        proj = dict(p._mapping)
        images = db.execute(
            text("""
                SELECT id, filename, is_cover, sort_order FROM portfolio_images
                WHERE project_id = :pid
                ORDER BY is_cover DESC, sort_order ASC
            """),
            {"pid": proj["id"]}
        ).fetchall()
        proj["images"] = [dict(img._mapping) for img in images]
        result.append(proj)

    return result


@router.get("/{project_id}")
def get_project(project_id: int, db=Depends(get_db),
                _: str = Depends(get_current_admin)):
    row = db.execute(
        text("SELECT * FROM portfolio_projects WHERE id = :id"), {"id": project_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    proj = dict(row._mapping)
    images = db.execute(
        text("""
            SELECT id, filename, is_cover, sort_order FROM portfolio_images
            WHERE project_id = :pid ORDER BY is_cover DESC, sort_order ASC
        """),
        {"pid": project_id}
    ).fetchall()
    proj["images"] = [dict(img._mapping) for img in images]
    return proj


@router.post("/")
async def create_project(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form("web"),
    tags: str = Form(""),
    is_published: bool = Form(True),
    files: List[UploadFile] = File(default=[]),
    db=Depends(get_db),
    _: str = Depends(get_current_admin),
):
    """Cria um novo projeto com upload de múltiplas imagens."""
    result = db.execute(
        text("""
            INSERT INTO portfolio_projects (title, description, category, tags, is_published)
            VALUES (:title, :description, :category, :tags, :published)
        """),
        {
            "title": title, "description": description,
            "category": category, "tags": tags,
            "published": 1 if is_published else 0,
        }
    )
    db.commit()
    project_id = result.lastrowid

    # Salva as imagens
    for idx, file in enumerate(files):
        if not file.filename:
            continue
        filename = _save_image(file)
        db.execute(
            text("""
                INSERT INTO portfolio_images (project_id, filename, sort_order, is_cover)
                VALUES (:pid, :fn, :order, :cover)
            """),
            {"pid": project_id, "fn": filename, "order": idx, "cover": 1 if idx == 0 else 0}
        )
    db.commit()

    return {"ok": True, "id": project_id}


@router.put("/{project_id}")
async def update_project(
    project_id: int,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form("web"),
    tags: str = Form(""),
    is_published: bool = Form(True),
    files: List[UploadFile] = File(default=[]),
    db=Depends(get_db),
    _: str = Depends(get_current_admin),
):
    """Atualiza um projeto. Novas imagens enviadas são adicionadas às existentes."""
    existing = db.execute(
        text("SELECT id FROM portfolio_projects WHERE id = :id"), {"id": project_id}
    ).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    db.execute(
        text("""
            UPDATE portfolio_projects
            SET title = :title, description = :description,
                category = :category, tags = :tags, is_published = :published
            WHERE id = :id
        """),
        {
            "title": title, "description": description,
            "category": category, "tags": tags,
            "published": 1 if is_published else 0, "id": project_id,
        }
    )
    db.commit()

    # Adiciona novas imagens, se houver
    if files and any(f.filename for f in files):
        current_max = db.execute(
            text("SELECT COALESCE(MAX(sort_order), -1) FROM portfolio_images WHERE project_id = :pid"),
            {"pid": project_id}
        ).scalar()

        for idx, file in enumerate(files):
            if not file.filename:
                continue
            filename = _save_image(file)
            db.execute(
                text("""
                    INSERT INTO portfolio_images (project_id, filename, sort_order, is_cover)
                    VALUES (:pid, :fn, :order, 0)
                """),
                {"pid": project_id, "fn": filename, "order": current_max + idx + 1}
            )
        db.commit()

    return {"ok": True}


@router.delete("/{project_id}")
def delete_project(project_id: int, db=Depends(get_db),
                   _: str = Depends(get_current_admin)):
    """Exclui um projeto e todas suas imagens (banco e disco)."""
    images = db.execute(
        text("SELECT filename FROM portfolio_images WHERE project_id = :pid"),
        {"pid": project_id}
    ).fetchall()

    for img in images:
        filepath = os.path.join(UPLOADS_DIR, img.filename)
        if os.path.isfile(filepath):
            os.remove(filepath)

    db.execute(text("DELETE FROM portfolio_projects WHERE id = :id"), {"id": project_id})
    db.commit()
    return {"ok": True}


@router.delete("/{project_id}/image/{image_id}")
def delete_image(project_id: int, image_id: int, db=Depends(get_db),
                 _: str = Depends(get_current_admin)):
    """Remove uma imagem específica de um projeto."""
    img = db.execute(
        text("SELECT filename FROM portfolio_images WHERE id = :id AND project_id = :pid"),
        {"id": image_id, "pid": project_id}
    ).fetchone()
    if not img:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")

    filepath = os.path.join(UPLOADS_DIR, img.filename)
    if os.path.isfile(filepath):
        os.remove(filepath)

    db.execute(text("DELETE FROM portfolio_images WHERE id = :id"), {"id": image_id})
    db.commit()
    return {"ok": True}


@router.put("/{project_id}/cover/{image_id}")
def set_cover_image(project_id: int, image_id: int, db=Depends(get_db),
                    _: str = Depends(get_current_admin)):
    """Define qual imagem é a capa do projeto."""
    db.execute(
        text("UPDATE portfolio_images SET is_cover = 0 WHERE project_id = :pid"),
        {"pid": project_id}
    )
    db.execute(
        text("UPDATE portfolio_images SET is_cover = 1 WHERE id = :id AND project_id = :pid"),
        {"id": image_id, "pid": project_id}
    )
    db.commit()
    return {"ok": True}