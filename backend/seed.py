from .database import SessionLocal
from .models import Aluno


def seed():
	db = SessionLocal()
	# limpar e inserir exemplos mínimos
	db.query(Aluno).delete()
	db.add_all([
		Aluno(nome='Ana Silva', status='ativo'),
		Aluno(nome='Bruno Costa', status='inativo'),
	])
	db.commit()
	db.close()


if __name__ == '__main__':
	seed()

