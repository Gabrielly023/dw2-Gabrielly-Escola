# REPORT - Sistema Escola

Este relatório descreve a implementação do mini-sistema "Escola" (frontend HTML/CSS/JS e backend FastAPI + SQLite). Contém arquitetura, decisões, validações, peculiaridades implementadas e como rodar.

## Arquitetura
- Frontend: pasta `frontend/` (index.html, styles.css, scripts.js)
- Backend: pasta `backend/` (app.py, models.py, database.py, seed.py)
- Banco: `backend/app.db` (SQLite, criado ao rodar o seed)

Fluxo simplificado: navegador -> HTTP -> FastAPI (`app.py`) -> SQLAlchemy (`models.py`) -> SQLite -> resposta JSON/CSV

## Tecnologias e versões
- Python 3.x
- FastAPI
- SQLAlchemy
- SQLite
- JavaScript (ES6+), HTML5, CSS3

## Prompts do Copilot
1. Gerar esqueleto FastAPI com endpoints CRUD para alunos/turmas. (aceitei e ajustei validações de idade e email)
2. Criar modelos SQLAlchemy para `Aluno` e `Turma`. (aceitei, corrigi relacionamentos)
3. Gerar seed script com ~20 alunos. (aceitei e personalizei datas/emails)
4. Adicionar endpoint de export CSV/JSON. (aceitei e padronizei formatos)
5. Criar frontend simples com modal de cadastro. (aceitei e melhorei acessibilidade)
6. Criar testes HTTP (.http) para smoke tests. (aceitei e incluí exemplos)

Para cada prompt eu revisei o código gerado, corrigi imports, ajustei validações e mensagens de erro.

## Peculiaridades implementadas
- Validações no back-end: idade mínima (≥5 anos), email único.
- Seed: script populando 3 turmas e 20 alunos plausíveis.
- Export CSV/JSON da lista filtrada de alunos (`GET /alunos/export`).
- Acessibilidade básica: `aria-label`, foco visível, atalhos (accesskey n).
- Testes manuais: `tests.http` com endpoints de health, listar, criar, exportar, matricular.

## Validações (exemplos)
- Aluno: nome 3–80 chars, data_nascimento válida e ≥5 anos atrás, email no formato, status ativo/inativo.
- Matrícula: não exceder capacidade da turma; ao matricular, `aluno.status` é definido como `ativo`.

## Como rodar (passo a passo)
1. Abra terminal (PowerShell) na raiz do projeto.
2. Instale dependências:
```
pip install -r backend/requirements.txt
```
3. Popular o banco:
```
python backend/seed.py
```
4. Iniciar API:
```
uvicorn backend.app:app --reload
```
5. Abrir `frontend/index.html` no navegador (ou servir via Live Server).

## Limitações e melhorias futuras
- Frontend: adicionar edição/remoção de alunos, paginação no UI, indicadores por turma e export direto do filtro aplicado.
- Testes automatizados: criar testes unitários/integração.
- Autenticação e autorizações para rotas sensíveis.

---
Relatório gerado automaticamente a partir do estado atual do repositório; revise e adicione prints/gifs antes da entrega.
