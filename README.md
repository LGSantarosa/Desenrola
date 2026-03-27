# desenrola!

Plataforma de troca de habilidades entre pessoas. Cadastre o que voce sabe, encontre quem sabe o que voce quer aprender e troque conhecimento usando um sistema justo de creditos.

## Stack

**Frontend:** HTML, CSS, JavaScript, Tailwind CSS

**Backend:** Python, FastAPI

**Banco de dados:** PostgreSQL

## Estrutura

```
Desenrola-/
├── frontend/
│   ├── index.html
│   ├── css/
│   ├── js/
│   ├── pages/
│   └── assets/images/
└── backend/
    └── app/
        ├── core/
        ├── models/
        ├── schemas/
        ├── routes/
        └── services/
```

## Funcionalidades

- Cadastro e autenticacao de usuarios (Admin e Cliente)
- CRUD de categorias de skills (Admin)
- Cadastro de skills que ensina e quer aprender
- Sistema de matching entre usuarios complementares
- Proposta e gerenciamento de trocas
- Sistema de creditos por hora
- Avaliacao pos-troca
- Upload de avatar
- Filtros de pesquisa por categoria e disponibilidade
- Interface responsiva

## Como rodar

### Frontend
Abra `frontend/index.html` no navegador.

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
