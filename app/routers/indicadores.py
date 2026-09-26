"""
Indicadores zootecnicos da propriedade aberta. Tudo sai do historico reprodutivo ja
lancado (ver app/ficha.py para situacao e DEL, e app/calculo_indicadores.py para as
taxas); nada e gravado, exceto a meta de cada indicador.

Quem entra nas contas e "vaca": animal ativo da propriedade cujo tipo produz leite.
Eventos sao so os lancados nesta propriedade, como em qualquer dado de propriedade.
"""
from collections import Counter, defaultdict
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import ficha as calculo
from app import calculo_indicadores as ind
from app.acesso import propriedade_atual
from app.database import get_db
from app.erros_db import confirmar
from app.models import Animal, EventoReprodutivo, MetaIndicador, Propriedade, PropriedadeAnimal, TipoAnimal
from app.schemas import (
    CicloFertilidade, DelIndicador, DelLinha, Fertilidade, FaseRoda, GrupoInseminacao, IndicadorPorAnimal,
    LinhaIndicador, MetaIn, MetasRead, PeriodoIndicador, RodaReproducao,
)
from app.security import exigir_escrita

router = APIRouter(prefix="/indicadores", tags=["Indicadores"])

# Meta (ou parametro) usada enquanto a propriedade nao definir a sua. So chaves desta
# lista aceitam valor. As de tempo estao em dias (DEL, intervalo, espera) ou meses
# (idades); as taxas em %.
METAS_PADRAO = {
    "DEL": 160.0,
    "INTERVALO_PARTOS": 395.0,
    "IDADE_PRIMEIRO_PARTO": 24.0,
    "IDADE_COBERTURA": 15.0,
    "TAXA_SERVICO": 60.0,
    "TAXA_CONCEPCAO": 40.0,
    "TAXA_PRENHEZ": 20.0,
    "SERVICO_CONCEPCAO": 2.5,
    # Periodo voluntario de espera: dias depois do parto em que a vaca ainda nao e inseminada.
    "PERIODO_ESPERA": 50.0,
}


def _metas(db: Session, propriedade: Propriedade) -> dict[str, float]:
    metas = dict(METAS_PADRAO)
    for m in db.execute(select(MetaIndicador).where(MetaIndicador.propriedade_id == propriedade.id)).scalars():
        if m.indicador in metas:
            metas[m.indicador] = float(m.valor)
    return metas


def _periodo(data_inicio: date | None, data_fim: date | None) -> tuple[date, date]:
    """Sem datas, os ultimos 12 meses: janela grande o bastante para rebanho pequeno."""
    fim = data_fim or date.today()
    inicio = data_inicio or fim - timedelta(days=365)
    if inicio > fim:
        raise HTTPException(status_code=400, detail="A data inicial nao pode ser depois da final")
    return inicio, fim


def _da_propriedade(propriedade: Propriedade):
    return Animal.id.in_(select(PropriedadeAnimal.animal_id).where(PropriedadeAnimal.propriedade_id == propriedade.id))


def animais_produtores(db: Session, propriedade: Propriedade) -> list[Animal]:
    """Animais ativos da propriedade cujo tipo produz leite (as 'vacas' dos indicadores)."""
    return list(db.execute(
        select(Animal)
        .join(TipoAnimal, TipoAnimal.id == Animal.tipo_animal_id)
        .where(_da_propriedade(propriedade), Animal.ativo.is_(True), TipoAnimal.produz_leite.is_(True))
        .order_by(Animal.nome)
    ).scalars().unique())


def historicos(db: Session, propriedade: Propriedade, animais: list[Animal]) -> dict[int, list[calculo.Evento]]:
    """Eventos de cada animal, so os lancados nesta propriedade."""
    por_animal: dict[int, list[calculo.Evento]] = defaultdict(list)
    if not animais:
        return por_animal
    eventos = db.execute(
        select(EventoReprodutivo).where(
            EventoReprodutivo.propriedade_id == propriedade.id,
            EventoReprodutivo.animal_id.in_([a.id for a in animais]),
        )
    ).scalars()
    for e in eventos:
        por_animal[e.animal_id].append(calculo.Evento(codigo=e.tipo_evento.codigo, data=e.data_evento, id=e.id))
    return por_animal


