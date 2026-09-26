"""
Regras dos indicadores reprodutivos, em funcoes puras sobre o historico de eventos de
uma vaca (`ficha.Evento`), para dar para testar sem banco. As definicoes seguem o que
se usa na pecuaria leiteira; onde a planilha nao dizia, a escolha esta comentada.
"""
from datetime import date, timedelta

from app.ficha import INSEMINACOES, Evento, _ordenar, situacao

# Ciclo do manejo reprodutivo: as taxas de servico se medem de 21 em 21 dias.
DIAS_CICLO = 21
DIAS_POR_MES = 30.4375

CONCEBEU = "CONCEBEU"
NAO_CONCEBEU = "NAO_CONCEBEU"
PENDENTE = "PENDENTE"


def resultado_inseminacoes(eventos: list[Evento]) -> list[tuple[Evento, str]]:
    """Resultado de cada inseminacao pelo que veio depois dela: prenhez confirmada (ou
    parto/secagem, que so existem com prenhez) e concepcao; retorno de cio, nova
    inseminacao ou aborto e falha; sem nada depois, ainda pendente (fica fora das taxas,
    pois nao da para dizer se pegou). Descarte tambem nao diz nada sobre a inseminacao."""
    ordenados = _ordenar(eventos)
    saida = []
    for i, e in enumerate(ordenados):
        if e.codigo not in INSEMINACOES:
            continue
        resultado = PENDENTE
        for seguinte in ordenados[i + 1:]:
            if seguinte.codigo in ("PRENHEZ", "PARTO", "SECAGEM"):
                resultado = CONCEBEU
                break
            if seguinte.codigo in INSEMINACOES or seguinte.codigo in ("RETORNO_CIO", "ABORTO"):
                resultado = NAO_CONCEBEU
                break
            if seguinte.codigo == "DESCARTE":
                break
        saida.append((e, resultado))
    return saida


def apta_em(eventos: list[Evento], dia: date, periodo_espera: int) -> bool:
    """Vaca apta a ser inseminada no dia: ja tem historico, esta vazia (nao inseminada,
    prenhe, seca nem descartada) e passou o periodo voluntario de espera desde o parto."""
    antes = [e for e in eventos if e.data < dia]
    if not antes or situacao(antes) != "Vazia":
        return False
    partos = [e.data for e in antes if e.codigo == "PARTO"]
    return not partos or (dia - max(partos)).days >= periodo_espera


def inicios_de_ciclo(inicio: date, fim: date) -> list[date]:
    """Ciclos de 21 dias inteiros dentro do periodo (o ultimo, incompleto, fica de fora)."""
    inicios = []
    atual = inicio
    while atual + timedelta(days=DIAS_CICLO - 1) <= fim:
        inicios.append(atual)
        atual += timedelta(days=DIAS_CICLO)
    return inicios


def intervalos_entre_partos(eventos: list[Evento]) -> list[tuple[date, int]]:
    """(data do parto mais novo, dias desde o parto anterior) para cada par de partos seguidos."""
    partos = [e.data for e in _ordenar(eventos) if e.codigo == "PARTO"]
    return [(atual, (atual - anterior).days) for anterior, atual in zip(partos, partos[1:])]


def idade_em_meses(nascimento: date, dia: date) -> float:
    return round((dia - nascimento).days / DIAS_POR_MES, 1)


def percentual(parte: int | float, todo: int | float) -> float | None:
    return round(parte / todo * 100, 1) if todo else None
