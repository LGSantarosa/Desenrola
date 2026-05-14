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

## RECEITAS FRONT + BACK + BD (CRUD novo — INSERT + SELECT)

Padrao geral pra adicionar uma feature nova que toca as 3 camadas:

1. **BD** — adicionar `CREATE TABLE` no `seed.py` (e o `DROP TABLE IF EXISTS` correspondente no topo, **antes** das tabelas que dependem dela). Rodar `python seed.py`.
2. **BACK (INSERT)** — criar `POST /...` em `routes/<feature>.py` ou em arquivo existente. Registrar o router em `main.py` (`app.include_router(...)`).
3. **BACK (SELECT)** — adicionar query na rota GET que renderiza a pagina (em `main.py`) e passar pro template.
4. **FRONT (INSERT)** — `<form method="POST" action="/...">` no template.
5. **FRONT (SELECT)** — `{% for x in lista %}` no template.

### Feature A — Comentarios em posts

**BD** (`seed.py`):
```sql
CREATE TABLE comment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB
```
Colocar `DROP TABLE IF EXISTS comment` **antes** de `DROP TABLE IF EXISTS post`.

**BACK (INSERT)** — em `routes/post.py` (mesmo arquivo, ja tem contexto de post):
```python
@router.post("/comments/create")
def create_comment(request: Request, post_id: int = Form(...), content: str = Form(...), db: Connection = Depends(get_db)):
    user = get_current_user(request, db)
    if not user: return RedirectResponse("/login", status_code=303)
    content = content.strip()
    if not content: return RedirectResponse("/dashboard", status_code=303)
    with db.cursor() as cur:
        cur.execute("INSERT INTO comment (post_id, user_id, content) VALUES (%s, %s, %s)",
                    (post_id, user["id"], content))
        db.commit()
    return RedirectResponse("/dashboard", status_code=303)
```

**BACK (SELECT)** — em `main.py`, na `page_dashboard`, depois de buscar `posts`:
```python
for p in posts:
    with db.cursor() as cur:
        cur.execute("""SELECT c.id, c.content, c.created_at, u.name AS author_name, u.avatar AS author_avatar
                       FROM comment c JOIN user u ON u.id = c.user_id
                       WHERE c.post_id = %s ORDER BY c.created_at ASC""", (p["id"],))
        p["comments"] = cur.fetchall()
```

**FRONT** — em `templates/dashboard.html`, dentro do `{% for post in posts %}`:
```html
<div class="comments">
  {% for c in post.comments %}
    <div class="comment"><strong>{{ c.author_name }}:</strong> {{ c.content }}</div>
  {% endfor %}
  <form method="POST" action="/comments/create">
    <input type="hidden" name="post_id" value="{{ post.id }}">
    <input name="content" placeholder="Comentar..." required>
    <button type="submit">Enviar</button>
  </form>
</div>
```

---

### Feature B — Avaliacao de troca (rating)

**BD** (`seed.py`):
```sql
CREATE TABLE rating (
    id INT AUTO_INCREMENT PRIMARY KEY,
    swap_id INT NOT NULL,
    rater_id INT NOT NULL,
    stars INT NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_rating (swap_id, rater_id),
    FOREIGN KEY (swap_id) REFERENCES swap_request(id) ON DELETE CASCADE,
    FOREIGN KEY (rater_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB
```
`DROP TABLE IF EXISTS rating` antes de `swap_request` e `user`.

**BACK (INSERT)** — novo arquivo `routes/rating.py`:
```python
@router.post("/ratings/create")
def create_rating(request: Request, swap_id: int = Form(...), stars: int = Form(...),
                  comment: str = Form(""), db: Connection = Depends(get_db)):
    user = get_current_user(request, db)
    if not user: return RedirectResponse("/login", status_code=303)
    if stars < 1 or stars > 5: return RedirectResponse("/swaps", status_code=303)
    with db.cursor() as cur:
        cur.execute("""SELECT status, sender_id, receiver_id FROM swap_request WHERE id = %s""", (swap_id,))
        sw = cur.fetchone()
        if not sw or sw["status"] != "accepted": return RedirectResponse("/swaps", status_code=303)
        if user["id"] not in (sw["sender_id"], sw["receiver_id"]): return RedirectResponse("/swaps", status_code=303)
        cur.execute("INSERT IGNORE INTO rating (swap_id, rater_id, stars, comment) VALUES (%s,%s,%s,%s)",
                    (swap_id, user["id"], stars, comment.strip()))
        db.commit()
    return RedirectResponse("/swaps", status_code=303)
```
Registrar em `main.py`: `from app.routes import ..., rating` e `app.include_router(rating.router)`.

