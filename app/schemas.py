"""
Schemas Pydantic. Padrao adotado para cada entidade:
  - <Nome>Base:    campos comuns de entrada
  - <Nome>Create:  o que a API recebe para criar
  - <Nome>Read:    o que a API devolve (inclui id e datas de auditoria)

model_config = ConfigDict(from_attributes=True) permite converter direto
de um objeto SQLAlchemy para o schema de resposta (antigo orm_mode).
"""
import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _so_digitos(valor: str | None, tamanho: int, rotulo: str) -> str | None:
    """Tira mascara (pontos, tracos, espacos) e confere o tamanho. Vazio vira None:
    os indices unicos do banco ignoram NULL, mas nao ignoram string vazia."""
    if valor is None:
        return None
    digitos = re.sub(r"\D", "", valor)
    if not digitos:
        return None
    if len(digitos) != tamanho:
        raise ValueError(f"{rotulo} deve ter {tamanho} digitos")
    return digitos


def _vazio_como_none(valor: str | None) -> str | None:
    if valor is None:
        return None
    valor = valor.strip()
    return valor or None


# ---------------------------------------------------------------------
# USUARIOS / AUTENTICACAO
# ---------------------------------------------------------------------

class PapelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    descricao: str | None
    ativo: bool


class UsuarioCreate(BaseModel):
    """Auto-cadastro em /auth/registrar (so vale para o primeiro usuario)."""
    nome: str
    email: str
    senha: str = Field(min_length=8)


class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    email: str
    papel_id: int
    papel_nome: str
    pessoa_id: int | None
    ativo: bool
    data_inclusao: datetime


class UsuarioAdminCreate(BaseModel):
    """Cadastro feito na tela de Usuarios por alguem ja autenticado."""
    nome: str
    email: str
    senha: str = Field(min_length=8)
    papel_id: int
    pessoa_id: int | None = None
    ativo: bool = True


class UsuarioUpdate(BaseModel):
    """Edicao de cadastro. A senha nao trafega aqui - ver /usuarios/{id}/senha."""
    nome: str
    email: str
    papel_id: int
    pessoa_id: int | None = None
    ativo: bool = True


class SenhaReset(BaseModel):
    """Redefinicao de senha de outro usuario: nao pede a senha antiga."""
    nova_senha: str = Field(min_length=8)


class SenhaAlteracao(BaseModel):
    """Troca da propria senha: exige a senha atual como confirmacao."""
    senha_atual: str
    nova_senha: str = Field(min_length=8)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------
# GEOGRAFIA
# ---------------------------------------------------------------------

class EstadoBase(BaseModel):
    nome: str
    sigla: str = Field(min_length=2, max_length=2)

    @field_validator("sigla")
    @classmethod
    def _sigla_maiuscula(cls, v: str) -> str:
        return v.strip().upper()


