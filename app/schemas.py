# app/schemas.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class OcorrenciaCreate(BaseModel):
    # (Esta classe não muda, pois os campos de despacho são adicionados depois)
    logradouro: str
    fato: str
    telefone: str
    historico: str
    atendente: str
    empenho_pm: bool = False
    empenho_bm: bool = False
    empenho_pc: bool = False
    bairro: Optional[str] = None
    referencia: Optional[str] = None
    solicitante: Optional[str] = None

class OcorrenciaUpdate(BaseModel):
    # (Adicionamos os novos campos aqui, pois eles serão atualizados)
    logradouro: Optional[str] = None
    bairro: Optional[str] = None
    referencia: Optional[str] = None
    solicitante: Optional[str] = None
    fato: Optional[str] = None
    telefone: Optional[str] = None
    historico: Optional[str] = None
    atendente: Optional[str] = None
    empenho_pm: Optional[bool] = None
    empenho_bm: Optional[bool] = None
    empenho_pc: Optional[bool] = None
    # --- NOVOS ---
    viatura: Optional[str] = None
    conclusao: Optional[str] = None
    analista_empenho: Optional[str] = None
    para_delegacia: Optional[bool] = None
    delegacia_destino: Optional[str] = None
    batalhao_area: Optional[str] = None

# Esta é a versão final da classe Ocorrencia em app/schemas.py
class Ocorrencia(OcorrenciaCreate):
    id: int
    protocolo: str  # O novo protocolo que adicionamos
    data_registro: datetime

    # Campos de despacho que podem ser nulos
    viatura: Optional[str] = None
    hora_visualizacao: Optional[datetime] = None
    conclusao: Optional[str] = None
    hora_conclusao: Optional[datetime] = None
    analista_empenho: Optional[str] = None
    para_delegacia: bool
    delegacia_destino: Optional[str] = None
    batalhao_area: Optional[str] = None

    # Configuração para funcionar com o SQLAlchemy
    model_config = ConfigDict(from_attributes=True)