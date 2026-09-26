"""reproducao e producao de leite

- reprodutores: cadastro geral (referencia comum, como raca) de touros e vacas
  que aparecem na genealogia. Quase nunca existiram na propriedade, por isso nao
  ficam em `animais`. pai_id/mae_id apontam para a propria tabela, entao avos e
  bisavos saem da cadeia, sem coluna extra.
- animais: pai, mae, peso ao nascimento e observacao.
- tipos_evento: referencia comum semeada aqui. O `codigo` e o que o sistema usa para
  reconhecer o evento (situacao da vaca, prazos); a descricao e so o que se le na tela.
- eventos_reprodutivos: historico da vaca (inseminacao, prenhez, parto...). Uma tabela
  so, com colunas opcionais (reprodutor/valor na inseminacao, cria no parto).
- producoes_leite: um lancamento por animal e data. `dias_referentes` deixa lancar
  o total do mes de uma vez (data do fechamento e 30, por exemplo) sem perder a media.

Situacao, DEL, retorno de cio, secagem e provavel parto sao calculados, nao gravados.

Revision ID: 0009_reproducao_producao
Revises: 0008_pesagens
Create Date: 2026-09-25
"""
from alembic import op

revision = "0009_reproducao_producao"
down_revision = "0008_pesagens"
branch_labels = None
depends_on = None

