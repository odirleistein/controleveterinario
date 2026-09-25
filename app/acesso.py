"""
Quais propriedades cada usuario enxerga.

  - MASTER enxerga todas.
  - Os demais enxergam so as propriedades ligadas a eles: pelo login
    (propriedades_usuarios) ou, quando o usuario e um veterinario, pelas que ele
    atende (veterinarios_propriedades).

Ao contrario de um filtro automatico, aqui cada rota chama estas funcoes de
proposito: o recorte vale para propriedades e para o que pende delas (animais),
e o restante dos cadastros (pessoas, geografia) e comum a todos.
"""
from fastapi import HTTPException
from sqlalchemy import select, union
from sqlalchemy.orm import Session

from app.models import (
    MASTER, Propriedade, PropriedadeUsuario, Usuario, Veterinario, VeterinarioPropriedade,
)


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
