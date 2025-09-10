from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Aluno(Base):
	__tablename__ = 'alunos'
	id = Column(Integer, primary_key=True)
	nome = Column(String(80), nullable=False)
	status = Column(String(20), nullable=False, default='inativo')

