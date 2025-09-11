from fastapi import FastAPI, Depends, Query, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from . import models
from . import database
from .database import SessionLocal
from typing import Optional
from pydantic import BaseModel, Field, validator, ValidationError
from datetime import date, datetime
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar instância do FastAPI
app = FastAPI(
    title="Sistema Escola API",
    description="API para gerenciamento de alunos e turmas",
    version="1.0.0"
)

# Handler para erros internos do servidor
@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    logger.error(f"Erro interno do servidor: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Ocorreu um erro inesperado no servidor. Tente novamente mais tarde."
        }
    )

# Handler para erros de banco de dados
@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request, exc: SQLAlchemyError):
    logger.error(f"Erro de banco de dados: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Database Error",
            "message": "Erro na operação do banco de dados. Tente novamente mais tarde."
        }
    )

# Handler personalizado para erros de validação
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    # Verificar se é erro de data de nascimento
    for error in exc.errors():
        if 'data_nascimento' in error.get('loc', []) and 'Aluno deve ter pelo menos 5 anos' in str(error.get('msg', '')):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Bad Request",
                    "message": "Aluno deve ter pelo menos 5 anos"
                }
            )
        # Verificar se é erro de email
        if 'email' in error.get('loc', []) and 'Email inválido ou já existente' in str(error.get('msg', '')):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Bad Request", 
                    "message": "Email inválido ou já existente"
                }
            )
    
    # Para outros erros de validação, retornar 422
    return JSONResponse(
        status_code=422,
        content={
            "error": "Unprocessable Entity",
            "message": "Os dados fornecidos são inválidos",
            "details": exc.errors()
        }
    )

# Criar tabelas do banco de dados automaticamente
models.Base.metadata.create_all(bind=database.engine)

# Dependência para obter sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schema Pydantic para criação de aluno
class AlunoCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=80, description="Nome do aluno (3-80 caracteres)")
    data_nascimento: date = Field(..., description="Data de nascimento do aluno")
    email: Optional[str] = Field(None, description="Email do aluno (opcional)")
    status: str = Field(..., description="Status do aluno: ativo ou inativo")
    turma_id: Optional[int] = Field(None, description="ID da turma (opcional)")

    @validator('data_nascimento')
    def validar_data_nascimento(cls, v):
        hoje = date.today()
        idade_minima = hoje.replace(year=hoje.year - 5)
        if v > idade_minima:
            raise ValueError('Aluno deve ter pelo menos 5 anos')
        return v

    @validator('email')
    def validar_email(cls, v):
        if v is not None:
            # Regex para validar email
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, v):
                raise ValueError('Email inválido ou já existente')
        return v

    @validator('status')
    def validar_status(cls, v):
        if v not in ['ativo', 'inativo']:
            raise ValueError('Status deve ser "ativo" ou "inativo"')
        return v

# Endpoint GET /health
@app.get('/health', status_code=status.HTTP_200_OK)
def health():
    """Verificar saúde da API"""
    return {
        "status": "ok",
        "message": "API funcionando corretamente"
    }

# Endpoint GET /alunos
@app.get('/alunos', status_code=status.HTTP_200_OK)
def get_alunos(
    search: Optional[str] = Query(None, description="Buscar por nome do aluno"),
    turma_id: Optional[int] = Query(None, description="Filtrar por ID da turma"),
    status: Optional[str] = Query(None, description="Filtrar por status (ativo/inativo)"),
    db: Session = Depends(get_db)
):
    """Listar todos os alunos com filtros opcionais"""
    try:
    # Começar com query base
    query = db.query(models.Aluno)
    
    # Aplicar filtro de busca por nome (case-insensitive)
    if search:
        query = query.filter(models.Aluno.nome.ilike(f"%{search}%"))
    
    # Aplicar filtro por turma_id
    if turma_id is not None:
        query = query.filter(models.Aluno.turma_id == turma_id)
    
    # Aplicar filtro por status
    if status:
        query = query.filter(models.Aluno.status == status)
    
    # Executar query e buscar resultados
    alunos = query.all()
    
    # Converter para formato JSON
    alunos_json = []
    for aluno in alunos:
        aluno_dict = {
            "id": aluno.id,
            "nome": aluno.nome,
            "data_nascimento": aluno.data_nascimento.isoformat() if aluno.data_nascimento else None,
            "email": aluno.email,
            "status": aluno.status,
            "turma_id": aluno.turma_id,
            "turma_nome": aluno.turma.nome if aluno.turma else None
        }
        alunos_json.append(aluno_dict)
    
        return {
            "total": len(alunos_json),
            "filtros_aplicados": {
                "search": search,
                "turma_id": turma_id,
                "status": status
            },
            "alunos": alunos_json
        }
    except SQLAlchemyError as e:
        logger.error(f"Erro ao buscar alunos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "Erro ao buscar alunos no banco de dados"
            }
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar alunos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error", 
                "message": "Erro inesperado ao processar solicitação"
            }
        )

