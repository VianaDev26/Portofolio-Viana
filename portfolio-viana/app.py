"""
PORTFÓLIO DO VIANADEV - feito com Flask (Python)

COMO FUNCIONA, EM RESUMO:
  - A página pública (/) mostra o seu portfólio para qualquer pessoa.
  - A página /login pede usuário e senha. Só você entra.
  - Depois do login você cai no /dashboard, onde edita tudo.
  - O que você edita fica salvo no arquivo data/site.json.

PARA RODAR:  python app.py   e abra  http://127.0.0.1:5000
"""

# ---------------------------------------------------------------
# 1) IMPORTS: ferramentas que o Python vai usar
# ---------------------------------------------------------------
import json                      # ler/gravar arquivos .json (onde guardamos seus dados)
import os                        # ler variáveis de ambiente (ex: PRODUCAO=1)
import secrets                   # gerar códigos aleatórios seguros
import time                      # pausa quando erram a senha + controle do bloqueio
from datetime import timedelta   # define por quanto tempo o login dura
from functools import wraps      # ajuda a criar o "porteiro" login_required
from pathlib import Path         # facilita trabalhar com pastas e arquivos

from flask import (Flask, abort, flash, redirect, render_template, request,
                   session, url_for)
# Flask = o framework do site | render_template = mostra uma página HTML
# request = dados que o visitante enviou | session = "memória" de quem está logado
# redirect/url_for = mandar o visitante para outra página | flash = mensagem rápida
# abort = parar com erro (ex: 400)

from werkzeug.security import check_password_hash, generate_password_hash
# Essas duas funções transformam a senha em um "hash" (embaralhada).
# Assim a senha NUNCA fica salva de forma legível.

# ---------------------------------------------------------------
# 2) CAMINHOS DOS ARQUIVOS
# ---------------------------------------------------------------
BASE = Path(__file__).parent     # pasta onde está este arquivo app.py
DATA = BASE / "data"             # pasta "data" (guarda seus dados)
DATA.mkdir(exist_ok=True)        # cria a pasta se ainda não existir

F_SITE = DATA / "site.json"      # seu conteúdo (nome, linguagens, projetos)
F_USER = DATA / "user.json"      # seu usuário + senha (já embaralhada)
F_KEY = DATA / "secret.key"      # chave secreta que protege o login

# ---------------------------------------------------------------
# 3) CONTEÚDO INICIAL (aparece até você editar no dashboard)
# ---------------------------------------------------------------
DEFAULT = {
    "name": "VianaDev",                        # seu nome no site
    "title": "Desenvolvedor Júnior",           # seu cargo
    "bio": "Dev júnior aprendendo e construindo projetos todos os dias.",
    "github": "", "linkedin": "", "email": "",  # links (vazio = não aparece)
    "skills": [                                # linguagens, em grupos
        {"g": "Front-end", "items": ["HTML", "CSS", "JavaScript"]},
        {"g": "Back-end", "items": ["Python", "Java"]},
    ],
    "projects": [],                            # seus projetos (começa vazio)
}

# ---------------------------------------------------------------
# 4) CRIA O APP E CONFIGURA A SEGURANÇA
# ---------------------------------------------------------------
app = Flask(__name__)

# A chave secreta é criada sozinha na primeira vez e guardada em data/secret.key.
if not F_KEY.exists():
    F_KEY.write_text(secrets.token_hex(32))
app.secret_key = F_KEY.read_text()

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,   # o navegador esconde o cookie do JavaScript
    SESSION_COOKIE_SAMESITE="Lax",  # protege contra sites mal-intencionados
)
# O login expira sozinho depois de 2 horas (você entra de novo).
app.permanent_session_lifetime = timedelta(hours=2)

# Na internet (com HTTPS) rode com a variável PRODUCAO=1 e o cookie de
# login só viaja por conexão segura. No seu PC (http) deixe sem.
if os.environ.get("PRODUCAO") == "1":
    app.config["SESSION_COOKIE_SECURE"] = True

# ---------------------------------------------------------------
# 5) FUNÇÕES AUXILIARES
# ---------------------------------------------------------------
# Tons de azul usados para dar cor às etiquetas (tags) de cada tecnologia.
HUES = [195, 205, 215, 225, 235, 245]


@app.template_filter("hue")
def hue(texto):
    """Escolhe sempre o mesmo tom de azul para o mesmo texto (ex: 'Python')."""
    h = 0
    for letra in texto:
        h = (h * 37 + ord(letra)) % 997
    return HUES[h % len(HUES)]


