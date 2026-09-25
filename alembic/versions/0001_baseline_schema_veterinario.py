"""baseline do schema do controle veterinario

O schema inicial e criado por schema_bd/modelo_ajustado.sql (rodado uma vez num
banco vazio). Esta revisao nao cria nada: serve so como ponto de partida para
as proximas migrations, e por isso o banco e marcado com "alembic stamp head"
logo depois de aplicar o .sql.

Revision ID: 0001_baseline
Revises:
Create Date: 2026-09-24
"""
from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
