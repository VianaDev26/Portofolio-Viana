# Portfólio do VianaDev (Flask)

Site público + login + dashboard para você editar tudo (perfil, linguagens, projetos).
Só o dono (usuário `viana`) entra no dashboard; quem visita vê só o site público.

## Rodando no VS Code
1. Abra esta pasta no VS Code (File > Open Folder).
2. Terminal (Ctrl+`):
   ```
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   source .venv/bin/activate     # Linux / Mac
   pip install -r requirements.txt
   python app.py
   ```
3. Abra http://127.0.0.1:5000
4. Para editar: http://127.0.0.1:5000/login (o acesso já vem criado em `data/user.json`).

## Trocar a senha
```
python trocar_senha.py
```
Use uma senha longa e única (frase com 12+ caracteres é ótimo).

## Estrutura
- `app.py` – rotas, login, sessão e salvamento
- `trocar_senha.py` – troca usuário/senha com segurança
- `templates/` – páginas (index, login, setup, dashboard)
- `static/` – CSS e as fagulhas (JS)
- `data/` – `user.json` (senha com hash). `site.json` (seu conteúdo) e `secret.key` são criados sozinhos.
  Se você já tinha editado o site antes, copie o seu `site.json` antigo para dentro de `data/`.

## Segurança já incluída
- Senha guardada só como hash (scrypt), nunca em texto.
- Bloqueio de 5 minutos após 5 senhas erradas seguidas.
- Login expira em 2 horas; proteção CSRF; cookie HttpOnly.
- Todas as rotas de edição exigem login.

## Antes de publicar na internet
- Use HTTPS e rode com a variável `PRODUCAO=1` (deixa o cookie de login só em conexão segura).
- Rode com `gunicorn app:app` (pip install gunicorn) em vez de `python app.py`.
- Não envie a pasta `data/` para o GitHub (já está no .gitignore).
