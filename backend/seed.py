from . import database
from . import models
from datetime import date


def seed():
	# Garantir que as tabelas existam
	models.Base.metadata.create_all(bind=database.engine)
	
	db = database.SessionLocal()
	try:
		# Limpar dados existentes
		db.query(models.Aluno).delete()
		db.query(models.Turma).delete()
		
		# Inserir 5 turmas de exemplo
		turmas = [
			models.Turma(nome='6º Ano A', capacidade=25),
			models.Turma(nome='7º Ano A', capacidade=28),
			models.Turma(nome='8º Ano A', capacidade=30),
			models.Turma(nome='9º Ano A', capacidade=32),
			models.Turma(nome='1º Ano Médio', capacidade=35),
		]
		db.add_all(turmas)
		db.flush()  # Para obter os IDs das turmas
		
		# Inserir 15 alunos de exemplo
		alunos = [
			# 6º Ano A
			models.Aluno(nome='Ana Silva', data_nascimento=date(2010, 3, 15), email='ana.silva@email.com', status='ativo', turma_id=turmas[0].id),
			models.Aluno(nome='Bruno Costa', data_nascimento=date(2010, 7, 22), email='bruno.costa@email.com', status='ativo', turma_id=turmas[0].id),
			models.Aluno(nome='Carlos Santos', data_nascimento=date(2010, 11, 8), email='carlos.santos@email.com', status='inativo', turma_id=turmas[0].id),
			
			# 7º Ano A
			models.Aluno(nome='Diana Oliveira', data_nascimento=date(2009, 1, 30), email='diana.oliveira@email.com', status='ativo', turma_id=turmas[1].id),
			models.Aluno(nome='Eduardo Lima', data_nascimento=date(2009, 9, 12), email='eduardo.lima@email.com', status='ativo', turma_id=turmas[1].id),
			models.Aluno(nome='Fernanda Rocha', data_nascimento=date(2009, 5, 18), email='fernanda.rocha@email.com', status='ativo', turma_id=turmas[1].id),
			
			# 8º Ano A
			models.Aluno(nome='Gabriel Torres', data_nascimento=date(2008, 12, 3), email='gabriel.torres@email.com', status='ativo', turma_id=turmas[2].id),
			models.Aluno(nome='Helena Martins', data_nascimento=date(2008, 4, 25), email='helena.martins@email.com', status='inativo', turma_id=turmas[2].id),
			models.Aluno(nome='Igor Pereira', data_nascimento=date(2008, 8, 14), email='igor.pereira@email.com', status='ativo', turma_id=turmas[2].id),
			models.Aluno(nome='Júlia Andrade', data_nascimento=date(2008, 6, 7), status='ativo', turma_id=turmas[2].id),  # sem email
			
			# 9º Ano A
			models.Aluno(nome='Kaique Ferreira', data_nascimento=date(2007, 2, 20), email='kaique.ferreira@email.com', status='ativo', turma_id=turmas[3].id),
			models.Aluno(nome='Larissa Mendes', data_nascimento=date(2007, 10, 11), email='larissa.mendes@email.com', status='ativo', turma_id=turmas[3].id),
			models.Aluno(nome='Marcos Vieira', data_nascimento=date(2007, 7, 29), status='inativo', turma_id=turmas[3].id),  # sem email
			
			# 1º Ano Médio
			models.Aluno(nome='Natália Cardoso', data_nascimento=date(2006, 3, 16), email='natalia.cardoso@email.com', status='ativo', turma_id=turmas[4].id),
			models.Aluno(nome='Otávio Ribeiro', data_nascimento=date(2006, 11, 2), email='otavio.ribeiro@email.com', status='ativo', turma_id=turmas[4].id),
		]
		db.add_all(alunos)
		
		# Salvar no banco
		db.commit()
		print("✅ Dados inseridos com sucesso no banco app.db!")
		print(f"📚 Turmas criadas: {len(turmas)}")
		print(f"👨‍🎓 Alunos criados: {len(alunos)}")
		
		# Mostrar estatísticas por turma
		print("\n📊 Distribuição por turma:")
		for turma in turmas:
			count = db.query(models.Aluno).filter(models.Aluno.turma_id == turma.id).count()
			print(f"  • {turma.nome}: {count} alunos (capacidade: {turma.capacidade})")
		
	except Exception as e:
		print(f"❌ Erro ao inserir dados: {e}")
		db.rollback()
	finally:
		db.close()


if __name__ == '__main__':
	seed()


if __name__ == '__main__':
	seed()

