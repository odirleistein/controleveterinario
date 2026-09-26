from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import ficha as calculo
from app.acesso import conferir_animal_da_propriedade, propriedade_atual
from app.database import get_db
from app.models import Animal, EventoReprodutivo, Pesagem, ProducaoLeite, Propriedade, Reprodutor
from app.schemas import (
    AnimalRead, EventoReprodutivoRead, FichaAnimal, GenealogiaFicha, PartoFicha, PesagemRead, PrazosFicha,
    ProducaoFicha,
)

router = APIRouter(prefix="/animais", tags=["Ficha do animal"])


def _nome(reprodutor: Reprodutor | None) -> str | None:
    return reprodutor.nome if reprodutor else None


def _genealogia(animal: Animal) -> GenealogiaFicha:
    mae, pai = animal.mae, animal.pai
    avo_materno = mae.pai if mae else None
    avo_paterno = pai.pai if pai else None
    return GenealogiaFicha(
        mae=_nome(mae), pai=_nome(pai),
        avo_materno=_nome(avo_materno), bisavo_materno=_nome(avo_materno.pai if avo_materno else None),
        avo_paterno=_nome(avo_paterno), bisavo_paterno=_nome(avo_paterno.pai if avo_paterno else None),
    )


@router.get("/{animal_id}/ficha", response_model=FichaAnimal)
def ficha_do_animal(
    animal_id: int, db: Session = Depends(get_db), propriedade: Propriedade = Depends(propriedade_atual),
):
    """Ficha da vaca na propriedade aberta. Eventos, producao e pesagens sao so os
    lancados nesta propriedade, como em qualquer dado de propriedade."""
    conferir_animal_da_propriedade(db, propriedade, animal_id)
    animal = db.get(Animal, animal_id)

    eventos = db.execute(
        select(EventoReprodutivo)
        .where(EventoReprodutivo.animal_id == animal_id, EventoReprodutivo.propriedade_id == propriedade.id)
        .order_by(EventoReprodutivo.data_evento, EventoReprodutivo.id)
    ).scalars().all()
    para_calculo = [calculo.Evento(codigo=e.tipo_evento.codigo, data=e.data_evento, id=e.id) for e in eventos]
    hoje = date.today()

    partos = [e for e in eventos if e.tipo_evento.codigo == "PARTO"]
    datas_partos = [e.data_evento for e in partos]

    producoes = db.execute(
        select(ProducaoLeite)
        .where(ProducaoLeite.animal_id == animal_id, ProducaoLeite.propriedade_id == propriedade.id)
        .order_by(ProducaoLeite.data_producao)
    ).scalars().all()
    # Acumulado zera a cada parto: e a producao da lactacao, nao da vida da vaca.
    acumulado: dict[date | None, float] = {}
    linhas_producao = []
    for p in producoes:
        lactacao = calculo.inicio_lactacao(datas_partos, p.data_producao)
        acumulado[lactacao] = acumulado.get(lactacao, 0.0) + float(p.litros)
        linhas_producao.append(ProducaoFicha(
            id=p.id, data_producao=p.data_producao, litros=float(p.litros), dias_referentes=p.dias_referentes,
            litros_por_dia=p.litros_por_dia, acumulado_lactacao=round(acumulado[lactacao], 2),
        ))

    # Lactacao atual: a que abriu no ultimo parto (some se a vaca nao esta lactando).
    lactacao_atual = calculo.dias_em_lactacao(para_calculo, hoje) is not None
    litros_atual = media_atual = None
    if lactacao_atual:
        inicio = max(datas_partos)
        da_lactacao = [p for p in producoes if p.data_producao >= inicio]
        litros_atual = round(sum(float(p.litros) for p in da_lactacao), 2)
        dias = sum(p.dias_referentes for p in da_lactacao)
        media_atual = round(litros_atual / dias, 2) if dias else None

    pesagens = db.execute(
        select(Pesagem)
        .where(Pesagem.animal_id == animal_id, Pesagem.propriedade_id == propriedade.id)
        .order_by(Pesagem.data_pesagem.desc())
    ).scalars().all()

    return FichaAnimal(
        animal=AnimalRead.model_validate(animal),
        genealogia=_genealogia(animal),
        situacao=calculo.situacao(para_calculo),
        dias_em_lactacao=calculo.dias_em_lactacao(para_calculo, hoje),
        prazos=PrazosFicha(**calculo.prazos(para_calculo)),
        doses_ate_confirmacao=calculo.doses_ate_confirmacao(para_calculo),
        partos=[PartoFicha(numero=i, data_evento=e.data_evento, sexo_cria=e.sexo_cria) for i, e in enumerate(partos, 1)],
        historico=[EventoReprodutivoRead.model_validate(e) for e in eventos],
        producao=list(reversed(linhas_producao)),
        litros_lactacao_atual=litros_atual,
        media_litros_dia_lactacao_atual=media_atual,
        pesagens=[PesagemRead.model_validate(p) for p in pesagens],
    )
