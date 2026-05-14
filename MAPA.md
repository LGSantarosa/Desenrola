# MAPA — Desenrola

Cola rapida pra achar o arquivo certo na hora da prova.

## Como subir o sistema

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload     # http://localhost:8000
python seed.py                    # recria DB do zero (drop + create + seed)
```

Usuarios de teste: `lucas@email.com`, `ana@email.com`, ... — senha `123456`.

---

## BANCO DE DADOS

| Arquivo | Pra que serve |
|---|---|
| `backend/seed.py` | Cria DB, todas as tabelas e popula com 10 usuarios + 15 posts |
| `backend/app/core/database.py` | Conexao MySQL e dependencia `get_db()` injetada nas rotas |

**Tabelas:** `user`, `category`, `skill`, `user_skill` (teaches/learns), `swap_request`, `post`.

Pra mexer no schema → editar `seed.py` e rodar `python seed.py` de novo.

---

## AUTENTICACAO / VALIDACAO

| Arquivo | Pra que serve |
|---|---|
| `backend/app/core/auth.py` | JWT (HS256), bcrypt, cookie `session` (30 min, sliding) |
| `backend/app/core/validation.py` | Regras dos forms: nome (5+), email (regex), CPF (digito verificador), phone (DDD), birth_date (16+), senha forte |

---

## ROTAS — paginas (GET) que renderizam HTML

`backend/app/main.py`

| Rota | Template |
|---|---|
| `GET /` | `index.html` |
| `GET /login` | `login.html` |
| `GET /register` | `register.html` |
| `GET /dashboard` | `dashboard.html` |
| `GET /onboarding` | `onboarding.html` |
| `GET /match` | `match.html` |
| `GET /profile` | `profile.html` |
| `GET /swaps` | `swaps.html` |
| `GET /user/{id}` | `user.html` |

---

## ROTAS — acoes (POST)

| Arquivo | Endpoints |
|---|---|
| `backend/app/routes/auth.py` | `POST /auth/register`, `/auth/login`, `/auth/logout` |
| `backend/app/routes/user.py` | `POST /users/me/update`, `/users/me/delete` |
| `backend/app/routes/skill.py` | `POST /skills/me/save` (apaga tudo e reinsere) |
| `backend/app/routes/swap.py` | `POST /swaps/create`, `/swaps/{id}/accept`, `/swaps/{id}/reject` |
| `backend/app/routes/post.py` | `POST /posts/create`, `/posts/{id}/delete` |
| `backend/app/routes/upload.py` | `POST /upload/avatar` |

---

## FRONT — templates (Jinja2)

`backend/templates/`

| Arquivo | Tela |
|---|---|
| `index.html` | Landing page publica |
| `login.html` | Form de login |
| `register.html` | Form de cadastro |
| `dashboard.html` | Feed + descobrir pessoas (com filtro de categoria) |
| `onboarding.html` | Selecao de skills (ensina/aprende) + upload de avatar |
| `match.html` | Estilo Tinder (swipe) |
| `profile.html` | Editar dados, trocar senha, deletar conta |
| `swaps.html` | Trocas recebidas e enviadas (aceitar / recusar) |
| `user.html` | Perfil publico de outro usuario |
| `_nav.html` | Navbar reutilizada (include) |

---

## FRONT — JavaScript

`backend/static/js/`

| Arquivo | Pra que serve |
|---|---|
| `main.js` | Landing: scroll reveal e menu mobile |
| `validation.js` | Compartilhado: regex, mascaras (CPF/phone), validadores |
| `login.js` | Validacao basica de email/senha |
| `register.js` | Mascaras + validacoes do form de cadastro |
| `dashboard.js` | Preview de imagem ao postar + modal de exclusao |
| `onboarding.js` | Avatar, accordion de categorias, navegacao steps |
| `profile.js` | Validacoes + modal de exclusao da conta |
| `match.js` | Swipe Tinder + modal de selecao de skills |
| `swaps.js` | Tabs Recebidas/Enviadas |

---

## RECEITAS RAPIDAS

### Adicionar campo no usuario
1. `seed.py` — adiciona coluna no `CREATE TABLE user`
2. Rodar `python seed.py`
3. `routes/user.py` — adicionar Form e incluir no UPDATE
4. `routes/auth.py` — incluir no INSERT (se for cadastro)
5. `templates/profile.html` — adicionar input no form
6. `templates/user.html` (opcional) — mostrar publicamente

### Mudar regra de validacao
- Mexer apenas em `core/validation.py`. Rotas ja chamam.
- Se quiser validar tambem no front: `static/js/validation.js`.

### Criar nova rota POST
1. Cria `@router.post("/...")` no `routes/<arquivo>.py`
2. Sempre comecar com `user = get_current_user(request, db)`
3. SQL com `%s` parametrizado
4. `db.commit()` no fim
5. `RedirectResponse(...)` (ou TemplateResponse com erro)

### Criar formulario novo no front
```html
<form method="POST" action="/rota">
  <input name="campo" required>
  <button type="submit">Enviar</button>
</form>
```
Se enviar arquivo: adicionar `enctype="multipart/form-data"`.

---

## CHECKLIST PRA QUALQUER MUDANCA

- [ ] SQL usa `%s`, nunca f-string com input do usuario
- [ ] Rota verifica `get_current_user` no inicio
- [ ] Quando edita/deleta dado de outro usuario → `WHERE owner_id = user.id`
- [ ] `db.commit()` depois do INSERT/UPDATE/DELETE
- [ ] Reiniciou o `uvicorn` (com `--reload` ele recarrega sozinho)
- [ ] Se mexeu no `seed.py` → rodou `python seed.py` de novo