def load_site():
    """Lê os dados do site. Se ainda não existe arquivo, usa o DEFAULT."""
    d = json.loads(json.dumps(DEFAULT))          # cópia do DEFAULT
    if F_SITE.exists():
        d.update(json.loads(F_SITE.read_text("utf-8")))
    return d


def save_site(d):
    """Grava os dados do site no arquivo data/site.json."""
    F_SITE.write_text(json.dumps(d, ensure_ascii=False, indent=2), "utf-8")


def load_user():
    """Lê o usuário/senha salvos. Retorna None se ainda não criou o acesso."""
    return json.loads(F_USER.read_text("utf-8")) if F_USER.exists() else None


def safe_url(u):
    """Só aceita links que começam com http:// ou https://.
    Isso impede links perigosos (ex: javascript:...)."""
    u = (u or "").strip()
    return u if u.lower().startswith(("http://", "https://")) else ""


def login_required(f):
    """'Porteiro': se a pessoa não estiver logada, manda para /login."""
    @wraps(f)
    def wrapper(*a, **k):
        if not session.get("auth"):
            return redirect(url_for("login"))
        return f(*a, **k)
    return wrapper


# Proteção CSRF: todo formulário (POST) precisa levar um código secreto.
# Assim outro site não consegue enviar formulários "fingindo" ser você.
@app.before_request
def check_csrf():
    if request.method == "POST":
        tok = request.form.get("csrf", "")
        if not tok or tok != session.get("csrf"):
            abort(400)


@app.context_processor
def inject_csrf():
    """Deixa a variável {{ csrf }} disponível em todas as páginas HTML."""
    session.setdefault("csrf", secrets.token_hex(16))
    return {"csrf": session["csrf"]}


@app.after_request
def security_headers(resp):
    """Cabeçalhos que o navegador obedece para proteger o site."""
    resp.headers["X-Frame-Options"] = "DENY"            # ninguém embute seu site em outro
    resp.headers["X-Content-Type-Options"] = "nosniff"  # navegador não "adivinha" tipos de arquivo
    resp.headers["Referrer-Policy"] = "same-origin"     # não vaza de onde você veio
    if request.path.startswith(("/dashboard", "/login", "/setup")):
        resp.headers["Cache-Control"] = "no-store"      # páginas privadas não ficam guardadas em cache
    return resp


# ---------------------------------------------------------------
# 6) PÁGINA PÚBLICA
# ---------------------------------------------------------------
@app.route("/")
def index():
    # Mostra templates/index.html com os dados do site
    return render_template("index.html", d=load_site())


# ---------------------------------------------------------------
# 7) CRIAR ACESSO (só funciona UMA vez) E LOGIN
# ---------------------------------------------------------------
@app.route("/setup", methods=["GET", "POST"])
def setup():
    # Se o acesso já foi criado, essa página fica bloqueada.
    if load_user():
        return redirect(url_for("login"))
    if request.method == "POST":                      # quando clica em "Criar"
        u = request.form.get("usuario", "").strip()
        p = request.form.get("senha", "")
        if len(u) < 3 or len(p) < 8:
            flash("Usuário com 3+ caracteres e senha com 8+ caracteres.")
        else:
            # Salva o usuário e a senha embaralhada (hash)
            F_USER.write_text(json.dumps({"u": u, "h": generate_password_hash(p)}))
            session.clear()
            session.permanent = True                  # login com prazo de 2h
            session["auth"] = True                    # já entra logado
            return redirect(url_for("dashboard"))
    return render_template("setup.html")


# Controle de tentativas erradas (fica na memória, por endereço de IP).
# Depois de 5 erros seguidos, aquele IP fica 5 minutos bloqueado.
FALHAS = {}          # { ip: [quantidade_de_erros, bloqueado_ate_a_hora] }
MAX_FALHAS = 5
BLOQUEIO_SEG = 300


