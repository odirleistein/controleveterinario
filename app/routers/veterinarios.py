from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.acesso import buscar_propriedade_visivel, ids_propriedades_visiveis
from app.database import get_db
from app.erros_db import confirmar
from app.models import Pessoa, Usuario, Veterinario, VeterinarioPropriedade
from app.schemas import (
    VeterinarioBase, VeterinarioCandidato, VeterinarioRead, VinculosIn, VinculosRead,
)
from app.security import exigir_escrita, exigir_master, get_current_user
from app.vinculos import sincronizar

router = APIRouter(prefix="/veterinarios", tags=["Veterinarios"])

NAO_ENCONTRADO = "Veterinario nao encontrado"


def _validar_referencias(db: Session, payload: VeterinarioBase) -> None:
    """A pessoa precisa ser fisica e o usuario precisa existir; o banco so
    garantiria que os ids existem, nao que a pessoa e um profissional humano."""
    pessoa = db.get(Pessoa, payload.pessoa_id)
    if not pessoa:
        raise HTTPException(status_code=400, detail="Pessoa nao encontrada")
    if pessoa.tipo_pessoa != "F":
        raise HTTPException(status_code=400, detail="O veterinario precisa ser uma pessoa fisica")
    if not db.get(Usuario, payload.usuario_id):
        raise HTTPException(status_code=400, detail="Usuario nao encontrado")


def _visiveis(db: Session, usuario: Usuario, propriedade_id: int | None):
    """Consulta base: veterinarios que o usuario pode ver.

    MASTER ve todos. Os demais, so os que atendem as propriedades que enxergam.
    Com propriedade_id, so os dessa propriedade (que precisa ser visivel)."""
    stmt = select(Veterinario).join(Pessoa, Pessoa.id == Veterinario.pessoa_id)
    if propriedade_id is not None:
        buscar_propriedade_visivel(db, usuario, propriedade_id)
        stmt = stmt.where(
            Veterinario.id.in_(
                select(VeterinarioPropriedade.veterinario_id).where(
                    VeterinarioPropriedade.propriedade_id == propriedade_id
                )
            )
        )
    else:
        visiveis = ids_propriedades_visiveis(usuario)
        if visiveis is not None:
            stmt = stmt.where(
                Veterinario.id.in_(
                    select(VeterinarioPropriedade.veterinario_id).where(
                        VeterinarioPropriedade.propriedade_id.in_(visiveis)
                    )
                )
            )
    return stmt


# O cadastro do veterinario (pessoa + login) e do MASTER. Quem administra uma
# propriedade escolhe entre os ja cadastrados (ver /candidatos) e os vincula a ela.
@router.post("/", response_model=VeterinarioRead, status_code=201, dependencies=[Depends(exigir_master)])
def criar_veterinario(payload: VeterinarioBase, db: Session = Depends(get_db)):
    _validar_referencias(db, payload)
    veterinario = Veterinario(**payload.model_dump())
    db.add(veterinario)
    confirmar(db)
    db.refresh(veterinario)
    return veterinario


@router.get("/", response_model=list[VeterinarioRead])
def listar_veterinarios(
    propriedade_id: int | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    stmt = _visiveis(db, usuario, propriedade_id).order_by(Pessoa.nome)
    return db.execute(stmt).unique().scalars().all()


# Antes de "/{veterinario_id}": senao "candidatos" seria lido como um id.
@router.get("/candidatos", response_model=list[VeterinarioCandidato])
def listar_candidatos(db: Session = Depends(get_db), _: Usuario = Depends(exigir_escrita)):
    """Veterinarios ativos para escolher ao vincular a uma propriedade. Devolve so
    id e nome: quem administra uma propriedade nao precisa ver o resto do cadastro
    de profissionais que nao atendem as suas."""
    stmt = (
        select(Veterinario).join(Pessoa, Pessoa.id == Veterinario.pessoa_id)
        .where(Veterinario.ativo.is_(True)).order_by(Pessoa.nome)
    )
    return db.execute(stmt).unique().scalars().all()


@router.get("/{veterinario_id}", response_model=VeterinarioRead)
def obter_veterinario(
    veterinario_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user),
):
    stmt = _visiveis(db, usuario, None).where(Veterinario.id == veterinario_id)
    veterinario = db.execute(stmt).unique().scalar_one_or_none()
    if not veterinario:
        raise HTTPException(status_code=404, detail=NAO_ENCONTRADO)
    return veterinario


@router.put("/{veterinario_id}", response_model=VeterinarioRead, dependencies=[Depends(exigir_master)])
def atualizar_veterinario(veterinario_id: int, payload: VeterinarioBase, db: Session = Depends(get_db)):
    veterinario = db.get(Veterinario, veterinario_id)
    if not veterinario:
        raise HTTPException(status_code=404, detail=NAO_ENCONTRADO)
    _validar_referencias(db, payload)
    for campo, valor in payload.model_dump().items():
        setattr(veterinario, campo, valor)
    confirmar(db)
    db.refresh(veterinario)
    return veterinario


@router.delete("/{veterinario_id}", status_code=204, dependencies=[Depends(exigir_master)])
def desativar_veterinario(veterinario_id: int, db: Session = Depends(get_db)):
    """Soft delete: deixa de enxergar as propriedades (ver acesso.py), mas o
    historico de vinculos fica."""
    veterinario = db.get(Veterinario, veterinario_id)
    if not veterinario:
        raise HTTPException(status_code=404, detail=NAO_ENCONTRADO)
    veterinario.ativo = False
    db.commit()


# ---------------------------------------------------------------------
# PROPRIEDADES QUE O VETERINARIO ATENDE
# ---------------------------------------------------------------------
# Quem nao e MASTER so mexe nos vinculos das propriedades que ele mesmo
# enxerga; os das outras ficam como estao (ver app/vinculos.py).

def _ids_visiveis(db: Session, usuario: Usuario) -> set[int] | None:
    visiveis = ids_propriedades_visiveis(usuario)
    return None if visiveis is None else set(db.execute(visiveis).scalars())


@router.get("/{veterinario_id}/propriedades", response_model=VinculosRead)
def listar_propriedades_do_veterinario(
    veterinario_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user),
):
    if not db.get(Veterinario, veterinario_id):
        raise HTTPException(status_code=404, detail=NAO_ENCONTRADO)
    ids = set(
        db.execute(
            select(VeterinarioPropriedade.propriedade_id).where(
                VeterinarioPropriedade.veterinario_id == veterinario_id
            )
        ).scalars()
    )
    visiveis = _ids_visiveis(db, usuario)
    if visiveis is not None:
        ids &= visiveis
    return VinculosRead(ids=sorted(ids))


@router.put("/{veterinario_id}/propriedades", response_model=VinculosRead)
def definir_propriedades_do_veterinario(
    veterinario_id: int,
    payload: VinculosIn,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_escrita),
):
    if not db.get(Veterinario, veterinario_id):
        raise HTTPException(status_code=404, detail=NAO_ENCONTRADO)
    sincronizar(
        db, VeterinarioPropriedade, VeterinarioPropriedade.veterinario_id, veterinario_id,
        VeterinarioPropriedade.propriedade_id, payload.ids, _ids_visiveis(db, usuario),
    )
    confirmar(db)
    return VinculosRead(ids=sorted(set(payload.ids)))
