from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.acesso import conferir_animal_da_propriedade, propriedade_atual
from app.database import get_db
from app.erros_db import confirmar
from app.models import Animal, ProducaoLeite, Propriedade, Usuario
from app.schemas import ProducaoLeiteBase, ProducaoLeiteRead
from app.security import exigir_escrita

router = APIRouter(prefix="/producoes-leite", tags=["Producao de leite"])


# Producao sempre no contexto de UMA propriedade. O lancamento pode ser diario ou o
# total do mes (data do fechamento + dias_referentes), por isso a media por dia e
# calculada, nao gravada.

def _conferir_animal(db: Session, propriedade: Propriedade, animal_id: int) -> None:
    """Animal da propriedade e de um tipo que produz leite: a tela ja so oferece esses,
    mas a API nao confia so na tela."""
    conferir_animal_da_propriedade(db, propriedade, animal_id)
    if not db.get(Animal, animal_id).tipo_produz_leite:
        raise HTTPException(status_code=400, detail="Esse tipo de animal nao produz leite")


def _buscar(db: Session, propriedade: Propriedade, producao_id: int) -> ProducaoLeite:
    producao = db.execute(
        select(ProducaoLeite).where(ProducaoLeite.id == producao_id, ProducaoLeite.propriedade_id == propriedade.id)
    ).scalar_one_or_none()
    if not producao:
        raise HTTPException(status_code=404, detail="Lancamento de producao nao encontrado")
    return producao


@router.get("/", response_model=list[ProducaoLeiteRead])
def listar_producoes(
    animal_id: int | None = None,
    tipo_animal_id: int | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    db: Session = Depends(get_db),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    stmt = (
        select(ProducaoLeite)
        .join(Animal, Animal.id == ProducaoLeite.animal_id)
        .where(ProducaoLeite.propriedade_id == propriedade.id)
    )
    if animal_id:
        stmt = stmt.where(ProducaoLeite.animal_id == animal_id)
    if tipo_animal_id:
        stmt = stmt.where(Animal.tipo_animal_id == tipo_animal_id)
    if data_inicio:
        stmt = stmt.where(ProducaoLeite.data_producao >= data_inicio)
    if data_fim:
        stmt = stmt.where(ProducaoLeite.data_producao <= data_fim)
    return db.execute(stmt.order_by(ProducaoLeite.data_producao.desc(), Animal.nome)).scalars().all()


@router.post("/", response_model=ProducaoLeiteRead, status_code=201)
def criar_producao(
    payload: ProducaoLeiteBase,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_escrita),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    _conferir_animal(db, propriedade, payload.animal_id)
    producao = ProducaoLeite(**payload.model_dump(), propriedade_id=propriedade.id, usuario_inclusao_id=usuario.id)
    db.add(producao)
    confirmar(db)
    db.refresh(producao)
    return producao


@router.put("/{producao_id}", response_model=ProducaoLeiteRead, dependencies=[Depends(exigir_escrita)])
def atualizar_producao(
    producao_id: int,
    payload: ProducaoLeiteBase,
    db: Session = Depends(get_db),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    producao = _buscar(db, propriedade, producao_id)
    _conferir_animal(db, propriedade, payload.animal_id)
    for campo, valor in payload.model_dump().items():
        setattr(producao, campo, valor)
    confirmar(db)
    db.refresh(producao)
    return producao


@router.delete("/{producao_id}", status_code=204, dependencies=[Depends(exigir_escrita)])
def remover_producao(
    producao_id: int, db: Session = Depends(get_db), propriedade: Propriedade = Depends(propriedade_atual),
):
    db.delete(_buscar(db, propriedade, producao_id))
    db.commit()
