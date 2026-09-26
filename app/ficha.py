"""
Calculos da ficha da vaca: o que a planilha de controle faz com formulas e que aqui
sai do historico de eventos, sem gravar nada (situacao, DEL, prazos, doses).

Sao funcoes puras (recebem listas de eventos ja lidas) para dar para testar sem banco.
Os prazos abaixo sao o padrao da pecuaria leiteira; se um dia variarem por raca, o
lugar de mudar e este arquivo.
"""
from dataclasses import dataclass
from datetime import date, timedelta

DIAS_RETORNO_CIO = 21
# 282 dias e o que a planilha da granja usa (inseminacao 22/05/2020 -> parto 28/02/2021).
DIAS_GESTACAO = 282
DIAS_SECA_ANTES_DO_PARTO = 60

INSEMINACOES = {"INSEMINACAO", "IATF"}


@dataclass
class Evento:
    """So o que o calculo precisa de um evento reprodutivo."""
    codigo: str
    data: date
    id: int = 0


def _ordenar(eventos: list[Evento]) -> list[Evento]:
    return sorted(eventos, key=lambda e: (e.data, e.id))


def situacao(eventos: list[Evento]) -> str:
    """Situacao pelo ultimo evento: e ele que diz onde a vaca esta hoje."""
    if not eventos:
        return "Vazia"
    ultimo = _ordenar(eventos)[-1].codigo
    if ultimo == "DESCARTE":
        return "Descartada"
    if ultimo == "SECAGEM":
        return "Seca"
    if ultimo == "PRENHEZ":
        return "Prenhe"
    if ultimo in INSEMINACOES:
        return "Inseminada"
    return "Vazia"  # parto, aborto ou retorno de cio: pronta para nova cobertura


def dias_em_lactacao(eventos: list[Evento], hoje: date) -> int | None:
    """DEL: dias desde o ultimo parto, enquanto a vaca esta lactando (sem secagem ou
    descarte depois dele)."""
    ordenados = _ordenar(eventos)
    partos = [e for e in ordenados if e.codigo == "PARTO"]
    if not partos:
        return None
    parto = partos[-1]
    depois = [e for e in ordenados if (e.data, e.id) > (parto.data, parto.id)]
    if any(e.codigo in ("SECAGEM", "DESCARTE") for e in depois):
        return None
    return (hoje - parto.data).days


def prazos(eventos: list[Evento]) -> dict:
    """Datas previstas a partir da ultima inseminacao. Retorno de cio so faz sentido
    enquanto a vaca esta so inseminada; provavel parto e secagem, com prenhez ou seca."""
    ordenados = _ordenar(eventos)
    vazio = {"inseminacao": None, "retorno_cio": None, "provavel_parto": None, "secagem": None}
    atual = situacao(ordenados)
    inseminacoes = [e for e in ordenados if e.codigo in INSEMINACOES]
    if not inseminacoes or atual not in ("Inseminada", "Prenhe", "Seca"):
        return vazio
    insem = inseminacoes[-1].data
    parto = insem + timedelta(days=DIAS_GESTACAO)
    return {
        "inseminacao": insem,
        "retorno_cio": insem + timedelta(days=DIAS_RETORNO_CIO) if atual == "Inseminada" else None,
        "provavel_parto": parto,
        "secagem": parto - timedelta(days=DIAS_SECA_ANTES_DO_PARTO) if atual != "Seca" else None,
    }


def doses_ate_confirmacao(eventos: list[Evento]) -> int:
    """Inseminacoes desde o ultimo parto ou aborto, ate a prenhez confirmada (ou todas
    as que houver, se ainda nao foi confirmada)."""
    ordenados = _ordenar(eventos)
    ultimo_ciclo = max(
        (i for i, e in enumerate(ordenados) if e.codigo in ("PARTO", "ABORTO")), default=-1
    )
    do_ciclo = ordenados[ultimo_ciclo + 1:]
    prenhez = next((i for i, e in enumerate(do_ciclo) if e.codigo == "PRENHEZ"), None)
    if prenhez is not None:
        do_ciclo = do_ciclo[:prenhez]
    return sum(1 for e in do_ciclo if e.codigo in INSEMINACOES)


def inicio_lactacao(partos: list[date], data: date) -> date | None:
    """Data do parto que abriu a lactacao em que `data` cai (o ultimo parto ate ela)."""
    anteriores = [p for p in partos if p <= data]
    return max(anteriores) if anteriores else None
