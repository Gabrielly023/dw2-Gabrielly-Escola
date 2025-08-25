// Funções JS para consumir a API e manipular o DOM
// Exemplo de busca de alunos
fetch('http://localhost:8000/alunos')
  .then(r => r.json())
  .then(alunos => {
    const lista = document.getElementById('lista-alunos');
    lista.innerHTML = alunos.map(a => `<div><b>${a.nome}</b> - ${a.status}</div>`).join('');
  });
// Adicione aqui as demais funções de CRUD, filtros, modais, etc.