# Endpoint POST /alunos
@app.post('/alunos', status_code=status.HTTP_201_CREATED)
def criar_aluno(aluno: AlunoCreate, db: Session = Depends(get_db)):
    """Criar um novo aluno"""
    try:
        # Validar se email é único (se informado)
        if aluno.email:
            email_existente = db.query(models.Aluno).filter(models.Aluno.email == aluno.email).first()
            if email_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Bad Request",
                        "message": "Email inválido ou já existente"
                    }
                )
        
        # Validar se turma_id existe (se informado)
        if aluno.turma_id:
            turma_existe = db.query(models.Turma).filter(models.Turma.id == aluno.turma_id).first()
            if not turma_existe:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": "Not Found",
                        "message": "Turma não encontrada"
                    }
                )
    
    # Criar novo aluno
    novo_aluno = models.Aluno(
        nome=aluno.nome,
        data_nascimento=aluno.data_nascimento,
        email=aluno.email,
        status=aluno.status,
        turma_id=aluno.turma_id
    )
    
    # Salvar no banco
    db.add(novo_aluno)
    db.commit()
    db.refresh(novo_aluno)  # Para obter o ID gerado
    
    # Buscar dados da turma se existir
    turma_nome = None
    if novo_aluno.turma:
        turma_nome = novo_aluno.turma.nome
    
        # Retornar aluno criado
        return {
            "message": "Aluno criado com sucesso",
            "aluno": {
                "id": novo_aluno.id,
                "nome": novo_aluno.nome,
                "data_nascimento": novo_aluno.data_nascimento.isoformat(),
                "email": novo_aluno.email,
                "status": novo_aluno.status,
                "turma_id": novo_aluno.turma_id,
                "turma_nome": turma_nome
            }
        }
    except HTTPException:
        raise  # Re-raise HTTPExceptions (400, 404)
    except SQLAlchemyError as e:
        logger.error(f"Erro ao criar aluno: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "Erro ao salvar aluno no banco de dados"
            }
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao criar aluno: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "Erro inesperado ao processar solicitação"
            }
        )# Schema Pydantic para atualização de aluno (mesmas validações do POST)
class AlunoUpdate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=80, description="Nome do aluno (3-80 caracteres)")
    data_nascimento: date = Field(..., description="Data de nascimento do aluno")
    email: Optional[str] = Field(None, description="Email do aluno (opcional)")
    status: str = Field(..., description="Status do aluno: ativo ou inativo")
    turma_id: Optional[int] = Field(None, description="ID da turma (opcional)")

    @validator('data_nascimento')
    def validar_data_nascimento(cls, v):
        hoje = date.today()
        idade_minima = hoje.replace(year=hoje.year - 5)
        if v > idade_minima:
            raise ValueError('Aluno deve ter pelo menos 5 anos')
        return v

    @validator('email')
    def validar_email(cls, v):
        if v is not None:
            # Regex para validar email
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, v):
                raise ValueError('Email inválido ou já existente')
        return v

    @validator('status')
    def validar_status(cls, v):
        if v not in ['ativo', 'inativo']:
            raise ValueError('Status deve ser "ativo" ou "inativo"')
        return v

