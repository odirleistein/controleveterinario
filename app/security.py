"""
Utilitarios de autenticacao (hash de senha bcrypt, tokens JWT) e de autorizacao
por papel. SECRET_KEY vem do .env - nunca deixe hardcoded aqui.

Tres papeis (tabela papeis):
  MASTER        acesso total, inclusive usuarios
  ADMIN         grava os cadastros do dia a dia
  VISUALIZADOR  somente consulta
Alem do papel, quem nao e MASTER so enxerga as propriedades a que esta
vinculado - ver app/acesso.py.
"""
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ADMIN, MASTER, Usuario

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY nao encontrada. Verifique se o arquivo .env existe "
        "na raiz do projeto e contem a variavel SECRET_KEY."
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha, senha_hash)


def criar_access_token(sub: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": sub, "exp": expira}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais invalidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id = payload.get("sub")
        if usuario_id is None:
            raise credenciais_invalidas
    except JWTError:
        raise credenciais_invalidas

    usuario = db.get(Usuario, int(usuario_id))
    if not usuario or not usuario.ativo:
        raise credenciais_invalidas
    return usuario


def exigir_papel(*papeis: str):
    """Fabrica de dependencia: barra (403) quem nao tem um dos papeis dados."""

    def dependencia(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.papel.nome not in papeis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seu perfil nao tem permissao para esta operacao.",
            )
        return usuario

    return dependencia


# Rotas que gravam cadastros: VISUALIZADOR fica so na leitura.
exigir_escrita = exigir_papel(MASTER, ADMIN)
# Usuarios e configuracoes: so o administrador do sistema.
exigir_master = exigir_papel(MASTER)
