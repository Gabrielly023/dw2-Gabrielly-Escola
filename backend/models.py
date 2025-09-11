from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Turma(Base):
    __tablename__ = 'turmas'
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    capacidade = Column(Integer, nullable=False)
    
    # Relacionamento bidirecional com Aluno
    alunos = relationship("Aluno", back_populates="turma")


class Aluno(Base):
    __tablename__ = 'alunos'
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    status = Column(String(20), nullable=False, default='inativo')
    turma_id = Column(Integer, ForeignKey('turmas.id'), nullable=True)
    
    # Relacionamento bidirecional com Turma
    turma = relationship("Turma", back_populates="alunos")

