"""
seed_portfolio.py — Cadastra os projetos da Divisions Tech no portfólio.

Uso (dentro da pasta backend):
    python seed_portfolio.py

É idempotente: se já existir um projeto com o mesmo título, apenas atualiza
descrição, categoria, tags e link (não duplica e não mexe nas imagens).
Imagens/capas podem ser enviadas depois pelo painel admin (Portfólio > Editar).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from database import engine


def _ensure_schema():
    """Garante a coluna project_url (independente do restante da API)."""
    with engine.begin() as conn:
        col = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'portfolio_projects' "
            "AND COLUMN_NAME = 'project_url'"
        )).scalar()
        if not col:
            conn.execute(text(
                "ALTER TABLE portfolio_projects "
                "ADD COLUMN project_url VARCHAR(500) NULL DEFAULT NULL AFTER tags"
            ))

PROJECTS = [
    {
        "title": "BarberOne",
        "description": (
            "Plataforma completa para barbearias: agendamento online, agenda por barbeiro, "
            "gestão de equipe e horários, pagamentos com cartão e Pix via Mercado Pago e "
            "painel administrativo. App mobile para clientes e versão web."
        ),
        "category": "mobile",
        "tags": "NestJS, Expo, React Native, Next.js, Mercado Pago",
        "project_url": "https://app.barberone.store",
        "sort_order": 1,
    },
    {
        "title": "Eleva One",
        "description": (
            "Sistema de agendamento para salões de beleza femininos: a cliente reserva cabelo, "
            "unhas e outros serviços no mesmo lugar, busca salões por área de atuação e conta "
            "com painel de gestão para o salão. App, versão web e landing page."
        ),
        "category": "mobile",
        "tags": "NestJS, Expo, React Native, Next.js",
        "project_url": "https://elevaone.store",
        "sort_order": 2,
    },
    {
        "title": "EasyFood",
        "description": (
            "Praça de alimentação digital multi-loja: pedidos por QR Code, painéis separados para "
            "cliente, restaurante e administrador, apps mobile, pagamentos e reembolsos com split "
            "via Pagar.me."
        ),
        "category": "sistema",
        "tags": "Flask, React Native, MySQL, Pagar.me",
        "project_url": "https://easyfood.pro",
        "sort_order": 3,
    },
    {
        "title": "lavaê",
        "description": (
            "Aplicativo de agendamento para lava jatos: o cliente escolhe o serviço e o horário "
            "pelo celular, e o lava jato gerencia agenda, equipe e atendimentos em um painel próprio."
        ),
        "category": "mobile",
        "tags": "NestJS, Expo, React Native",
        "project_url": "",
        "sort_order": 4,
    },
    {
        "title": "PDV SaaS",
        "description": (
            "Ponto de venda em nuvem para lojas de rua, no computador e no celular: integração com "
            "maquininhas Mercado Pago e Pagar.me, parcelamento com juros calculado automaticamente, "
            "emissão de cupom fiscal e cobrança por mensalidade."
        ),
        "category": "sistema",
        "tags": "Node.js, MySQL, Mercado Pago, Pagar.me",
        "project_url": "https://pdv.divisionstech.com",
        "sort_order": 5,
    },
    {
        "title": "ERP Divisions",
        "description": (
            "ERP modular para empresas: RH com folha de pagamento (tabelas INSS/IRRF), ponto "
            "eletrônico com GPS e home office, além de módulos financeiro, frotas, produção e qualidade."
        ),
        "category": "sistema",
        "tags": "Flask, Python, MySQL",
        "project_url": "",
        "sort_order": 6,
    },
]


def main():
    _ensure_schema()
    created = updated = 0
    with engine.begin() as conn:
        for p in PROJECTS:
            row = conn.execute(
                text("SELECT id FROM portfolio_projects WHERE title = :t LIMIT 1"),
                {"t": p["title"]},
            ).fetchone()
            params = {**p, "url": p["project_url"] or None}
            if row:
                conn.execute(
                    text("""
                        UPDATE portfolio_projects
                        SET description = :description, category = :category, tags = :tags,
                            project_url = :url, sort_order = :sort_order, is_published = 1
                        WHERE id = :id
                    """),
                    {**params, "id": row.id},
                )
                updated += 1
            else:
                conn.execute(
                    text("""
                        INSERT INTO portfolio_projects
                            (title, description, category, tags, project_url, sort_order, is_published)
                        VALUES (:title, :description, :category, :tags, :url, :sort_order, 1)
                    """),
                    params,
                )
                created += 1
    print(f"Portfólio atualizado: {created} criado(s), {updated} atualizado(s).")


if __name__ == "__main__":
    main()
