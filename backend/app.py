from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional, List
import io, csv, json
from datetime import date

from .database import SessionLocal, engine
from .models import Base, Aluno, Turma
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


class AlunoSchema(BaseModel):
	nome: constr(min_length=3, max_length=80)
	data_nascimento: date
	email: Optional[EmailStr] = None
	status: Optional[constr(min_length=1, max_length=10)] = "inativo"
	turma_id: Optional[int] = None

	@validator('data_nascimento')
	def idade_minima(cls, v):
		hoje = date.today()
		idade = hoje.year - v.year - ((hoje.month, hoje.day) < (v.month, v.day))
		if idade < 5:
			raise ValueError('Aluno deve ter pelo menos 5 anos')
		return v


class TurmaSchema(BaseModel):
	nome: constr(min_length=2, max_length=40)
	capacidade: int


@app.get('/health')
def health():
	return {"status": "ok"}


@app.get('/alunos', response_model=List[AlunoSchema])
def listar_alunos(search: str = '', turma_id: Optional[int] = None, status: Optional[str] = None,
                  limit: int = 20, offset: int = 0, sort: Optional[str] = None, db: Session = Depends(get_db)):
	q = db.query(Aluno)
	if search:
		q = q.filter(Aluno.nome.ilike(f"%{search}%"))
	if turma_id:
		q = q.filter(Aluno.turma_id == turma_id)
	if status:
		q = q.filter(Aluno.status == status)

	# sorting: allow 'nome' or 'data_nascimento', prefix with '-' for desc
	if sort:
		direction = 'asc'
		field = sort
		if sort.startswith('-'):
			direction = 'desc'
			field = sort[1:]
		if field == 'nome':
			q = q.order_by(Aluno.nome.desc() if direction == 'desc' else Aluno.nome.asc())
		elif field == 'data_nascimento':
			q = q.order_by(Aluno.data_nascimento.desc() if direction == 'desc' else Aluno.data_nascimento.asc())
	return q.offset(offset).limit(limit).all()


@app.get('/alunos/export')
def export_alunos(format: str = 'csv', search: str = '', turma_id: Optional[int] = None, status: Optional[str] = None,
                  sort: Optional[str] = None, db: Session = Depends(get_db)):
	"""Exporta a lista de alunos filtrada em CSV ou JSON. Use ?format=csv or ?format=json"""
	q = db.query(Aluno)
	if search:
		q = q.filter(Aluno.nome.ilike(f"%{search}%"))
	if turma_id:
		q = q.filter(Aluno.turma_id == turma_id)
	if status:
		q = q.filter(Aluno.status == status)
	# apply same sorting logic as listar
	if sort:
		direction = 'asc'
		field = sort
		if sort.startswith('-'):
			direction = 'desc'
			field = sort[1:]
		if field == 'nome':
			q = q.order_by(Aluno.nome.desc() if direction == 'desc' else Aluno.nome.asc())
		elif field == 'data_nascimento':
			q = q.order_by(Aluno.data_nascimento.desc() if direction == 'desc' else Aluno.data_nascimento.asc())
	alunos = q.all()
	if format == 'json':
		# reuse pydantic serialization by building list of dicts
		data = [
			{
				"id": a.id,
				"nome": a.nome,
				"data_nascimento": a.data_nascimento.isoformat(),
				"email": a.email,
				"status": a.status,
				"turma_id": a.turma_id
			} for a in alunos
		]
		return JSONResponse(content=data)
	# CSV
	output = io.StringIO()
	csv_writer = csv.writer(output)
	csv_writer.writerow(["id","nome","data_nascimento","email","status","turma_id"])
	for a in alunos:
		csv_writer.writerow([a.id, a.nome, a.data_nascimento.isoformat(), a.email or '', a.status, a.turma_id or ''])
	output.seek(0)
	headers = {'Content-Disposition': 'attachment; filename="alunos_export.csv"'}
	return StreamingResponse(output, media_type='text/csv', headers=headers)


@app.post('/alunos', status_code=status.HTTP_201_CREATED)
def criar_aluno(payload: AlunoSchema, db: Session = Depends(get_db)):
	if payload.email:
		existe = db.query(Aluno).filter(Aluno.email == payload.email).first()
		if existe:
			raise HTTPException(status_code=400, detail='Email já cadastrado')
	aluno = Aluno(**payload.dict())
	db.add(aluno)
	db.commit()
	db.refresh(aluno)
	return aluno


@app.put('/alunos/{aluno_id}')
def atualizar_aluno(aluno_id: int, payload: AlunoSchema, db: Session = Depends(get_db)):
	aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
	if not aluno:
		raise HTTPException(status_code=404, detail='Aluno não encontrado')
	if payload.email and payload.email != aluno.email:
		existe = db.query(Aluno).filter(Aluno.email == payload.email).first()
		if existe:
			raise HTTPException(status_code=400, detail='Email já cadastrado')
	for k, v in payload.dict().items():
		setattr(aluno, k, v)
	db.commit()
	db.refresh(aluno)
	return aluno


@app.delete('/alunos/{aluno_id}', status_code=status.HTTP_204_NO_CONTENT)
def deletar_aluno(aluno_id: int, db: Session = Depends(get_db)):
	aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
	if not aluno:
		raise HTTPException(status_code=404, detail='Aluno não encontrado')
	db.delete(aluno)
	db.commit()
	return


@app.get('/turmas')
def listar_turmas(db: Session = Depends(get_db)):
	turmas = db.query(Turma).all()
	return turmas


@app.post('/turmas', status_code=status.HTTP_201_CREATED)
def criar_turma(payload: TurmaSchema, db: Session = Depends(get_db)):
	turma = Turma(**payload.dict())
	db.add(turma)
	db.commit()
	db.refresh(turma)
	return turma


@app.post('/matriculas')
def matricular(aluno_id: int, turma_id: int, db: Session = Depends(get_db)):
	turma = db.query(Turma).filter(Turma.id == turma_id).first()
	aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
	if not turma or not aluno:
		raise HTTPException(status_code=404, detail='Aluno ou turma não encontrada')
	ocupacao = db.query(Aluno).filter(Aluno.turma_id == turma_id).count()
	if ocupacao >= turma.capacidade:
		raise HTTPException(status_code=400, detail='Capacidade da turma excedida')
	aluno.status = 'ativo'
	aluno.turma_id = turma_id
	db.commit()
	db.refresh(aluno)
	return {"message": "Aluno matriculado com sucesso"}

