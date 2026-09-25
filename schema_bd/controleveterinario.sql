--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2
-- Dumped by pg_dump version 17.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: animais; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.animais (
    animal_id bigint NOT NULL,
    tipo_animal_id integer NOT NULL,
    codigo character varying(30),
    nome character varying(100) NOT NULL,
    ativo boolean DEFAULT true NOT NULL,
    usuario_inclusao_id bigint
);


--
-- Name: animais_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.animais_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: animais_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.animais_seq OWNED BY public.animais.animal_id;


--
-- Name: bairros; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bairros (
    bairro_id bigint NOT NULL,
    cidade_id bigint NOT NULL,
    nome character varying(100) NOT NULL,
    ativo boolean DEFAULT true NOT NULL
);


--
-- Name: bairros_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bairros_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bairros_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bairros_seq OWNED BY public.bairros.bairro_id;


--
-- Name: ceps; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ceps (
    cep character varying(8) NOT NULL,
    cidade_id bigint NOT NULL
);


--
-- Name: ceps_bairros; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ceps_bairros (
    cep_bairro_id bigint NOT NULL,
    cep character varying(8) NOT NULL,
    bairro_id bigint NOT NULL
);


--
-- Name: ceps_bairros_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ceps_bairros_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ceps_bairros_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ceps_bairros_seq OWNED BY public.ceps_bairros.cep_bairro_id;


--
-- Name: ceps_localidades; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ceps_localidades (
    cep_localidade_id bigint NOT NULL,
    cep character varying(8) NOT NULL,
    localidade_id bigint NOT NULL
);


--
-- Name: ceps_localidades_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ceps_localidades_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ceps_localidades_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ceps_localidades_seq OWNED BY public.ceps_localidades.cep_localidade_id;


--
-- Name: cidades; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cidades (
    cidade_id bigint NOT NULL,
    estado_id integer NOT NULL,
    nome character varying(100) NOT NULL,
    codigo_ibge integer,
    ativa boolean DEFAULT true NOT NULL
);


--
-- Name: cidades_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cidades_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cidades_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cidades_seq OWNED BY public.cidades.cidade_id;


--
-- Name: estados; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.estados (
    estado_id integer NOT NULL,
    nome character varying(100) NOT NULL,
    sigla character varying(2) NOT NULL
);


--
-- Name: estados_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.estados_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: estados_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.estados_seq OWNED BY public.estados.estado_id;


--
-- Name: localidades; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.localidades (
    localidade_id bigint NOT NULL,
    nome character varying(100) NOT NULL,
    ativa boolean DEFAULT true NOT NULL,
    cidade_id bigint NOT NULL
);


--
-- Name: localidades_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.localidades_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: localidades_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.localidades_seq OWNED BY public.localidades.localidade_id;


--
-- Name: papeis; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.papeis (
    papel_id integer NOT NULL,
    nome character varying(50) NOT NULL,
    descricao character varying(150),
    ativo boolean DEFAULT true NOT NULL
);


--
-- Name: papeis_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.papeis_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: papeis_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.papeis_seq OWNED BY public.papeis.papel_id;


--
-- Name: pessoas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pessoas (
    pessoa_id bigint NOT NULL,
    tipo_pessoa character(1) NOT NULL,
    nome character varying(150) NOT NULL,
    email character varying(150),
    cep character varying(8),
    endereco character varying(100),
    numero character varying(15),
    complemento character varying(100),
    ativo boolean DEFAULT true NOT NULL,
    data_inclusao timestamp with time zone DEFAULT now() NOT NULL,
    data_alteracao timestamp with time zone DEFAULT now() NOT NULL,
    bairro_id bigint,
    localidade_id bigint,
    CONSTRAINT ck_pessoas_bairro_localidade CHECK (((bairro_id IS NULL) OR (localidade_id IS NULL))),
    CONSTRAINT ck_pessoas_tipo_pessoa CHECK ((tipo_pessoa = ANY (ARRAY['F'::bpchar, 'J'::bpchar])))
);


