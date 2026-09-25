"""racas: cadastro de racas e raca opcional no animal

Raca e referencia comum (como o tipo de animal): visivel a todos. O animal pode
ou nao ter raca, por isso a coluna e nula - o cadastro de racas existe por si so
e o vinculo vem depois, animal a animal.

Revision ID: 0007_racas
Revises: 0006_pessoa_criador
Create Date: 2026-09-24
"""
from alembic import op

revision = "0007_racas"
down_revision = "0006_pessoa_criador"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("create sequence racas_seq")
    op.execute(
        """
        create table racas (
            raca_id integer not null,
            descricao varchar(100) not null,
            ativo boolean not null default true,
            constraint pk_racas primary key (raca_id)
        )
        """
    )
    op.execute("alter table racas alter column raca_id set default nextval('racas_seq')")
    op.execute("alter sequence racas_seq owned by racas.raca_id")

    op.execute("alter table animais add column raca_id integer null")
    op.execute(
        "alter table animais add constraint fk_animais_raca_id_ref_racas "
        "foreign key (raca_id) references racas (raca_id) "
        "on delete restrict on update restrict"
    )
    op.execute("create index idx_animais_raca_id on animais (raca_id)")


def downgrade() -> None:
    op.execute("drop index idx_animais_raca_id")
    op.execute("alter table animais drop constraint fk_animais_raca_id_ref_racas")
    op.execute("alter table animais drop column raca_id")
    op.execute("drop table racas")
