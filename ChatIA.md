# ChatIA

Este arquivo irá registrar todas as conversas sobre o projeto.

---

**18/08/2025**
- Usuário solicitou a criação dos arquivos para um mini-sistema web completo, individual, com as seguintes orientações:

	- Front-end: HTML5, CSS3 (Flex/Grid), JavaScript (ES6+, sem framework).
	- Back-end/API: Python (FastAPI ou Flask), SQLite via SQLAlchemy (ou sqlite3).
	- Ferramentas: VS Code, Copilot, Git/GitHub, Thunder Client/Insomnia.
	- Entrega: repositório público no GitHub + relatório técnico.

- Estrutura inicial criada automaticamente:

	- backend/main.py, backend/models.py, backend/database.py, backend/requirements.txt
	- frontend/index.html, frontend/style.css, frontend/script.js
	- Diretórios backend/ e frontend/ criados.
	- Dependências do backend listadas em requirements.txt.
	- Pronto para evoluir com rotas, modelos e funcionalidades específicas.

	---

	**25/08/2025**
	- Usuario pediu para melhorar o sistema "Escola" e deixar completo.
	- Ações realizadas:
		- Padronizei a estrutura do backend/frontend e removi arquivos duplicados.
		- Implementei backend usando FastAPI com endpoints: listar/criar/atualizar/deletar alunos e turmas, matriculas, export CSV/JSON, paginação e ordenação.
		- Adicionei validações (idade mínima 5 anos, email único, capacidade de turma) e mensagens de erro HTTP apropriadas.
		- Criei `backend/seed.py` para popular o banco com ~20 alunos plausíveis e turmas.
		- Atualizei `REPORT.md` com peculiaridades e instruções de execução.
		- Rodei `pip install -r backend/requirements.txt`, executei o seed e fiz `uvicorn backend.app:app` para testes locais.
		- Commit e push realizados para o repositório GitHub.

	Próximo: posso continuar adicionando CRUD completo no frontend, acessibilidade avançada e coleção Thunder Client se desejar.

	---

	Instruções de uso:
	- Sempre que conversar comigo sobre o projeto, peça para registrar a conversa aqui com a data. Eu atualizarei este arquivo automaticamente e irei commitar/push quando solicitado.
