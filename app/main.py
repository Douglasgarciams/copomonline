# app/main.py - VERSÃO FINAL COM MÉTODO DE FILTRO ROBUSTO

from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import pytz
from datetime import datetime

from . import crud, models, schemas
from .db import SessionLocal, engine
from fastapi import WebSocket
from fastapi.responses import JSONResponse
from .websocket_manager import manager # Importa nosso gerenciador
from .geodata import MAPA_BAIRRO_BATALHAO

# 1. Cria a instância da aplicação
app = FastAPI(title="COPOM Online")

# 2. Define nossa função de filtro para converter datas
def format_datetime_local(utc_dt: datetime):
    if utc_dt is None: return "" 
    local_tz = pytz.timezone("America/Campo_Grande")
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_dt.strftime('%d/%m/%Y %H:%M:%S')

# 3. CRIA o objeto de templates e JÁ PASSA o filtro para ele na criação
#    Esta é a mudança crucial que resolve o problema do 'reload'
templates = Jinja2Templates(
    directory="templates",
    context_processors=[lambda request: {"to_local": format_datetime_local}]
)

# 4. Define o evento de inicialização para criar as tabelas
@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)

# 5. Monta o diretório de arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROTAS DA INTERFACE WEB ---

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/atendimento")

@app.get("/atendimento", response_class=HTMLResponse)
async def pagina_atendimento(request: Request):
    protocolo = request.query_params.get('protocolo', None)
    return templates.TemplateResponse("atendimento.html", {"request": request, "protocolo": protocolo})

@app.get("/ocorrencias_view", response_class=HTMLResponse)
async def pagina_listar_ocorrencias(request: Request, db: Session = Depends(get_db)):
    ocorrencias = crud.get_ocorrencias(db)
    return templates.TemplateResponse("ocorrencias_view.html", {"request": request, "ocorrencias": ocorrencias})

@app.get("/ocorrencia_despacho/{ocorrencia_id}", response_class=HTMLResponse)
async def pagina_detalhe_ocorrencia(request: Request, ocorrencia_id: int, db: Session = Depends(get_db)):
    db_ocorrencia = crud.get_ocorrencia(db, ocorrencia_id=ocorrencia_id)
    if db_ocorrencia is None:
        raise HTTPException(status_code=404, detail="Ocorrência não encontrada")
    return templates.TemplateResponse("despacho_detalhe.html", {"request": request, "ocorrencia": db_ocorrencia})

# Em app/main.py, substitua a sua função com erro por esta versão:

@app.post("/ocorrencias_form")
async def criar_ocorrencia_form(
    db: Session = Depends(get_db),
    logradouro: str = Form(...),
    fato: str = Form(...),
    telefone: str = Form(...),
    historico: str = Form(...),
    atendente: str = Form(...),
    bairro: Optional[str] = Form(None),
    referencia: Optional[str] = Form(None),
    solicitante: Optional[str] = Form(None),
    empenho_pm: bool = Form(False),
    empenho_bm: bool = Form(False),
    empenho_pc: bool = Form(False)
):
    ocorrencia_schema = schemas.OcorrenciaCreate(
        logradouro=logradouro, fato=fato, telefone=telefone, historico=historico,
        atendente=atendente, bairro=bairro, referencia=referencia, solicitante=solicitante,
        empenho_pm=empenho_pm, empenho_bm=empenho_bm, empenho_pc=empenho_pc
    )
    nova_ocorrencia = crud.create_ocorrencia(db=db, ocorrencia=ocorrencia_schema)
    
    # Avisa todos os clientes conectados sobre a nova ocorrência
    await manager.broadcast(f"Nova ocorrência recebida: #{nova_ocorrencia.protocolo}")

    redirect_url = f"/atendimento?protocolo={nova_ocorrencia.protocolo}"
    return RedirectResponse(url=redirect_url, status_code=303)

# Em app/main.py, substitua a função inteira por esta versão:

@app.post("/ocorrencia_despacho/{ocorrencia_id}/update")
async def atualizar_ocorrencia_form(
    ocorrencia_id: int,
    db: Session = Depends(get_db),
    viatura: Optional[str] = Form(None),
    analista_empenho: Optional[str] = Form(None),
    conclusao: Optional[str] = Form(None),
    para_delegacia: bool = Form(False),
    delegacia_destino: Optional[str] = Form(None),
    empenho_pm: bool = Form(False),
    empenho_bm: bool = Form(False),
    empenho_pc: bool = Form(False),
    batalhao_area: Optional[str] = Form(None) # <-- PARÂMETRO NOVO AQUI
):
    ocorrencia_update_schema = schemas.OcorrenciaUpdate(
        viatura=viatura,
        analista_empenho=analista_empenho,
        conclusao=conclusao,
        para_delegacia=para_delegacia,
        delegacia_destino=delegacia_destino,
        empenho_pm=empenho_pm,
        empenho_bm=empenho_bm,
        empenho_pc=empenho_pc,
        batalhao_area=batalhao_area # <-- E SENDO PASSADO AQUI
    )
    crud.update_ocorrencia(db, ocorrencia_id=ocorrencia_id, ocorrencia=ocorrencia_update_schema)
    return RedirectResponse(url="/ocorrencias_view", status_code=303)

@app.post("/ocorrencias/delete_all")
async def deletar_todas_ocorrencias_form(db: Session = Depends(get_db)):
    crud.delete_all_ocorrencias(db)
    return RedirectResponse(url="/ocorrencias_view", status_code=303)

    # Adicione esta rota em app/main.py

@app.get("/relatorio/completo", response_class=HTMLResponse)
async def pagina_relatorio_completo(request: Request, db: Session = Depends(get_db)):
    # Busca todas as ocorrências
    ocorrencias = crud.get_ocorrencias(db)
    # Renderiza o novo template de relatório
    return templates.TemplateResponse("relatorio_completo.html", {"request": request, "ocorrencias": ocorrencias})

    # Adicione esta rota em app/main.py

@app.websocket("/ws/despacho")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Apenas mantém a conexão viva
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)
        # Adicione este novo endpoint no final de app/main.py

# Adicione este novo endpoint no final de app/main.py

# Em app/main.py, substitua a função search_bairros existente

@app.get("/api/search-bairros/")
async def search_bairros(q: Optional[str] = None):
    if not q:
        return []
    
    termo_busca = q.upper().strip()
    
    # Agora, criamos uma lista de dicionários (objetos) com bairro e batalhão
    resultados = [
        {"bairro": bairro, "batalhao": batalhao}
        for bairro, batalhao in MAPA_BAIRRO_BATALHAO.items()
        if termo_busca in bairro
    ]
    
    return resultados[:10]