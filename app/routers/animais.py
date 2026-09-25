from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.acesso import ids_propriedades_visiveis
from app.busca import contem
from app.database import get_db
from app.erros_db import confirmar
from app.models import Animal, PropriedadeAnimal, TipoAnimal, Usuario
from app.schemas import AnimalBase, AnimalRead, TipoAnimalBase, TipoAnimalRead
from app.security import exigir_escrita, get_current_user

router_tipos = APIRouter(prefix="/tipos-animal", tags=["Tipos de animal"])
router = APIRouter(prefix="/animais", tags=["Animais"])


# ---------------------------------------------------------------------
# TIPOS DE ANIMAL (bovino, equino, suino...)
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
# ANIMAIS
# ---------------------------------------------------------------------
# Quem nao e MASTER ve o animal se ele esta numa propriedade que enxerga, ou se
# ainda nao esta em propriedade nenhuma e foi ele quem o cadastrou (antes de ser
# vinculado, senao o autor nao o acharia para vincular).

def condicao_visivel(usuario: Usuario):
    visiveis = ids_propriedades_visiveis(usuario)
    if visiveis is None:
        return None
    em_visivel = exists().where(
        PropriedadeAnimal.animal_id == Animal.id, PropriedadeAnimal.propriedade_id.in_(visiveis)
    )
    em_qualquer = exists().where(PropriedadeAnimal.animal_id == Animal.id)
    return em_visivel | (~em_qualquer & (Animal.usuario_inclusao_id == usuario.id))


def _buscar_visivel(db: Session, usuario: Usuario, animal_id: int) -> Animal:
    stmt = select(Animal).where(Animal.id == animal_id)
    condicao = condicao_visivel(usuario)
    if condicao is not None:
        stmt = stmt.where(condicao)
    animal = db.execute(stmt).scalar_one_or_none()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal nao encontrado")
    return animal


@router.post("/", response_model=AnimalRead, status_code=201, dependencies=[Depends(exigir_escrita)])
def criar_animal(
    payload: AnimalBase, db: Session = Depends(get_db), usuario: Usuario = Depends(exigir_escrita),
):
    animal = Animal(**payload.model_dump(), usuario_inclusao_id=usuario.id)
    db.add(animal)
    confirmar(db)
    db.refresh(animal)
    return animal


@router.get("/", response_model=list[AnimalRead])
def listar_animais(
    busca: str | None = None,
    tipo_animal_id: int | None = None,
    propriedade_id: int | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    stmt = select(Animal)
    condicao = condicao_visivel(usuario)
    if condicao is not None:
        stmt = stmt.where(condicao)
    if tipo_animal_id:
        stmt = stmt.where(Animal.tipo_animal_id == tipo_animal_id)
    if propriedade_id:
        stmt = stmt.where(
            exists().where(
                PropriedadeAnimal.animal_id == Animal.id,
                PropriedadeAnimal.propriedade_id == propriedade_id,
            )
        )
    if busca:
        stmt = stmt.where(contem(Animal.nome, busca) | contem(Animal.codigo, busca))
    return db.execute(stmt.order_by(Animal.nome)).scalars().all()


@router.get("/{animal_id}", response_model=AnimalRead)
def obter_animal(
    animal_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user),
):
    return _buscar_visivel(db, usuario, animal_id)


@router.put("/{animal_id}", response_model=AnimalRead, dependencies=[Depends(exigir_escrita)])
def atualizar_animal(
    animal_id: int,
    payload: AnimalBase,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    animal = _buscar_visivel(db, usuario, animal_id)
    for campo, valor in payload.model_dump().items():
        setattr(animal, campo, valor)
    confirmar(db)
    db.refresh(animal)
    return animal


@router.delete("/{animal_id}", status_code=204, dependencies=[Depends(exigir_escrita)])
def desativar_animal(
    animal_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user),
):
    _buscar_visivel(db, usuario, animal_id).ativo = False
    db.commit()
