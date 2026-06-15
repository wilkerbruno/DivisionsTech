"""clients.py — CRUD de clientes (MySQL)"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import text
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_db
from routers.auth import get_current_admin

router = APIRouter()


@router.get("/")
def list_clients(
    search: str = "",
    status: str = "",
    plan:   str = "",
    db=Depends(get_db),
    _: str = Depends(get_current_admin),
):
    q      = "SELECT * FROM clients WHERE 1=1"
    params = {}

    if search:
        q += " AND (name LIKE :s OR email LIKE :s OR phone LIKE :s OR cpf LIKE :s)"
        params["s"] = f"%{search}%"
    if status:
        q += " AND status = :status"
        params["status"] = status
    if plan:
        q += " AND plan = :plan"
        params["plan"] = plan

    q += " ORDER BY created_at DESC"
    rows = db.execute(text(q), params).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/{client_id}")
def get_client(
    client_id: int,
    db=Depends(get_db),
    _: str = Depends(get_current_admin),
):
    row = db.execute(
        text("SELECT * FROM clients WHERE id = :id LIMIT 1"), {"id": client_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return dict(row._mapping)


class ClientUpdate(BaseModel):
    name:       Optional[str] = None
    cpf:        Optional[str] = None
    email:      Optional[str] = None
    phone:      Optional[str] = None
    plan:       Optional[str] = None
    domain:     Optional[str] = None
    status:     Optional[str] = None
    expires_at: Optional[str] = None


@router.put("/{client_id}")
def update_client(
    client_id: int,
    data: ClientUpdate,
    db=Depends(get_db),
    _: str = Depends(get_current_admin),
):
    fields = {k: v for k, v in data.dict().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

    set_clause = ", ".join(f"{k} = :{k}" for k in fields)
    fields["_id"] = client_id
    db.execute(
        text(f"UPDATE clients SET {set_clause} WHERE id = :_id"), fields
    )
    db.commit()
    return {"ok": True}


@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    db=Depends(get_db),
    _: str = Depends(get_current_admin),
):
    db.execute(text("DELETE FROM clients WHERE id = :id"), {"id": client_id})
    db.commit()
    return {"ok": True}
