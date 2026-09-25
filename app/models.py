"""
Modelos SQLAlchemy que espelham o schema criado via schema_bd/modelo_ajustado.sql.

IMPORTANTE: as tabelas ja existem no banco (aplicadas via .sql + baseline do
Alembic). A fonte da verdade do schema e o arquivo .sql + as migrations, nao
este arquivo.

Convencao do banco: a chave de cada tabela se chama <tabela_no_singular>_id
(pessoa_id, animal_id...). Aqui o atributo Python e sempre `id`, mapeado para
essa coluna - assim a API e o frontend seguem o mesmo padrao do restante do
sistema (`item.id`) sem que o banco perca o nome descritivo.
"""
from datetime import date, datetime

from sqlalchemy import (
    BigInteger, Boolean, CHAR, Column, Date, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String,
    Table, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Nomes dos papeis semeados no .sql (tabela papeis).
MASTER = "MASTER"
ADMIN = "ADMIN"
VISUALIZADOR = "VISUALIZADOR"


# =====================================================================
# 1. GEOGRAFIA (estado -> cidade -> bairros e localidades; cep -> cidade)
# =====================================================================

class Estado(Base):
    __tablename__ = "estados"

    id: Mapped[int] = mapped_column("estado_id", Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    sigla: Mapped[str] = mapped_column(String(2), nullable=False)


class Cidade(Base):
    __tablename__ = "cidades"

    id: Mapped[int] = mapped_column("cidade_id", BigInteger, primary_key=True)
    estado_id: Mapped[int] = mapped_column(ForeignKey("estados.estado_id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo_ibge: Mapped[int | None] = mapped_column(Integer)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    estado: Mapped["Estado"] = relationship(lazy="joined")

    @property
    def estado_sigla(self) -> str:
        return self.estado.sigla

    @property
    def rotulo(self) -> str:
        return f"{self.nome}/{self.estado.sigla}"


class Bairro(Base):
    __tablename__ = "bairros"

    id: Mapped[int] = mapped_column("bairro_id", BigInteger, primary_key=True)
    cidade_id: Mapped[int] = mapped_column(ForeignKey("cidades.cidade_id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    cidade: Mapped["Cidade"] = relationship(lazy="joined")

    @property
    def cidade_rotulo(self) -> str:
        return self.cidade.rotulo

    @property
    def rotulo(self) -> str:
        return f"{self.nome} - {self.cidade.rotulo}"


class Localidade(Base):
    """Sub-area da cidade (na zona rural: linha, distrito, comunidade). E um
    cadastro paralelo ao bairro: os dois pertencem a cidade, nenhum ao outro."""
    __tablename__ = "localidades"

    id: Mapped[int] = mapped_column("localidade_id", BigInteger, primary_key=True)
    cidade_id: Mapped[int] = mapped_column(ForeignKey("cidades.cidade_id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    cidade: Mapped["Cidade"] = relationship(lazy="joined")

    @property
    def cidade_rotulo(self) -> str:
        return self.cidade.rotulo

    @property
    def rotulo(self) -> str:
        return f"{self.nome} - {self.cidade.rotulo}"


# Tabelas associativas do CEP. So as colunas de ligacao entram aqui: a chave
# (cep_bairro_id / cep_localidade_id) tem default de sequence no banco.
ceps_bairros = Table(
    "ceps_bairros", Base.metadata,
    Column("cep_bairro_id", BigInteger, primary_key=True),
    Column("cep", ForeignKey("ceps.cep"), nullable=False),
    Column("bairro_id", ForeignKey("bairros.bairro_id"), nullable=False),
)
ceps_localidades = Table(
    "ceps_localidades", Base.metadata,
    Column("cep_localidade_id", BigInteger, primary_key=True),
    Column("cep", ForeignKey("ceps.cep"), nullable=False),
    Column("localidade_id", ForeignKey("localidades.localidade_id"), nullable=False),
)


class Cep(Base):
    """Chave natural: o proprio CEP (8 digitos, sem hifen).

    Pertence a uma cidade e pode cobrir varios bairros e varias localidades (em
    cidade pequena, todos os enderecos dividem o mesmo CEP). Sem nenhum dos dois
    ele so identifica a cidade."""
    __tablename__ = "ceps"

    cep: Mapped[str] = mapped_column(String(8), primary_key=True)
    cidade_id: Mapped[int] = mapped_column(ForeignKey("cidades.cidade_id"), nullable=False)

    cidade: Mapped["Cidade"] = relationship(lazy="joined")
    bairros: Mapped[list["Bairro"]] = relationship(secondary=ceps_bairros, order_by="Bairro.nome")
    localidades: Mapped[list["Localidade"]] = relationship(secondary=ceps_localidades, order_by="Localidade.nome")

    @property
    def id(self) -> str:
        # O CrudPage identifica o registro por `id`; no CEP ele e o proprio codigo.
        return self.cep

    @property
    def cidade_uf(self) -> str:
        return self.cidade.rotulo

    @property
    def bairro_ids(self) -> list[int]:
        return [b.id for b in self.bairros]

    @property
    def localidade_ids(self) -> list[int]:
        return [l.id for l in self.localidades]

    @property
    def bairros_nomes(self) -> str:
        return ", ".join(b.nome for b in self.bairros)

    @property
    def localidades_nomes(self) -> str:
        return ", ".join(l.nome for l in self.localidades)

    @property
    def rotulo(self) -> str:
        return f"{self.cep} - {self.cidade.rotulo}"


# =====================================================================
# 2. ACESSO (papeis e usuarios)
# =====================================================================

class Papel(Base):
    __tablename__ = "papeis"

    id: Mapped[int] = mapped_column("papel_id", Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(50), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(150))
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column("usuario_id", BigInteger, primary_key=True)
    pessoa_id: Mapped[int | None] = mapped_column(ForeignKey("pessoas.pessoa_id"))
    papel_id: Mapped[int] = mapped_column(ForeignKey("papeis.papel_id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    data_inclusao: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    data_alteracao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    papel: Mapped["Papel"] = relationship(lazy="joined")

    @property
    def papel_nome(self) -> str:
        return self.papel.nome


# =====================================================================
# 3. PESSOAS (supertipo) e subtipos fisica/juridica
# =====================================================================

class Pessoa(Base):
    __tablename__ = "pessoas"

    id: Mapped[int] = mapped_column("pessoa_id", BigInteger, primary_key=True)
    tipo_pessoa: Mapped[str] = mapped_column(CHAR(1), nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150))
    cep: Mapped[str | None] = mapped_column(ForeignKey("ceps.cep"))
    # Qual bairro OU qual localidade do CEP e o da pessoa (nunca os dois).
    bairro_id: Mapped[int | None] = mapped_column(ForeignKey("bairros.bairro_id"))
    localidade_id: Mapped[int | None] = mapped_column(ForeignKey("localidades.localidade_id"))
    endereco: Mapped[str | None] = mapped_column(String(100))
    numero: Mapped[str | None] = mapped_column(String(15))
    complemento: Mapped[str | None] = mapped_column(String(100))
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # Quem cadastrou: enquanto a pessoa nao esta ligada a uma propriedade, so ele a enxerga.
    usuario_inclusao_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.usuario_id"))
    data_inclusao: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    data_alteracao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    bairro: Mapped["Bairro | None"] = relationship(lazy="joined")
    localidade: Mapped["Localidade | None"] = relationship(lazy="joined")

    # Subtipo: so um dos dois existe, conforme tipo_pessoa. O cascade cuida do
    # ciclo de vida; no banco o vinculo e ON DELETE CASCADE.
    fisica: Mapped["PessoaFisica | None"] = relationship(
        back_populates="pessoa", uselist=False, cascade="all, delete-orphan", lazy="joined",
    )
    juridica: Mapped["PessoaJuridica | None"] = relationship(
        back_populates="pessoa", uselist=False, cascade="all, delete-orphan", lazy="joined",
    )
    telefones: Mapped[list["PessoaTelefone"]] = relationship(
        back_populates="pessoa", cascade="all, delete-orphan",
        order_by="PessoaTelefone.principal.desc(), PessoaTelefone.id",
    )
    cep_ref: Mapped["Cep | None"] = relationship(lazy="joined")

    # Achata o subtipo para a API: o front trabalha com um formulario so.
    @property
    def cpf(self) -> str | None:
        return self.fisica.cpf if self.fisica else None

    @property
    def data_nascimento(self) -> date | None:
        return self.fisica.data_nascimento if self.fisica else None

    @property
    def cnpj(self) -> str | None:
        return self.juridica.cnpj if self.juridica else None

    @property
    def razao_social(self) -> str | None:
        return self.juridica.razao_social if self.juridica else None

    @property
    def nome_fantasia(self) -> str | None:
        return self.juridica.nome_fantasia if self.juridica else None

    @property
    def data_fundacao(self) -> date | None:
        return self.juridica.data_fundacao if self.juridica else None

    @property
    def documento(self) -> str | None:
        return self.cpf if self.tipo_pessoa == "F" else self.cnpj

    @property
    def telefone_principal(self) -> str | None:
        return self.telefones[0].numero if self.telefones else None

    @property
    def cidade_uf(self) -> str | None:
        return self.cep_ref.cidade_uf if self.cep_ref else None

    @property
    def local_nome(self) -> str | None:
        """Nome do bairro ou da localidade, o que a pessoa tiver."""
        escolhido = self.bairro or self.localidade
        return escolhido.nome if escolhido else None


class PessoaFisica(Base):
    __tablename__ = "pessoas_fisicas"

    pessoa_id: Mapped[int] = mapped_column(
        ForeignKey("pessoas.pessoa_id", ondelete="CASCADE"), primary_key=True, autoincrement=False,
    )
    cpf: Mapped[str | None] = mapped_column(String(11))
    data_nascimento: Mapped[date | None] = mapped_column(Date)

    pessoa: Mapped["Pessoa"] = relationship(back_populates="fisica")


class PessoaJuridica(Base):
    __tablename__ = "pessoas_juridicas"

    pessoa_id: Mapped[int] = mapped_column(
        ForeignKey("pessoas.pessoa_id", ondelete="CASCADE"), primary_key=True, autoincrement=False,
    )
    cnpj: Mapped[str | None] = mapped_column(String(14))
    razao_social: Mapped[str] = mapped_column(String(150), nullable=False)
    nome_fantasia: Mapped[str | None] = mapped_column(String(150))
    data_fundacao: Mapped[date | None] = mapped_column(Date)

    pessoa: Mapped["Pessoa"] = relationship(back_populates="juridica")


class PessoaTelefone(Base):
    __tablename__ = "pessoas_telefones"

    id: Mapped[int] = mapped_column("pessoa_telefone_id", BigInteger, primary_key=True)
    pessoa_id: Mapped[int] = mapped_column(ForeignKey("pessoas.pessoa_id", ondelete="CASCADE"), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    tipo_telefone: Mapped[str | None] = mapped_column(String(20))
    principal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    pessoa: Mapped["Pessoa"] = relationship(back_populates="telefones")


# =====================================================================
# 4. ANIMAIS E PROPRIEDADES
# =====================================================================

class TipoAnimal(Base):
    __tablename__ = "tipos_animal"

    id: Mapped[int] = mapped_column("tipo_animal_id", Integer, primary_key=True)
    descricao: Mapped[str] = mapped_column(String(100), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Raca(Base):
    __tablename__ = "racas"

    id: Mapped[int] = mapped_column("raca_id", Integer, primary_key=True)
    descricao: Mapped[str] = mapped_column(String(100), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Animal(Base):
    __tablename__ = "animais"

    id: Mapped[int] = mapped_column("animal_id", BigInteger, primary_key=True)
    tipo_animal_id: Mapped[int] = mapped_column(ForeignKey("tipos_animal.tipo_animal_id"), nullable=False)
    # Opcional: o cadastro de racas existe sozinho e o animal so e ligado a ele se quiser.
    raca_id: Mapped[int | None] = mapped_column(ForeignKey("racas.raca_id"))
    codigo: Mapped[str | None] = mapped_column(String(30))
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    data_nascimento: Mapped[date | None] = mapped_column(Date)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # Quem cadastrou: enquanto o animal nao esta em propriedade, so ele o enxerga.
    usuario_inclusao_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.usuario_id"))

    tipo_animal: Mapped["TipoAnimal"] = relationship(lazy="joined")
    raca: Mapped["Raca | None"] = relationship(lazy="joined")

    @property
    def tipo_descricao(self) -> str:
        return self.tipo_animal.descricao

    @property
    def raca_descricao(self) -> str | None:
        return self.raca.descricao if self.raca else None


class PadraoPeso(Base):
    """Peso ideal de uma raca numa idade (meses). Referencia comum a todos."""
    __tablename__ = "padroes_peso"

    id: Mapped[int] = mapped_column("padrao_peso_id", Integer, primary_key=True)
    raca_id: Mapped[int] = mapped_column(ForeignKey("racas.raca_id"), nullable=False)
    idade_meses: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    peso_ideal_kg: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text)

    raca: Mapped["Raca"] = relationship(lazy="joined")

    @property
    def raca_descricao(self) -> str:
        return self.raca.descricao


class Pesagem(Base):
    """Peso real de um animal numa data, lancado no contexto de uma propriedade."""
    __tablename__ = "pesagens"

    id: Mapped[int] = mapped_column("pesagem_id", BigInteger, primary_key=True)
    propriedade_id: Mapped[int] = mapped_column(ForeignKey("propriedades.propriedade_id"), nullable=False)
    animal_id: Mapped[int] = mapped_column(ForeignKey("animais.animal_id"), nullable=False)
    data_pesagem: Mapped[date] = mapped_column(Date, nullable=False)
    peso_kg: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text)
    usuario_inclusao_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.usuario_id"))

    animal: Mapped["Animal"] = relationship(lazy="joined")

    @property
    def animal_nome(self) -> str:
        return self.animal.nome

    @property
    def animal_codigo(self) -> str | None:
        return self.animal.codigo

    @property
    def tipo_animal_id(self) -> int:
        return self.animal.tipo_animal_id


class Propriedade(Base):
    __tablename__ = "propriedades"

    id: Mapped[int] = mapped_column("propriedade_id", BigInteger, primary_key=True)
    proprietario_pessoa_id: Mapped[int] = mapped_column(ForeignKey("pessoas.pessoa_id"), nullable=False)
    cep: Mapped[str] = mapped_column(ForeignKey("ceps.cep"), nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    endereco: Mapped[str | None] = mapped_column(String(100))
    numero: Mapped[str | None] = mapped_column(String(15))
    complemento: Mapped[str | None] = mapped_column(String(100))

    proprietario: Mapped["Pessoa"] = relationship(lazy="joined")
    cep_ref: Mapped["Cep"] = relationship(lazy="joined")

    @property
    def proprietario_nome(self) -> str:
        return self.proprietario.nome

    @property
    def cidade_uf(self) -> str:
        return self.cep_ref.cidade_uf


class PropriedadeAnimal(Base):
    __tablename__ = "propriedades_animais"

    id: Mapped[int] = mapped_column("propriedade_animal_id", BigInteger, primary_key=True)
    propriedade_id: Mapped[int] = mapped_column(ForeignKey("propriedades.propriedade_id"), nullable=False)
    animal_id: Mapped[int] = mapped_column(ForeignKey("animais.animal_id"), nullable=False)


# =====================================================================
# 5. VETERINARIOS E CONTROLE DE ACESSO POR PROPRIEDADE
# =====================================================================

class Veterinario(Base):
    """Papel profissional de uma pessoa. Os dados pessoais ficam em Pessoa."""
    __tablename__ = "veterinarios"

    id: Mapped[int] = mapped_column("veterinario_id", BigInteger, primary_key=True)
    pessoa_id: Mapped[int] = mapped_column(ForeignKey("pessoas.pessoa_id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.usuario_id"), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    pessoa: Mapped["Pessoa"] = relationship(lazy="joined")
    usuario: Mapped["Usuario"] = relationship(lazy="joined")

    @property
    def nome(self) -> str:
        return self.pessoa.nome

    @property
    def usuario_email(self) -> str:
        return self.usuario.email

    @property
    def telefone_principal(self) -> str | None:
        return self.pessoa.telefone_principal


class VeterinarioPropriedade(Base):
    """Um veterinario enxerga todas as propriedades que atende, por este vinculo."""
    __tablename__ = "veterinarios_propriedades"

    id: Mapped[int] = mapped_column("veterinario_propriedade_id", BigInteger, primary_key=True)
    veterinario_id: Mapped[int] = mapped_column(ForeignKey("veterinarios.veterinario_id"), nullable=False)
    propriedade_id: Mapped[int] = mapped_column(ForeignKey("propriedades.propriedade_id"), nullable=False)


class PropriedadeUsuario(Base):
    """Quais logins acessam quais propriedades (o dono e, se houver, outros autorizados)."""
    __tablename__ = "propriedades_usuarios"

    id: Mapped[int] = mapped_column("propriedade_usuario_id", BigInteger, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.usuario_id"), nullable=False)
    propriedade_id: Mapped[int] = mapped_column(ForeignKey("propriedades.propriedade_id"), nullable=False)
