FROM python:3.11-slim

WORKDIR /app

# Instala dependências
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o projeto
COPY . .

# Porta
EXPOSE 8000

# Inicia o backend (que também serve o frontend via StaticFiles)
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]