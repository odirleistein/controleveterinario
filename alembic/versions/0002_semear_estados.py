"""semeia os 27 estados (UFs) do Brasil

O .sql cria a tabela estados vazia. As UFs sao dado de referencia fixo (o IBGE
nao muda isso), e todo o restante da cadeia de endereco - cidade, bairro,
localidade, CEP - depende delas. Idempotente: nao duplica se a sigla ja existe
(o indice udx_estados_sigla e unico).

Revision ID: 0002_semear_estados
Revises: 0001_baseline
Create Date: 2026-09-24
"""
from alembic import op

revision = "0002_semear_estados"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None

ESTADOS = [
    ("Acre", "AC"), ("Alagoas", "AL"), ("Amapá", "AP"), ("Amazonas", "AM"),
    ("Bahia", "BA"), ("Ceará", "CE"), ("Distrito Federal", "DF"), ("Espírito Santo", "ES"),
    ("Goiás", "GO"), ("Maranhão", "MA"), ("Mato Grosso", "MT"), ("Mato Grosso do Sul", "MS"),
    ("Minas Gerais", "MG"), ("Pará", "PA"), ("Paraíba", "PB"), ("Paraná", "PR"),
    ("Pernambuco", "PE"), ("Piauí", "PI"), ("Rio de Janeiro", "RJ"), ("Rio Grande do Norte", "RN"),
    ("Rio Grande do Sul", "RS"), ("Rondônia", "RO"), ("Roraima", "RR"), ("Santa Catarina", "SC"),
    ("São Paulo", "SP"), ("Sergipe", "SE"), ("Tocantins", "TO"),
]


def upgrade() -> None:
    for nome, sigla in ESTADOS:
        op.execute(
            f"insert into estados (nome, sigla) values ('{nome}', '{sigla}') "
            "on conflict (sigla) do nothing"
        )


def downgrade() -> None:
    # So remove as UFs que nenhuma cidade usa: apagar as em uso violaria a FK.
    op.execute(
        "delete from estados e where not exists "
        "(select 1 from cidades c where c.estado_id = e.estado_id)"
    )
