"""metas_indicadores: meta de cada indicador zootecnico, por propriedade

DEL, intervalo entre partos, idade ao primeiro parto etc. tem uma meta que muda de
granja para granja. Uma tabela chave/valor (propriedade + indicador) evita uma coluna
nova em `propriedades` a cada indicador. Sem linha, vale a meta padrao do sistema
(app/routers/indicadores.py).

Revision ID: 0011_metas_indicadores
Revises: 0010_tipo_produz_leite
Create Date: 2026-09-25
"""
from alembic import op

revision = "0011_metas_indicadores"
down_revision = "0010_tipo_produz_leite"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("create sequence metas_indicadores_seq")
    op.execute(
        """
        create table metas_indicadores (
            meta_indicador_id bigint not null,
            propriedade_id bigint not null,
            indicador varchar(30) not null,
            valor numeric(10,2) not null,
            constraint pk_metas_indicadores primary key (meta_indicador_id),
            constraint ck_metas_indicadores_valor check (valor > 0),
            constraint fk_metas_indicadores_propriedade_id_ref_propriedades foreign key (propriedade_id)
                references propriedades (propriedade_id) on delete restrict on update restrict
        )
        """
    )
    op.execute("alter table metas_indicadores alter column meta_indicador_id set default nextval('metas_indicadores_seq')")
    op.execute("alter sequence metas_indicadores_seq owned by metas_indicadores.meta_indicador_id")
    op.execute(
        "create unique index udx_metas_indicadores_propriedade_id_indicador "
        "on metas_indicadores (propriedade_id, indicador)"
    )


def downgrade() -> None:
    op.execute("drop table metas_indicadores")
