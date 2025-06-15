# app/models.py - VERSÃO CORRIGIDA PARA TIDB/MYSQL

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text # Adicionamos 'Text' aqui
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ocorrencia(Base):
    __tablename__ = "ocorrencias"

    id = Column(Integer, primary_key=True, index=True)
    data_registro = Column(DateTime(timezone=True), server_default=func.now())
    protocolo = Column(String(10), unique=True, index=True, nullable=False)
    logradouro = Column(String(255), nullable=False)
    bairro = Column(String(100), nullable=True)
    referencia = Column(String(255), nullable=True)
    solicitante = Column(String(150), nullable=True)
    fato = Column(String(150), nullable=False)
    telefone = Column(String(20), nullable=False)
    atendente = Column(String(100), nullable=False)
    empenho_pm = Column(Boolean, default=False)
    empenho_bm = Column(Boolean, default=False)
    empenho_pc = Column(Boolean, default=False)
    
    # --- NOVOS CAMPOS DE DESPACHO ---
    viatura = Column(String(100), nullable=True)
    hora_visualizacao = Column(DateTime(timezone=True), nullable=True)
    analista_empenho = Column(String(100), nullable=True)
    para_delegacia = Column(Boolean, default=False, nullable=False)
    delegacia_destino = Column(String(100), nullable=True)
    batalhao_area = Column(String(50), nullable=True)

    # --- CAMPOS CORRIGIDOS DE STRING PARA TEXT ---
    historico = Column(Text, nullable=False)
    conclusao = Column(Text, nullable=True)
    hora_conclusao = Column(DateTime(timezone=True), nullable=True)

    # --- CAMPOS DE MEMÓRIA PERMANENTE ---
    historico_delegacia_flag = Column(Boolean, default=False)
    historico_delegacia_nome = Column(String(100), nullable=True)