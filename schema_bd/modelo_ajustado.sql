/*==============================================================*/
/* Convenções aplicadas:                                        */
/*  - Tabelas no plural (cidade -> cidades)                      */
/*  - PK: pk_<nometabela>                                        */
/*  - Sequence própria por tabela: <nometabela>_seq, ligada via   */
/*    DEFAULT nextval() + OWNED BY (em vez de SERIAL/BIGSERIAL)   */
/*  - FK: fk_<nometabela>_<coluna>_ref_<tabelapai> (max 63 chars) */
/*  - Índice comum: idx_<nometabela>_<coluna(s)>                  */
/*  - Índice único: udx_<nometabela>_<coluna(s)>                  */
/*  - Check constraint: ck_<nometabela>_<coluna>                  */
/*==============================================================*/

/*==============================================================*/
/* Tabela: estados                                               */
/*==============================================================*/
create sequence estados_seq;

create table estados (
   estado_id            INT4                 not null,
   nome                 VARCHAR(100)         not null,
   sigla                VARCHAR(2)           not null,
   constraint pk_estados primary key (estado_id)
);

alter table estados alter column estado_id set default nextval('estados_seq');
alter sequence estados_seq owned by estados.estado_id;

create unique index udx_estados_sigla on estados (sigla);

/*==============================================================*/
/* Tabela: cidades                                               */
/*==============================================================*/
create sequence cidades_seq;

create table cidades (
   cidade_id            BIGINT               not null,
   estado_id            INT4                 not null,
   nome                 VARCHAR(100)         not null,
   codigo_ibge          INT4                 null,
   ativa                BOOL                 not null default true,
   constraint pk_cidades primary key (cidade_id),
   constraint fk_cidades_estado_id_ref_estados foreign key (estado_id)
      references estados (estado_id)
      on delete restrict on update restrict
);

alter table cidades alter column cidade_id set default nextval('cidades_seq');
alter sequence cidades_seq owned by cidades.cidade_id;

create index idx_cidades_estado_id on cidades (estado_id);

/*==============================================================*/
/* Tabela: bairros                                               */
/*==============================================================*/
create sequence bairros_seq;

create table bairros (
   bairro_id            BIGINT               not null,
   cidade_id            BIGINT               not null,
   nome                 VARCHAR(100)         not null,
   ativo                BOOL                 not null default true,
   constraint pk_bairros primary key (bairro_id),
   constraint fk_bairros_cidade_id_ref_cidades foreign key (cidade_id)
      references cidades (cidade_id)
      on delete restrict on update restrict
);

alter table bairros alter column bairro_id set default nextval('bairros_seq');
alter sequence bairros_seq owned by bairros.bairro_id;

create index idx_bairros_cidade_id on bairros (cidade_id);

/*==============================================================*/
/* Tabela: localidades                                           */
/* Sub-área dentro de um bairro (útil para zona rural: linhas,    */
/* distritos, comunidades).                                       */
/*==============================================================*/
create sequence localidades_seq;

create table localidades (
   localidade_id        BIGINT               not null,
   bairro_id            BIGINT               not null,
   nome                 VARCHAR(100)         not null,
   ativa                BOOL                 not null default true,
   constraint pk_localidades primary key (localidade_id),
   constraint fk_localidades_bairro_id_ref_bairros foreign key (bairro_id)
      references bairros (bairro_id)
      on delete restrict on update restrict
);

alter table localidades alter column localidade_id set default nextval('localidades_seq');
alter sequence localidades_seq owned by localidades.localidade_id;

create index idx_localidades_bairro_id on localidades (bairro_id);

/*==============================================================*/
/* Tabela: ceps                                                  */
/* Chave natural (o próprio CEP) — sem sequence. Aponta para       */
/* localidades (nível mais granular); cidade/estado vêm via join   */
/* na cadeia localidades -> bairros -> cidades -> estados.         */
/*==============================================================*/
create table ceps (
   cep                  VARCHAR(8)           not null,
   localidade_id        BIGINT               not null,
   constraint pk_ceps primary key (cep),
   constraint fk_ceps_localidade_id_ref_localidades foreign key (localidade_id)
      references localidades (localidade_id)
      on delete restrict on update restrict
);

