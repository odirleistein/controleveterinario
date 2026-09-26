"""tipos_animal: marca quais tipos produzem leite

A producao de leite so faz sentido para alguns tipos (vacas; nao terneiras nem
novilhas). Em vez de o sistema fixar o nome ou o id de "Vacas", o tipo diz se
produz leite: a tela de producao so oferece esses tipos e a API recusa o resto.
Quem cadastrar outro tipo produtor (ex.: cabras) so marca a caixa.

Revision ID: 0010_tipo_produz_leite
Revises: 0009_reproducao_producao
Create Date: 2026-09-25
"""
from alembic import op

revision = "0010_tipo_produz_leite"
down_revision = "0009_reproducao_producao"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("alter table tipos_animal add column produz_leite boolean not null default false")
    # Os tipos ja cadastrados: so "Vacas" produz. Comparacao sem depender de maiusculas.
    op.execute("update tipos_animal set produz_leite = true where lower(descricao) = 'vacas'")


def downgrade() -> None:
    op.execute("alter table tipos_animal drop column produz_leite")
