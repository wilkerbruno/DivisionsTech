FROM python:3.11-slim

WORKDIR /app

# Instala dependências
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o projeto
COPY . .

# Porta
EXPOSE 8000

# Variável que indica ambiente de produção (não tenta abrir navegador)
ENV PRODUCAO=true

# Inicia o backend com 1 worker — mais previsível para health checks
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]