# ---------------------------------------------------------------------
# METAS
# ---------------------------------------------------------------------

@router.get("/metas", response_model=MetasRead)
def obter_metas(db: Session = Depends(get_db), propriedade: Propriedade = Depends(propriedade_atual)):
    return MetasRead(metas=_metas(db, propriedade))


@router.put("/metas/{indicador}", response_model=MetasRead, dependencies=[Depends(exigir_escrita)])
def definir_meta(
    indicador: str,
    payload: MetaIn,
    db: Session = Depends(get_db),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    if indicador not in METAS_PADRAO:
        raise HTTPException(status_code=404, detail="Indicador nao encontrado")
    meta = db.execute(
        select(MetaIndicador).where(
            MetaIndicador.propriedade_id == propriedade.id, MetaIndicador.indicador == indicador
        )
    ).scalar_one_or_none()
    if meta:
        meta.valor = payload.valor
    else:
        db.add(MetaIndicador(propriedade_id=propriedade.id, indicador=indicador, valor=payload.valor))
    confirmar(db)
    return MetasRead(metas=_metas(db, propriedade))


# ---------------------------------------------------------------------
# DEL
# ---------------------------------------------------------------------

@router.get("/del", response_model=DelIndicador)
def indicador_del(db: Session = Depends(get_db), propriedade: Propriedade = Depends(propriedade_atual)):
    """DEL de cada vaca em lactacao e a media do rebanho contra a meta. Vaca seca,
    sem parto ou descartada nao entra: a media so faz sentido entre as que lactam."""
    vacas = animais_produtores(db, propriedade)
    historico = historicos(db, propriedade, vacas)
    hoje = date.today()

    linhas = []
    for v in vacas:
        dias = calculo.dias_em_lactacao(historico.get(v.id, []), hoje)
        if dias is not None:
            linhas.append(DelLinha(animal_id=v.id, animal_nome=v.nome, dias=dias))
    linhas.sort(key=lambda l: l.dias, reverse=True)

    meta = _metas(db, propriedade)["DEL"]
    media = round(sum(l.dias for l in linhas) / len(linhas), 1) if linhas else None
    return DelIndicador(
        meta=meta,
        media=media,
        vacas_em_lactacao=len(linhas),
        total_vacas=len(vacas),
        acima_da_meta=sum(1 for l in linhas if l.dias > meta),
        linhas=linhas,
    )


# ---------------------------------------------------------------------
# FERTILIDADE: taxa de servico, concepcao, prenhez, servico de concepcao e IATF
# ---------------------------------------------------------------------

def _grupo(resultados: list[str]) -> GrupoInseminacao:
    contagem = Counter(resultados)
    concebeu, nao = contagem[ind.CONCEBEU], contagem[ind.NAO_CONCEBEU]
    return GrupoInseminacao(
        inseminacoes=len(resultados), concepcoes=concebeu, nao_concebeu=nao, pendentes=contagem[ind.PENDENTE],
        taxa_concepcao=ind.percentual(concebeu, concebeu + nao),
    )


@router.get("/fertilidade", response_model=Fertilidade)
def indicador_fertilidade(
    data_inicio: date | None = None,
    data_fim: date | None = None,
    db: Session = Depends(get_db),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    """
    - Taxa de concepcao: prenhezes / inseminacoes com resultado (as sem resultado ainda
      ficam de fora), das inseminacoes feitas no periodo.
    - Servico de concepcao: inseminacoes com resultado por prenhez.
    - Taxa de servico: em cada ciclo de 21 dias, vacas aptas inseminadas / vacas aptas
      (apta = vazia e fora do periodo voluntario de espera); soma dos ciclos do periodo.
    - Taxa de prenhez: taxa de servico x taxa de concepcao.
    """
    inicio, fim = _periodo(data_inicio, data_fim)
    metas = _metas(db, propriedade)
    espera = int(metas["PERIODO_ESPERA"])
    vacas = animais_produtores(db, propriedade)
    historico = historicos(db, propriedade, vacas)

    resultados = {"IATF": [], "INSEMINACAO": []}
    for v in vacas:
        for evento, resultado in ind.resultado_inseminacoes(historico.get(v.id, [])):
            if inicio <= evento.data <= fim:
                resultados["IATF" if evento.codigo == "IATF" else "INSEMINACAO"].append(resultado)
    geral = _grupo(resultados["IATF"] + resultados["INSEMINACAO"])

    ciclos = []
    for abertura in ind.inicios_de_ciclo(inicio, fim):
        ultimo_dia = abertura + timedelta(days=ind.DIAS_CICLO - 1)
        aptas = [v for v in vacas if ind.apta_em(historico.get(v.id, []), abertura, espera)]
        servidas = sum(
            1 for v in aptas
            if any(e.codigo in calculo.INSEMINACOES and abertura <= e.data <= ultimo_dia for e in historico.get(v.id, []))
        )
        ciclos.append(CicloFertilidade(
            inicio=abertura, elegiveis=len(aptas), servidas=servidas, taxa_servico=ind.percentual(servidas, len(aptas)),
        ))
    elegiveis = sum(c.elegiveis for c in ciclos)
    servidas = sum(c.servidas for c in ciclos)
    taxa_servico = ind.percentual(servidas, elegiveis)
    taxa_prenhez = (
        round(taxa_servico * geral.taxa_concepcao / 100, 1)
        if taxa_servico is not None and geral.taxa_concepcao is not None else None
    )
    com_resultado = geral.concepcoes + geral.nao_concebeu

    return Fertilidade(
        periodo=PeriodoIndicador(data_inicio=inicio, data_fim=fim),
        metas={k: metas[k] for k in ("TAXA_SERVICO", "TAXA_CONCEPCAO", "TAXA_PRENHEZ", "SERVICO_CONCEPCAO", "PERIODO_ESPERA")},
        taxa_servico=taxa_servico,
        taxa_concepcao=geral.taxa_concepcao,
        taxa_prenhez=taxa_prenhez,
        servico_concepcao=round(com_resultado / geral.concepcoes, 2) if geral.concepcoes else None,
        vacas_aptas_ciclos=elegiveis,
        vacas_servidas=servidas,
        ciclos=ciclos,
        geral=geral,
        iatf=_grupo(resultados["IATF"]),
        convencional=_grupo(resultados["INSEMINACAO"]),
        percentual_iatf=ind.percentual(len(resultados["IATF"]), geral.inseminacoes),
    )


# ---------------------------------------------------------------------
# INDICADORES POR ANIMAL: intervalo entre partos e idades (1o parto, cobertura)
# ---------------------------------------------------------------------

def _por_animal(meta: float, inicio: date, fim: date, linhas: list[LinhaIndicador], media: float | None) -> IndicadorPorAnimal:
    linhas.sort(key=lambda l: l.valor, reverse=True)
    return IndicadorPorAnimal(
        meta=meta, media=media, total=len(linhas), acima_da_meta=sum(1 for l in linhas if l.valor > meta),
        periodo=PeriodoIndicador(data_inicio=inicio, data_fim=fim), linhas=linhas,
    )


@router.get("/intervalo-partos", response_model=IndicadorPorAnimal)
def indicador_intervalo_partos(
    data_inicio: date | None = None,
    data_fim: date | None = None,
    db: Session = Depends(get_db),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    """Dias entre partos seguidos, dos partos ocorridos no periodo. A media e de todos os
    intervalos (uma vaca com varios pesa mais); cada linha e a media da propria vaca."""
    inicio, fim = _periodo(data_inicio, data_fim)
    vacas = animais_produtores(db, propriedade)
    historico = historicos(db, propriedade, vacas)
    linhas, todos = [], []
    for v in vacas:
        dias = [d for quando, d in ind.intervalos_entre_partos(historico.get(v.id, [])) if inicio <= quando <= fim]
        if dias:
            todos += dias
            linhas.append(LinhaIndicador(animal_id=v.id, animal_nome=v.nome, valor=round(sum(dias) / len(dias), 1)))
    media = round(sum(todos) / len(todos), 1) if todos else None
    return _por_animal(_metas(db, propriedade)["INTERVALO_PARTOS"], inicio, fim, linhas, media)


def _idades(db: Session, propriedade: Propriedade, inicio: date, fim: date, animais: list[Animal], codigos: set[str]):
    """Idade (meses) de cada animal com nascimento na primeira ocorrencia de um dos
    eventos, quando ela cai no periodo. Sem data de nascimento nao ha idade."""
    historico = historicos(db, propriedade, animais)
    linhas = []
    for a in animais:
        if not a.data_nascimento:
            continue
        primeiro = next((e for e in calculo._ordenar(historico.get(a.id, [])) if e.codigo in codigos), None)
        if primeiro and inicio <= primeiro.data <= fim:
            linhas.append(LinhaIndicador(
                animal_id=a.id, animal_nome=a.nome, valor=ind.idade_em_meses(a.data_nascimento, primeiro.data),
                data=primeiro.data,
            ))
    media = round(sum(l.valor for l in linhas) / len(linhas), 1) if linhas else None
    return linhas, media


@router.get("/idade-primeiro-parto", response_model=IndicadorPorAnimal)
def indicador_idade_primeiro_parto(
    data_inicio: date | None = None,
    data_fim: date | None = None,
    db: Session = Depends(get_db),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    """Meses do nascimento ao primeiro parto lancado, dos partos ocorridos no periodo."""
    inicio, fim = _periodo(data_inicio, data_fim)
    linhas, media = _idades(db, propriedade, inicio, fim, animais_produtores(db, propriedade), {"PARTO"})
    return _por_animal(_metas(db, propriedade)["IDADE_PRIMEIRO_PARTO"], inicio, fim, linhas, media)


@router.get("/idade-cobertura", response_model=IndicadorPorAnimal)
def indicador_idade_cobertura(
    data_inicio: date | None = None,
    data_fim: date | None = None,
    db: Session = Depends(get_db),
    propriedade: Propriedade = Depends(propriedade_atual),
):
    """Meses do nascimento a primeira inseminacao lancada (novilhas e vacas), das
    inseminacoes feitas no periodo. Olha todos os animais da propriedade, nao so as vacas,
    porque a primeira cobertura acontece quando ainda sao novilhas."""
    inicio, fim = _periodo(data_inicio, data_fim)
    animais = list(db.execute(
        select(Animal).where(_da_propriedade(propriedade), Animal.ativo.is_(True)).order_by(Animal.nome)
    ).scalars().unique())
    linhas, media = _idades(db, propriedade, inicio, fim, animais, calculo.INSEMINACOES)
    return _por_animal(_metas(db, propriedade)["IDADE_COBERTURA"], inicio, fim, linhas, media)


# ---------------------------------------------------------------------
# RODA DA REPRODUCAO
# ---------------------------------------------------------------------

@router.get("/roda", response_model=RodaReproducao)
def indicador_roda(db: Session = Depends(get_db), propriedade: Propriedade = Depends(propriedade_atual)):
    """Quantas vacas estao em cada fase do ciclo hoje, pela situacao de cada uma."""
    vacas = animais_produtores(db, propriedade)
    historico = historicos(db, propriedade, vacas)
    hoje = date.today()
    contagem = Counter(calculo.situacao(historico.get(v.id, [])) for v in vacas)
    ordem = ["Vazia", "Inseminada", "Prenhe", "Seca", "Descartada"]
    return RodaReproducao(
        total_vacas=len(vacas),
        em_lactacao=sum(1 for v in vacas if calculo.dias_em_lactacao(historico.get(v.id, []), hoje) is not None),
        fases=[FaseRoda(situacao=s, quantidade=contagem[s]) for s in ordem],
    )
