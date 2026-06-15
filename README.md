# Divisions Tech — Sistema Completo

## Estrutura do Projeto

```
divisions-tech/
├── index.html              # Página inicial
├── admin/
│   └── index.html          # Painel administrativo
├── assets/
│   ├── css/style.css
│   └── js/script.js
├── pages/
│   ├── servicos.html
│   ├── hospedagem.html     # Com modal de checkout
│   ├── portfolio.html
│   ├── sobre.html
│   ├── contato.html
│   └── obrigado.html       # Pós-pagamento
└── backend/
    ├── config.py           # ⚠️ CONFIGURE AQUI
    ├── database.py         # Conexão MySQL
    ├── create_tables.py    # Script de criação das tabelas
    ├── main.py             # Servidor FastAPI
    ├── requirements.txt
    ├── start.sh            # Script de inicialização
    └── routers/
        ├── auth.py         # Login JWT
        ├── clients.py      # CRUD clientes
        ├── payments.py     # Mercado Pago
        ├── webhooks.py     # IPN Mercado Pago
        ├── admin.py        # Stats + CSV export
        └── whatsapp.py     # Notificações WhatsApp
```

---

## Instalação e Configuração

### 1. Configure as variáveis em `backend/config.py`

```python
MP_ACCESS_TOKEN = "seu_token_mercado_pago"
BASE_URL        = "https://divisions.tech"      # URL do seu servidor
ADMIN_WHATSAPP  = "5583993654478"               # DDI+DDD+número
WA_PROVIDER     = "evolution"                   # ou "zapi"
WA_EVOLUTION_URL = "http://seu-evolution:8080"
WA_EVOLUTION_KEY = "sua_api_key"
JWT_SECRET      = "chave_aleatoria_segura_32chars"
```

### 2. Instale as dependências

```bash
cd backend
pip install -r requirements.txt
```

### 3. Crie as tabelas no MySQL (rode UMA vez)

```bash
python create_tables.py
```

### 4. Inicie o servidor

```bash
bash start.sh
# ou
python main.py
```

---

## Banco de Dados MySQL

**String de conexão:**
```
mysql+pymysql://mysql:0h5j6srwidut7rpv3uwz@easypanel.pontocomdesconto.com.br:3020/divisionstech
```

**Tabelas criadas:**
- `admins` — usuários do painel admin
- `clients` — clientes e suas contratações
- `payments` — histórico de pagamentos

---

## Acesso ao Painel Admin

URL: `/admin/index.html`  
Usuário padrão: `admin`  
Senha padrão: `admin123`  
⚠️ **Troque a senha imediatamente após o primeiro acesso!**

---

## API Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/auth/login` | Login admin |
| GET | `/api/clients/` | Listar clientes |
| PUT | `/api/clients/{id}` | Editar cliente |
| DELETE | `/api/clients/{id}` | Excluir cliente |
| POST | `/api/payments/checkout` | Criar checkout MP |
| POST | `/api/webhooks/mercadopago` | Webhook IPN |
| GET | `/api/admin/stats` | Estatísticas |
| GET | `/api/admin/export/csv` | Exportar CSV |
| POST | `/api/admin/change-password` | Alterar senha |

Documentação interativa: `http://localhost:8000/docs`

---

## Fluxo de Contratação

1. Cliente acessa `pages/hospedagem.html`
2. Clica em "Contratar Agora" → abre modal
3. Pergunta se já tem domínio
4. Preenche dados (nome, email, telefone, CPF)
5. Redireciona para **Mercado Pago** (cartão/Pix/boleto)
6. Após pagamento → webhook atualiza status no MySQL
7. Admin recebe notificação no **WhatsApp**
8. Cliente é redirecionado para `pages/obrigado.html`
