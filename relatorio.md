# Relatório Técnico – Mini-Sistema Web

## 1. Introdução
Este documento apresenta o relatório técnico do desenvolvimento do mini-sistema web individual, conforme orientações do projeto.

## 2. Tecnologias Utilizadas
- **Front-end:** HTML5, CSS3 (Flex/Grid), JavaScript (ES6+)
- **Back-end/API:** Python (FastAPI), SQLite via SQLAlchemy
- **Ferramentas:** VS Code, Copilot, Git/GitHub, Thunder Client/Insomnia

## 3. Estrutura do Projeto
```
backend/
  main.py
  models.py
  database.py
  requirements.txt
frontend/
  index.html
  style.css
  script.js
relatorio.md
README.md
```

## 4. Funcionalidades Implementadas
- Estrutura básica de API com FastAPI
- Integração com banco de dados SQLite
- Front-end simples consumindo a API

## 5. Como Executar
1. Instale as dependências do backend:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Inicie a API:
   ```bash
   uvicorn backend.main:app --reload
   ```
3. Abra o arquivo `frontend/index.html` em seu navegador.

## 6. Considerações Finais
O projeto está pronto para ser expandido com novas rotas, modelos e funcionalidades conforme a necessidade.
