from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()


class Aluno(BaseModel):
	id: int
	nome: str
	status: Optional[str] = 'inativo'


@app.get('/health')
def health():
	return {'status': 'ok'}


@app.get('/alunos', response_model=List[Aluno])
def listar_alunos():
	# retorno estático mínimo para template
	return [
		{'id': 1, 'nome': 'Ana Silva', 'status': 'ativo'},
		{'id': 2, 'nome': 'Bruno Costa', 'status': 'inativo'},
	]


