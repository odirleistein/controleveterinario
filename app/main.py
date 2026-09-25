"""
Ponto de entrada da API do controle veterinario. Rode com:
    uvicorn app.main:app --reload

Em producao local (sem --reload), este processo tambem serve o build do
frontend (frontend/dist) no mesmo host:porta - ver o bloco no fim do arquivo.
"""
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers import (
    animais, auth, dashboard, geografia, pesagens, pessoas, propriedades, usuarios, veterinarios,
)
from app.security import get_current_user

app = FastAPI(
    title="API Controle Veterinario",
    description="Backend do controle veterinario: propriedades, animais, veterinarios e pessoas.",
    version="0.1.0",
)

# Frontend roda em outra origem (Vite dev server na 5175); libera CORS so para ela.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

# Todas as demais rotas exigem login. O controle fino fica em cada rota: gravar
# exige MASTER/ADMIN (security.exigir_escrita) e o recorte de propriedades por
# usuario esta em app/acesso.py.
logado = [Depends(get_current_user)]
app.include_router(usuarios.router, dependencies=logado)
app.include_router(usuarios.router_papeis, dependencies=logado)
app.include_router(geografia.router_estados, dependencies=logado)
app.include_router(geografia.router_cidades, dependencies=logado)
app.include_router(geografia.router_bairros, dependencies=logado)
app.include_router(geografia.router_localidades, dependencies=logado)
app.include_router(geografia.router_ceps, dependencies=logado)
app.include_router(pessoas.router, dependencies=logado)
app.include_router(animais.router_tipos, dependencies=logado)
app.include_router(animais.router_racas, dependencies=logado)
app.include_router(animais.router, dependencies=logado)
app.include_router(pesagens.router_padroes, dependencies=logado)
app.include_router(pesagens.router, dependencies=logado)
app.include_router(propriedades.router, dependencies=logado)
app.include_router(veterinarios.router, dependencies=logado)
app.include_router(dashboard.router, dependencies=logado)


@app.get("/api/status")
def status():
    return {"status": "ok", "mensagem": "API Controle Veterinario rodando"}


@app.get("/health/db")
def verificar_conexao_banco(db: Session = Depends(get_db)):
    """Endpoint simples para confirmar que a API consegue falar com o Postgres."""
    db.execute(text("SELECT 1"))
    return {"database": "conectado", "nome_banco": "controleveterinario"}


# ---------------------------------------------------------------------
# Frontend (build estatico) - so ativa se "frontend/dist" existir, ou seja,
# depois de rodar "npm run build". Em dev com "npm run dev" (Vite na porta
# 5175) este bloco fica inerte e nada muda.
# ---------------------------------------------------------------------
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="frontend-assets")

    @app.get("/{caminho_completo:path}", include_in_schema=False)
    def servir_frontend(caminho_completo: str):
        """Serve o SPA: arquivo estatico se existir (favicon, etc.), senao
        index.html - o React Router cuida do resto no navegador."""
        candidato = FRONTEND_DIST / caminho_completo
        if caminho_completo and candidato.is_file():
            return FileResponse(candidato)
        return FileResponse(FRONTEND_DIST / "index.html")
