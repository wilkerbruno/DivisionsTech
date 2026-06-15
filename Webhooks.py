"""webhooks.py — Webhook Mercado Pago IPN (MySQL)"""

from fastapi import APIRouter, Request, BackgroundTasks, Depends
from sqlalchemy import text
from datetime import datetime, timedelta
import mercadopago
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_db, get_conn
from config import MP_ACCESS_TOKEN
from routers.whatsapp import notify_admin_new_client

router = APIRouter()
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)


@router.post("/mercadopago")
async def mp_webhook(request: Request, background_tasks: BackgroundTasks, db=Depends(get_db)):
    try:
        body = await request.json()
    except Exception:
        body = {}

    topic       = body.get("type") or request.query_params.get("topic", "")
    resource_id = (body.get("data", {}).get("id")
                   or request.query_params.get("id", ""))

    if topic == "payment" and resource_id:
        payment_info = sdk.payment().get(resource_id)
        if payment_info["status"] == 200:
            payment   = payment_info["response"]
            mp_status = payment.get("status")
            client_id = payment.get("external_reference")
            mp_pay_id = str(payment.get("id", ""))

            if not client_id:
                return {"ok": True}

            now     = datetime.now().strftime("%d/%m/%Y %H:%M")
            expires = (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")

            if mp_status == "approved":
                db.execute(
                    text("""
                        UPDATE clients
                        SET payment_status='approved', status='active',
                            contracted_at=:ca, expires_at=:exp, payment_id=:pid
                        WHERE id=:id
                    """),
                    {"ca": now, "exp": expires, "pid": mp_pay_id, "id": client_id}
                )
                db.commit()

                # Busca cliente para notificar
                client = db.execute(
                    text("SELECT * FROM clients WHERE id = :id"), {"id": client_id}
                ).fetchone()

                if client:
                    background_tasks.add_task(
                        notify_admin_new_client, dict(client._mapping)
                    )
            else:
                db.execute(
                    text("UPDATE clients SET payment_status=:s WHERE id=:id"),
                    {"s": mp_status, "id": client_id}
                )
                db.commit()

    return {"ok": True}