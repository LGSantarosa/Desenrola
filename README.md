<p align="center">
  <img src="frontend/assets/images/camaleon.png" alt="desenrola!" width="360">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/HTML%20%7C%20CSS%20%7C%20JS-00DC82?style=flat-square&logo=html5&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-FF6B00?style=flat-square&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Jinja2-00DC82?style=flat-square&logo=jinja&logoColor=white"/>
  <img src="https://img.shields.io/badge/MySQL-FF6B00?style=flat-square&logo=mysql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Python-00DC82?style=flat-square&logo=python&logoColor=white"/>
</p>

<p align="center">
  Plataforma de troca de habilidades entre pessoas.<br>
  Cadastre o que voce sabe, encontre quem sabe o que voce quer aprender e troque conhecimento — sem custo, so troca.
</p>

<img src="https://capsule-render.vercel.app/api?type=rect&color=00DC82&height=2&width=100%25" width="100%"/>

## Preview

<p align="center">
  <img src="docs/Screenshot_1.png" alt="Landing page" width="80%">
  <img src="docs/Screenshot_2.png" alt="Categorias e footer" width="80%">
  <img src="docs/Screenshot_3.png" alt="Feed e descobrir pessoas" width="80%">
</p>

<img src="https://capsule-render.vercel.app/api?type=rect&color=FF6B00&height=2&width=100%25" width="100%"/>

## Modelagem do Banco

<p align="center">
  <img width="800" height="509" alt="image" src="https://github.com/user-attachments/assets/c5f24831-d63b-4edb-aaf9-3e4e0a296fec" />

</p>


## Funcionalidades

```
🟢 Cadastro e autenticacao de usuarios (Admin e Cliente)
🟢 CRUD completo de usuario (criar, ver, editar, excluir)
🟢 Autenticacao com senha criptografada (bcrypt) e JWT
🟢 Validacao de formularios com RegEx e JavaScript
🟢 Mascaras de input (CPF, telefone)
🟢 Interface responsiva (desktop e mobile)
🟢 Identificacao do usuario autenticado em todas as telas
🟠 Sistema de matching entre usuarios (Sprint 2)
🟠 Solicitacao de troca de habilidades (Sprint 2)
🟠 Upload de avatar (Sprint 2)
🟠 Filtros de pesquisa por categoria (Sprint 2)
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=FF6B00&height=2&width=100%25" width="100%"/>

## Estrutura

```
Desenrola/
├── backend/
│   ├── seed.py
│   ├── requirements.txt
│   ├── .env
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── database.py
│   │   │   └── auth.py
│   │   ├── schemas/
│   │   │   └── user.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── user.py
│   │       ├── skill.py
│   │       ├── match.py
│   │       ├── swap.py
│   │       ├── feed.py
│   │       ├── post.py
│   │       └── upload.py
│   ├── templates/
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── onboarding.html
│   │   ├── match.html
│   │   ├── profile.html
│   │   ├── swaps.html
│   │   └── user.html
│   └── static/
│       ├── css/
│       ├── js/
│       └── assets/images/
├── frontend/
└── docs/
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=00DC82&height=2&width=100%25" width="100%"/>

## Como rodar

### 1. Usuario do MySQL
No Ubuntu o `root` usa `auth_socket` e nao aceita senha via TCP. Crie um usuario dedicado:
```bash
sudo mysql -e "CREATE USER 'desenrola'@'localhost' IDENTIFIED BY 'desenrola123'; GRANT ALL PRIVILEGES ON desenrola.* TO 'desenrola'@'localhost'; FLUSH PRIVILEGES;"
```

### 2. Variaveis de ambiente
Crie o arquivo `backend/.env`:
```env
DB_HOST=localhost
DB_USER=desenrola
DB_PASSWORD=desenrola123
DB_NAME=desenrola
DB_PORT=3306
JWT_SECRET=troque-esta-chave
```

### 3. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Banco de dados
O `seed.py` cria o database, todas as tabelas e popula com dados de exemplo:
```bash
python seed.py
```

### 5. Subir o servidor
```bash
uvicorn app.main:app --reload
```

### Acessar
Abra `http://localhost:8000` no navegador. O backend serve as paginas via Jinja2.

<img src="https://capsule-render.vercel.app/api?type=rect&color=00DC82&height=2&width=100%25" width="100%"/>

## Contribuidores

<a href="https://github.com/LGSantarosa">
  <img src="https://github.com/LGSantarosa.png" width="80" style="border-radius:50%" alt="Luiz Santarosa"/>
</a>
<a href="https://github.com/Mateuscruz19">
  <img src="https://github.com/Mateuscruz19.png" width="80" style="border-radius:50%" alt="Mateus Cruz"/>
</a>
