"""pesagens e padroes de peso ideal por raca e idade

- animais.data_nascimento: sem ela nao ha idade em meses, e sem idade nao da para
  comparar o peso real com o ideal.
- padroes_peso: referencia comum (como raca e tipo de animal) com o peso ideal de
  cada raca em cada idade (meses), mais observacoes.
- pesagens: lancamento do peso real de um animal numa data. Guarda a propriedade
  onde foi feito (a propriedade e o centro do acesso), e a API confere que o animal
  pertence a ela.

Revision ID: 0008_pesagens
Revises: 0007_racas
Create Date: 2026-09-24
"""
from alembic import op

revision = "0008_pesagens"
down_revision = "0007_racas"
branch_labels = None
depends_on = None


def _tabela(nome: str, pk: str, tipo_pk: str, colunas: str) -> None:
    op.execute(f"create sequence {nome}_seq")
    op.execute(
        f"""
        create table {nome} (
            {pk} {tipo_pk} not null,
            {colunas},
            constraint pk_{nome} primary key ({pk})
        )
        """
    )
    op.execute(f"alter table {nome} alter column {pk} set default nextval('{nome}_seq')")
    op.execute(f"alter sequence {nome}_seq owned by {nome}.{pk}")


def upgrade() -> None:
    op.execute("alter table animais add column data_nascimento date null")

    _tabela(
        "padroes_peso", "padrao_peso_id", "integer",
        """raca_id integer not null,
            idade_meses smallint not null,
            peso_ideal_kg numeric(7,2) not null,
            observacao text null,
            constraint ck_padroes_peso_idade check (idade_meses >= 0),
            constraint ck_padroes_peso_peso check (peso_ideal_kg > 0),
            constraint fk_padroes_peso_raca_id_ref_racas foreign key (raca_id)
                references racas (raca_id) on delete restrict on update restrict""",
    )
    op.execute("create unique index udx_padroes_peso_raca_id_idade_meses on padroes_peso (raca_id, idade_meses)")

    _tabela(
        "pesagens", "pesagem_id", "bigint",
        """propriedade_id bigint not null,
            animal_id bigint not null,
            data_pesagem date not null,
            peso_kg numeric(7,2) not null,
            observacao text null,
            usuario_inclusao_id bigint null,
            constraint ck_pesagens_peso check (peso_kg > 0),
            constraint fk_pesagens_propriedade_id_ref_propriedades foreign key (propriedade_id)
                references propriedades (propriedade_id) on delete restrict on update restrict,
            constraint fk_pesagens_animal_id_ref_animais foreign key (animal_id)
                references animais (animal_id) on delete restrict on update restrict,
            constraint fk_pesagens_usuario_inclusao_id_ref_usuarios foreign key (usuario_inclusao_id)
                references usuarios (usuario_id) on delete restrict on update restrict""",
    )
    op.execute("create unique index udx_pesagens_animal_id_data_pesagem on pesagens (animal_id, data_pesagem)")
    op.execute("create index idx_pesagens_propriedade_id on pesagens (propriedade_id)")


def downgrade() -> None:
    op.execute("drop table pesagens")
    op.execute("drop table padroes_peso")
    op.execute("alter table animais drop column data_nascimento")
