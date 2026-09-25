from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.busca import contem
from app.database import get_db
from app.erros_db import confirmar, traduzir_integridade
from app.acesso import condicao_pessoa_visivel
from app.models import Cep, Pessoa, Usuario, PessoaFisica, PessoaJuridica, PessoaTelefone
from app.schemas import PessoaCreate, PessoaRead
from app.security import exigir_escrita, get_current_user

router = APIRouter(prefix="/pessoas", tags=["Pessoas"])

NAO_ENCONTRADA = "Pessoa nao encontrada"


def _buscar(db: Session, usuario: Usuario, pessoa_id: int) -> Pessoa:
    """404 tanto para pessoa inexistente quanto para a que o usuario nao enxerga."""
    stmt = select(Pessoa).where(Pessoa.id == pessoa_id)
    condicao = condicao_pessoa_visivel(usuario)
    if condicao is not None:
        stmt = stmt.where(condicao)
    pessoa = db.execute(stmt).unique().scalar_one_or_none()
    if not pessoa:
        raise HTTPException(status_code=404, detail=NAO_ENCONTRADA)
    return pessoa


def _validar_local(db: Session, payload: PessoaCreate) -> None:
    """O bairro/localidade escolhido precisa ser um dos que o CEP da pessoa cobre:
    o banco so garante que eles existem, nao que combinam com o CEP."""
    if not (payload.bairro_id or payload.localidade_id):
        return
    if not payload.cep:
        raise HTTPException(status_code=400, detail="Informe o CEP para escolher o bairro ou a localidade")
    cep = db.get(Cep, payload.cep)
    if not cep:
        raise HTTPException(status_code=400, detail="CEP nao cadastrado")
    if payload.bairro_id and payload.bairro_id not in cep.bairro_ids:
        raise HTTPException(status_code=400, detail="Esse bairro nao pertence ao CEP informado")
    if payload.localidade_id and payload.localidade_id not in cep.localidade_ids:
        raise HTTPException(status_code=400, detail="Essa localidade nao pertence ao CEP informado")


def _aplicar(db: Session, pessoa: Pessoa, payload: PessoaCreate) -> None:
    """Grava a pessoa e o subtipo/telefones que o tipo_pessoa pede.

    Serve para criar e para editar. Trocar de fisica para juridica (ou o
    inverso) remove o subtipo antigo - o cascade delete-orphan apaga a linha.
    """
    pessoa.tipo_pessoa = payload.tipo_pessoa
    pessoa.nome = payload.nome
    pessoa.email = payload.email
    pessoa.cep = payload.cep
    pessoa.bairro_id = payload.bairro_id
    pessoa.localidade_id = payload.localidade_id
    pessoa.endereco = payload.endereco
    pessoa.numero = payload.numero
    pessoa.complemento = payload.complemento
    pessoa.ativo = payload.ativo

    if payload.tipo_pessoa == "F":
        pessoa.juridica = None
        fisica = pessoa.fisica or PessoaFisica()
        fisica.cpf = payload.cpf
        fisica.data_nascimento = payload.data_nascimento
        pessoa.fisica = fisica
    else:
        pessoa.fisica = None
        juridica = pessoa.juridica or PessoaJuridica()
        juridica.cnpj = payload.cnpj
        juridica.razao_social = payload.razao_social
        juridica.nome_fantasia = payload.nome_fantasia
        juridica.data_fundacao = payload.data_fundacao
        pessoa.juridica = juridica

    # Lista substituida por inteiro: o front sempre manda o conjunto completo.
    # Os antigos saem ANTES de entrar os novos (flush no meio): o indice unico
    # parcial "um principal por pessoa" estouraria se o novo principal fosse
    # inserido com o antigo ainda la.
    if pessoa.telefones:
        pessoa.telefones.clear()
        db.flush()
    pessoa.telefones = [
        PessoaTelefone(numero=t.numero, tipo_telefone=t.tipo_telefone, principal=t.principal)
        for t in payload.telefones
    ]


@router.post("/", response_model=PessoaRead, status_code=201)
def criar_pessoa(
    payload: PessoaCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(exigir_escrita),
):
    _validar_local(db, payload)
    pessoa = Pessoa(usuario_inclusao_id=usuario.id)
    with traduzir_integridade(db):
        _aplicar(db, pessoa, payload)
    db.add(pessoa)
    confirmar(db)
    db.refresh(pessoa)
    return pessoa


@router.get("/", response_model=list[PessoaRead])
def listar_pessoas(
    busca: str | None = None,
    tipo_pessoa: str | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    stmt = select(Pessoa)
    condicao = condicao_pessoa_visivel(usuario)
    if condicao is not None:
        stmt = stmt.where(condicao)
    if tipo_pessoa:
        stmt = stmt.where(Pessoa.tipo_pessoa == tipo_pessoa)
    if busca:
        stmt = stmt.where(contem(Pessoa.nome, busca))
    return db.execute(stmt.order_by(Pessoa.nome)).unique().scalars().all()


@router.get("/{pessoa_id}", response_model=PessoaRead)
def obter_pessoa(pessoa_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return _buscar(db, usuario, pessoa_id)


@router.put("/{pessoa_id}", response_model=PessoaRead, dependencies=[Depends(exigir_escrita)])
def atualizar_pessoa(
    pessoa_id: int, payload: PessoaCreate, db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    pessoa = _buscar(db, usuario, pessoa_id)
    _validar_local(db, payload)
    with traduzir_integridade(db):
        _aplicar(db, pessoa, payload)
    confirmar(db)
    db.refresh(pessoa)
    return pessoa


@router.delete("/{pessoa_id}", status_code=204, dependencies=[Depends(exigir_escrita)])
def desativar_pessoa(pessoa_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    """Soft delete: a pessoa pode ser dona de propriedade ou ter usuario, entao
    o cadastro so fica inativo."""
    pessoa = _buscar(db, usuario, pessoa_id)
    pessoa.ativo = False
    db.commit()
