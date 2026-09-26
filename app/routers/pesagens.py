from datetime import date
from itertools import groupby

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.acesso import conferir_animal_da_propriedade, propriedade_atual
from app.database import get_db
from app.erros_db import confirmar
from app.models import Animal, PadraoPeso, Pesagem, Propriedade, Usuario
from app.schemas import (
    ComparativoPesoLinha, PadraoPesoBase, PadraoPesoRead, PesagemBase, PesagemRead,
)
from app.security import exigir_escrita

router_padroes = APIRouter(prefix="/padroes-peso", tags=["Padroes de peso"])
router = APIRouter(prefix="/pesagens", tags=["Pesagens"])


# ---------------------------------------------------------------------
# PADROES DE PESO IDEAL (raca x idade em meses) - referencia comum a todos
# ---------------------------------------------------------------------

@router_padroes.get("/", response_model=list[PadraoPesoRead])
def listar_padroes(raca_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(PadraoPeso)
    if raca_id:
        stmt = stmt.where(PadraoPeso.raca_id == raca_id)
    return db.execute(stmt.order_by(PadraoPeso.raca_id, PadraoPeso.idade_meses)).scalars().all()


@router_padroes.post("/", response_model=PadraoPesoRead, status_code=201, dependencies=[Depends(exigir_escrita)])
def criar_padrao(payload: PadraoPesoBase, db: Session = Depends(get_db)):
    padrao = PadraoPeso(**payload.model_dump())
    db.add(padrao)
    confirmar(db)
    db.refresh(padrao)
    return padrao


@router_padroes.put("/{padrao_id}", response_model=PadraoPesoRead, dependencies=[Depends(exigir_escrita)])
def atualizar_padrao(padrao_id: int, payload: PadraoPesoBase, db: Session = Depends(get_db)):
    padrao = db.get(PadraoPeso, padrao_id)
    if not padrao:
        raise HTTPException(status_code=404, detail="Padrao de peso nao encontrado")
    for campo, valor in payload.model_dump().items():
        setattr(padrao, campo, valor)
    confirmar(db)
    db.refresh(padrao)
    return padrao


@router_padroes.delete("/{padrao_id}", status_code=204, dependencies=[Depends(exigir_escrita)])
def remover_padrao(padrao_id: int, db: Session = Depends(get_db)):
    padrao = db.get(PadraoPeso, padrao_id)
    if not padrao:
        raise HTTPException(status_code=404, detail="Padrao de peso nao encontrado")
    db.delete(padrao)
    confirmar(db)


# ---------------------------------------------------------------------
# PESAGENS - sempre no contexto de UMA propriedade (cabecalho X-Propriedade-Id)
# ---------------------------------------------------------------------
# A pesagem nasce com a propriedade do contexto e so se lanca peso de animal que
# pertence a ela; listagem, edicao e exclusao tambem filtram por ela.

def _buscar(db: Session, propriedade: Propriedade, pesagem_id: int) -> Pesagem:
    pesagem = db.execute(
        select(Pesagem).where(Pesagem.id == pesagem_id, Pesagem.propriedade_id == propriedade.id)
    ).scalar_one_or_none()
    if not pesagem:
        raise HTTPException(status_code=404, detail="Pesagem nao encontrada")
    return pesagem


def _da_propriedade(propriedade: Propriedade, animal_id: int | None, tipo_animal_id: int | None):
    stmt = select(Pesagem).join(Animal, Animal.id == Pesagem.animal_id).where(Pesagem.propriedade_id == propriedade.id)
    if animal_id:
        stmt = stmt.where(Pesagem.animal_id == animal_id)
    if tipo_animal_id:
        stmt = stmt.where(Animal.tipo_animal_id == tipo_animal_id)
    return stmt


@router.post("/", response_model=PesagemRead, status_code=201)
def criar_pesagem(
    payload: PesagemBase,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_escrita),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    conferir_animal_da_propriedade(db, propriedade, payload.animal_id)
    pesagem = Pesagem(**payload.model_dump(), propriedade_id=propriedade.id, usuario_inclusao_id=usuario.id)
    db.add(pesagem)
    confirmar(db)
    db.refresh(pesagem)
    return pesagem


@router.get("/", response_model=list[PesagemRead])
def listar_pesagens(
    animal_id: int | None = None,
    tipo_animal_id: int | None = None,
    db: Session = Depends(get_db),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    stmt = _da_propriedade(propriedade, animal_id, tipo_animal_id)
    return db.execute(stmt.order_by(Pesagem.data_pesagem.desc(), Animal.nome)).scalars().all()


def _idade_em_meses(nascimento: date, data: date) -> int:
    meses = (data.year - nascimento.year) * 12 + data.month - nascimento.month
    return meses - 1 if data.day < nascimento.day else meses


@router.get("/comparativo", response_model=list[ComparativoPesoLinha])
def comparativo_peso(
    animal_id: int | None = None,
    tipo_animal_id: int | None = None,
    raca_id: int | None = None,
    db: Session = Depends(get_db),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    """Cada pesagem da propriedade contra o peso ideal da raca do animal na idade que
    ele tinha no dia. Sem raca ou sem data de nascimento nao ha ideal para comparar
    (os campos vem nulos); o GMD real e o ganho desde a pesagem anterior do animal,
    e o GMD ideal e o ganho do padrao entre as duas idades."""
    stmt = _da_propriedade(propriedade, animal_id, tipo_animal_id)
    if raca_id:
        stmt = stmt.where(Animal.raca_id == raca_id)
    pesagens = db.execute(stmt.order_by(Pesagem.animal_id, Pesagem.data_pesagem)).scalars().all()

    ideais = {(p.raca_id, p.idade_meses): float(p.peso_ideal_kg) for p in db.execute(select(PadraoPeso)).scalars()}

    linhas = []
    for _, do_animal in groupby(pesagens, key=lambda p: p.animal_id):
        anterior = None  # (data, peso real, peso ideal)
        for p in do_animal:
            animal = p.animal
            real = float(p.peso_kg)
            idade = _idade_em_meses(animal.data_nascimento, p.data_pesagem) if animal.data_nascimento else None
            ideal = ideais.get((animal.raca_id, idade)) if animal.raca_id is not None and idade is not None else None
            gmd_real = gmd_ideal = None
            if anterior:
                dias = (p.data_pesagem - anterior[0]).days
                gmd_real = round((real - anterior[1]) / dias, 3)
                if ideal is not None and anterior[2] is not None:
                    gmd_ideal = round((ideal - anterior[2]) / dias, 3)
            linhas.append(ComparativoPesoLinha(
                pesagem_id=p.id, animal_id=p.animal_id, animal_nome=animal.nome,
                raca_descricao=animal.raca_descricao, data_pesagem=p.data_pesagem, idade_meses=idade,
                peso_real_kg=real, peso_ideal_kg=ideal,
                diferenca_kg=round(real - ideal, 2) if ideal is not None else None,
                gmd_real_kg=gmd_real, gmd_ideal_kg=gmd_ideal,
            ))
            anterior = (p.data_pesagem, real, ideal)
    return sorted(linhas, key=lambda l: (l.animal_nome, l.data_pesagem))


@router.put("/{pesagem_id}", response_model=PesagemRead, dependencies=[Depends(exigir_escrita)])
def atualizar_pesagem(
    pesagem_id: int,
    payload: PesagemBase,
    db: Session = Depends(get_db),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    pesagem = _buscar(db, propriedade, pesagem_id)
    conferir_animal_da_propriedade(db, propriedade, payload.animal_id)
    for campo, valor in payload.model_dump().items():
        setattr(pesagem, campo, valor)
    confirmar(db)
    db.refresh(pesagem)
    return pesagem


@router.delete("/{pesagem_id}", status_code=204, dependencies=[Depends(exigir_escrita)])
def remover_pesagem(
    pesagem_id: int, db: Session = Depends(get_db), propriedade: Propriedade = Depends(propriedade_atual),
):
    db.delete(_buscar(db, propriedade, pesagem_id))
    db.commit()