create index idx_ceps_localidade_id on ceps (localidade_id);

/*==============================================================*/
/* Tabela: papeis                                                 */
/* Controle de acesso por papel: MASTER (administrador do          */
/* sistema), ADMIN (gerencia cadastros) e VISUALIZADOR             */
/* (somente leitura). Um usuário tem exatamente um papel.          */
/*==============================================================*/
create sequence papeis_seq;

create table papeis (
   papel_id             INT4                 not null,
   nome                 VARCHAR(50)          not null,
   descricao            VARCHAR(150)         null,
   ativo                BOOL                 not null default true,
   constraint pk_papeis primary key (papel_id)
);

alter table papeis alter column papel_id set default nextval('papeis_seq');
alter sequence papeis_seq owned by papeis.papel_id;

create unique index udx_papeis_nome on papeis (nome);

insert into papeis (papel_id, nome, descricao) values
   (1, 'MASTER', 'Administrador master do sistema — acesso total, inclusive configurações'),
   (2, 'ADMIN', 'Usuário administrativo — gerencia cadastros do dia a dia'),
   (3, 'VISUALIZADOR', 'Acesso somente para consulta/visualização');

select setval('papeis_seq', 3, true);

/*==============================================================*/
/* Tabela: pessoas                                                */
/* Supertipo: dados comuns a pessoa física e jurídica.             */
/* Identidade central do sistema — veterinários, donos de           */
/* propriedade e usuários passam a referenciar esta tabela.        */
/* tipo_pessoa: 'F' = física, 'J' = jurídica.                      */
/*==============================================================*/
create sequence pessoas_seq;

create table pessoas (
   pessoa_id            BIGINT                    not null,
   tipo_pessoa          CHAR(1)                   not null,
   nome                 VARCHAR(150)              not null,
   email                VARCHAR(150)              null,
   cep                  VARCHAR(8)                null,
   endereco             VARCHAR(100)              null,
   numero               VARCHAR(15)               null,
   complemento          VARCHAR(100)              null,
   ativo                BOOL                      not null default true,
   data_inclusao        TIMESTAMP WITH TIME ZONE  not null default now(),
   data_alteracao       TIMESTAMP WITH TIME ZONE  not null default now(),
   constraint pk_pessoas primary key (pessoa_id),
   constraint fk_pessoas_cep_ref_ceps foreign key (cep)
      references ceps (cep)
      on delete restrict on update restrict,
   constraint ck_pessoas_tipo_pessoa check (tipo_pessoa in ('F','J'))
);

alter table pessoas alter column pessoa_id set default nextval('pessoas_seq');
alter sequence pessoas_seq owned by pessoas.pessoa_id;

create index idx_pessoas_cep on pessoas (cep);
create unique index udx_pessoas_email on pessoas (email);

/*==============================================================*/
/* Tabela: pessoas_fisicas                                        */
/* Subtipo de pessoas. pessoa_id é PK e FK ao mesmo tempo          */
/* (relação identificadora, sem sequence própria). CPF fica         */
/* opcional por enquanto (cadastro não obrigatório ainda).         */
/*==============================================================*/
create table pessoas_fisicas (
   pessoa_id            BIGINT               not null,
   cpf                  VARCHAR(11)          null,
   data_nascimento      DATE                 null,
   constraint pk_pessoas_fisicas primary key (pessoa_id),
   constraint fk_pessoas_fisicas_pessoa_id_ref_pessoas foreign key (pessoa_id)
      references pessoas (pessoa_id)
      on delete cascade on update cascade
);

create unique index udx_pessoas_fisicas_cpf on pessoas_fisicas (cpf);

