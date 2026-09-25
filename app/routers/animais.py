from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.acesso import propriedade_atual
from app.busca import contem
from app.database import get_db
from app.erros_db import confirmar, traduzir_integridade
from app.models import Animal, Propriedade, PropriedadeAnimal, Raca, TipoAnimal, Usuario
from app.schemas import AnimalBase, AnimalRead, RacaBase, RacaRead, TipoAnimalBase, TipoAnimalRead
from app.security import exigir_escrita, get_current_user

router_tipos = APIRouter(prefix="/tipos-animal", tags=["Tipos de animal"])
router_racas = APIRouter(prefix="/racas", tags=["Racas"])
router = APIRouter(prefix="/animais", tags=["Animais"])


# ---------------------------------------------------------------------
# TIPOS DE ANIMAL (bovino, equino, suino...) - referencia comum a todos
# ---------------------------------------------------------------------

@router_tipos.post("/", response_model=TipoAnimalRead, status_code=201, dependencies=[Depends(exigir_escrita)])
def criar_tipo(payload: TipoAnimalBase, db: Session = Depends(get_db)):
    tipo = TipoAnimal(**payload.model_dump())
    db.add(tipo)
    db.commit()
    db.refresh(tipo)
    return tipo


@router_tipos.get("/", response_model=list[TipoAnimalRead])
def listar_tipos(db: Session = Depends(get_db)):
    return db.execute(select(TipoAnimal).order_by(TipoAnimal.descricao)).scalars().all()


@router_tipos.get("/{tipo_id}", response_model=TipoAnimalRead)
def obter_tipo(tipo_id: int, db: Session = Depends(get_db)):
    tipo = db.get(TipoAnimal, tipo_id)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de animal nao encontrado")
    return tipo


@router_tipos.put("/{tipo_id}", response_model=TipoAnimalRead, dependencies=[Depends(exigir_escrita)])
def atualizar_tipo(tipo_id: int, payload: TipoAnimalBase, db: Session = Depends(get_db)):
    tipo = db.get(TipoAnimal, tipo_id)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de animal nao encontrado")
    for campo, valor in payload.model_dump().items():
        setattr(tipo, campo, valor)
    db.commit()
    db.refresh(tipo)
    return tipo


@router_tipos.delete("/{tipo_id}", status_code=204, dependencies=[Depends(exigir_escrita)])
def desativar_tipo(tipo_id: int, db: Session = Depends(get_db)):
    tipo = db.get(TipoAnimal, tipo_id)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de animal nao encontrado")
    tipo.ativo = False
    db.commit()


# ---------------------------------------------------------------------
# RACAS - referencia comum a todos; o animal pode ou nao ter uma
# ---------------------------------------------------------------------

@router_racas.post("/", response_model=RacaRead, status_code=201, dependencies=[Depends(exigir_escrita)])
def criar_raca(payload: RacaBase, db: Session = Depends(get_db)):
    raca = Raca(**payload.model_dump())
    db.add(raca)
    db.commit()
    db.refresh(raca)
    return raca


@router_racas.get("/", response_model=list[RacaRead])
def listar_racas(db: Session = Depends(get_db)):
    return db.execute(select(Raca).order_by(Raca.descricao)).scalars().all()


@router_racas.get("/{raca_id}", response_model=RacaRead)
def obter_raca(raca_id: int, db: Session = Depends(get_db)):
    raca = db.get(Raca, raca_id)
    if not raca:
        raise HTTPException(status_code=404, detail="Raca nao encontrada")
    return raca


@router_racas.put("/{raca_id}", response_model=RacaRead, dependencies=[Depends(exigir_escrita)])
def atualizar_raca(raca_id: int, payload: RacaBase, db: Session = Depends(get_db)):
    raca = db.get(Raca, raca_id)
    if not raca:
        raise HTTPException(status_code=404, detail="Raca nao encontrada")
    for campo, valor in payload.model_dump().items():
        setattr(raca, campo, valor)
    db.commit()
    db.refresh(raca)
    return raca


@router_racas.delete("/{raca_id}", status_code=204, dependencies=[Depends(exigir_escrita)])
def desativar_raca(raca_id: int, db: Session = Depends(get_db)):
    raca = db.get(Raca, raca_id)
    if not raca:
        raise HTTPException(status_code=404, detail="Raca nao encontrada")
    raca.ativo = False
    db.commit()


# ---------------------------------------------------------------------
# ANIMAIS - sempre no contexto de UMA propriedade (cabecalho X-Propriedade-Id)
# ---------------------------------------------------------------------
# O animal so existe para o usuario dentro da propriedade escolhida: a listagem,
# a busca por id e a edicao passam todas pelo vinculo com ela. Um animal criado
# aqui ja nasce vinculado a propriedade do contexto.

def _da_propriedade(propriedade: Propriedade):
    return Animal.id.in_(
        select(PropriedadeAnimal.animal_id).where(PropriedadeAnimal.propriedade_id == propriedade.id)
    )


def _buscar(db: Session, propriedade: Propriedade, animal_id: int) -> Animal:
    animal = db.execute(
        select(Animal).where(Animal.id == animal_id, _da_propriedade(propriedade))
    ).scalar_one_or_none()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal nao encontrado")
    return animal


@router.post("/", response_model=AnimalRead, status_code=201)
def criar_animal(
    payload: AnimalBase,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_escrita),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    animal = Animal(**payload.model_dump(), usuario_inclusao_id=usuario.id)
    db.add(animal)
    with traduzir_integridade(db):
        db.flush()
    db.add(PropriedadeAnimal(propriedade_id=propriedade.id, animal_id=animal.id))
    confirmar(db)
    db.refresh(animal)
    return animal


@router.get("/", response_model=list[AnimalRead])
def listar_animais(
    busca: str | None = None,
    tipo_animal_id: int | None = None,
    db: Session = Depends(get_db),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    stmt = select(Animal).where(_da_propriedade(propriedade))
    if tipo_animal_id:
        stmt = stmt.where(Animal.tipo_animal_id == tipo_animal_id)
    if busca:
        stmt = stmt.where(contem(Animal.nome, busca) | contem(Animal.codigo, busca))
    return db.execute(stmt.order_by(Animal.nome)).scalars().all()


@router.get("/{animal_id}", response_model=AnimalRead)
def obter_animal(
    animal_id: int, db: Session = Depends(get_db), propriedade: Propriedade = Depends(propriedade_atual),
):
    return _buscar(db, propriedade, animal_id)


@router.put("/{animal_id}", response_model=AnimalRead, dependencies=[Depends(exigir_escrita)])
def atualizar_animal(
    animal_id: int,
    payload: AnimalBase,
    db: Session = Depends(get_db),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    animal = _buscar(db, propriedade, animal_id)
    for campo, valor in payload.model_dump().items():
        setattr(animal, campo, valor)
    confirmar(db)
    db.refresh(animal)
    return animal


@router.delete("/{animal_id}", status_code=204, dependencies=[Depends(exigir_escrita)])
def desativar_animal(
    animal_id: int, db: Session = Depends(get_db), propriedade: Propriedade = Depends(propriedade_atual),
):
    _buscar(db, propriedade, animal_id).ativo = False
    db.commit()