# Endpoint PUT /alunos/{id}
@app.put('/alunos/{id}')
def atualizar_aluno(id: int, aluno_dados: AlunoUpdate, db: Session = Depends(get_db)):
    # Buscar o aluno pelo ID
    aluno_existente = db.query(models.Aluno).filter(models.Aluno.id == id).first()
    
    # Se não existir, retornar 404
    if not aluno_existente:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    # Validar se email é único (se informado e diferente do atual)
    if aluno_dados.email and aluno_dados.email != aluno_existente.email:
        email_existente = db.query(models.Aluno).filter(
            models.Aluno.email == aluno_dados.email,
            models.Aluno.id != id
        ).first()
        if email_existente:
            raise HTTPException(status_code=400, detail="Email inválido ou já existente")
    
    # Validar se turma_id existe (se informado)
    if aluno_dados.turma_id:
        turma_existe = db.query(models.Turma).filter(models.Turma.id == aluno_dados.turma_id).first()
        if not turma_existe:
            raise HTTPException(status_code=400, detail="Turma não encontrada")
    
    # Atualizar dados do aluno
    aluno_existente.nome = aluno_dados.nome
    aluno_existente.data_nascimento = aluno_dados.data_nascimento
    aluno_existente.email = aluno_dados.email
    aluno_existente.status = aluno_dados.status
    aluno_existente.turma_id = aluno_dados.turma_id
    
    # Salvar no banco
    db.commit()
    db.refresh(aluno_existente)  # Para atualizar os relacionamentos
    
    # Buscar dados da turma se existir
    turma_nome = None
    if aluno_existente.turma:
        turma_nome = aluno_existente.turma.nome
    
    # Retornar aluno atualizado
    return {
        "message": "Aluno atualizado com sucesso",
        "aluno": {
            "id": aluno_existente.id,
            "nome": aluno_existente.nome,
            "data_nascimento": aluno_existente.data_nascimento.isoformat(),
            "email": aluno_existente.email,
            "status": aluno_existente.status,
            "turma_id": aluno_existente.turma_id,
            "turma_nome": turma_nome
        }
    }

# Endpoint DELETE /alunos/{id}
@app.delete('/alunos/{id}', status_code=status.HTTP_200_OK)
def deletar_aluno(id: int, db: Session = Depends(get_db)):
    """Deletar um aluno por ID"""
    try:
        # Buscar o aluno pelo ID
        aluno_existente = db.query(models.Aluno).filter(models.Aluno.id == id).first()
        
        # Se não existir, retornar 404
        if not aluno_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Not Found",
                    "message": "Aluno não encontrado"
                }
            )
        
        # Excluir do banco
        db.delete(aluno_existente)
        db.commit()
        
        # Retornar mensagem de sucesso
        return {
            "message": "Aluno deletado com sucesso",
            "aluno_id": id
        }
    except HTTPException:
        raise  # Re-raise HTTPExceptions (404)
    except SQLAlchemyError as e:
        logger.error(f"Erro ao deletar aluno {id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "Erro ao deletar aluno do banco de dados"
            }
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao deletar aluno {id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "Erro inesperado ao processar solicitação"
            }
        )

# Endpoint GET /turmas
@app.get('/turmas', status_code=status.HTTP_200_OK)
def get_turmas(db: Session = Depends(get_db)):
    """Listar todas as turmas com informações de ocupação"""
    try:
    # Buscar todas as turmas no banco de dados
    turmas = db.query(models.Turma).all()
    
    # Converter para formato JSON com contagem de alunos
    turmas_json = []
    for turma in turmas:
        # Contar quantos alunos estão matriculados na turma
        quantidade_alunos = db.query(models.Aluno).filter(models.Aluno.turma_id == turma.id).count()
        
        turma_dict = {
            "id": turma.id,
            "nome": turma.nome,
            "capacidade": turma.capacidade,
            "alunos_matriculados": quantidade_alunos,
            "vagas_disponíveis": turma.capacidade - quantidade_alunos
        }
        turmas_json.append(turma_dict)
    
        return {
            "total": len(turmas_json),
            "turmas": turmas_json
        }
    except SQLAlchemyError as e:
        logger.error(f"Erro ao buscar turmas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "Erro ao buscar turmas no banco de dados"
            }
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar turmas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "Erro inesperado ao processar solicitação"
            }
        )