@app.route("/login", methods=["GET", "POST"])
def login():
    user = load_user()
    if not user:                                      # ainda não criou acesso
        return redirect(url_for("setup"))
    if request.method == "POST":
        ip = request.remote_addr or "?"
        agora = time.time()
        erros, bloqueado_ate = FALHAS.get(ip, [0, 0])

        # Está bloqueado? Nem confere a senha.
        if bloqueado_ate > agora:
            flash("Muitas tentativas erradas. Espere alguns minutos.")
            return render_template("login.html"), 429

        # Confere usuário E senha (os dois sempre, para não dar pista de qual errou).
        # compare_digest compara sem vazar informação pelo tempo de resposta.
        usuario_ok = secrets.compare_digest(
            request.form.get("usuario", "").strip().encode(), user["u"].encode())
        senha_ok = check_password_hash(user["h"], request.form.get("senha", ""))

        if usuario_ok and senha_ok:
            FALHAS.pop(ip, None)                      # acertou: zera os erros
            session.clear()
            session.permanent = True                  # login com prazo de 2h
            session["auth"] = True                    # marca como logado
            return redirect(url_for("dashboard"))

        # Errou: soma um erro; se chegou no limite, bloqueia por 5 minutos
        erros += 1
        if erros >= MAX_FALHAS:
            erros, bloqueado_ate = 0, agora + BLOQUEIO_SEG
        FALHAS[ip] = [erros, bloqueado_ate]
        time.sleep(0.6)                               # pausa: atrapalha quem tenta adivinhar
        flash("Usuário ou senha incorretos.")
    return render_template("login.html")


@app.post("/logout")
def logout():
    session.clear()                                   # esquece o login
    return redirect(url_for("index"))


# ---------------------------------------------------------------
# 8) DASHBOARD (só quem está logado entra)
# ---------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", d=load_site())


def edit(fn, msg="Salvo!"):
    """Atalho: lê o site, aplica a mudança (fn), salva e volta pro dashboard."""
    d = load_site()
    fn(d)
    save_site(d)
    flash(msg)
    return redirect(url_for("dashboard"))


def idx(nome, lista):
    """Pega um número (posição) enviado pelo formulário e confere se é válido."""
    try:
        i = int(request.form.get(nome, ""))
    except ValueError:
        abort(400)
    if not 0 <= i < len(lista):
        abort(400)
    return i


@app.post("/dashboard/perfil")
@login_required
def perfil():
    """Salva nome, cargo, sobre, e-mail e links."""
    def fn(d):
        for k in ("name", "title", "bio", "email"):
            d[k] = request.form.get(k, "").strip()
        d["github"] = safe_url(request.form.get("github"))
        d["linkedin"] = safe_url(request.form.get("linkedin"))
    return edit(fn)


@app.post("/dashboard/skill/add")
@login_required
def skill_add():
    """Adiciona uma tecnologia em um grupo existente OU cria um grupo novo."""
    skill = request.form.get("skill", "").strip()
    group = request.form.get("group", "").strip()

    def fn(d):
        if not skill:
            return
        if group:  # veio um nome de grupo: usa o grupo com esse nome ou cria um novo
            g = next((x for x in d["skills"] if x["g"].lower() == group.lower()), None)
            if not g:
                g = {"g": group, "items": []}
                d["skills"].append(g)
        else:      # veio a posição de um grupo que já existe
            g = d["skills"][idx("g", d["skills"])]
        g["items"].append(skill)
    return edit(fn, "Especialidade adicionada!")


@app.post("/dashboard/skill/del")
@login_required
def skill_del():
    """Remove uma tecnologia de um grupo."""
    def fn(d):
        g = d["skills"][idx("g", d["skills"])]
        g["items"].pop(idx("i", g["items"]))
    return edit(fn, "Removida.")


@app.post("/dashboard/grupo/del")
@login_required
def grupo_del():
    """Remove um grupo inteiro de linguagens."""
    return edit(lambda d: d["skills"].pop(idx("g", d["skills"])), "Grupo removido.")


@app.post("/dashboard/projeto/save")
@login_required
def projeto_save():
    """Cria um projeto novo (i = 'new') ou atualiza um que já existe."""
    def fn(d):
        p = {
            "title": request.form.get("title", "").strip(),
            "desc": request.form.get("desc", "").strip(),
            "url": safe_url(request.form.get("url")),
            # "Python, CSS" vira a lista ["Python", "CSS"]
            "tags": [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()],
        }
        if request.form.get("i") == "new":
            if p["title"]:
                d["projects"].append(p)
        else:
            d["projects"][idx("i", d["projects"])] = p
    return edit(fn, "Projeto salvo!")


@app.post("/dashboard/projeto/del")
@login_required
def projeto_del():
    """Apaga um projeto."""
    return edit(lambda d: d["projects"].pop(idx("i", d["projects"])), "Projeto removido.")


# ---------------------------------------------------------------
# 9) LIGA O SERVIDOR (só quando você roda: python app.py)
# ---------------------------------------------------------------
if __name__ == "__main__":
    # 127.0.0.1 = só o seu PC enxerga o site. Ninguém da rede entra.
    app.run(host="127.0.0.1", port=5000, debug=False)
