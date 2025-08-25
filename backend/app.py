from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine
from models import Base, Aluno, Turma
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr, constr
from datetime import date

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class AlunoBase(BaseModel):
    nome: constr(min_length=3, max_length=80)
    data_nascimento: date
    email: EmailStr | None = None
    status: constr(to_lower=True) = "ativo"
    turma_id: int | None = None

class AlunoCreate(AlunoBase):
    pass

class AlunoOut(AlunoBase):
    id: int
    class Config:
        orm_mode = True

class TurmaBase(BaseModel):
    nome: constr(min_length=2, max_length=40)
    capacidade: int

class TurmaCreate(TurmaBase):
    pass

class TurmaOut(TurmaBase):
    id: int
    class Config:
        orm_mode = True

# Dependência
from fastapi import Depends
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/alunos", response_model=List[AlunoOut])
def listar_alunos(search: str = "", turma_id: int = None, status: str = None, db: Session = Depends(get_db)):
    query = db.query(Aluno)
    if search:
        query = query.filter(Aluno.nome.ilike(f"%{search}%"))
    if turma_id:
        query = query.filter(Aluno.turma_id == turma_id)
    if status:
        query = query.filter(Aluno.status == status)
    return query.all()

@app.post("/alunos", response_model=AlunoOut, status_code=status.HTTP_201_CREATED)
def criar_aluno(aluno: AlunoCreate, db: Session = Depends(get_db)):
    novo_aluno = Aluno(**aluno.dict())
    db.add(novo_aluno)
    db.commit()
    db.refresh(novo_aluno)
    return novo_aluno

@app.put("/alunos/{aluno_id}", response_model=AlunoOut)
def atualizar_aluno(aluno_id: int, aluno: AlunoCreate, db: Session = Depends(get_db)):
    db_aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if not db_aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    for key, value in aluno.dict().items():
        setattr(db_aluno, key, value)
    db.commit()
    db.refresh(db_aluno)
    return db_aluno

@app.delete("/alunos/{aluno_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_aluno(aluno_id: int, db: Session = Depends(get_db)):
    db_aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if not db_aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    db.delete(db_aluno)
    db.commit()
    return

@app.get("/turmas", response_model=List[TurmaOut])
def listar_turmas(db: Session = Depends(get_db)):
    return db.query(Turma).all()

@app.post("/turmas", response_model=TurmaOut, status_code=status.HTTP_201_CREATED)
def criar_turma(turma: TurmaCreate, db: Session = Depends(get_db)):
    nova_turma = Turma(**turma.dict())
    db.add(nova_turma)
    db.commit()
    db.refresh(nova_turma)
    return nova_turma

@app.post("/matriculas", status_code=status.HTTP_201_CREATED)
def matricular_aluno(aluno_id: int, turma_id: int, db: Session = Depends(get_db)):
    turma = db.query(Turma).filter(Turma.id == turma_id).first()
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if not turma or not aluno:
        raise HTTPException(status_code=404, detail="Aluno ou turma não encontrada")
    total_matriculados = db.query(Aluno).filter(Aluno.turma_id == turma_id).count()
    if total_matriculados >= turma.capacidade:
        raise HTTPException(status_code=400, detail="Capacidade da turma excedida")
    aluno.status = "ativo"
    aluno.turma_id = turma_id
    db.commit()
    db.refresh(aluno)
    return {"message": "Aluno matriculado com sucesso"}

@app.get("/health")
def health():
    return {"status": "ok"}
