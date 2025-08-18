// Exemplo de requisição para a API
fetch('http://localhost:8000/')
  .then(response => response.json())
  .then(data => {
    document.getElementById('app').innerText = data.message;
  });
