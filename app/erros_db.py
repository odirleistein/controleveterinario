"""
Traduz erros de integridade do Postgres em respostas HTTP compreensiveis.

O banco e a ultima barreira (indices unicos, FKs com ON DELETE RESTRICT); em vez
de cada rota repetir o try/except com a sua mensagem, o nome da constraint
violada (convencao udx_/fk_ do schema) decide o texto.
"""
from contextlib import contextmanager

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

MENSAGENS = {
    "udx_pessoas_email": "Ja existe uma pessoa com esse e-mail",
    "udx_pessoas_fisicas_cpf": "Ja existe uma pessoa com esse CPF",
    "udx_pessoas_juridicas_cnpj": "Ja existe uma pessoa com esse CNPJ",
    "udx_usuarios_email": "Ja existe um usuario com esse e-mail",
    "udx_usuarios_pessoa_id": "Essa pessoa ja tem um usuario",
    "udx_veterinarios_pessoa_id": "Essa pessoa ja e veterinario",
    "udx_veterinarios_usuario_id": "Esse usuario ja esta vinculado a outro veterinario",
    "udx_estados_sigla": "Ja existe um estado com essa sigla",
    "pk_ceps": "Esse CEP ja esta cadastrado",
    "udx_propriedades_animais_propriedade_id_animal_id": "Esse animal ja esta na propriedade",
}


def _nome_constraint(erro: IntegrityError) -> str | None:
    diag = getattr(erro.orig, "diag", None)
    return getattr(diag, "constraint_name", None)


@contextmanager
def traduzir_integridade(db: Session, mensagem_em_uso: str = "Registro em uso: existem outros cadastros ligados a ele"):
    """Converte IntegrityError em HTTPException dentro do bloco (e faz rollback).

    Violacao de unicidade usa a mensagem da constraint; violacao de FK (apagar
    algo ainda referenciado, ou apontar para um id inexistente) usa a mensagem
    em_uso / referencia invalida. O flush no meio de uma rota tambem pode
    estourar, por isso o bloco existe alem do confirmar().
    """
    try:
        yield
    except IntegrityError as erro:
        db.rollback()
        nome = _nome_constraint(erro)
        if nome in MENSAGENS:
            raise HTTPException(status_code=409, detail=MENSAGENS[nome])
        sqlstate = getattr(erro.orig, "pgcode", None)
        if sqlstate == "23503":  # foreign_key_violation
            # Numa exclusao, a FK violada e a de quem ainda referencia o registro.
            # Nao da para ler isso da mensagem do Postgres: ela sai no idioma do servidor.
            if (erro.statement or "").lstrip().upper().startswith("DELETE"):
                raise HTTPException(status_code=409, detail=mensagem_em_uso)
            raise HTTPException(status_code=400, detail="Referencia invalida: registro relacionado nao existe")
        raise HTTPException(status_code=409, detail="Registro duplicado ou em conflito com outro")


def confirmar(db: Session, mensagem_em_uso: str = "Registro em uso: existem outros cadastros ligados a ele") -> None:
    """commit() que vira 409/400 em vez de 500 quando o banco recusa."""
    with traduzir_integridade(db, mensagem_em_uso):
        db.commit()
