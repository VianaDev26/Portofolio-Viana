"""
TROCAR USUÁRIO / SENHA DO PORTFÓLIO

Use quando quiser mudar a senha (ou o usuário) sem mexer no código.
PARA RODAR:  python trocar_senha.py
Não precisa reiniciar o site: o login já usa a senha nova.
"""
import getpass                   # pede a senha sem mostrar o que você digita
import json
from pathlib import Path
from werkzeug.security import generate_password_hash   # embaralha a senha (hash)

# Arquivo onde ficam o usuário e a senha embaralhada
destino = Path(__file__).parent / "data" / "user.json"
destino.parent.mkdir(exist_ok=True)

usuario = input("Usuário: ").strip()
senha = getpass.getpass("Nova senha (não aparece enquanto digita): ")
repete = getpass.getpass("Repita a senha: ")

# Confere se está tudo certo antes de salvar
if len(usuario) < 3:
    raise SystemExit("O usuário precisa ter 3+ caracteres.")
if len(senha) < 8:
    raise SystemExit("A senha precisa ter 8+ caracteres.")
if senha != repete:
    raise SystemExit("As senhas não são iguais. Nada foi alterado.")

# Salva só o hash: a senha de verdade nunca fica gravada
destino.write_text(json.dumps({"u": usuario, "h": generate_password_hash(senha)}))
print("Pronto! Usuário e senha atualizados.")
