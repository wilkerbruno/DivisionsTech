#!/bin/bash
# ════════════════════════════════════════════════════════════
#  Divisions Tech — Script de inicialização do backend
# ════════════════════════════════════════════════════════════
set -e
cd "$(dirname "$0")"

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║     Divisions Tech — Backend v2.0        ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

echo "📦 Instalando dependências..."
pip install -r requirements.txt -q
echo "   ✅ Dependências instaladas"
echo ""

echo "🗄️  Criando/verificando tabelas no MySQL..."
python3 create_tables.py
echo ""

echo "🚀 Iniciando servidor na porta 8000..."
echo "   Documentação: http://localhost:8000/docs"
echo ""
python3 main.py
