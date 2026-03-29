import random
from app.core.database import SessionLocal
from app.core.auth import hash_password
from app.models.skill import Category, Skill, UserSkill
from app.models.user import User
from app.models.post import Post

db = SessionLocal()

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
    cat = db.query(Category).filter(Category.name == cat_name).first()
    if not cat:
        cat = Category(name=cat_name)
        db.add(cat)
        db.flush()

    for skill_name in skills:
        existing = db.query(Skill).filter(Skill.name == skill_name, Skill.category_id == cat.id).first()
        if not existing:
            db.add(Skill(name=skill_name, category_id=cat.id))

db.commit()

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

all_skills = db.query(Skill).all()
hashed = hash_password("123456")

for u in fake_users:
    existing = db.query(User).filter(User.email == u["email"]).first()
    if existing:
        continue

    user = User(
        name=u["name"],
        email=u["email"],
        password=hashed,
        cpf=u["cpf"],
        phone=u["phone"],
        birth_date=u["birth_date"],
    )
    db.add(user)
    db.flush()

    teaches = random.sample(all_skills, random.randint(2, 4))
    remaining = [s for s in all_skills if s not in teaches]
    learns = random.sample(remaining, random.randint(2, 4))

    for skill in teaches:
        db.add(UserSkill(user_id=user.id, skill_id=skill.id, type="teaches"))
    for skill in learns:
        db.add(UserSkill(user_id=user.id, skill_id=skill.id, type="learns"))

db.commit()

posts_data = [
    {"email": "lucas@email.com", "content": "Alguem aqui manja de React? To tentando migrar um projeto de jQuery e ta sendo uma aventura"},
    {"email": "ana@email.com", "content": "Acabei de terminar meu primeiro bolo decorado! Confeitaria e terapia demais"},
    {"email": "rafael@email.com", "content": "Dica pra quem ta comecando com Python: foca em entender listas e dicionarios antes de partir pra frameworks"},
    {"email": "mariana@email.com", "content": "Alguem quer praticar espanhol comigo? To no nivel intermediario e preciso de conversacao"},
    {"email": "pedro@email.com", "content": "Montei um mini estudio de fotografia em casa gastando menos de 200 reais. Se alguem quiser as dicas, chama!"},
    {"email": "julia@email.com", "content": "Primeira vez tocando piano em publico hoje e nao travei! Valeu a pena cada hora de pratica"},
    {"email": "gabriel@email.com", "content": "Quem mais acha que Figma revolucionou o design? Antes era Photoshop pra tudo"},
    {"email": "camila@email.com", "content": "Terminei um curso de SEO e ja to vendo resultado no meu blog. Organico > pago"},
    {"email": "bruno@email.com", "content": "To aprendendo japones por conta propria. Hiragana ja foi, agora vem o katakana"},
    {"email": "fernanda@email.com", "content": "Dica de investimento pra iniciante: comeca pelo Tesouro Direto, nao vai direto pra day trade"},
    {"email": "lucas@email.com", "content": "Quem quiser trocar uma ideia sobre Node.js, to disponivel! Bora montar um grupo de estudos"},
    {"email": "ana@email.com", "content": "Pessoal, vale muito a pena aprender Libras. Alem de ser lindo, abre um mundo novo de comunicacao"},
    {"email": "rafael@email.com", "content": "Fiz meu primeiro churrasco sozinho nesse fds. A picanha ficou no ponto, mas a farofa... vamos ignorar"},
    {"email": "mariana@email.com", "content": "UI/UX nao e so deixar bonito, e sobre resolver problemas. Mudei minha visao depois de estudar design thinking"},
    {"email": "pedro@email.com", "content": "Lightroom mobile e subestimado demais. Da pra editar foto profissional so no celular"},
]

for p in posts_data:
    user = db.query(User).filter(User.email == p["email"]).first()
    if user:
        db.add(Post(user_id=user.id, content=p["content"]))

db.commit()
db.close()
print("Seed concluido! 10 usuarios e 15 posts criados.")
