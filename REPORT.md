# Relatório Técnico — Mini Sistema Escola

## Arquitetura
- FastAPI + SQLAlchemy + SQLite (backend)
- HTML5, CSS3, JS (frontend)

## Tecnologias e versões
- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite
- JavaScript ES6+
- VS Code, Copilot

## Prompts do Copilot
- (Inclua aqui os prompts e trechos gerados/editados durante o desenvolvimento)

## Peculiaridades implementadas
- Seed de dados (script `backend/seed.py`) com ~20 alunos plausíveis e turmas.
- Filtro avançado na API (`/alunos` com parâmetros search, turma_id, status, sort, limit, offset).
- Export CSV/JSON via endpoint `/alunos/export`.
- Validações de negócio no backend: idade mínima (>=5 anos), email único, validação de capacidade ao matricular.
- Acessibilidade aplicada no frontend: `aria-label`, foco visível, `accesskey` para abrir modal novo aluno.

## Validações
- Front: nome, data, email, status, turma
- Back: nome, data, email, status, turma, capacidade

## Como rodar
1. Instale dependências:
```bash
pip install -r backend/requirements.txt
```
2. Rode o seed para popular o banco:
```bash
python backend/seed.py
```
3. Inicie a API:
```bash
uvicorn backend.app:app --reload
```
4. Abra `frontend/index.html` no navegador.

## Limitações e melhorias
- Adicionar autenticação
- Melhorar layout e responsividade
- Implementar testes automatizados
