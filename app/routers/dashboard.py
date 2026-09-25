"""
Painel da propriedade escolhida e comparativo entre propriedades.

O painel (/dashboard/resumo) e sempre de UMA propriedade: a do cabecalho
X-Propriedade-Id. O comparativo (/dashboard/comparativo) e o unico lugar onde
propriedades aparecem lado a lado - e so as que o usuario tem acesso, sejam
todas ou as que ele escolher.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.acesso import ids_propriedades_visiveis, propriedade_atual
from app.database import get_db
from app.models import (
    Animal, Propriedade, PropriedadeAnimal, PropriedadeUsuario, TipoAnimal, Usuario,
    Veterinario, VeterinarioPropriedade,
)
from app.schemas import (
    AnimaisPorTipo, ComparativoLinha, ComparativoPropriedades, ResumoPainel,
)
from app.security import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _animais_por_tipo(db: Session, ids_propriedades) -> list[tuple[int, str, int]]:
    """(propriedade_id, tipo, total) dos animais ativos, para as propriedades dadas."""
    return db.execute(
        select(PropriedadeAnimal.propriedade_id, TipoAnimal.descricao, func.count(Animal.id))
        .join(Animal, Animal.id == PropriedadeAnimal.animal_id)
        .join(TipoAnimal, TipoAnimal.id == Animal.tipo_animal_id)
        .where(Animal.ativo.is_(True), PropriedadeAnimal.propriedade_id.in_(ids_propriedades))
        .group_by(PropriedadeAnimal.propriedade_id, TipoAnimal.descricao)
    ).all()


def _contagem_vinculos(db: Session, ids_propriedades) -> tuple[dict[int, int], dict[int, int]]:
    """Veterinarios ativos e usuarios por propriedade."""
    vets = dict(
        db.execute(
            select(VeterinarioPropriedade.propriedade_id, func.count(Veterinario.id))
            .join(Veterinario, Veterinario.id == VeterinarioPropriedade.veterinario_id)
            .where(Veterinario.ativo.is_(True), VeterinarioPropriedade.propriedade_id.in_(ids_propriedades))
            .group_by(VeterinarioPropriedade.propriedade_id)
        ).all()
    )
    usuarios = dict(
        db.execute(
            select(PropriedadeUsuario.propriedade_id, func.count(PropriedadeUsuario.id))
            .where(PropriedadeUsuario.propriedade_id.in_(ids_propriedades))
            .group_by(PropriedadeUsuario.propriedade_id)
        ).all()
    )
    return vets, usuarios


@router.get("/resumo", response_model=ResumoPainel)
def resumo(db: Session = Depends(get_db), propriedade: Propriedade = Depends(propriedade_atual)):
    """Numeros da Visao Geral: so da propriedade escolhida."""
    por_tipo = sorted(
        ((tipo, total) for _, tipo, total in _animais_por_tipo(db, [propriedade.id])),
        key=lambda t: (-t[1], t[0]),
    )
    vets, usuarios = _contagem_vinculos(db, [propriedade.id])
    return ResumoPainel(
        propriedade_id=propriedade.id,
        propriedade_nome=propriedade.nome,
        cidade_uf=propriedade.cidade_uf,
        proprietario_nome=propriedade.proprietario_nome,
        animais=sum(total for _, total in por_tipo),
        animais_por_tipo=[AnimaisPorTipo(tipo=t, total=n) for t, n in por_tipo],
        veterinarios=vets.get(propriedade.id, 0),
        usuarios=usuarios.get(propriedade.id, 0),
    )


@router.get("/comparativo", response_model=ComparativoPropriedades)
def comparativo(
    propriedade_id: list[int] | None = Query(None, description="Sem informar, compara todas as suas propriedades ativas"),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Propriedades lado a lado. Considera SO as que o usuario enxerga: um id de
    propriedade alheia e simplesmente ignorado, nao devolve nada dela."""
    stmt = select(Propriedade).where(Propriedade.ativa.is_(True))
    visiveis = ids_propriedades_visiveis(usuario)
    if visiveis is not None:
        stmt = stmt.where(Propriedade.id.in_(visiveis))
    if propriedade_id:
        stmt = stmt.where(Propriedade.id.in_(propriedade_id))
    propriedades = db.execute(stmt.order_by(Propriedade.nome)).scalars().all()
    ids = [p.id for p in propriedades]
    if not ids:
        return ComparativoPropriedades(tipos=[], linhas=[])

    por_tipo: dict[int, dict[str, int]] = {}
    tipos: set[str] = set()
    for pid, tipo, total in _animais_por_tipo(db, ids):
        por_tipo.setdefault(pid, {})[tipo] = total
        tipos.add(tipo)
    vets, usuarios = _contagem_vinculos(db, ids)

    return ComparativoPropriedades(
        tipos=sorted(tipos),
        linhas=[
            ComparativoLinha(
                propriedade_id=p.id,
                nome=p.nome,
                cidade_uf=p.cidade_uf,
                proprietario_nome=p.proprietario_nome,
                animais=sum(por_tipo.get(p.id, {}).values()),
                por_tipo=por_tipo.get(p.id, {}),
                veterinarios=vets.get(p.id, 0),
                usuarios=usuarios.get(p.id, 0),
            )
            for p in propriedades
        ],
    )
