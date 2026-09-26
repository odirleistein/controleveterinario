from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.acesso import conferir_animal_da_propriedade, propriedade_atual
from app.database import get_db
from app.erros_db import confirmar
from app.models import Animal, EventoReprodutivo, Propriedade, Reprodutor, TipoEvento, Usuario
from app.schemas import (
    EventoReprodutivoBase, EventoReprodutivoRead, ReprodutorBase, ReprodutorRead, TipoEventoRead,
)
from app.security import exigir_escrita

router_reprodutores = APIRouter(prefix="/reprodutores", tags=["Reprodutores"])
router_tipos_evento = APIRouter(prefix="/tipos-evento", tags=["Tipos de evento"])
router = APIRouter(prefix="/eventos-reprodutivos", tags=["Eventos reprodutivos"])


# ---------------------------------------------------------------------
# REPRODUTORES (touros e vacas da genealogia) - cadastro geral, visivel a todos
# ---------------------------------------------------------------------
# Quase nunca existiram na propriedade: por isso nao pertencem a nenhuma. Como as racas,
# quem grava altera para todas as propriedades.

def _conferir_pais(db: Session, payload: ReprodutorBase, proprio_id: int | None = None) -> None:
    for campo, sexo, rotulo in (("pai_id", "M", "pai"), ("mae_id", "F", "mae")):
        reprodutor_id = getattr(payload, campo)
        if reprodutor_id is None:
            continue
        if reprodutor_id == proprio_id:
            raise HTTPException(status_code=400, detail="Um reprodutor nao pode ser o proprio " + rotulo)
        pai_ou_mae = db.get(Reprodutor, reprodutor_id)
        if not pai_ou_mae or pai_ou_mae.sexo != sexo:
            raise HTTPException(status_code=400, detail=f"O {rotulo} informado nao e um reprodutor {'macho' if sexo == 'M' else 'femea'}")


@router_reprodutores.get("/", response_model=list[ReprodutorRead])
def listar_reprodutores(sexo: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Reprodutor)
    if sexo:
        stmt = stmt.where(Reprodutor.sexo == sexo)
    return db.execute(stmt.order_by(Reprodutor.nome)).scalars().all()


@router_reprodutores.post("/", response_model=ReprodutorRead, status_code=201, dependencies=[Depends(exigir_escrita)])
def criar_reprodutor(payload: ReprodutorBase, db: Session = Depends(get_db)):
    _conferir_pais(db, payload)
    reprodutor = Reprodutor(**payload.model_dump())
    db.add(reprodutor)
    confirmar(db)
    db.refresh(reprodutor)
    return reprodutor


@router_reprodutores.put("/{reprodutor_id}", response_model=ReprodutorRead, dependencies=[Depends(exigir_escrita)])
def atualizar_reprodutor(reprodutor_id: int, payload: ReprodutorBase, db: Session = Depends(get_db)):
    reprodutor = db.get(Reprodutor, reprodutor_id)
    if not reprodutor:
        raise HTTPException(status_code=404, detail="Reprodutor nao encontrado")
    _conferir_pais(db, payload, proprio_id=reprodutor_id)
    for campo, valor in payload.model_dump().items():
        setattr(reprodutor, campo, valor)
    confirmar(db)
    db.refresh(reprodutor)
    return reprodutor


@router_reprodutores.delete("/{reprodutor_id}", status_code=204, dependencies=[Depends(exigir_escrita)])
def desativar_reprodutor(reprodutor_id: int, db: Session = Depends(get_db)):
    reprodutor = db.get(Reprodutor, reprodutor_id)
    if not reprodutor:
        raise HTTPException(status_code=404, detail="Reprodutor nao encontrado")
    reprodutor.ativo = False
    db.commit()


# ---------------------------------------------------------------------
# TIPOS DE EVENTO - referencia comum semeada na migration; so leitura
# ---------------------------------------------------------------------
# O sistema reconhece cada evento pelo `codigo`, por isso nao ha cadastro livre.

@router_tipos_evento.get("/", response_model=list[TipoEventoRead])
def listar_tipos_evento(db: Session = Depends(get_db)):
    return db.execute(select(TipoEvento).order_by(TipoEvento.id)).scalars().all()


# ---------------------------------------------------------------------
# EVENTOS REPRODUTIVOS - sempre no contexto de UMA propriedade
# ---------------------------------------------------------------------

def _conferir_evento(db: Session, propriedade: Propriedade, payload: EventoReprodutivoBase) -> None:
    conferir_animal_da_propriedade(db, propriedade, payload.animal_id)
    if payload.cria_animal_id is not None:
        conferir_animal_da_propriedade(db, propriedade, payload.cria_animal_id)
    if payload.reprodutor_id is not None:
        reprodutor = db.get(Reprodutor, payload.reprodutor_id)
        if not reprodutor or reprodutor.sexo != "M":
            raise HTTPException(status_code=400, detail="O reprodutor da inseminacao deve ser um touro")


def _buscar(db: Session, propriedade: Propriedade, evento_id: int) -> EventoReprodutivo:
    evento = db.execute(
        select(EventoReprodutivo).where(
            EventoReprodutivo.id == evento_id, EventoReprodutivo.propriedade_id == propriedade.id
        )
    ).scalar_one_or_none()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento nao encontrado")
    return evento


@router.get("/", response_model=list[EventoReprodutivoRead])
def listar_eventos(
    animal_id: int | None = None,
    tipo_animal_id: int | None = None,
    tipo_evento_id: int | None = None,
    db: Session = Depends(get_db),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    stmt = (
        select(EventoReprodutivo)
        .join(Animal, Animal.id == EventoReprodutivo.animal_id)
        .where(EventoReprodutivo.propriedade_id == propriedade.id)
    )
    if animal_id:
        stmt = stmt.where(EventoReprodutivo.animal_id == animal_id)
    if tipo_animal_id:
        stmt = stmt.where(Animal.tipo_animal_id == tipo_animal_id)
    if tipo_evento_id:
        stmt = stmt.where(EventoReprodutivo.tipo_evento_id == tipo_evento_id)
    return db.execute(stmt.order_by(EventoReprodutivo.data_evento.desc(), Animal.nome)).scalars().all()


@router.post("/", response_model=EventoReprodutivoRead, status_code=201)
def criar_evento(
    payload: EventoReprodutivoBase,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_escrita),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    _conferir_evento(db, propriedade, payload)
    evento = EventoReprodutivo(**payload.model_dump(), propriedade_id=propriedade.id, usuario_inclusao_id=usuario.id)
    db.add(evento)
    confirmar(db)
    db.refresh(evento)
    return evento


@router.put("/{evento_id}", response_model=EventoReprodutivoRead, dependencies=[Depends(exigir_escrita)])
def atualizar_evento(
    evento_id: int,
    payload: EventoReprodutivoBase,
    db: Session = Depends(get_db),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    evento = _buscar(db, propriedade, evento_id)
    _conferir_evento(db, propriedade, payload)
    for campo, valor in payload.model_dump().items():
        setattr(evento, campo, valor)
    confirmar(db)
    db.refresh(evento)
    return evento


@router.delete("/{evento_id}", status_code=204, dependencies=[Depends(exigir_escrita)])
def remover_evento(
    evento_id: int, db: Session = Depends(get_db), propriedade: Propriedade = Depends(propriedade_atual),
):
    db.delete(_buscar(db, propriedade, evento_id))
    db.commit()
