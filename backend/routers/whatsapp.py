"""
whatsapp.py — Notificações WhatsApp
Suporta Evolution API e Z-API
"""

import httpx
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import (
    WA_PROVIDER, ADMIN_WHATSAPP,
    WA_EVOLUTION_URL, WA_EVOLUTION_KEY, WA_INSTANCE_NAME,
    WA_ZAPI_INSTANCE, WA_ZAPI_TOKEN, WA_ZAPI_CLIENT_TOKEN,
)

PLAN_LABEL = {
    "standard": "Standard — R$39,90/mês",
    "plus":     "Plus — R$69,90/mês",
    "pro":      "Pro — R$89,90/mês",
}


async def send_whatsapp(phone: str, message: str):
    """Envia mensagem WhatsApp para o número informado."""
    if WA_PROVIDER == "zapi":
        await _send_zapi(phone, message)
    else:
        await _send_evolution(phone, message)


async def _send_evolution(phone: str, message: str):
    url     = f"{WA_EVOLUTION_URL}/message/sendText/{WA_INSTANCE_NAME}"
    headers = {"apikey": WA_EVOLUTION_KEY, "Content-Type": "application/json"}
    payload = {"number": phone, "text": message}
    async with httpx.AsyncClient(timeout=12) as client:
        try:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            print(f"[WhatsApp Evolution] Mensagem enviada para {phone}")
        except Exception as e:
            print(f"[WhatsApp Evolution] Erro ao enviar: {e}")


async def _send_zapi(phone: str, message: str):
    url = (
        f"https://api.z-api.io/instances/{WA_ZAPI_INSTANCE}"
        f"/token/{WA_ZAPI_TOKEN}/send-text"
    )
    headers = {"Client-Token": WA_ZAPI_CLIENT_TOKEN, "Content-Type": "application/json"}
    payload = {"phone": phone, "message": message}
    async with httpx.AsyncClient(timeout=12) as client:
        try:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            print(f"[WhatsApp Z-API] Mensagem enviada para {phone}")
        except Exception as e:
            print(f"[WhatsApp Z-API] Erro ao enviar: {e}")


async def notify_admin_new_client(client: dict):
    """Notifica o admin quando um novo pagamento é aprovado."""
    plan  = PLAN_LABEL.get(client.get("plan", ""), client.get("plan", ""))
    msg = (
        f"🚀 *NOVO CLIENTE — DIVISIONS TECH*\n\n"
        f"👤 *Nome:* {client.get('name', '')}\n"
        f"📱 *Telefone:* {client.get('phone') or 'Não informado'}\n"
        f"📧 *E-mail:* {client.get('email', '')}\n"
        f"🌐 *Plano:* {plan}\n"
        f"🔗 *Domínio:* {client.get('domain') or 'Não informado'}\n"
        f"💳 *Pagamento:* ✅ APROVADO\n"
        f"📅 *Data:* {client.get('contracted_at', '')}\n"
        f"📅 *Vencimento:* {client.get('expires_at', '')}"
    )
    await send_whatsapp(ADMIN_WHATSAPP, msg)
