"""
A propriedade e o centro do sistema: o usuario escolhe uma propriedade e, dentro
desse contexto, so os dados dela aparecem. Este modulo decide o que cada usuario
pode enxergar.

  - MASTER enxerga todas as propriedades.
  - Os demais enxergam so as ligadas a eles: pelo login (propriedades_usuarios)
    ou, quando o usuario e um veterinario ativo, pelas que ele atende
    (veterinarios_propriedades).

Tres niveis de dado:
  1. Da propriedade (animais): so aparecem dentro do contexto de UMA propriedade
     escolhida - dependencia `propriedade_atual` (cabecalho X-Propriedade-Id).
  2. Das pessoas ligadas as propriedades (pessoas, usuarios, veterinarios): quem
     nao e MASTER ve so as ligadas as suas propriedades - `condicao_pessoa_visivel`
     e `condicao_usuario_visivel`.
  3. Referencia comum (estados, cidades, CEPs, tipos de animal): visivel a todos.

Ao contrario de um filtro automatico, cada rota chama estas funcoes de proposito;
rota nova que devolva dado de propriedade ou de pessoa PRECISA usa-las.
"""
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select, union
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    MASTER, Pessoa, Propriedade, PropriedadeUsuario, Usuario, Veterinario,
    VeterinarioPropriedade,
)
from app.security import get_current_user


def ids_propriedades_visiveis(usuario: Usuario):
    """Subconsulta com os ids visiveis, ou None quando o usuario ve todas."""
    if usuario.papel.nome == MASTER:
        return None
    return union(
        select(PropriedadeUsuario.propriedade_id).where(PropriedadeUsuario.usuario_id == usuario.id),
        select(VeterinarioPropriedade.propriedade_id)
        .join(Veterinario, Veterinario.id == VeterinarioPropriedade.veterinario_id)
        .where(Veterinario.usuario_id == usuario.id, Veterinario.ativo.is_(True)),
    )


def buscar_propriedade_visivel(db: Session, usuario: Usuario, propriedade_id: int) -> Propriedade:
    """404 tanto para propriedade inexistente quanto para a que o usuario nao
    enxerga: nao vaza que ela existe."""
    stmt = select(Propriedade).where(Propriedade.id == propriedade_id)
    visiveis = ids_propriedades_visiveis(usuario)
    if visiveis is not None:
        stmt = stmt.where(Propriedade.id.in_(visiveis))
    propriedade = db.execute(stmt).scalar_one_or_none()
    if not propriedade:
        raise HTTPException(status_code=404, detail="Propriedade nao encontrada")
    return propriedade


def propriedade_atual(
    x_propriedade_id: int | None = Header(
        None, alias="X-Propriedade-Id",
        description="Propriedade em que a requisicao opera (escolhida no inicio do acesso).",
    ),
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Propriedade:
    """Resolve a propriedade do contexto e garante que o usuario tem acesso a ela.

    Sem o cabecalho: 400 (a tela deve mandar o usuario escolher). Propriedade
    que ele nao enxerga: 403 - o recurso pode existir, o acesso e que nao.
    """
    if x_propriedade_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escolha uma propriedade para continuar.")
    try:
        propriedade = buscar_propriedade_visivel(db, usuario, x_propriedade_id)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem acesso a esta propriedade.")
    if not propriedade.ativa:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Esta propriedade esta inativa.")
    return propriedade


def condicao_pessoa_visivel(usuario: Usuario):
    """Filtro para consultas de Pessoa, ou None quando o usuario ve todas.

    Vê: a propria pessoa, as que cadastrou, os donos das propriedades que
    enxerga e as pessoas dos veterinarios e dos usuarios ligados a elas."""
    visiveis = ids_propriedades_visiveis(usuario)
    if visiveis is None:
        return None
    donos = select(Propriedade.proprietario_pessoa_id).where(Propriedade.id.in_(visiveis))
    veterinarios = (
        select(Veterinario.pessoa_id)
        .join(VeterinarioPropriedade, VeterinarioPropriedade.veterinario_id == Veterinario.id)
        .where(VeterinarioPropriedade.propriedade_id.in_(visiveis))
    )
    usuarios = (
        select(Usuario.pessoa_id)
        .join(PropriedadeUsuario, PropriedadeUsuario.usuario_id == Usuario.id)
        .where(PropriedadeUsuario.propriedade_id.in_(visiveis), Usuario.pessoa_id.is_not(None))
    )
    condicao = (
        Pessoa.id.in_(donos)
        | Pessoa.id.in_(veterinarios)
        | Pessoa.id.in_(usuarios)
        | (Pessoa.usuario_inclusao_id == usuario.id)
    )
    if usuario.pessoa_id:
        condicao = condicao | (Pessoa.id == usuario.pessoa_id)
    return condicao


def condicao_usuario_visivel(usuario: Usuario):
    """Filtro para consultas de Usuario, ou None quando o usuario ve todos.

    Vê: a si mesmo e quem tem acesso (login ou veterinario) as propriedades que enxerga."""
    visiveis = ids_propriedades_visiveis(usuario)
    if visiveis is None:
        return None
    com_acesso = select(PropriedadeUsuario.usuario_id).where(PropriedadeUsuario.propriedade_id.in_(visiveis))
    vets = (
        select(Veterinario.usuario_id)
        .join(VeterinarioPropriedade, VeterinarioPropriedade.veterinario_id == Veterinario.id)
        .where(VeterinarioPropriedade.propriedade_id.in_(visiveis))
    )
    return (Usuario.id == usuario.id) | Usuario.id.in_(com_acesso) | Usuario.id.in_(vets)
