from database import SessionLocal
from models import Aluno, Turma
from datetime import date

def seed():
    db = SessionLocal()
    turmas = [
        Turma(nome="1º Ano A", capacidade=10),
        Turma(nome="2º Ano B", capacidade=12),
        Turma(nome="3º Ano C", capacidade=8)
    ]
    db.add_all(turmas)
    db.commit()
    alunos = [
        Aluno(nome=f"Aluno {i+1}", data_nascimento=date(2010, 1, (i%28)+1), status="ativo") for i in range(20)
    ]
    db.add_all(alunos)
    db.commit()
    db.close()

if __name__ == "__main__":
    seed()
