"""pessoas: bairro ou localidade do endereco

O CEP sozinho nao diz onde a pessoa mora: em cidade pequena o mesmo CEP cobre
varios bairros e localidades (ver 0004). A pessoa passa a guardar QUAL deles e o
dela - um bairro OU uma localidade, nunca os dois (ck_pessoas_bairro_localidade).
Que o escolhido pertence ao CEP da pessoa e validado pela API; o banco garante
so a existencia e a exclusividade.

Revision ID: 0005_pessoa_local
Revises: 0004_enderecos_cep_nn
Create Date: 2026-09-24
"""
from alembic import op

revision = "0005_pessoa_local"
down_revision = "0004_enderecos_cep_nn"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("alter table pessoas add column bairro_id BIGINT null")
    op.execute("alter table pessoas add column localidade_id BIGINT null")
    op.execute(
        "alter table pessoas add constraint fk_pessoas_bairro_id_ref_bairros "
        "foreign key (bairro_id) references bairros (bairro_id) "
        "on delete restrict on update restrict"
    )
    op.execute(
        "alter table pessoas add constraint fk_pessoas_localidade_id_ref_localidades "
        "foreign key (localidade_id) references localidades (localidade_id) "
        "on delete restrict on update restrict"
    )
    op.execute(
        "alter table pessoas add constraint ck_pessoas_bairro_localidade "
        "check (bairro_id is null or localidade_id is null)"
    )
    op.execute("create index idx_pessoas_bairro_id on pessoas (bairro_id)")
    op.execute("create index idx_pessoas_localidade_id on pessoas (localidade_id)")


def downgrade() -> None:
    op.execute("drop index idx_pessoas_localidade_id")
    op.execute("drop index idx_pessoas_bairro_id")
    op.execute("alter table pessoas drop constraint ck_pessoas_bairro_localidade")
    op.execute("alter table pessoas drop column localidade_id")
    op.execute("alter table pessoas drop column bairro_id")
