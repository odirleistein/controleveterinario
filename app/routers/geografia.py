"""
Cadeia geografica: estado -> cidade -> bairro -> localidade -> CEP.

Cinco routers no mesmo arquivo porque sao cadastros pequenos e iguais no
formato. Leitura para qualquer usuario logado; gravacao so para MASTER/ADMIN.
Cidade, bairro e localidade nao sao apagados (viram inativos), para nao
esconder o endereco de propriedades e pessoas ja cadastradas; estado e CEP
sao removidos de fato, e o banco recusa (FK RESTRICT) se ainda estiverem em uso.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.busca import contem
from app.database import get_db
from app.erros_db import confirmar
from app.models import Bairro, Cep, Cidade, Estado, Localidade
from app.schemas import (
    BairroBase, BairroRead, CepCreate, CepRead, CepUpdate, CidadeBase, CidadeRead,
    EstadoBase, EstadoRead, LocalidadeBase, LocalidadeRead,
)
from app.security import exigir_escrita

router_estados = APIRouter(prefix="/estados", tags=["Estados"])
router_cidades = APIRouter(prefix="/cidades", tags=["Cidades"])
router_bairros = APIRouter(prefix="/bairros", tags=["Bairros"])
router_localidades = APIRouter(prefix="/localidades", tags=["Localidades"])
router_ceps = APIRouter(prefix="/ceps", tags=["CEPs"])


def _obter(db: Session, modelo, chave, mensagem: str):
    registro = db.get(modelo, chave)
    if not registro:
        raise HTTPException(status_code=404, detail=mensagem)
    return registro


def _aplicar(registro, payload) -> None:
    for campo, valor in payload.model_dump().items():
        setattr(registro, campo, valor)


# ---------------------------------------------------------------------
# ESTADOS
# ---------------------------------------------------------------------

@router_estados.post("/", response_model=EstadoRead, status_code=201, dependencies=[Depends(exigir_escrita)])
def criar_estado(payload: EstadoBase, db: Session = Depends(get_db)):
    estado = Estado(**payload.model_dump())
    db.add(estado)
    confirmar(db)
    db.refresh(estado)
    return estado


@router_estados.get("/", response_model=list[EstadoRead])
def listar_estados(db: Session = Depends(get_db)):
    return db.execute(select(Estado).order_by(Estado.nome)).scalars().all()


@router_estados.get("/{estado_id}", response_model=EstadoRead)
def obter_estado(estado_id: int, db: Session = Depends(get_db)):
    return _obter(db, Estado, estado_id, "Estado nao encontrado")


@router_estados.put("/{estado_id}", response_model=EstadoRead, dependencies=[Depends(exigir_escrita)])
def atualizar_estado(estado_id: int, payload: EstadoBase, db: Session = Depends(get_db)):
    estado = _obter(db, Estado, estado_id, "Estado nao encontrado")
    _aplicar(estado, payload)
    confirmar(db)
    db.refresh(estado)
    return estado


@router_estados.delete("/{estado_id}", status_code=204, dependencies=[Depends(exigir_escrita)])
def remover_estado(estado_id: int, db: Session = Depends(get_db)):
    db.delete(_obter(db, Estado, estado_id, "Estado nao encontrado"))
    confirmar(db, "Estado em uso: existem cidades cadastradas nele")


# ---------------------------------------------------------------------
# CIDADES
# ---------------------------------------------------------------------

@router_cidades.post("/", response_model=CidadeRead, status_code=201, dependencies=[Depends(exigir_escrita)])
def criar_cidade(payload: CidadeBase, db: Session = Depends(get_db)):
    cidade = Cidade(**payload.model_dump())
    db.add(cidade)
    confirmar(db)
    db.refresh(cidade)
    return cidade


@router_cidades.get("/", response_model=list[CidadeRead])
def listar_cidades(
    estado_id: int | None = None, busca: str | None = None, db: Session = Depends(get_db),
):
    stmt = select(Cidade)
    if estado_id:
        stmt = stmt.where(Cidade.estado_id == estado_id)
    if busca:
        stmt = stmt.where(contem(Cidade.nome, busca))
    return db.execute(stmt.order_by(Cidade.nome)).scalars().all()


@router_cidades.get("/{cidade_id}", response_model=CidadeRead)
def obter_cidade(cidade_id: int, db: Session = Depends(get_db)):
    return _obter(db, Cidade, cidade_id, "Cidade nao encontrada")


@router_cidades.put("/{cidade_id}", response_model=CidadeRead, dependencies=[Depends(exigir_escrita)])
def atualizar_cidade(cidade_id: int, payload: CidadeBase, db: Session = Depends(get_db)):
    cidade = _obter(db, Cidade, cidade_id, "Cidade nao encontrada")
    _aplicar(cidade, payload)
    confirmar(db)
    db.refresh(cidade)
    return cidade


@router_cidades.delete("/{cidade_id}", status_code=204, dependencies=[Depends(exigir_escrita)])
def desativar_cidade(cidade_id: int, db: Session = Depends(get_db)):
    _obter(db, Cidade, cidade_id, "Cidade nao encontrada").ativa = False
    db.commit()


# ---------------------------------------------------------------------
# BAIRROS
# ---------------------------------------------------------------------

@router_bairros.post("/", response_model=BairroRead, status_code=201, dependencies=[Depends(exigir_escrita)])
def criar_bairro(payload: BairroBase, db: Session = Depends(get_db)):
    bairro = Bairro(**payload.model_dump())
    db.add(bairro)
    confirmar(db)
    db.refresh(bairro)
    return bairro


@router_bairros.get("/", response_model=list[BairroRead])
def listar_bairros(cidade_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(Bairro)
    if cidade_id:
        stmt = stmt.where(Bairro.cidade_id == cidade_id)
    return db.execute(stmt.order_by(Bairro.nome)).scalars().all()


@router_bairros.get("/{bairro_id}", response_model=BairroRead)
def obter_bairro(bairro_id: int, db: Session = Depends(get_db)):
    return _obter(db, Bairro, bairro_id, "Bairro nao encontrado")


@router_bairros.put("/{bairro_id}", response_model=BairroRead, dependencies=[Depends(exigir_escrita)])
def atualizar_bairro(bairro_id: int, payload: BairroBase, db: Session = Depends(get_db)):
    bairro = _obter(db, Bairro, bairro_id, "Bairro nao encontrado")
    _aplicar(bairro, payload)
    confirmar(db)
    db.refresh(bairro)
    return bairro


@router_bairros.delete("/{bairro_id}", status_code=204, dependencies=[Depends(exigir_escrita)])
def desativar_bairro(bairro_id: int, db: Session = Depends(get_db)):
    _obter(db, Bairro, bairro_id, "Bairro nao encontrado").ativo = False
    db.commit()


# ---------------------------------------------------------------------
# LOCALIDADES
# ---------------------------------------------------------------------

@router_localidades.post("/", response_model=LocalidadeRead, status_code=201, dependencies=[Depends(exigir_escrita)])
def criar_localidade(payload: LocalidadeBase, db: Session = Depends(get_db)):
    localidade = Localidade(**payload.model_dump())
    db.add(localidade)
    confirmar(db)
    db.refresh(localidade)
    return localidade


@router_localidades.get("/", response_model=list[LocalidadeRead])
def listar_localidades(bairro_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(Localidade)
    if bairro_id:
        stmt = stmt.where(Localidade.bairro_id == bairro_id)
    return db.execute(stmt.order_by(Localidade.nome)).scalars().all()


@router_localidades.get("/{localidade_id}", response_model=LocalidadeRead)
def obter_localidade(localidade_id: int, db: Session = Depends(get_db)):
    return _obter(db, Localidade, localidade_id, "Localidade nao encontrada")


@router_localidades.put("/{localidade_id}", response_model=LocalidadeRead, dependencies=[Depends(exigir_escrita)])
def atualizar_localidade(localidade_id: int, payload: LocalidadeBase, db: Session = Depends(get_db)):
    localidade = _obter(db, Localidade, localidade_id, "Localidade nao encontrada")
    _aplicar(localidade, payload)
    confirmar(db)
    db.refresh(localidade)
    return localidade


@router_localidades.delete("/{localidade_id}", status_code=204, dependencies=[Depends(exigir_escrita)])
def desativar_localidade(localidade_id: int, db: Session = Depends(get_db)):
    _obter(db, Localidade, localidade_id, "Localidade nao encontrada").ativa = False
    db.commit()


# ---------------------------------------------------------------------
# CEPS (chave natural: o proprio CEP)
# ---------------------------------------------------------------------

@router_ceps.post("/", response_model=CepRead, status_code=201, dependencies=[Depends(exigir_escrita)])
def criar_cep(payload: CepCreate, db: Session = Depends(get_db)):
    cep = Cep(**payload.model_dump())
    db.add(cep)
    confirmar(db)
    db.refresh(cep)
    return cep


@router_ceps.get("/", response_model=list[CepRead])
def listar_ceps(localidade_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(Cep)
    if localidade_id:
        stmt = stmt.where(Cep.localidade_id == localidade_id)
    return db.execute(stmt.order_by(Cep.cep)).scalars().all()


@router_ceps.get("/{cep}", response_model=CepRead)
def obter_cep(cep: str, db: Session = Depends(get_db)):
    """Usado pelos formularios para mostrar a cidade/bairro assim que o CEP e digitado."""
    return _obter(db, Cep, "".join(c for c in cep if c.isdigit()), "CEP nao cadastrado")


@router_ceps.put("/{cep}", response_model=CepRead, dependencies=[Depends(exigir_escrita)])
def atualizar_cep(cep: str, payload: CepUpdate, db: Session = Depends(get_db)):
    registro = _obter(db, Cep, cep, "CEP nao cadastrado")
    registro.localidade_id = payload.localidade_id
    confirmar(db)
    db.refresh(registro)
    return registro


@router_ceps.delete("/{cep}", status_code=204, dependencies=[Depends(exigir_escrita)])
def remover_cep(cep: str, db: Session = Depends(get_db)):
    db.delete(_obter(db, Cep, cep, "CEP nao cadastrado"))
    confirmar(db, "CEP em uso por pessoas ou propriedades")