/*==============================================================*/
/* Tabela: pessoas_juridicas                                      */
/* Subtipo de pessoas. CNPJ opcional por enquanto (cadastro         */
/* não obrigatório ainda).                                          */
/*==============================================================*/
create table pessoas_juridicas (
   pessoa_id            BIGINT               not null,
   cnpj                 VARCHAR(14)          null,
   razao_social         VARCHAR(150)         not null,
   nome_fantasia        VARCHAR(150)         null,
   data_fundacao        DATE                 null,
   constraint pk_pessoas_juridicas primary key (pessoa_id),
   constraint fk_pessoas_juridicas_pessoa_id_ref_pessoas foreign key (pessoa_id)
      references pessoas (pessoa_id)
      on delete cascade on update cascade
);

create unique index udx_pessoas_juridicas_cnpj on pessoas_juridicas (cnpj);

/*==============================================================*/
/* Tabela: pessoas_telefones                                      */
/* Uma pessoa pode ter 1 ou mais telefones de contato.             */
/*==============================================================*/
create sequence pessoas_telefones_seq;

create table pessoas_telefones (
   pessoa_telefone_id   BIGINT               not null,
   pessoa_id            BIGINT               not null,
   numero               VARCHAR(20)          not null,
   tipo_telefone        VARCHAR(20)          null,
   principal            BOOL                 not null default false,
   constraint pk_pessoas_telefones primary key (pessoa_telefone_id),
   constraint fk_pessoas_telefones_pessoa_id_ref_pessoas foreign key (pessoa_id)
      references pessoas (pessoa_id)
      on delete cascade on update cascade
);

alter table pessoas_telefones alter column pessoa_telefone_id set default nextval('pessoas_telefones_seq');
alter sequence pessoas_telefones_seq owned by pessoas_telefones.pessoa_telefone_id;

create index idx_pessoas_telefones_pessoa_id on pessoas_telefones (pessoa_id);
-- garante no máximo um telefone marcado como principal por pessoa
create unique index udx_pessoas_telefones_pessoa_id_principal on pessoas_telefones (pessoa_id) where principal = true;

/*==============================================================*/
/* Tabela: usuarios                                              */
/* (login / autenticação). pessoa_id (nullable): vincula o login  */
/* à identidade real da pessoa; fica nulo para contas de serviço. */
/* papel_id: nível de acesso do usuário no sistema.                */
/*==============================================================*/
create sequence usuarios_seq;

create table usuarios (
   usuario_id           BIGINT                    not null,
   pessoa_id            BIGINT                    null,
   papel_id             INT4                      not null,
   nome                 VARCHAR(150)              not null,
   email                VARCHAR(150)              not null,
   senha_hash           VARCHAR(255)              not null,
   ativo                BOOL                      not null default true,
   data_inclusao        TIMESTAMP WITH TIME ZONE  not null default now(),
   data_alteracao       TIMESTAMP WITH TIME ZONE  not null default now(),
   constraint pk_usuarios primary key (usuario_id),
   constraint fk_usuarios_pessoa_id_ref_pessoas foreign key (pessoa_id)
      references pessoas (pessoa_id)
      on delete restrict on update restrict,
   constraint fk_usuarios_papel_id_ref_papeis foreign key (papel_id)
      references papeis (papel_id)
      on delete restrict on update restrict
);

alter table usuarios alter column usuario_id set default nextval('usuarios_seq');
alter sequence usuarios_seq owned by usuarios.usuario_id;

create unique index udx_usuarios_email on usuarios (email);
create index idx_usuarios_pessoa_id on usuarios (pessoa_id);
create unique index udx_usuarios_pessoa_id on usuarios (pessoa_id);
create index idx_usuarios_papel_id on usuarios (papel_id);

/*==============================================================*/
/* Tabela: tipos_animal                                          */
/*==============================================================*/
create sequence tipos_animal_seq;

create table tipos_animal (
   tipo_animal_id       INT4                 not null,
   descricao            VARCHAR(100)         not null,
   ativo                BOOL                 not null default true,
   constraint pk_tipos_animal primary key (tipo_animal_id)
);

alter table tipos_animal alter column tipo_animal_id set default nextval('tipos_animal_seq');
alter sequence tipos_animal_seq owned by tipos_animal.tipo_animal_id;

