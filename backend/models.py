# Modelos SQLAlchemy para o mini-sistema web
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Turma(Base):
    __tablename__ = 'turmas'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(40), nullable=False)
    capacidade = Column(Integer, nullable=False)
    alunos = relationship("Aluno", back_populates="turma")

class Aluno(Base):
    __tablename__ = 'alunos'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(80), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    status = Column(String(10), nullable=False, default="ativo")
    turma_id = Column(Integer, ForeignKey('turmas.id'), nullable=True)
    turma = relationship("Turma", back_populates="alunos")
 
