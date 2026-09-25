"""pessoas: registra quem cadastrou

Com a propriedade no centro de tudo, quem nao e MASTER so enxerga as pessoas
ligadas as suas propriedades (donos, veterinarios, usuarios com acesso). Uma
pessoa recem-cadastrada ainda nao esta ligada a nenhuma: ate la, so quem a
cadastrou a enxerga - senao nao teria como escolhe-la como proprietaria.

Revision ID: 0006_pessoa_criador
Revises: 0005_pessoa_local
Create Date: 2026-09-24
"""
from alembic import op

revision = "0006_pessoa_criador"
down_revision = "0005_pessoa_local"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("alter table pessoas add column usuario_inclusao_id BIGINT null")
    op.execute(
        "alter table pessoas add constraint fk_pessoas_usuario_inclusao_id_ref_usuarios "
        "foreign key (usuario_inclusao_id) references usuarios (usuario_id) "
        "on delete restrict on update restrict"
    )
    op.execute("create index idx_pessoas_usuario_inclusao_id on pessoas (usuario_inclusao_id)")


def downgrade() -> None:
    op.execute("drop index idx_pessoas_usuario_inclusao_id")
    op.execute("alter table pessoas drop constraint fk_pessoas_usuario_inclusao_id_ref_usuarios")
    op.execute("alter table pessoas drop column usuario_inclusao_id")