# Schema Pydantic para criação de turma
class TurmaCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da turma (não pode estar vazio)")
    capacidade: int = Field(..., gt=0, description="Capacidade da turma (deve ser maior que zero)")

    @validator('nome')
    def validar_nome(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome da turma não pode estar vazio')
        return v.strip()

    @validator('capacidade')
    def validar_capacidade(cls, v):
        if v <= 0:
            raise ValueError('Capacidade deve ser maior que zero')
        return v

# Endpoint POST /turmas
@app.post('/turmas', status_code=status.HTTP_201_CREATED)
def criar_turma(turma: TurmaCreate, db: Session = Depends(get_db)):
    """Criar uma nova turma"""
    try:
        # Verificar se já existe uma turma com o mesmo nome
        turma_existente = db.query(models.Turma).filter(models.Turma.nome == turma.nome).first()
        if turma_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Bad Request",
                    "message": "Já existe uma turma com este nome"
                }
            )
    
    # Criar nova turma
    nova_turma = models.Turma(
        nome=turma.nome,
        capacidade=turma.capacidade
    )
    
    # Salvar no banco
    db.add(nova_turma)
    db.commit()
    db.refresh(nova_turma)  # Para obter o ID gerado
    
        # Retornar turma criada
        return {
            "message": "Turma criada com sucesso",
            "turma": {
                "id": nova_turma.id,
                "nome": nova_turma.nome,
                "capacidade": nova_turma.capacidade,
                "alunos_matriculados": 0,
                "vagas_disponíveis": nova_turma.capacidade
            }
        }
    except HTTPException:
        raise  # Re-raise HTTPExceptions (400)
    except SQLAlchemyError as e:
        logger.error(f"Erro ao criar turma: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "Erro ao salvar turma no banco de dados"
            }
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao criar turma: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "Erro inesperado ao processar solicitação"
            }
        )# Schema Pydantic para matrícula
class MatriculaCreate(BaseModel):
    aluno_id: int = Field(..., gt=0, description="ID do aluno a ser matriculado")
    turma_id: int = Field(..., gt=0, description="ID da turma para matrícula")

    @validator('aluno_id')
    def validar_aluno_id(cls, v):
        if v <= 0:
            raise ValueError('ID do aluno deve ser maior que zero')
        return v

    @validator('turma_id')
    def validar_turma_id(cls, v):
        if v <= 0:
            raise ValueError('ID da turma deve ser maior que zero')
        return v

# Endpoint POST /matriculas
@app.post('/matriculas')
def matricular_aluno(matricula: MatriculaCreate, db: Session = Depends(get_db)):
    # Validar se aluno existe
    aluno = db.query(models.Aluno).filter(models.Aluno.id == matricula.aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    # Validar se turma existe
    turma = db.query(models.Turma).filter(models.Turma.id == matricula.turma_id).first()
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    # Verificar capacidade da turma
    alunos_matriculados = db.query(models.Aluno).filter(models.Aluno.turma_id == turma.id).count()
    if alunos_matriculados >= turma.capacidade:
        raise HTTPException(
            status_code=400, 
            detail=f"Turma '{turma.nome}' já atingiu sua capacidade máxima ({turma.capacidade} alunos)"
        )
    
    # Verificar se aluno já está matriculado nesta turma
    if aluno.turma_id == turma.id:
        raise HTTPException(
            status_code=400, 
            detail=f"Aluno '{aluno.nome}' já está matriculado na turma '{turma.nome}'"
        )
    
    # Matricular o aluno
    aluno.turma_id = matricula.turma_id
    aluno.status = "ativo"  # Alterar status para ativo
    
    # Salvar no banco
    db.commit()
    db.refresh(aluno)
    
    # Retornar sucesso com informações detalhadas
    return {
        "message": "Aluno matriculado com sucesso",
        "detalhes": {
            "aluno": {
                "id": aluno.id,
                "nome": aluno.nome,
                "status": aluno.status
            },
            "turma": {
                "id": turma.id,
                "nome": turma.nome,
                "alunos_matriculados": alunos_matriculados + 1,
                "vagas_restantes": turma.capacidade - (alunos_matriculados + 1)
            }
        }
    }

# Configuração para rodar com uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


