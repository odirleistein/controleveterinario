"""enderecos: localidade passa a ser da cidade e o CEP liga a varios bairros/localidades

Antes: estado -> cidade -> bairro -> localidade -> CEP (cadeia, um CEP por
localidade). Isso nao serve para cidade pequena, onde todos os enderecos - de
varios bairros e localidades - dividem o mesmo CEP.

Agora:
  - localidades pertence a uma cidade (cidade_id), nao a um bairro; bairro e
    localidade sao dois cadastros paralelos da cidade;
  - ceps pertence a uma cidade (cidade_id) e se liga a N bairros
    (ceps_bairros) e a N localidades (ceps_localidades). Um CEP pode nao ter
    nenhum dos dois: ai ele so identifica a cidade.

Os dados existentes sao preservados: cada CEP mantem a localidade e o bairro
que tinha. Convencoes de nome iguais as do modelo_ajustado.sql.

Revision ID: 0004_enderecos_cep_nn
Revises: 0003_animal_criador
Create Date: 2026-09-24
"""
from alembic import op

revision = "0004_enderecos_cep_nn"
down_revision = "0003_animal_criador"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Localidade passa a apontar para a cidade (backfill pelo bairro antigo).
    op.execute("alter table localidades add column cidade_id BIGINT null")
    op.execute(
        "update localidades l set cidade_id = b.cidade_id "
        "from bairros b where b.bairro_id = l.bairro_id"
    )
    op.execute("alter table localidades alter column cidade_id set not null")
    op.execute(
        "alter table localidades add constraint fk_localidades_cidade_id_ref_cidades "
        "foreign key (cidade_id) references cidades (cidade_id) "
        "on delete restrict on update restrict"
    )
    op.execute("create index idx_localidades_cidade_id on localidades (cidade_id)")

    # 2. CEP passa a apontar para a cidade.
    op.execute("alter table ceps add column cidade_id BIGINT null")
    op.execute(
        "update ceps c set cidade_id = l.cidade_id "
        "from localidades l where l.localidade_id = c.localidade_id"
    )
    op.execute("alter table ceps alter column cidade_id set not null")
    op.execute(
        "alter table ceps add constraint fk_ceps_cidade_id_ref_cidades "
        "foreign key (cidade_id) references cidades (cidade_id) "
        "on delete restrict on update restrict"
    )
    op.execute("create index idx_ceps_cidade_id on ceps (cidade_id)")

    # 3. Tabelas associativas CEP x bairro e CEP x localidade.
    for tabela, filho, pai in (("ceps_bairros", "bairro", "bairros"), ("ceps_localidades", "localidade", "localidades")):
        pk = f"cep_{filho}_id"
        op.execute(f"create sequence {tabela}_seq")
        op.execute(
            f"""
            create table {tabela} (
               {pk}            BIGINT      not null,
               cep             VARCHAR(8)  not null,
               {filho}_id      BIGINT      not null,
               constraint pk_{tabela} primary key ({pk}),
               constraint fk_{tabela}_cep_ref_ceps foreign key (cep)
                  references ceps (cep) on delete cascade on update cascade,
               constraint fk_{tabela}_{filho}_id_ref_{pai} foreign key ({filho}_id)
                  references {pai} ({filho}_id) on delete restrict on update restrict
            )
            """
        )
        op.execute(f"alter table {tabela} alter column {pk} set default nextval('{tabela}_seq')")
        op.execute(f"alter sequence {tabela}_seq owned by {tabela}.{pk}")
        op.execute(f"create index idx_{tabela}_cep on {tabela} (cep)")
        op.execute(f"create index idx_{tabela}_{filho}_id on {tabela} ({filho}_id)")
        op.execute(f"create unique index udx_{tabela}_cep_{filho}_id on {tabela} (cep, {filho}_id)")

    # 4. Backfill: cada CEP fica ligado a localidade e ao bairro que ja tinha.
    op.execute("insert into ceps_localidades (cep, localidade_id) select cep, localidade_id from ceps")
    op.execute(
        "insert into ceps_bairros (cep, bairro_id) "
        "select distinct c.cep, l.bairro_id from ceps c "
        "join localidades l on l.localidade_id = c.localidade_id"
    )

    # 5. Remove a cadeia antiga (as FKs e indices caem junto com as colunas).
    op.execute("alter table ceps drop column localidade_id")
    op.execute("alter table localidades drop column bairro_id")


def downgrade() -> None:
    # Nao ha volta sem perda: o modelo antigo exige exatamente uma localidade por
    # CEP e um bairro por localidade, e o novo permite varias (ou nenhuma).
    raise NotImplementedError(
        "Downgrade indisponivel: o modelo N:N de CEP nao cabe na cadeia antiga. "
        "Restaure o backup anterior a esta migration."
    )
