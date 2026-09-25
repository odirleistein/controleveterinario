from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.acesso import ids_propriedades_visiveis
from app.database import get_db
from app.models import (
    Animal, Bairro, Cep, Cidade, Estado, Localidade, Pessoa, Propriedade,
    PropriedadeAnimal, TipoAnimal, Usuario, Veterinario,
)
from app.schemas import AnimaisPorTipo, PropriedadesPorCidade, ResumoPainel
from app.security import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/resumo", response_model=ResumoPainel)
def resumo(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    """Numeros da Visao Geral. Propriedades e animais respeitam o recorte do
    usuario (ver app/acesso.py); veterinarios e pessoas sao cadastros comuns."""
    visiveis = ids_propriedades_visiveis(usuario)

    prop = select(Propriedade.id).where(Propriedade.ativa.is_(True))
    if visiveis is not None:
        prop = prop.where(Propriedade.id.in_(visiveis))

    # Animal so conta se esta em alguma propriedade ativa visivel: e o que da
    # sentido a "rebanho" no painel (animal solto no cadastro nao entra).
    vinculos = (
        select(PropriedadeAnimal.animal_id)
        .join(Animal, Animal.id == PropriedadeAnimal.animal_id)
        .where(Animal.ativo.is_(True), PropriedadeAnimal.propriedade_id.in_(prop))
        .distinct()
    )

    por_tipo = db.execute(
        select(TipoAnimal.descricao, func.count(Animal.id))
        .join(Animal, Animal.tipo_animal_id == TipoAnimal.id)
        .where(Animal.id.in_(vinculos))
        .group_by(TipoAnimal.descricao)
        .order_by(func.count(Animal.id).desc())
    ).all()

    por_cidade = db.execute(
        select(Cidade.nome, Estado.sigla, func.count(Propriedade.id))
        .select_from(Propriedade)
        .join(Cep, Cep.cep == Propriedade.cep)
        .join(Localidade, Localidade.id == Cep.localidade_id)
        .join(Bairro, Bairro.id == Localidade.bairro_id)
        .join(Cidade, Cidade.id == Bairro.cidade_id)
        .join(Estado, Estado.id == Cidade.estado_id)
        .where(Propriedade.id.in_(prop))
        .group_by(Cidade.nome, Estado.sigla)
        .order_by(func.count(Propriedade.id).desc(), Cidade.nome)
        .limit(8)
    ).all()

    def contar(stmt) -> int:
        return db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    return ResumoPainel(
        propriedades=contar(prop),
        animais=contar(vinculos),
        veterinarios=db.execute(
            select(func.count()).select_from(Veterinario).where(Veterinario.ativo.is_(True))
        ).scalar_one(),
        pessoas=db.execute(
            select(func.count()).select_from(Pessoa).where(Pessoa.ativo.is_(True))
        ).scalar_one(),
        animais_por_tipo=[AnimaisPorTipo(tipo=t, total=n) for t, n in por_tipo],
        propriedades_por_cidade=[
            PropriedadesPorCidade(cidade=f"{c}/{uf}", total=n) for c, uf, n in por_cidade
        ],
    )