--
-- Name: pessoas_fisicas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pessoas_fisicas (
    pessoa_id bigint NOT NULL,
    cpf character varying(11),
    data_nascimento date
);


--
-- Name: pessoas_juridicas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pessoas_juridicas (
    pessoa_id bigint NOT NULL,
    cnpj character varying(14),
    razao_social character varying(150) NOT NULL,
    nome_fantasia character varying(150),
    data_fundacao date
);


--
-- Name: pessoas_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.pessoas_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pessoas_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.pessoas_seq OWNED BY public.pessoas.pessoa_id;


--
-- Name: pessoas_telefones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pessoas_telefones (
    pessoa_telefone_id bigint NOT NULL,
    pessoa_id bigint NOT NULL,
    numero character varying(20) NOT NULL,
    tipo_telefone character varying(20),
    principal boolean DEFAULT false NOT NULL
);


--
-- Name: pessoas_telefones_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.pessoas_telefones_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pessoas_telefones_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.pessoas_telefones_seq OWNED BY public.pessoas_telefones.pessoa_telefone_id;


--
-- Name: propriedades; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.propriedades (
    propriedade_id bigint NOT NULL,
    proprietario_pessoa_id bigint NOT NULL,
    cep character varying(8) NOT NULL,
    nome character varying(100) NOT NULL,
    ativa boolean DEFAULT true NOT NULL,
    endereco character varying(100),
    numero character varying(15),
    complemento character varying(100)
);


--
-- Name: propriedades_animais; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.propriedades_animais (
    propriedade_animal_id bigint NOT NULL,
    propriedade_id bigint NOT NULL,
    animal_id bigint NOT NULL
);


--
-- Name: propriedades_animais_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.propriedades_animais_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: propriedades_animais_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.propriedades_animais_seq OWNED BY public.propriedades_animais.propriedade_animal_id;


--
-- Name: propriedades_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.propriedades_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: propriedades_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.propriedades_seq OWNED BY public.propriedades.propriedade_id;


--
-- Name: propriedades_usuarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.propriedades_usuarios (
    propriedade_usuario_id bigint NOT NULL,
    usuario_id bigint NOT NULL,
    propriedade_id bigint NOT NULL
);


--
-- Name: propriedades_usuarios_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.propriedades_usuarios_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: propriedades_usuarios_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.propriedades_usuarios_seq OWNED BY public.propriedades_usuarios.propriedade_usuario_id;


--
-- Name: tipos_animal; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tipos_animal (
    tipo_animal_id integer NOT NULL,
    descricao character varying(100) NOT NULL,
    ativo boolean DEFAULT true NOT NULL
);


