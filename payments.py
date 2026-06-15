"""payments.py — Integração Mercado Pago (MySQL)"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import text
from datetime import datetime, timedelta
import mercadopago
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_db
from config import MP_ACCESS_TOKEN, BASE_URL, PLANS

router = APIRouter()
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)


class CheckoutRequest(BaseModel):
    name: str
    email: str
    phone: str
    cpf: Optional[str] = None
    plan: str
    has_domain: bool
    domain: Optional[str] = None


@router.post("/checkout")
def create_checkout(req: CheckoutRequest, db=Depends(get_db)):
    if req.plan not in PLANS:
        raise HTTPException(status_code=400, detail="Plano inválido")

    plan_info = PLANS[req.plan]

    # Insere cliente como pending
    result = db.execute(
        text("""
            INSERT INTO clients (name, cpf, email, phone, plan, domain, has_domain, status, payment_status)
            VALUES (:name, :cpf, :email, :phone, :plan, :domain, :has_domain, 'pending', 'pending')
        """),
        {
            "name": req.name, "cpf": req.cpf or None,
            "email": req.email, "phone": req.phone,
            "plan": req.plan, "domain": req.domain or None,
            "has_domain": 1 if req.has_domain else 0,
        }
    )
    db.commit()
    client_id = result.lastrowid

    # Preferência Mercado Pago
    preference_data = {
        "items": [{
            "title": f"Hospedagem {plan_info['name']} — Divisions Tech",
            "description": f"Plano {plan_info['name']} mensal",
            "quantity": 1,
            "unit_price": plan_info["price"],
            "currency_id": "BRL",
        }],
        "payer": {"name": req.name, "email": req.email},
        "back_urls": {
            "success": f"{BASE_URL}/api/payments/success?client_id={client_id}",
            "failure": f"{BASE_URL}/api/payments/failure?client_id={client_id}",
            "pending": f"{BASE_URL}/api/payments/pending?client_id={client_id}",
        },
        "auto_return": "approved",
        "notification_url": f"{BASE_URL}/api/webhooks/mercadopago",
        "external_reference": str(client_id),
        "statement_descriptor": "DIVISIONS TECH",
    }

    result_mp = sdk.preference().create(preference_data)
    if result_mp["status"] != 201:
        raise HTTPException(status_code=500, detail="Erro ao criar preferência no Mercado Pago")

    pref = result_mp["response"]

    # Salva preference_id
    db.execute(
        text("UPDATE clients SET payment_id = :pid WHERE id = :id"),
        {"pid": pref["id"], "id": client_id}
    )
    db.commit()

    return {
        "client_id": client_id,
        "preference_id": pref["id"],
        "init_point": pref["init_point"],
        "sandbox_init_point": pref.get("sandbox_init_point"),
    }


@router.get("/success")
def payment_success(client_id: int, payment_id: str = None,
                    status: str = None, db=Depends(get_db)):
    now     = datetime.now().strftime("%d/%m/%Y %H:%M")
    expires = (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")
    db.execute(
        text("""
            UPDATE clients
            SET payment_status='approved', status='active',
                contracted_at=:ca, expires_at=:exp, payment_id=:pid
            WHERE id=:id
        """),
        {"ca": now, "exp": expires, "pid": payment_id or "", "id": client_id}
    )
    db.commit()
    # Redireciona para página de obrigado
    site = BASE_URL.split(":8000")[0]
    return RedirectResponse(url=f"{site}/pages/obrigado.html")


@router.get("/failure")
def payment_failure(client_id: int, db=Depends(get_db)):
    db.execute(
        text("UPDATE clients SET payment_status='failed' WHERE id=:id"),
        {"id": client_id}
    )
    db.commit()
    site = BASE_URL.split(":8000")[0]
    return RedirectResponse(url=f"{site}/pages/hospedagem.html?error=1")


@router.get("/pending")
def payment_pending(client_id: int, db=Depends(get_db)):
    db.execute(
        text("UPDATE clients SET payment_status='in_process' WHERE id=:id"),
        {"id": client_id}
    )
    db.commit()
    site = BASE_URL.split(":8000")[0]
    return RedirectResponse(url=f"{site}/pages/hospedagem.html?pending=1")