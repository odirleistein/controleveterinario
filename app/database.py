"""
Configuracao da conexao com o PostgreSQL via SQLAlchemy.
DATABASE_URL vem do arquivo .env (nunca deixe a senha hardcoded aqui).
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL nao encontrada. Verifique se o arquivo .env existe "
        "na raiz do projeto e contem a variavel DATABASE_URL."
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency do FastAPI: abre uma sessao por requisicao e fecha ao final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
