from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

from database import SessionLocal
from models import Aluno, Turma
from datetime import date


def seed():
	db = SessionLocal()
	# limpar
	db.query(Aluno).delete()
	db.query(Turma).delete()
	db.commit()

	turmas = [
		Turma(nome='1º Ano A', capacidade=10),
		Turma(nome='2º Ano B', capacidade=12),
		Turma(nome='3º Ano C', capacidade=8),
	]
	db.add_all(turmas)
	db.commit()

	nomes = [
		'Ana Silva','Bruno Costa','Carla Souza','Diego Oliveira','Eduarda Lima',
		'Fabio Rocha','Gabriela Martins','Henrique Alves','Isabela Pinto','Joao Fernandes',
		'Katia Ramos','Lucas Pereira','Mariana Gomes','Nathan Silva','Olivia Castro',
		'Paulo Nunes','Quenia Moraes','Rafael Dias','Sofia Andrade','Thiago Barros'
	]
	anos = [2012, 2011, 2010, 2009, 2008]
	alunos = []
	for i, nome in enumerate(nomes):
		ano = anos[i % len(anos)]
		dia = (i % 28) + 1
		mes = ((i % 12) + 1)
		data_nasc = date(ano, mes, dia)
		email = f"{nome.split()[0].lower()}.{nome.split()[-1].lower()}@escola.local"
		turma_id = turmas[i % len(turmas)].id
		alunos.append(Aluno(nome=nome, data_nascimento=data_nasc, email=email, status='ativo', turma_id=turma_id))

	db.add_all(alunos)
	db.commit()
	db.close()


if __name__ == '__main__':
	seed()

