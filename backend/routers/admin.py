"""admin.py — Estatísticas, exportação CSV e configurações"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import text
import io, csv
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_db
from security import hash_password
from routers.auth import get_current_admin

router = APIRouter()

PLAN_LABEL   = {"standard": "Standard", "plus": "Plus", "pro": "Pro"}
STATUS_LABEL = {"active": "Ativo", "pending": "Pendente", "cancelled": "Cancelado"}
PAY_LABEL    = {
    "pending":    "Pendente",
    "approved":   "Aprovado",
    "failed":     "Falhou",
    "in_process": "Em processamento",
    "rejected":   "Rejeitado",
}


@router.get("/stats")
def get_stats(db=Depends(get_db), _: str = Depends(get_current_admin)):
    total   = db.execute(text("SELECT COUNT(*) FROM clients")).scalar() or 0
    active  = db.execute(text("SELECT COUNT(*) FROM clients WHERE status = 'active'")).scalar() or 0
    pending = db.execute(text("SELECT COUNT(*) FROM clients WHERE payment_status = 'pending'")).scalar() or 0

    mrr = db.execute(text("""
        SELECT COALESCE(SUM(
            CASE plan
                WHEN 'standard' THEN 39.90
                WHEN 'plus'     THEN 69.90
                WHEN 'pro'      THEN 89.90
                ELSE 0
            END
        ), 0)
        FROM clients WHERE status = 'active'
    """)).scalar() or 0

    by_plan = db.execute(
        text("SELECT plan, COUNT(*) AS total FROM clients GROUP BY plan ORDER BY total DESC")
    ).fetchall()

    recent = db.execute(text("""
        SELECT name, plan, status, contracted_at
        FROM clients ORDER BY created_at DESC LIMIT 5
    """)).fetchall()

    return {
        "total_clients":   int(total),
        "active_clients":  int(active),
        "pending_clients": int(pending),
        "mrr":             round(float(mrr), 2),
        "by_plan":         [dict(r._mapping) for r in by_plan],
        "recent":          [dict(r._mapping) for r in recent],
    }


@router.get("/export/csv")
def export_csv(db=Depends(get_db), _: str = Depends(get_current_admin)):
    rows = db.execute(
        text("SELECT * FROM clients ORDER BY created_at DESC")
    ).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Nome", "CPF", "E-mail", "Telefone",
        "Plano", "Domínio", "Tem Domínio",
        "Status", "Status Pagamento",
        "Contratado em", "Vence em", "Criado em",
    ])

    for r in rows:
        d = dict(r._mapping)
        writer.writerow([
            d["id"], d["name"], d["cpf"] or "", d["email"], d["phone"] or "",
            PLAN_LABEL.get(d["plan"], d["plan"]),
            d["domain"] or "",
            "Sim" if d["has_domain"] else "Não",
            STATUS_LABEL.get(d["status"], d["status"]),
            PAY_LABEL.get(d["payment_status"], d["payment_status"]),
            d["contracted_at"] or "", d["expires_at"] or "",
            str(d["created_at"]),
        ])

    output.seek(0)
    content = output.getvalue().encode("utf-8-sig")  # abre certo no Excel
    return StreamingResponse(
        iter([content]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="clientes_divisions_tech.csv"'},
    )


@router.post("/change-password")
def change_password(data: dict, username: str = Depends(get_current_admin),
                    db=Depends(get_db)):
    new_password = data.get("password", "")
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Senha deve ter ao menos 6 caracteres")

    hashed = hash_password(new_password)
    db.execute(
        text("UPDATE admins SET password = :p WHERE username = :u"),
        {"p": hashed, "u": username}
    )
    db.commit()
    return {"ok": True}
