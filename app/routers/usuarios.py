from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.acesso import condicao_usuario_visivel
from app.database import get_db
from app.erros_db import confirmar
from app.models import ADMIN, MASTER, Papel, Usuario
from app.schemas import (
    PapelRead, SenhaReset, UsuarioAdminCreate, UsuarioRead, UsuarioUpdate,
)
from app.security import exigir_master, exigir_papel, get_current_user, hash_senha

# Gravar usuario e coisa de MASTER (define quem entra no sistema e com que
# perfil). ADMIN so lista, para poder vincular pessoas as propriedades.
router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
router_papeis = APIRouter(prefix="/papeis", tags=["Papeis"])

NAO_ENCONTRADO = "Usuario nao encontrado"


def _total_ativos(db: Session) -> int:
    stmt = select(func.count()).select_from(Usuario).where(Usuario.ativo.is_(True))
    return db.execute(stmt).scalar_one()


def _buscar(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail=NAO_ENCONTRADO)
    return usuario


def _validar_papel(db: Session, papel_id: int) -> Papel:
    papel = db.get(Papel, papel_id)
    if not papel or not papel.ativo:
        raise HTTPException(status_code=400, detail="Papel invalido")
    return papel


def _garantir_master_restante(db: Session, usuario: Usuario) -> None:
    """Impede ficar sem nenhum MASTER ativo (ninguem mais gerenciaria usuarios)."""
    outros = db.execute(
        select(func.count()).select_from(Usuario).join(Papel, Papel.id == Usuario.papel_id).where(
            Papel.nome == MASTER, Usuario.ativo.is_(True), Usuario.id != usuario.id
        )
    ).scalar_one()
    if outros == 0:
        raise HTTPException(status_code=400, detail="O sistema precisa de pelo menos um usuario master ativo")


@router_papeis.get("/", response_model=list[PapelRead])
def listar_papeis(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return db.execute(select(Papel).where(Papel.ativo.is_(True)).order_by(Papel.id)).scalars().all()


@router.post("/", response_model=UsuarioRead, status_code=201)
def criar_usuario(
    payload: UsuarioAdminCreate, db: Session = Depends(get_db), _: Usuario = Depends(exigir_master),
):
    _validar_papel(db, payload.papel_id)
    usuario = Usuario(
        nome=payload.nome,
        email=payload.email,
        senha_hash=hash_senha(payload.senha),
        papel_id=payload.papel_id,
        pessoa_id=payload.pessoa_id,
        ativo=payload.ativo,
    )
    db.add(usuario)
    confirmar(db)
    db.refresh(usuario)
    return usuario


@router.get("/", response_model=list[UsuarioRead])
def listar_usuarios(
    apenas_ativos: bool = False,
    db: Session = Depends(get_db),
    atual: Usuario = Depends(exigir_papel(MASTER, ADMIN)),
):
    """Lista ativos e inativos por padrao: a tela filtra os dois no lado do cliente.
    Quem nao e MASTER ve so quem tem acesso as suas propriedades (e a si mesmo)."""
    stmt = select(Usuario)
    condicao = condicao_usuario_visivel(atual)
    if condicao is not None:
        stmt = stmt.where(condicao)
    if apenas_ativos:
        stmt = stmt.where(Usuario.ativo.is_(True))
    return db.execute(stmt.order_by(Usuario.nome)).scalars().all()


@router.get("/{usuario_id}", response_model=UsuarioRead)
def obter_usuario(
    usuario_id: int, db: Session = Depends(get_db), atual: Usuario = Depends(exigir_papel(MASTER, ADMIN)),
):
    usuario = _buscar(db, usuario_id)
    condicao = condicao_usuario_visivel(atual)
    if condicao is not None and db.execute(select(Usuario.id).where(Usuario.id == usuario_id, condicao)).first() is None:
        raise HTTPException(status_code=404, detail=NAO_ENCONTRADO)
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioRead)
def atualizar_usuario(
    usuario_id: int,
    payload: UsuarioUpdate,
    db: Session = Depends(get_db),
    atual: Usuario = Depends(exigir_master),
):
    """Altera nome, e-mail, papel e situacao. A senha tem endpoint proprio."""
    usuario = _buscar(db, usuario_id)
    novo_papel = _validar_papel(db, payload.papel_id)
    if usuario.ativo and not payload.ativo:
        _validar_desativacao(db, usuario, atual)
    if usuario.papel.nome == MASTER and novo_papel.nome != MASTER:
        _garantir_master_restante(db, usuario)
    usuario.nome = payload.nome
    usuario.email = payload.email
    usuario.papel_id = payload.papel_id
    usuario.pessoa_id = payload.pessoa_id
    usuario.ativo = payload.ativo
    confirmar(db)
    db.refresh(usuario)
    return usuario


@router.patch("/{usuario_id}/senha", status_code=204)
def redefinir_senha(
    usuario_id: int, payload: SenhaReset, db: Session = Depends(get_db), _: Usuario = Depends(exigir_master),
):
    """Define uma nova senha sem pedir a antiga (uso administrativo).

    Para o usuario trocar a propria senha conferindo a atual, use
    POST /auth/alterar-senha.
    """
    usuario = _buscar(db, usuario_id)
    usuario.senha_hash = hash_senha(payload.nova_senha)
    db.commit()


@router.delete("/{usuario_id}", status_code=204)
def desativar_usuario(
    usuario_id: int, db: Session = Depends(get_db), atual: Usuario = Depends(exigir_master),
):
    """Soft delete: o cadastro fica inativo (login bloqueado) e pode ser reativado."""
    usuario = _buscar(db, usuario_id)
    if usuario.ativo:
        _validar_desativacao(db, usuario, atual)
    usuario.ativo = False
    db.commit()


def _validar_desativacao(db: Session, usuario: Usuario, atual: Usuario) -> None:
    """Impede os jeitos de ficar trancado para fora do sistema."""
    if usuario.id == atual.id:
        raise HTTPException(status_code=400, detail="Voce nao pode desativar o proprio usuario")
    if _total_ativos(db) <= 1:
        raise HTTPException(status_code=400, detail="Nao e possivel desativar o ultimo usuario ativo")
    if usuario.papel.nome == MASTER:
        _garantir_master_restante(db, usuario)
