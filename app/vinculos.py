"""
Sincronizacao de tabelas associativas (propriedades_animais,
veterinarios_propriedades, propriedades_usuarios).

O front manda sempre o conjunto completo de ids que devem ficar vinculados;
aqui se calcula o que entra e o que sai. Fazer o diff (em vez de apagar tudo e
reinserir) preserva o id dos vinculos que nao mudaram e nao mexe no indice unico.
"""
from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session


def sincronizar(
    db: Session,
    modelo,
    coluna_pai,
    pai_id: int,
    coluna_filho,
    ids_novos: list[int],
    permitidos: set[int] | None = None,
) -> None:
    """Deixa exatamente `ids_novos` vinculados ao pai.

    `permitidos` limita o que o chamador pode enxergar/mexer (None = tudo). Um id
    fora dele e recusado, e vinculos existentes fora dele sao preservados - e
    assim que quem ve so parte das propriedades nao apaga, sem querer, os
    vinculos das que nao ve.
    """
    novos = set(ids_novos)
    if permitidos is not None:
        invalidos = novos - permitidos
        if invalidos:
            raise HTTPException(
                status_code=400,
                detail=f"Item inexistente ou sem acesso: {sorted(invalidos)}",
            )

    atuais = set(db.execute(select(coluna_filho).where(coluna_pai == pai_id)).scalars())
    if permitidos is not None:
        atuais &= permitidos

    remover = atuais - novos
    if remover:
        db.execute(delete(modelo).where(coluna_pai == pai_id, coluna_filho.in_(remover)))
    for filho_id in novos - atuais:
        db.add(modelo(**{coluna_pai.key: pai_id, coluna_filho.key: filho_id}))
