import os
import random
import uuid
import ssl
import urllib.request
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
from app.core.database import get_connection, DB_CONFIG
from app.core.auth import hash_password

load_dotenv()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

DB_NAME = DB_CONFIG["database"]

bootstrap_conn = pymysql.connect(
    host=DB_CONFIG["host"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    port=DB_CONFIG["port"],
    cursorclass=DictCursor,
    autocommit=True,
)
with bootstrap_conn.cursor() as c:
    c.execute("CREATE DATABASE IF NOT EXISTS " + DB_NAME + " CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
bootstrap_conn.close()

ddl_conn = get_connection()
ddl_cur = ddl_conn.cursor()

ddl_cur.execute("DROP TABLE IF EXISTS post")
ddl_cur.execute("DROP TABLE IF EXISTS swap_request")
ddl_cur.execute("DROP TABLE IF EXISTS user_skill")
ddl_cur.execute("DROP TABLE IF EXISTS skill")
ddl_cur.execute("DROP TABLE IF EXISTS category")
ddl_cur.execute("DROP TABLE IF EXISTS user")

ddl_cur.execute("""
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    cpf VARCHAR(20) NOT NULL UNIQUE,
    phone VARCHAR(30),
    birth_date DATE,
    avatar VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'cliente',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB
""")

ddl_cur.execute("""
CREATE TABLE category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE
) ENGINE=InnoDB
""")

ddl_cur.execute("""
CREATE TABLE skill (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE CASCADE
) ENGINE=InnoDB
""")

ddl_cur.execute("""
CREATE TABLE user_skill (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    skill_id INT NOT NULL,
    type ENUM('teaches','learns') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skill(id) ON DELETE CASCADE
) ENGINE=InnoDB
""")

ddl_cur.execute("""
CREATE TABLE swap_request (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    offered_skill_id INT NOT NULL,
    desired_skill_id INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (offered_skill_id) REFERENCES skill(id) ON DELETE CASCADE,
    FOREIGN KEY (desired_skill_id) REFERENCES skill(id) ON DELETE CASCADE
) ENGINE=InnoDB
""")

ddl_cur.execute("""
CREATE TABLE post (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    image VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB
""")

ddl_conn.commit()
ddl_cur.close()
ddl_conn.close()
print("Tabelas criadas.")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def download_image(url, retries=3):
    filename = str(uuid.uuid4()) + ".jpg"
    filepath = os.path.join(UPLOAD_DIR, filename)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                with open(filepath, "wb") as f:
                    f.write(resp.read())
            print("  baixou: " + filename)
            return filename
        except Exception as e:
            if attempt < retries - 1:
                print("  tentativa " + str(attempt + 1) + " falhou, tentando de novo...")
            else:
                print("  falha ao baixar: " + str(e))
    return None


conn = get_connection()
cur = conn.cursor()

data = {
    "Programacao": ["Python", "JavaScript", "Java", "C++", "React", "Node.js", "SQL", "FastAPI", "HTML/CSS", "TypeScript"],
    "Musica": ["Violao", "Piano", "Canto", "Bateria", "Guitarra", "Ukulele", "Teoria Musical", "Producao Musical"],
    "Idiomas": ["Ingles", "Espanhol", "Frances", "Alemao", "Italiano", "Japones", "Coreano", "Libras"],
    "Design": ["Figma", "Photoshop", "Illustrator", "UI/UX", "Design Grafico", "Motion Design", "Canva"],
    "Culinaria": ["Confeitaria", "Cozinha Italiana", "Cozinha Japonesa", "Churrasco", "Panificacao", "Drinks"],
    "Fotografia": ["Fotografia de Retrato", "Fotografia de Rua", "Edicao de Fotos", "Lightroom", "Fotografia de Produto"],
    "Marketing": ["Marketing Digital", "SEO", "Google Ads", "Social Media", "Copywriting", "Email Marketing"],
    "Financas": ["Investimentos", "Excel Financeiro", "Contabilidade", "Day Trade", "Planejamento Financeiro"],
}

for cat_name, skills in data.items():
    cur.execute("SELECT id FROM category WHERE name = %s", (cat_name,))
    cat = cur.fetchone()
    if not cat:
        cur.execute("INSERT INTO category (name) VALUES (%s)", (cat_name,))
        cat_id = cur.lastrowid
    else:
        cat_id = cat["id"]

    for skill_name in skills:
        cur.execute("SELECT id FROM skill WHERE name = %s AND category_id = %s", (skill_name, cat_id))
        if not cur.fetchone():
            cur.execute("INSERT INTO skill (name, category_id) VALUES (%s, %s)", (skill_name, cat_id))

conn.commit()

fake_users = [
    {"name": "Lucas Costa", "email": "lucas@email.com", "cpf": "111.111.111-11", "phone": "(11) 91111-1111", "birth_date": "1998-03-15"},
    {"name": "Ana Martins", "email": "ana@email.com", "cpf": "222.222.222-22", "phone": "(11) 92222-2222", "birth_date": "2000-07-20"},
    {"name": "Rafael Oliveira", "email": "rafael@email.com", "cpf": "333.333.333-33", "phone": "(21) 93333-3333", "birth_date": "1999-01-10"},
    {"name": "Mariana Silva", "email": "mariana@email.com", "cpf": "444.444.444-44", "phone": "(31) 94444-4444", "birth_date": "2001-11-05"},
    {"name": "Pedro Henrique", "email": "pedro@email.com", "cpf": "555.555.555-55", "phone": "(41) 95555-5555", "birth_date": "1997-06-22"},
    {"name": "Julia Santos", "email": "julia@email.com", "cpf": "666.666.666-66", "phone": "(51) 96666-6666", "birth_date": "2002-09-30"},
    {"name": "Gabriel Souza", "email": "gabriel@email.com", "cpf": "777.777.777-77", "phone": "(61) 97777-7777", "birth_date": "1996-12-18"},
    {"name": "Camila Rodrigues", "email": "camila@email.com", "cpf": "888.888.888-88", "phone": "(71) 98888-8888", "birth_date": "2000-04-25"},
    {"name": "Bruno Almeida", "email": "bruno@email.com", "cpf": "999.999.999-99", "phone": "(81) 99999-9999", "birth_date": "1999-08-12"},
    {"name": "Fernanda Lima", "email": "fernanda@email.com", "cpf": "100.100.100-10", "phone": "(91) 90000-0000", "birth_date": "2001-02-14"},
]

cur.execute("SELECT id FROM skill")
all_skills = cur.fetchall()
all_skill_ids = [s["id"] for s in all_skills]
hashed = hash_password("123456")

print("Baixando avatares...")
for i, u in enumerate(fake_users):
    cur.execute("SELECT id, avatar FROM user WHERE email = %s", (u["email"],))
    existing = cur.fetchone()
    if existing:
        if not existing["avatar"]:
            avatar = download_image("https://i.pravatar.cc/200?img=" + str(i + 1))
            if avatar:
                cur.execute("UPDATE user SET avatar = %s WHERE id = %s", (avatar, existing["id"]))
        continue

    avatar = download_image("https://i.pravatar.cc/200?img=" + str(i + 1))

    cur.execute(
        """INSERT INTO user (name, email, password, cpf, phone, birth_date, avatar)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (u["name"], u["email"], hashed, u["cpf"], u["phone"], u["birth_date"], avatar),
    )
    user_id = cur.lastrowid

    teaches = random.sample(all_skill_ids, random.randint(2, 4))
    remaining = [s for s in all_skill_ids if s not in teaches]
    learns = random.sample(remaining, random.randint(2, 4))

    for skill_id in teaches:
        cur.execute(
            "INSERT INTO user_skill (user_id, skill_id, type) VALUES (%s, %s, 'teaches')",
            (user_id, skill_id),
        )
    for skill_id in learns:
        cur.execute(
            "INSERT INTO user_skill (user_id, skill_id, type) VALUES (%s, %s, 'learns')",
            (user_id, skill_id),
        )

conn.commit()

posts_data = [
    {"email": "lucas@email.com", "content": "Alguem aqui manja de React? To tentando migrar um projeto de jQuery e ta sendo uma aventura", "image": "https://picsum.photos/seed/code1/600/400"},
    {"email": "ana@email.com", "content": "Acabei de terminar meu primeiro bolo decorado! Confeitaria e terapia demais", "image": "https://picsum.photos/seed/cake1/600/400"},
    {"email": "rafael@email.com", "content": "Dica pra quem ta comecando com Python: foca em entender listas e dicionarios antes de partir pra frameworks", "image": None},
    {"email": "mariana@email.com", "content": "Alguem quer praticar espanhol comigo? To no nivel intermediario e preciso de conversacao", "image": None},
    {"email": "pedro@email.com", "content": "Montei um mini estudio de fotografia em casa gastando menos de 200 reais. Se alguem quiser as dicas, chama!", "image": "https://picsum.photos/seed/photo1/600/400"},
    {"email": "julia@email.com", "content": "Primeira vez tocando piano em publico hoje e nao travei! Valeu a pena cada hora de pratica", "image": "https://picsum.photos/seed/piano1/600/400"},
    {"email": "gabriel@email.com", "content": "Quem mais acha que Figma revolucionou o design? Antes era Photoshop pra tudo", "image": None},
    {"email": "camila@email.com", "content": "Terminei um curso de SEO e ja to vendo resultado no meu blog. Organico > pago", "image": "https://picsum.photos/seed/seo1/600/400"},
    {"email": "bruno@email.com", "content": "To aprendendo japones por conta propria. Hiragana ja foi, agora vem o katakana", "image": "https://picsum.photos/seed/japan1/600/400"},
    {"email": "fernanda@email.com", "content": "Dica de investimento pra iniciante: comeca pelo Tesouro Direto, nao vai direto pra day trade", "image": None},
    {"email": "lucas@email.com", "content": "Quem quiser trocar uma ideia sobre Node.js, to disponivel! Bora montar um grupo de estudos", "image": None},
    {"email": "ana@email.com", "content": "Pessoal, vale muito a pena aprender Libras. Alem de ser lindo, abre um mundo novo de comunicacao", "image": "https://picsum.photos/seed/libras1/600/400"},
    {"email": "rafael@email.com", "content": "Fiz meu primeiro churrasco sozinho nesse fds. A picanha ficou no ponto, mas a farofa... vamos ignorar", "image": "https://picsum.photos/seed/churras1/600/400"},
    {"email": "mariana@email.com", "content": "UI/UX nao e so deixar bonito, e sobre resolver problemas. Mudei minha visao depois de estudar design thinking", "image": None},
    {"email": "pedro@email.com", "content": "Lightroom mobile e subestimado demais. Da pra editar foto profissional so no celular", "image": "https://picsum.photos/seed/light1/600/400"},
]

cur.execute("SELECT COUNT(*) AS c FROM post")
if cur.fetchone()["c"] > 0:
    cur.execute("DELETE FROM post")
    conn.commit()

print("Baixando imagens dos posts...")
for p in posts_data:
    cur.execute("SELECT id FROM user WHERE email = %s", (p["email"],))
    user = cur.fetchone()
    if not user:
        continue

    image_name = None
    if p["image"]:
        image_name = download_image(p["image"])

    cur.execute(
        "INSERT INTO post (user_id, content, image) VALUES (%s, %s, %s)",
        (user["id"], p["content"], image_name),
    )

conn.commit()
cur.close()
conn.close()
print("Seed concluido! 10 usuarios com avatar e 15 posts com imagens.")