/*==============================================================*/
/* Tabela: animais                                               */
/*==============================================================*/
create sequence animais_seq;

create table animais (
   animal_id            BIGINT               not null,
   tipo_animal_id       INT4                 not null,
   codigo               VARCHAR(30)          null,
   nome                 VARCHAR(100)         not null,
   ativo                BOOL                 not null default true,
   constraint pk_animais primary key (animal_id),
   constraint fk_animais_tipo_animal_id_ref_tipos_animal foreign key (tipo_animal_id)
      references tipos_animal (tipo_animal_id)
      on delete restrict on update restrict
);

alter table animais alter column animal_id set default nextval('animais_seq');
alter sequence animais_seq owned by animais.animal_id;

create index idx_animais_tipo_animal_id on animais (tipo_animal_id);

/*==============================================================*/
/* Tabela: propriedades                                          */
/* proprietario_pessoa_id: dono da propriedade (pessoa física ou   */
/* jurídica).                                                      */
/*==============================================================*/
create sequence propriedades_seq;

create table propriedades (
   propriedade_id         BIGINT             not null,
   proprietario_pessoa_id BIGINT             not null,
   cep                    VARCHAR(8)         not null,
   nome                   VARCHAR(100)       not null,
   ativa                  BOOL               not null default true,
   endereco               VARCHAR(100)       null,
   numero                 VARCHAR(15)        null,
   complemento            VARCHAR(100)       null,
   constraint pk_propriedades primary key (propriedade_id),
   constraint fk_propriedades_proprietario_pessoa_id_ref_pessoas foreign key (proprietario_pessoa_id)
      references pessoas (pessoa_id)
      on delete restrict on update restrict,
   constraint fk_propriedades_cep_ref_ceps foreign key (cep)
      references ceps (cep)
      on delete restrict on update restrict
);

alter table propriedades alter column propriedade_id set default nextval('propriedades_seq');
alter sequence propriedades_seq owned by propriedades.propriedade_id;

create index idx_propriedades_proprietario_pessoa_id on propriedades (proprietario_pessoa_id);
create index idx_propriedades_cep on propriedades (cep);

/*==============================================================*/
/* Tabela: propriedades_animais (associativa)                    */
/*==============================================================*/
create sequence propriedades_animais_seq;

create table propriedades_animais (
   propriedade_animal_id BIGINT              not null,
   propriedade_id         BIGINT             not null,
   animal_id              BIGINT             not null,
   constraint pk_propriedades_animais primary key (propriedade_animal_id),
   constraint fk_propriedades_animais_propriedade_id_ref_propriedades foreign key (propriedade_id)
      references propriedades (propriedade_id)
      on delete restrict on update restrict,
   constraint fk_propriedades_animais_animal_id_ref_animais foreign key (animal_id)
      references animais (animal_id)
      on delete restrict on update restrict
);

alter table propriedades_animais alter column propriedade_animal_id set default nextval('propriedades_animais_seq');
alter sequence propriedades_animais_seq owned by propriedades_animais.propriedade_animal_id;

create index idx_propriedades_animais_propriedade_id on propriedades_animais (propriedade_id);
create index idx_propriedades_animais_animal_id on propriedades_animais (animal_id);
create unique index udx_propriedades_animais_propriedade_id_animal_id on propriedades_animais (propriedade_id, animal_id);

/*==============================================================*/
/* Tabela: veterinarios                                          */
/* Agora é apenas o "papel" profissional: os dados pessoais        */
/* (nome, endereço, telefone) vêm de pessoas / pessoas_telefones.  */
/* pessoa_id: identidade real do veterinário (obrigatório).        */
/* usuario_id: login do veterinário — agora obrigatório, todo       */
/* veterinário precisa acessar o sistema.                          */
/*==============================================================*/
create sequence veterinarios_seq;