--
-- Name: tipos_animal_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tipos_animal_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tipos_animal_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tipos_animal_seq OWNED BY public.tipos_animal.tipo_animal_id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuarios (
    usuario_id bigint NOT NULL,
    pessoa_id bigint,
    papel_id integer NOT NULL,
    nome character varying(150) NOT NULL,
    email character varying(150) NOT NULL,
    senha_hash character varying(255) NOT NULL,
    ativo boolean DEFAULT true NOT NULL,
    data_inclusao timestamp with time zone DEFAULT now() NOT NULL,
    data_alteracao timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: usuarios_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.usuarios_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: usuarios_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.usuarios_seq OWNED BY public.usuarios.usuario_id;


--
-- Name: veterinarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.veterinarios (
    veterinario_id bigint NOT NULL,
    pessoa_id bigint NOT NULL,
    usuario_id bigint NOT NULL,
    ativo boolean DEFAULT true NOT NULL
);


--
-- Name: veterinarios_propriedades; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.veterinarios_propriedades (
    veterinario_propriedade_id bigint NOT NULL,
    veterinario_id bigint NOT NULL,
    propriedade_id bigint NOT NULL
);


--
-- Name: veterinarios_propriedades_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.veterinarios_propriedades_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: veterinarios_propriedades_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.veterinarios_propriedades_seq OWNED BY public.veterinarios_propriedades.veterinario_propriedade_id;


--
-- Name: veterinarios_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.veterinarios_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: veterinarios_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.veterinarios_seq OWNED BY public.veterinarios.veterinario_id;


--
-- Name: animais animal_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.animais ALTER COLUMN animal_id SET DEFAULT nextval('public.animais_seq'::regclass);


--
-- Name: bairros bairro_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bairros ALTER COLUMN bairro_id SET DEFAULT nextval('public.bairros_seq'::regclass);


--
-- Name: ceps_bairros cep_bairro_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ceps_bairros ALTER COLUMN cep_bairro_id SET DEFAULT nextval('public.ceps_bairros_seq'::regclass);


--
-- Name: ceps_localidades cep_localidade_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ceps_localidades ALTER COLUMN cep_localidade_id SET DEFAULT nextval('public.ceps_localidades_seq'::regclass);


--
-- Name: cidades cidade_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cidades ALTER COLUMN cidade_id SET DEFAULT nextval('public.cidades_seq'::regclass);


--
-- Name: estados estado_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estados ALTER COLUMN estado_id SET DEFAULT nextval('public.estados_seq'::regclass);


--
-- Name: localidades localidade_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.localidades ALTER COLUMN localidade_id SET DEFAULT nextval('public.localidades_seq'::regclass);


--
-- Name: papeis papel_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.papeis ALTER COLUMN papel_id SET DEFAULT nextval('public.papeis_seq'::regclass);


--
-- Name: pessoas pessoa_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pessoas ALTER COLUMN pessoa_id SET DEFAULT nextval('public.pessoas_seq'::regclass);


--
-- Name: pessoas_telefones pessoa_telefone_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pessoas_telefones ALTER COLUMN pessoa_telefone_id SET DEFAULT nextval('public.pessoas_telefones_seq'::regclass);


--
-- Name: propriedades propriedade_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propriedades ALTER COLUMN propriedade_id SET DEFAULT nextval('public.propriedades_seq'::regclass);


--
-- Name: propriedades_animais propriedade_animal_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propriedades_animais ALTER COLUMN propriedade_animal_id SET DEFAULT nextval('public.propriedades_animais_seq'::regclass);


--
-- Name: propriedades_usuarios propriedade_usuario_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propriedades_usuarios ALTER COLUMN propriedade_usuario_id SET DEFAULT nextval('public.propriedades_usuarios_seq'::regclass);


--
-- Name: tipos_animal tipo_animal_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipos_animal ALTER COLUMN tipo_animal_id SET DEFAULT nextval('public.tipos_animal_seq'::regclass);


--
-- Name: usuarios usuario_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN usuario_id SET DEFAULT nextval('public.usuarios_seq'::regclass);


--
-- Name: veterinarios veterinario_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.veterinarios ALTER COLUMN veterinario_id SET DEFAULT nextval('public.veterinarios_seq'::regclass);


--
-- Name: veterinarios_propriedades veterinario_propriedade_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.veterinarios_propriedades ALTER COLUMN veterinario_propriedade_id SET DEFAULT nextval('public.veterinarios_propriedades_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: animais pk_animais; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.animais
    ADD CONSTRAINT pk_animais PRIMARY KEY (animal_id);


--
-- Name: bairros pk_bairros; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bairros
    ADD CONSTRAINT pk_bairros PRIMARY KEY (bairro_id);


--
-- Name: ceps pk_ceps; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ceps
    ADD CONSTRAINT pk_ceps PRIMARY KEY (cep);


--
-- Name: ceps_bairros pk_ceps_bairros; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ceps_bairros
    ADD CONSTRAINT pk_ceps_bairros PRIMARY KEY (cep_bairro_id);


--
-- Name: ceps_localidades pk_ceps_localidades; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ceps_localidades
    ADD CONSTRAINT pk_ceps_localidades PRIMARY KEY (cep_localidade_id);


--
-- Name: cidades pk_cidades; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cidades
    ADD CONSTRAINT pk_cidades PRIMARY KEY (cidade_id);


--
-- Name: estados pk_estados; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estados
    ADD CONSTRAINT pk_estados PRIMARY KEY (estado_id);


--
-- Name: localidades pk_localidades; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.localidades
    ADD CONSTRAINT pk_localidades PRIMARY KEY (localidade_id);


--
-- Name: papeis pk_papeis; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.papeis
    ADD CONSTRAINT pk_papeis PRIMARY KEY (papel_id);


--
-- Name: pessoas pk_pessoas; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pessoas
    ADD CONSTRAINT pk_pessoas PRIMARY KEY (pessoa_id);


--
-- Name: pessoas_fisicas pk_pessoas_fisicas; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pessoas_fisicas
    ADD CONSTRAINT pk_pessoas_fisicas PRIMARY KEY (pessoa_id);


--
-- Name: pessoas_juridicas pk_pessoas_juridicas; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pessoas_juridicas
    ADD CONSTRAINT pk_pessoas_juridicas PRIMARY KEY (pessoa_id);


--
-- Name: pessoas_telefones pk_pessoas_telefones; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pessoas_telefones
    ADD CONSTRAINT pk_pessoas_telefones PRIMARY KEY (pessoa_telefone_id);


--
-- Name: propriedades pk_propriedades; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propriedades
    ADD CONSTRAINT pk_propriedades PRIMARY KEY (propriedade_id);


--
-- Name: propriedades_animais pk_propriedades_animais; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propriedades_animais
    ADD CONSTRAINT pk_propriedades_animais PRIMARY KEY (propriedade_animal_id);


--
-- Name: propriedades_usuarios pk_propriedades_usuarios; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propriedades_usuarios
    ADD CONSTRAINT pk_propriedades_usuarios PRIMARY KEY (propriedade_usuario_id);


--
-- Name: tipos_animal pk_tipos_animal; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipos_animal
    ADD CONSTRAINT pk_tipos_animal PRIMARY KEY (tipo_animal_id);


--
-- Name: usuarios pk_usuarios; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT pk_usuarios PRIMARY KEY (usuario_id);


--
-- Name: veterinarios pk_veterinarios; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.veterinarios
    ADD CONSTRAINT pk_veterinarios PRIMARY KEY (veterinario_id);


--
-- Name: veterinarios_propriedades pk_veterinarios_propriedades; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.veterinarios_propriedades
    ADD CONSTRAINT pk_veterinarios_propriedades PRIMARY KEY (veterinario_propriedade_id);


--
-- Name: idx_animais_tipo_animal_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_animais_tipo_animal_id ON public.animais USING btree (tipo_animal_id);


--
-- Name: idx_animais_usuario_inclusao_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_animais_usuario_inclusao_id ON public.animais USING btree (usuario_inclusao_id);


--
-- Name: idx_bairros_cidade_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bairros_cidade_id ON public.bairros USING btree (cidade_id);


--
-- Name: idx_ceps_bairros_bairro_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ceps_bairros_bairro_id ON public.ceps_bairros USING btree (bairro_id);


--
-- Name: idx_ceps_bairros_cep; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ceps_bairros_cep ON public.ceps_bairros USING btree (cep);


--
-- Name: idx_ceps_cidade_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ceps_cidade_id ON public.ceps USING btree (cidade_id);


--
-- Name: idx_ceps_localidades_cep; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ceps_localidades_cep ON public.ceps_localidades USING btree (cep);


--
-- Name: idx_ceps_localidades_localidade_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ceps_localidades_localidade_id ON public.ceps_localidades USING btree (localidade_id);


--
-- Name: idx_cidades_estado_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cidades_estado_id ON public.cidades USING btree (estado_id);


--
-- Name: idx_localidades_cidade_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_localidades_cidade_id ON public.localidades USING btree (cidade_id);


--
-- Name: idx_pessoas_bairro_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_pessoas_bairro_id ON public.pessoas USING btree (bairro_id);


--
-- Name: idx_pessoas_cep; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_pessoas_cep ON public.pessoas USING btree (cep);


--
-- Name: idx_pessoas_localidade_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_pessoas_localidade_id ON public.pessoas USING btree (localidade_id);


--
-- Name: idx_pessoas_telefones_pessoa_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_pessoas_telefones_pessoa_id ON public.pessoas_telefones USING btree (pessoa_id);


--
-- Name: idx_propriedades_animais_animal_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_propriedades_animais_animal_id ON public.propriedades_animais USING btree (animal_id);


--
-- Name: idx_propriedades_animais_propriedade_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_propriedades_animais_propriedade_id ON public.propriedades_animais USING btree (propriedade_id);


--
-- Name: idx_propriedades_cep; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_propriedades_cep ON public.propriedades USING btree (cep);


--
-- Name: idx_propriedades_proprietario_pessoa_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_propriedades_proprietario_pessoa_id ON public.propriedades USING btree (proprietario_pessoa_id);


--
-- Name: idx_propriedades_usuarios_propriedade_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_propriedades_usuarios_propriedade_id ON public.propriedades_usuarios USING btree (propriedade_id);


--
-- Name: idx_propriedades_usuarios_usuario_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_propriedades_usuarios_usuario_id ON public.propriedades_usuarios USING btree (usuario_id);


--
-- Name: idx_usuarios_papel_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_usuarios_papel_id ON public.usuarios USING btree (papel_id);


--
-- Name: idx_usuarios_pessoa_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_usuarios_pessoa_id ON public.usuarios USING btree (pessoa_id);


--
-- Name: idx_veterinarios_pessoa_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_veterinarios_pessoa_id ON public.veterinarios USING btree (pessoa_id);


--
-- Name: idx_veterinarios_propriedades_propriedade_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_veterinarios_propriedades_propriedade_id ON public.veterinarios_propriedades USING btree (propriedade_id);


--
-- Name: idx_veterinarios_propriedades_veterinario_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_veterinarios_propriedades_veterinario_id ON public.veterinarios_propriedades USING btree (veterinario_id);


--
-- Name: idx_veterinarios_usuario_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_veterinarios_usuario_id ON public.veterinarios USING btree (usuario_id);


--
-- Name: udx_ceps_bairros_cep_bairro_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX udx_ceps_bairros_cep_bairro_id ON public.ceps_bairros USING btree (cep, bairro_id);


--
-- Name: udx_ceps_localidades_cep_localidade_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX udx_ceps_localidades_cep_localidade_id ON public.ceps_localidades USING btree (cep, localidade_id);


--
-- Name: udx_estados_sigla; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX udx_estados_sigla ON public.estados USING btree (sigla);


--
-- Name: udx_papeis_nome; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX udx_papeis_nome ON public.papeis USING btree (nome);


--
-- Name: udx_pessoas_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX udx_pessoas_email ON public.pessoas USING btree (email);


--
-- Name: udx_pessoas_fisicas_cpf; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX udx_pessoas_fisicas_cpf ON public.pessoas_fisicas USING btree (cpf);


--
-- Name: udx_pessoas_juridicas_cnpj; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX udx_pessoas_juridicas_cnpj ON public.pessoas_juridicas USING btree (cnpj);


--
-- Name: udx_pessoas_telefones_pessoa_id_principal; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX udx_pessoas_telefones_pessoa_id_principal ON public.pessoas_telefones USING btree (pessoa_id) WHERE (principal = true);


--
-- Name: udx_propriedades_animais_propriedade_id_animal_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX udx_propriedades_animais_propriedade_id_animal_id ON public.propriedades_animais USING btree (propriedade_id, animal_id);


--
-- Name: udx_propriedades_usuarios_usuario_id_propriedade_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX udx_propriedades_usuarios_usuario_id_propriedade_id ON public.propriedades_usuarios USING btree (usuario_id, propriedade_id);


--
-- Name: udx_usuarios_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX udx_usuarios_email ON public.usuarios USING btree (email);


--
-- Name: udx_usuarios_pessoa_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX udx_usuarios_pessoa_id ON public.usuarios USING btree (pessoa_id);


--
-- Name: udx_veterinarios_pessoa_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX udx_veterinarios_pessoa_id ON public.veterinarios USING btree (pessoa_id);


--
-- Name: udx_veterinarios_propriedades_veterinario_id_propriedade_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX udx_veterinarios_propriedades_veterinario_id_propriedade_id ON public.veterinarios_propriedades USING btree (veterinario_id, propriedade_id);


--
-- Name: udx_veterinarios_usuario_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX udx_veterinarios_usuario_id ON public.veterinarios USING btree (usuario_id);


--
-- Name: animais fk_animais_tipo_animal_id_ref_tipos_animal; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.animais
    ADD CONSTRAINT fk_animais_tipo_animal_id_ref_tipos_animal FOREIGN KEY (tipo_animal_id) REFERENCES public.tipos_animal(tipo_animal_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: animais fk_animais_usuario_inclusao_id_ref_usuarios; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.animais
    ADD CONSTRAINT fk_animais_usuario_inclusao_id_ref_usuarios FOREIGN KEY (usuario_inclusao_id) REFERENCES public.usuarios(usuario_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: bairros fk_bairros_cidade_id_ref_cidades; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bairros
    ADD CONSTRAINT fk_bairros_cidade_id_ref_cidades FOREIGN KEY (cidade_id) REFERENCES public.cidades(cidade_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: ceps_bairros fk_ceps_bairros_bairro_id_ref_bairros; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ceps_bairros
    ADD CONSTRAINT fk_ceps_bairros_bairro_id_ref_bairros FOREIGN KEY (bairro_id) REFERENCES public.bairros(bairro_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: ceps_bairros fk_ceps_bairros_cep_ref_ceps; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ceps_bairros
    ADD CONSTRAINT fk_ceps_bairros_cep_ref_ceps FOREIGN KEY (cep) REFERENCES public.ceps(cep) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: ceps fk_ceps_cidade_id_ref_cidades; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ceps
    ADD CONSTRAINT fk_ceps_cidade_id_ref_cidades FOREIGN KEY (cidade_id) REFERENCES public.cidades(cidade_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: ceps_localidades fk_ceps_localidades_cep_ref_ceps; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ceps_localidades
    ADD CONSTRAINT fk_ceps_localidades_cep_ref_ceps FOREIGN KEY (cep) REFERENCES public.ceps(cep) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: ceps_localidades fk_ceps_localidades_localidade_id_ref_localidades; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ceps_localidades
    ADD CONSTRAINT fk_ceps_localidades_localidade_id_ref_localidades FOREIGN KEY (localidade_id) REFERENCES public.localidades(localidade_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: cidades fk_cidades_estado_id_ref_estados; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cidades
    ADD CONSTRAINT fk_cidades_estado_id_ref_estados FOREIGN KEY (estado_id) REFERENCES public.estados(estado_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: localidades fk_localidades_cidade_id_ref_cidades; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.localidades
    ADD CONSTRAINT fk_localidades_cidade_id_ref_cidades FOREIGN KEY (cidade_id) REFERENCES public.cidades(cidade_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: pessoas fk_pessoas_bairro_id_ref_bairros; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pessoas
    ADD CONSTRAINT fk_pessoas_bairro_id_ref_bairros FOREIGN KEY (bairro_id) REFERENCES public.bairros(bairro_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: pessoas fk_pessoas_cep_ref_ceps; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pessoas
    ADD CONSTRAINT fk_pessoas_cep_ref_ceps FOREIGN KEY (cep) REFERENCES public.ceps(cep) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: pessoas_fisicas fk_pessoas_fisicas_pessoa_id_ref_pessoas; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pessoas_fisicas
    ADD CONSTRAINT fk_pessoas_fisicas_pessoa_id_ref_pessoas FOREIGN KEY (pessoa_id) REFERENCES public.pessoas(pessoa_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pessoas_juridicas fk_pessoas_juridicas_pessoa_id_ref_pessoas; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pessoas_juridicas
    ADD CONSTRAINT fk_pessoas_juridicas_pessoa_id_ref_pessoas FOREIGN KEY (pessoa_id) REFERENCES public.pessoas(pessoa_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pessoas fk_pessoas_localidade_id_ref_localidades; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pessoas
    ADD CONSTRAINT fk_pessoas_localidade_id_ref_localidades FOREIGN KEY (localidade_id) REFERENCES public.localidades(localidade_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: pessoas_telefones fk_pessoas_telefones_pessoa_id_ref_pessoas; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pessoas_telefones
    ADD CONSTRAINT fk_pessoas_telefones_pessoa_id_ref_pessoas FOREIGN KEY (pessoa_id) REFERENCES public.pessoas(pessoa_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: propriedades_animais fk_propriedades_animais_animal_id_ref_animais; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propriedades_animais
    ADD CONSTRAINT fk_propriedades_animais_animal_id_ref_animais FOREIGN KEY (animal_id) REFERENCES public.animais(animal_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: propriedades_animais fk_propriedades_animais_propriedade_id_ref_propriedades; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propriedades_animais
    ADD CONSTRAINT fk_propriedades_animais_propriedade_id_ref_propriedades FOREIGN KEY (propriedade_id) REFERENCES public.propriedades(propriedade_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: propriedades fk_propriedades_cep_ref_ceps; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propriedades
    ADD CONSTRAINT fk_propriedades_cep_ref_ceps FOREIGN KEY (cep) REFERENCES public.ceps(cep) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: propriedades fk_propriedades_proprietario_pessoa_id_ref_pessoas; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propriedades
    ADD CONSTRAINT fk_propriedades_proprietario_pessoa_id_ref_pessoas FOREIGN KEY (proprietario_pessoa_id) REFERENCES public.pessoas(pessoa_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: propriedades_usuarios fk_propriedades_usuarios_propriedade_id_ref_propriedades; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propriedades_usuarios
    ADD CONSTRAINT fk_propriedades_usuarios_propriedade_id_ref_propriedades FOREIGN KEY (propriedade_id) REFERENCES public.propriedades(propriedade_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: propriedades_usuarios fk_propriedades_usuarios_usuario_id_ref_usuarios; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propriedades_usuarios
    ADD CONSTRAINT fk_propriedades_usuarios_usuario_id_ref_usuarios FOREIGN KEY (usuario_id) REFERENCES public.usuarios(usuario_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: usuarios fk_usuarios_papel_id_ref_papeis; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT fk_usuarios_papel_id_ref_papeis FOREIGN KEY (papel_id) REFERENCES public.papeis(papel_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: usuarios fk_usuarios_pessoa_id_ref_pessoas; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT fk_usuarios_pessoa_id_ref_pessoas FOREIGN KEY (pessoa_id) REFERENCES public.pessoas(pessoa_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: veterinarios fk_veterinarios_pessoa_id_ref_pessoas; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.veterinarios
    ADD CONSTRAINT fk_veterinarios_pessoa_id_ref_pessoas FOREIGN KEY (pessoa_id) REFERENCES public.pessoas(pessoa_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: veterinarios_propriedades fk_veterinarios_propriedades_propriedade_id_ref_propriedades; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.veterinarios_propriedades
    ADD CONSTRAINT fk_veterinarios_propriedades_propriedade_id_ref_propriedades FOREIGN KEY (propriedade_id) REFERENCES public.propriedades(propriedade_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: veterinarios_propriedades fk_veterinarios_propriedades_veterinario_id_ref_veterinarios; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.veterinarios_propriedades
    ADD CONSTRAINT fk_veterinarios_propriedades_veterinario_id_ref_veterinarios FOREIGN KEY (veterinario_id) REFERENCES public.veterinarios(veterinario_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: veterinarios fk_veterinarios_usuario_id_ref_usuarios; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.veterinarios
    ADD CONSTRAINT fk_veterinarios_usuario_id_ref_usuarios FOREIGN KEY (usuario_id) REFERENCES public.usuarios(usuario_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

