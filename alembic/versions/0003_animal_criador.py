"""animais: registra quem cadastrou

Um animal recem-cadastrado ainda nao esta em nenhuma propriedade, e ate la so
quem o criou pode enxerga-lo (quem nao e MASTER). Sem esta coluna nao ha como
saber de quem e o animal solto.

Revision ID: 0003_animal_criador
Revises: 0002_semear_estados
Create Date: 2026-09-24
"""
from alembic import op

revision = "0003_animal_criador"
down_revision = "0002_semear_estados"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("alter table animais add column usuario_inclusao_id BIGINT null")
    op.execute(
        "alter table animais add constraint fk_animais_usuario_inclusao_id_ref_usuarios "
        "foreign key (usuario_inclusao_id) references usuarios (usuario_id) "
        "on delete restrict on update restrict"
    )
    op.execute("create index idx_animais_usuario_inclusao_id on animais (usuario_inclusao_id)")


def downgrade() -> None:
    op.execute("drop index idx_animais_usuario_inclusao_id")
    op.execute("alter table animais drop constraint fk_animais_usuario_inclusao_id_ref_usuarios")
    op.execute("alter table animais drop column usuario_inclusao_id")
