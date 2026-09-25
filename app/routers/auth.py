from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.erros_db import confirmar
from app.models import MASTER, Papel, Usuario
from app.schemas import SenhaAlteracao, Token, UsuarioCreate, UsuarioRead
from app.security import criar_access_token, get_current_user, hash_senha, verificar_senha

router = APIRouter(prefix="/auth", tags=["Autenticacao"])


@router.post("/registrar", response_model=UsuarioRead, status_code=201)
def registrar_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    """Cria o primeiro usuario do sistema, que nasce MASTER. Depois disso o
    cadastro e fechado: novos usuarios sao criados por um MASTER na tela de
    Usuarios, com o papel escolhido - senao qualquer um se cadastraria e
    passaria a ver os dados de propriedades e animais."""
    if db.execute(select(func.count()).select_from(Usuario)).scalar_one() > 0:
        raise HTTPException(
            status_code=403,
            detail="O cadastro de novos usuarios e feito por um administrador master, na tela de Usuarios.",
        )
    papel = db.execute(select(Papel).where(Papel.nome == MASTER)).scalar_one()
    usuario = Usuario(
        nome=payload.nome,
        email=payload.email,
        senha_hash=hash_senha(payload.senha),
        papel_id=papel.id,
    )
    db.add(usuario)
    confirmar(db)
    db.refresh(usuario)
    return usuario


@router.get("/registro-aberto")
def registro_aberto(db: Session = Depends(get_db)):
    """A tela de login usa isto para so oferecer 'criar conta' enquanto nao ha usuario."""
    total = db.execute(select(func.count()).select_from(Usuario)).scalar_one()
    return {"aberto": total == 0}


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """O campo 'username' do formulario OAuth2 recebe o e-mail do usuario."""
    usuario = db.execute(select(Usuario).where(Usuario.email == form.username)).scalar_one_or_none()
    if not usuario or not usuario.ativo or not verificar_senha(form.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha invalidos")
    token = criar_access_token(sub=str(usuario.id))
    return Token(access_token=token)


@router.get("/me", response_model=UsuarioRead)
def obter_usuario_atual(usuario: Usuario = Depends(get_current_user)):
    return usuario


@router.post("/alterar-senha", status_code=204)
def alterar_senha(
    payload: SenhaAlteracao,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Troca da propria senha. Exige a senha atual para nao permitir que uma
    sessao esquecida aberta em outra maquina troque a senha sozinha."""
    if not verificar_senha(payload.senha_atual, usuario.senha_hash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    usuario.senha_hash = hash_senha(payload.nova_senha)
    db.commit()