**BACK (SELECT)** — em `format_swap` (`main.py`), incluir flag se ja avaliou:
```python
with db.cursor() as cur:
    cur.execute("SELECT 1 FROM rating WHERE swap_id = %s AND rater_id = %s", (s["id"], me_id))
    item["already_rated"] = bool(cur.fetchone())
```
(Passar `me_id` como parametro pra `format_swap`.)

**FRONT** — em `templates/swaps.html`, dentro de cada swap `accepted` que ainda nao foi avaliada:
```html
{% if swap.status == 'accepted' and not swap.already_rated %}
  <form method="POST" action="/ratings/create">
    <input type="hidden" name="swap_id" value="{{ swap.id }}">
    <select name="stars">
      {% for n in [1,2,3,4,5] %}<option value="{{ n }}">{{ n }} estrelas</option>{% endfor %}
    </select>
    <textarea name="comment" placeholder="Como foi a troca?"></textarea>
    <button type="submit">Avaliar</button>
  </form>
{% endif %}
```

---

### Feature C — Favoritar pessoa

**BD** (`seed.py`):
```sql
CREATE TABLE favorite (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    favorited_user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_fav (user_id, favorited_user_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (favorited_user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB
```

**BACK (INSERT)** — novo `routes/favorite.py`:
```python
@router.post("/favorites/add")
def add_favorite(request: Request, target_id: int = Form(...), db: Connection = Depends(get_db)):
    user = get_current_user(request, db)
    if not user: return RedirectResponse("/login", status_code=303)
    if target_id == user["id"]: return RedirectResponse("/match", status_code=303)
    with db.cursor() as cur:
        cur.execute("INSERT IGNORE INTO favorite (user_id, favorited_user_id) VALUES (%s, %s)",
                    (user["id"], target_id))
        db.commit()
    return RedirectResponse("/favorites", status_code=303)
```
Registrar em `main.py`.

**BACK (SELECT)** — nova pagina GET `/favorites` em `main.py`:
```python
@app.get("/favorites")
def page_favorites(request: Request, db: Connection = Depends(get_db)):
    user = get_current_user(request, db)
    if not user: return redirect_login()
    with db.cursor() as cur:
        cur.execute("""SELECT u.id, u.name, u.avatar FROM favorite f
                       JOIN user u ON u.id = f.favorited_user_id
                       WHERE f.user_id = %s ORDER BY f.created_at DESC""", (user["id"],))
        favorites = cur.fetchall()
    return templates.TemplateResponse("favorites.html", {"request": request, "user": user, "favorites": favorites})
```

**FRONT (INSERT)** — botao em `templates/user.html` ou no card do `match.html`:
```html
<form method="POST" action="/favorites/add">
  <input type="hidden" name="target_id" value="{{ other.id }}">
  <button type="submit">Favoritar</button>
</form>
```

**FRONT (SELECT)** — novo `templates/favorites.html`:
```html
{% include "_nav.html" %}
<h1>Meus Favoritos</h1>
{% for u in favorites %}
  <a href="/user/{{ u.id }}">
    <img src="/uploads/{{ u.avatar }}"> {{ u.name }}
  </a>
{% endfor %}
```
Adicionar link `<a href="/favorites">` no `_nav.html`.

---

## CHECKLIST PRA QUALQUER MUDANCA

- [ ] SQL usa `%s`, nunca f-string com input do usuario
- [ ] Rota verifica `get_current_user` no inicio
- [ ] Quando edita/deleta dado de outro usuario → `WHERE owner_id = user.id`
- [ ] `db.commit()` depois do INSERT/UPDATE/DELETE
- [ ] Reiniciou o `uvicorn` (com `--reload` ele recarrega sozinho)
- [ ] Se mexeu no `seed.py` → rodou `python seed.py` de novo