create table veterinarios (
   veterinario_id       BIGINT               not null,
   pessoa_id            BIGINT               not null,
   usuario_id           BIGINT               not null,
   ativo                BOOL                 not null default true,
   constraint pk_veterinarios primary key (veterinario_id),
   constraint fk_veterinarios_pessoa_id_ref_pessoas foreign key (pessoa_id)
      references pessoas (pessoa_id)
      on delete restrict on update restrict,
   constraint fk_veterinarios_usuario_id_ref_usuarios foreign key (usuario_id)
      references usuarios (usuario_id)
      on delete restrict on update restrict
);

alter table veterinarios alter column veterinario_id set default nextval('veterinarios_seq');
alter sequence veterinarios_seq owned by veterinarios.veterinario_id;

create index idx_veterinarios_pessoa_id on veterinarios (pessoa_id);
create unique index udx_veterinarios_pessoa_id on veterinarios (pessoa_id);
create index idx_veterinarios_usuario_id on veterinarios (usuario_id);
create unique index udx_veterinarios_usuario_id on veterinarios (usuario_id);

/*==============================================================*/
/* Tabela: veterinarios_propriedades (associativa)                */
/* Controle de acesso: um veterinário enxerga todas as             */
/* propriedades que atende, via este vínculo.                     */
/*==============================================================*/
create sequence veterinarios_propriedades_seq;

create table veterinarios_propriedades (
   veterinario_propriedade_id BIGINT         not null,
   veterinario_id              BIGINT        not null,
   propriedade_id              BIGINT        not null,
   constraint pk_veterinarios_propriedades primary key (veterinario_propriedade_id),
   constraint fk_veterinarios_propriedades_veterinario_id_ref_veterinarios foreign key (veterinario_id)
      references veterinarios (veterinario_id)
      on delete restrict on update restrict,
   constraint fk_veterinarios_propriedades_propriedade_id_ref_propriedades foreign key (propriedade_id)
      references propriedades (propriedade_id)
      on delete restrict on update restrict
);

alter table veterinarios_propriedades alter column veterinario_propriedade_id set default nextval('veterinarios_propriedades_seq');
alter sequence veterinarios_propriedades_seq owned by veterinarios_propriedades.veterinario_propriedade_id;

create index idx_veterinarios_propriedades_veterinario_id on veterinarios_propriedades (veterinario_id);
create index idx_veterinarios_propriedades_propriedade_id on veterinarios_propriedades (propriedade_id);
create unique index udx_veterinarios_propriedades_veterinario_id_propriedade_id on veterinarios_propriedades (veterinario_id, propriedade_id);

/*==============================================================*/
/* Tabela: propriedades_usuarios (associativa)                    */
/* Controle de acesso (login): quais usuarios podem acessar        */
/* quais propriedades — inclui o dono, mas pode incluir outras     */
/* pessoas autorizadas (ex.: um familiar com login próprio).       */
/*==============================================================*/
create sequence propriedades_usuarios_seq;

create table propriedades_usuarios (
   propriedade_usuario_id BIGINT             not null,
   usuario_id              BIGINT            not null,
   propriedade_id          BIGINT            not null,
   constraint pk_propriedades_usuarios primary key (propriedade_usuario_id),
   constraint fk_propriedades_usuarios_usuario_id_ref_usuarios foreign key (usuario_id)
      references usuarios (usuario_id)
      on delete restrict on update restrict,
   constraint fk_propriedades_usuarios_propriedade_id_ref_propriedades foreign key (propriedade_id)
      references propriedades (propriedade_id)
      on delete restrict on update restrict
);

alter table propriedades_usuarios alter column propriedade_usuario_id set default nextval('propriedades_usuarios_seq');
alter sequence propriedades_usuarios_seq owned by propriedades_usuarios.propriedade_usuario_id;

create index idx_propriedades_usuarios_usuario_id on propriedades_usuarios (usuario_id);
create index idx_propriedades_usuarios_propriedade_id on propriedades_usuarios (propriedade_id);
create unique index udx_propriedades_usuarios_usuario_id_propriedade_id on propriedades_usuarios (usuario_id, propriedade_id);
