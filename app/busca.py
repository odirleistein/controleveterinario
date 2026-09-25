"""
Busca de texto que ignora acento, cedilha e caixa ("Cleber" acha "Cléber").

Sem a extensao unaccent do Postgres de proposito: criar extensao exige
superusuario e a busca precisa funcionar em qualquer banco onde o sistema rodar.
"""
import unicodedata

from sqlalchemy import func

_COM_ACENTO = "áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ"
_SEM_ACENTO = "aaaaaeeeeiiiiooooouuuucnAAAAAEEEEIIIIOOOOOUUUUCN"


def sem_acento(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c)).lower()


def contem(coluna, termo: str):
    """Condicao SQL: a coluna contem o termo, sem diferenciar acento nem caixa."""
    termo = sem_acento(termo.strip())
    for especial in ("\\", "%", "_"):
        termo = termo.replace(especial, "\\" + especial)
    normalizada = func.lower(func.translate(coluna, _COM_ACENTO, _SEM_ACENTO))
    return normalizada.like(f"%{termo}%", escape="\\")
