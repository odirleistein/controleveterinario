from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.acesso import buscar_propriedade_visivel, ids_propriedades_visiveis
from app.busca import contem
from app.database import get_db
from app.erros_db import confirmar, traduzir_integridade
from app.models import (
    MASTER, Propriedade, PropriedadeUsuario, Usuario, VeterinarioPropriedade,
)
from app.schemas import PropriedadeBase, PropriedadeRead, VinculosIn, VinculosRead
from app.security import exigir_escrita, get_current_user
from app.vinculos import sincronizar

router = APIRouter(prefix="/propriedades", tags=["Propriedades"])


@router.post("/", response_model=PropriedadeRead, status_code=201)
def criar_propriedade(
    payload: PropriedadeBase, db: Session = Depends(get_db), usuario: Usuario = Depends(exigir_escrita),
):
    propriedade = Propriedade(**payload.model_dump())
    db.add(propriedade)
    with traduzir_integridade(db):
        db.flush()
    # Quem nao e MASTER so ve o que esta vinculado a ele: sem este vinculo a
    # propriedade recem-criada sumiria da tela de quem acabou de cadastra-la.
    if usuario.papel.nome != MASTER:
        db.add(PropriedadeUsuario(usuario_id=usuario.id, propriedade_id=propriedade.id))
    confirmar(db)
    db.refresh(propriedade)
    return propriedade


@router.get("/", response_model=list[PropriedadeRead])
def listar_propriedades(
    busca: str | None = None,
    proprietario_pessoa_id: int | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    stmt = select(Propriedade)
    visiveis = ids_propriedades_visiveis(usuario)
    if visiveis is not None:
        stmt = stmt.where(Propriedade.id.in_(visiveis))
    if proprietario_pessoa_id:
        stmt = stmt.where(Propriedade.proprietario_pessoa_id == proprietario_pessoa_id)
    if busca:
        stmt = stmt.where(contem(Propriedade.nome, busca))
    return db.execute(stmt.order_by(Propriedade.nome)).scalars().all()


@router.get("/{propriedade_id}", response_model=PropriedadeRead)
def obter_propriedade(
    propriedade_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user),
):
    return buscar_propriedade_visivel(db, usuario, propriedade_id)


@router.put("/{propriedade_id}", response_model=PropriedadeRead, dependencies=[Depends(exigir_escrita)])
def atualizar_propriedade(
    propriedade_id: int,
    payload: PropriedadeBase,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    propriedade = buscar_propriedade_visivel(db, usuario, propriedade_id)
    for campo, valor in payload.model_dump().items():
        setattr(propriedade, campo, valor)
    confirmar(db)
    db.refresh(propriedade)
    return propriedade


@router.delete("/{propriedade_id}", status_code=204, dependencies=[Depends(exigir_escrita)])
def desativar_propriedade(
    propriedade_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user),
):
    """Soft delete: os vinculos com animais, veterinarios e usuarios ficam intactos."""
    buscar_propriedade_visivel(db, usuario, propriedade_id).ativa = False
    db.commit()


# ---------------------------------------------------------------------
# VINCULOS DA PROPRIEDADE (conjunto completo, ver app/vinculos.py)
# Os animais nao tem vinculo aqui: nascem dentro do contexto da propriedade (routers/animais.py).
# ---------------------------------------------------------------------

@router.get("/{propriedade_id}/veterinarios", response_model=VinculosRead)
def listar_veterinarios_da_propriedade(
    propriedade_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user),
):
    buscar_propriedade_visivel(db, usuario, propriedade_id)
    ids = db.execute(
        select(VeterinarioPropriedade.veterinario_id).where(
            VeterinarioPropriedade.propriedade_id == propriedade_id
        )
    ).scalars().all()
    return VinculosRead(ids=ids)


@router.put("/{propriedade_id}/veterinarios", response_model=VinculosRead)
def definir_veterinarios_da_propriedade(
    propriedade_id: int,
    payload: VinculosIn,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_escrita),
):
    buscar_propriedade_visivel(db, usuario, propriedade_id)
    sincronizar(
        db, VeterinarioPropriedade, VeterinarioPropriedade.propriedade_id, propriedade_id,
        VeterinarioPropriedade.veterinario_id, payload.ids,
    )
    confirmar(db)
    return VinculosRead(ids=sorted(set(payload.ids)))


@router.get("/{propriedade_id}/usuarios", response_model=VinculosRead)
def listar_usuarios_da_propriedade(
    propriedade_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user),
):
    buscar_propriedade_visivel(db, usuario, propriedade_id)
    ids = db.execute(
        select(PropriedadeUsuario.usuario_id).where(PropriedadeUsuario.propriedade_id == propriedade_id)
    ).scalars().all()
    return VinculosRead(ids=ids)


@router.put("/{propriedade_id}/usuarios", response_model=VinculosRead)
def definir_usuarios_da_propriedade(
    propriedade_id: int,
    payload: VinculosIn,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_escrita),
):
    propriedade = buscar_propriedade_visivel(db, usuario, propriedade_id)
    # Quem edita a lista nao pode se tirar dela: perderia o acesso a propriedade
    # na mesma hora (a nao ser que seja MASTER, que enxerga tudo de qualquer jeito).
    if usuario.papel.nome != MASTER and usuario.id not in payload.ids:
        raise HTTPException(
            status_code=400,
            detail="Voce nao pode se remover desta propriedade: perderia o acesso a ela.",
        )
    sincronizar(
        db, PropriedadeUsuario, PropriedadeUsuario.propriedade_id, propriedade.id,
        PropriedadeUsuario.usuario_id, payload.ids,
    )
    confirmar(db)
    return VinculosRead(ids=sorted(set(payload.ids)))
