// Funções JS para consumir a API e manipular o DOM
async function listarAlunos(){
    try{
        const res = await fetch('http://localhost:8000/alunos');
        const alunos = await res.json();
        const out = document.getElementById('lista-alunos');
        out.innerHTML = alunos.map(a=>`<div class="aluno"><strong>${a.nome}</strong> — ${a.status||'inativo'}</div>`).join('');
    }catch(e){ document.getElementById('lista-alunos').textContent='Erro ao conectar API' }
}

document.getElementById('btn-novo').addEventListener('click', ()=> alert('Use o endpoint /alunos para criar (demo).'))
document.getElementById('btn-export').addEventListener('click', ()=> window.location.href='http://localhost:8000/alunos/export?format=csv')

listarAlunos()