TIPOS_EVENTO = [
    ("INSEMINACAO", "Inseminação"),
    ("IATF", "IATF"),
    ("RETORNO_CIO", "Retorno de cio"),
    ("PRENHEZ", "Prenhez confirmada"),
    ("SECAGEM", "Secagem"),
    ("PARTO", "Parto"),
    ("ABORTO", "Aborto"),
    ("DESCARTE", "Descarte"),
]


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
    _tabela(
        "reprodutores", "reprodutor_id", "integer",
        """nome varchar(100) not null,
            registro varchar(50) null,
            sexo char(1) not null,
            raca_id integer null,
            empresa varchar(100) null,
            pai_id integer null,
            mae_id integer null,
            ativo boolean not null default true,
            constraint ck_reprodutores_sexo check (sexo in ('M', 'F')),
            constraint fk_reprodutores_raca_id_ref_racas foreign key (raca_id)
                references racas (raca_id) on delete restrict on update restrict,
            constraint fk_reprodutores_pai_id_ref_reprodutores foreign key (pai_id)
                references reprodutores (reprodutor_id) on delete restrict on update restrict,
            constraint fk_reprodutores_mae_id_ref_reprodutores foreign key (mae_id)
                references reprodutores (reprodutor_id) on delete restrict on update restrict""",
    )
    op.execute("create index idx_reprodutores_pai_id on reprodutores (pai_id)")
    op.execute("create index idx_reprodutores_mae_id on reprodutores (mae_id)")

    op.execute("alter table animais add column pai_id integer null")
    op.execute("alter table animais add column mae_id integer null")
    op.execute("alter table animais add column peso_nascimento_kg numeric(7,2) null")
    op.execute("alter table animais add column observacao text null")
    op.execute(
        "alter table animais add constraint fk_animais_pai_id_ref_reprodutores "
        "foreign key (pai_id) references reprodutores (reprodutor_id) on delete restrict on update restrict"
    )
    op.execute(
        "alter table animais add constraint fk_animais_mae_id_ref_reprodutores "
        "foreign key (mae_id) references reprodutores (reprodutor_id) on delete restrict on update restrict"
    )
    op.execute("alter table animais add constraint ck_animais_peso_nascimento check (peso_nascimento_kg > 0)")
    op.execute("create index idx_animais_pai_id on animais (pai_id)")
    op.execute("create index idx_animais_mae_id on animais (mae_id)")

    _tabela(
        "tipos_evento", "tipo_evento_id", "integer",
        """codigo varchar(30) not null,
            descricao varchar(100) not null,
            ativo boolean not null default true""",
    )
    op.execute("create unique index udx_tipos_evento_codigo on tipos_evento (codigo)")
    for codigo, descricao in TIPOS_EVENTO:
        op.execute(f"insert into tipos_evento (codigo, descricao) values ('{codigo}', '{descricao}')")

    _tabela(
        "eventos_reprodutivos", "evento_reprodutivo_id", "bigint",
        """propriedade_id bigint not null,
            animal_id bigint not null,
            tipo_evento_id integer not null,
            data_evento date not null,
            reprodutor_id integer null,
            valor_semen numeric(10,2) null,
            sexo_cria char(1) null,
            cria_animal_id bigint null,
            observacao text null,
            usuario_inclusao_id bigint null,
            constraint ck_eventos_reprodutivos_sexo_cria check (sexo_cria in ('M', 'F')),
            constraint ck_eventos_reprodutivos_valor check (valor_semen >= 0),
            constraint fk_eventos_reprodutivos_propriedade_id_ref_propriedades foreign key (propriedade_id)
                references propriedades (propriedade_id) on delete restrict on update restrict,
            constraint fk_eventos_reprodutivos_animal_id_ref_animais foreign key (animal_id)
                references animais (animal_id) on delete restrict on update restrict,
            constraint fk_eventos_reprodutivos_tipo_evento_id_ref_tipos_evento foreign key (tipo_evento_id)
                references tipos_evento (tipo_evento_id) on delete restrict on update restrict,
            constraint fk_eventos_reprodutivos_reprodutor_id_ref_reprodutores foreign key (reprodutor_id)
                references reprodutores (reprodutor_id) on delete restrict on update restrict,
            constraint fk_eventos_reprodutivos_cria_animal_id_ref_animais foreign key (cria_animal_id)
                references animais (animal_id) on delete restrict on update restrict,
            constraint fk_eventos_reprodutivos_usuario_inclusao_id_ref_usuarios foreign key (usuario_inclusao_id)
                references usuarios (usuario_id) on delete restrict on update restrict""",
    )
    op.execute("create index idx_eventos_reprodutivos_animal_id on eventos_reprodutivos (animal_id, data_evento)")
    op.execute("create index idx_eventos_reprodutivos_propriedade_id on eventos_reprodutivos (propriedade_id)")

    _tabela(
        "producoes_leite", "producao_leite_id", "bigint",
        """propriedade_id bigint not null,
            animal_id bigint not null,
            data_producao date not null,
            litros numeric(8,2) not null,
            dias_referentes smallint not null default 1,
            observacao text null,
            usuario_inclusao_id bigint null,
            constraint ck_producoes_leite_litros check (litros >= 0),
            constraint ck_producoes_leite_dias check (dias_referentes >= 1),
            constraint fk_producoes_leite_propriedade_id_ref_propriedades foreign key (propriedade_id)
                references propriedades (propriedade_id) on delete restrict on update restrict,
            constraint fk_producoes_leite_animal_id_ref_animais foreign key (animal_id)
                references animais (animal_id) on delete restrict on update restrict,
            constraint fk_producoes_leite_usuario_inclusao_id_ref_usuarios foreign key (usuario_inclusao_id)
                references usuarios (usuario_id) on delete restrict on update restrict""",
    )
    op.execute("create unique index udx_producoes_leite_animal_id_data_producao on producoes_leite (animal_id, data_producao)")
    op.execute("create index idx_producoes_leite_propriedade_id on producoes_leite (propriedade_id)")


def downgrade() -> None:
    op.execute("drop table producoes_leite")
    op.execute("drop table eventos_reprodutivos")
    op.execute("drop table tipos_evento")
    for coluna in ("peso_nascimento_kg", "observacao", "pai_id", "mae_id"):
        op.execute(f"alter table animais drop column {coluna}")
    op.execute("drop table reprodutores")
