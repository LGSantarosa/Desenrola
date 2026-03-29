# desenrola!

Plataforma de troca de habilidades entre pessoas. Cadastre o que voce sabe, encontre quem sabe o que voce quer aprender e troque conhecimento — sem custo, so troca.

## Stack

**Frontend:** HTML, CSS, JavaScript

**Backend:** Python, FastAPI

**Banco de dados:** MySQL

## Modelagem do Banco

![Diagrama ER](docs/db.png)

## Estrutura

```
Desenrola/
├── frontend/
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── profile.html
│   ├── css/
│   │   ├── style.css
│   │   └── app.css
│   ├── js/
│   │   ├── main.js
│   │   ├── validation.js
│   │   ├── auth.js
│   │   ├── register.js
│   │   ├── login.js
│   │   └── profile.js
│   └── assets/images/
├── backend/
│   ├── schema.sql
│   ├── requirements.txt
│   ├── .env
│   └── app/
│       ├── main.py
│       ├── core/
│       │   ├── database.py
│       │   └── auth.py
│       ├── models/
│       │   └── user.py
│       ├── schemas/
│       │   └── user.py
│       ├── routes/
│       │   ├── auth.py
│       │   └── user.py
│       └── services/
└── db.png
```

## Funcionalidades

- Cadastro e autenticacao de usuarios (Admin e Cliente)
- CRUD completo de usuario (criar, ver, editar, excluir)
- Autenticacao com senha criptografada (bcrypt) e JWT
- Validacao de formularios com RegEx e JavaScript
- Mascaras de input (CPF, telefone)
- Interface responsiva (desktop e mobile)
- Identificacao do usuario autenticado em todas as telas

## Como rodar

### Banco de dados
Importe o arquivo `backend/schema.sql` no MySQL Workbench ou execute via terminal:
```bash
mysql -u root -p < backend/schema.sql
```

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
Abra `frontend/index.html` no navegador.