class EstadoRead(EstadoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CidadeBase(BaseModel):
    estado_id: int
    nome: str
    codigo_ibge: int | None = None
    ativa: bool = True


class CidadeRead(CidadeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    estado_sigla: str
    rotulo: str


class BairroBase(BaseModel):
    cidade_id: int
    nome: str
    ativo: bool = True


class BairroRead(BairroBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cidade_rotulo: str
    rotulo: str


class LocalidadeBase(BaseModel):
    cidade_id: int
    nome: str
    ativa: bool = True


class LocalidadeRead(LocalidadeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cidade_rotulo: str
    rotulo: str


class CepUpdate(BaseModel):
    """O CEP e a chave: o resto pode mudar. Bairros e localidades sao o conjunto
    completo e precisam ser da mesma cidade do CEP; lista vazia e valida."""
    cidade_id: int
    bairro_ids: list[int] = []
    localidade_ids: list[int] = []


class CepCreate(CepUpdate):
    cep: str

    @field_validator("cep")
    @classmethod
    def _cep(cls, v: str) -> str:
        digitos = _so_digitos(v, 8, "CEP")
        if digitos is None:
            raise ValueError("Informe o CEP")
        return digitos


class ItemRef(BaseModel):
    """Id e nome de um bairro/localidade, para montar seletores."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str


class CepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    cep: str
    cidade_id: int
    cidade_uf: str
    bairros: list[ItemRef]
    localidades: list[ItemRef]
    bairro_ids: list[int]
    localidade_ids: list[int]
    bairros_nomes: str
    localidades_nomes: str
    rotulo: str


# ---------------------------------------------------------------------
# PESSOAS
# ---------------------------------------------------------------------

class TelefoneIn(BaseModel):
    numero: str
    tipo_telefone: str | None = None
    principal: bool = False

    @field_validator("numero")
    @classmethod
    def _numero(cls, v: str) -> str:
        digitos = re.sub(r"\D", "", v)
        if not 8 <= len(digitos) <= 13:
            raise ValueError("Telefone deve ter de 8 a 13 digitos (com DDD)")
        return digitos

    @field_validator("tipo_telefone")
    @classmethod
    def _tipo(cls, v: str | None) -> str | None:
        return _vazio_como_none(v)


class TelefoneRead(TelefoneIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class PessoaCreate(BaseModel):
    tipo_pessoa: Literal["F", "J"] = "F"
    nome: str
    email: str | None = None
    cep: str | None = None
    # Um bairro OU uma localidade do CEP, nunca os dois.
    bairro_id: int | None = None
    localidade_id: int | None = None
    endereco: str | None = None
    numero: str | None = None
    complemento: str | None = None
    ativo: bool = True
    # Pessoa fisica
    cpf: str | None = None
    data_nascimento: date | None = None
    # Pessoa juridica
    cnpj: str | None = None
    razao_social: str | None = None
    nome_fantasia: str | None = None
    data_fundacao: date | None = None
    telefones: list[TelefoneIn] = []

    @field_validator("email", "endereco", "numero", "complemento", "razao_social", "nome_fantasia")
    @classmethod
    def _texto_opcional(cls, v: str | None) -> str | None:
        return _vazio_como_none(v)

    @field_validator("cep")
    @classmethod
    def _cep(cls, v: str | None) -> str | None:
        return _so_digitos(v, 8, "CEP")

    @field_validator("cpf")
    @classmethod
    def _cpf(cls, v: str | None) -> str | None:
        return _so_digitos(v, 11, "CPF")

    @field_validator("cnpj")
    @classmethod
    def _cnpj(cls, v: str | None) -> str | None:
        return _so_digitos(v, 14, "CNPJ")

    @model_validator(mode="after")
    def _telefones_e_subtipo(self):
        principais = [t for t in self.telefones if t.principal]
        if self.bairro_id and self.localidade_id:
            raise ValueError("Informe o bairro ou a localidade, nao os dois")
        if len(principais) > 1:
            raise ValueError("Marque apenas um telefone como principal")
        if self.telefones and not principais:
            self.telefones[0].principal = True
        # Campos do outro subtipo nao valem: nao os deixa vazar para o banco.
        if self.tipo_pessoa == "F":
            self.cnpj = self.razao_social = self.nome_fantasia = self.data_fundacao = None
        else:
            self.cpf = self.data_nascimento = None
            self.razao_social = self.razao_social or self.nome
        return self


class PessoaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo_pessoa: str
    nome: str
    email: str | None
    cep: str | None
    cidade_uf: str | None
    bairro_id: int | None
    localidade_id: int | None
    local_nome: str | None
    endereco: str | None
    numero: str | None
    complemento: str | None
    ativo: bool
    cpf: str | None
    data_nascimento: date | None
    cnpj: str | None
    razao_social: str | None
    nome_fantasia: str | None
    data_fundacao: date | None
    documento: str | None
    telefone_principal: str | None
    telefones: list[TelefoneRead]
    data_inclusao: datetime
    data_alteracao: datetime


# ---------------------------------------------------------------------
# ANIMAIS
# ---------------------------------------------------------------------

class TipoAnimalBase(BaseModel):
    descricao: str
    ativo: bool = True


class TipoAnimalRead(TipoAnimalBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class RacaBase(BaseModel):
    descricao: str
    ativo: bool = True


class RacaRead(RacaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class AnimalBase(BaseModel):
    tipo_animal_id: int
    raca_id: int | None = None
    codigo: str | None = None
    nome: str
    data_nascimento: date | None = None
    ativo: bool = True

    @field_validator("codigo")
    @classmethod
    def _codigo(cls, v: str | None) -> str | None:
        return _vazio_como_none(v)


class AnimalRead(AnimalBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo_descricao: str
    raca_descricao: str | None = None


# ---------------------------------------------------------------------
# PESO: padrao ideal por raca/idade e pesagens (peso real)
# ---------------------------------------------------------------------

class PadraoPesoBase(BaseModel):
    raca_id: int
    idade_meses: int = Field(ge=0, le=240)
    peso_ideal_kg: float = Field(gt=0)
    observacao: str | None = None

    @field_validator("observacao")
    @classmethod
    def _observacao(cls, v: str | None) -> str | None:
        return _vazio_como_none(v)


class PadraoPesoRead(PadraoPesoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    raca_descricao: str


class PesagemBase(BaseModel):
    animal_id: int
    data_pesagem: date
    peso_kg: float = Field(gt=0)
    observacao: str | None = None

    @field_validator("observacao")
    @classmethod
    def _observacao(cls, v: str | None) -> str | None:
        return _vazio_como_none(v)


class PesagemRead(PesagemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    animal_nome: str
    animal_codigo: str | None = None
    tipo_animal_id: int


class ComparativoPesoLinha(BaseModel):
    """Uma pesagem confrontada com o peso ideal da raca do animal na idade dela."""
    pesagem_id: int
    animal_id: int
    animal_nome: str
    raca_descricao: str | None
    data_pesagem: date
    idade_meses: int | None
    peso_real_kg: float
    peso_ideal_kg: float | None
    diferenca_kg: float | None
    gmd_real_kg: float | None
    gmd_ideal_kg: float | None


# ---------------------------------------------------------------------
# PROPRIEDADES E VETERINARIOS
# ---------------------------------------------------------------------

class PropriedadeBase(BaseModel):
    proprietario_pessoa_id: int
    cep: str
    nome: str
    ativa: bool = True
    endereco: str | None = None
    numero: str | None = None
    complemento: str | None = None

    @field_validator("cep")
    @classmethod
    def _cep(cls, v: str) -> str:
        digitos = _so_digitos(v, 8, "CEP")
        if digitos is None:
            raise ValueError("Informe o CEP")
        return digitos

    @field_validator("endereco", "numero", "complemento")
    @classmethod
    def _texto_opcional(cls, v: str | None) -> str | None:
        return _vazio_como_none(v)


class PropriedadeRead(PropriedadeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    proprietario_nome: str
    cidade_uf: str


class VeterinarioBase(BaseModel):
    pessoa_id: int
    usuario_id: int
    ativo: bool = True


class VeterinarioRead(VeterinarioBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    usuario_email: str
    telefone_principal: str | None


class VeterinarioCandidato(BaseModel):
    """So o necessario para escolher um veterinario ao vincula-lo a uma propriedade."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str


class VinculosIn(BaseModel):
    """Conjunto completo de ids vinculados: o que nao estiver na lista e desvinculado."""
    ids: list[int]


class VinculosRead(BaseModel):
    ids: list[int]


# ---------------------------------------------------------------------
# PAINEL
# ---------------------------------------------------------------------

class AnimaisPorTipo(BaseModel):
    tipo: str
    total: int


class ResumoPainel(BaseModel):
    """Painel de UMA propriedade (a do contexto)."""
    propriedade_id: int
    propriedade_nome: str
    cidade_uf: str
    proprietario_nome: str
    animais: int
    animais_por_tipo: list[AnimaisPorTipo]
    veterinarios: int
    usuarios: int


class ComparativoLinha(BaseModel):
    propriedade_id: int
    nome: str
    cidade_uf: str
    proprietario_nome: str
    animais: int
    por_tipo: dict[str, int]
    veterinarios: int
    usuarios: int


class ComparativoPropriedades(BaseModel):
    """Propriedades lado a lado; "tipos" e a uniao dos tipos de animal que aparecem."""
    tipos: list[str]
    linhas: list[ComparativoLinha]
