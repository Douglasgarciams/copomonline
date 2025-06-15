# app/crud.py

import random
from datetime import datetime
from sqlalchemy.orm import Session
from . import models, schemas

# Adicione este import no topo do arquivo:
from .geodata import MAPA_BAIRRO_BATALHAO

# Substitua a função create_ocorrencia por esta:
def create_ocorrencia(db: Session, ocorrencia: schemas.OcorrenciaCreate):
    dados_da_ocorrencia = ocorrencia.dict()
    dados_da_ocorrencia['protocolo'] = f"{random.randint(100000, 999999)}"

    # --- NOVA LÓGICA DE GEOLOCALIZAÇÃO ---
    # Pega o bairro, normaliza (maiúsculas, sem espaços extras) para a busca
    bairro_para_busca = dados_da_ocorrencia.get("bairro", "").upper().strip()
    # Busca o batalhão no nosso mapa, retorna None se não encontrar
    batalhao = MAPA_BAIRRO_BATALHAO.get(bairro_para_busca, None)
    # Adiciona o batalhão encontrado aos dados
    dados_da_ocorrencia['batalhao_area'] = batalhao
    
    db_ocorrencia = models.Ocorrencia(**dados_da_ocorrencia)
    
    db.add(db_ocorrencia)
    db.commit()
    db.refresh(db_ocorrencia)
    return db_ocorrencia

# --- Funções de Leitura (Read) ---
def get_ocorrencia(db: Session, ocorrencia_id: int):
    return db.query(models.Ocorrencia).filter(models.Ocorrencia.id == ocorrencia_id).first()

def get_ocorrencias(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Ocorrencia).offset(skip).limit(limit).all()

# --- Funções de Atualização (Update) ---

# Em app/crud.py, substitua a função update_ocorrencia

def update_ocorrencia(db: Session, ocorrencia_id: int, ocorrencia: schemas.OcorrenciaUpdate):
    db_ocorrencia = db.query(models.Ocorrencia).filter(models.Ocorrencia.id == ocorrencia_id).first()

    if db_ocorrencia:
        update_data = ocorrencia.dict(exclude_unset=True)

        # --- LÓGICA FINAL E DEFINITIVA ---

        # 1. Se 'para_delegacia' está sendo marcado como True AGORA...
        if 'para_delegacia' in update_data and update_data['para_delegacia']:
            # ...nós gravamos nos campos de memória permanente. Isso só acontece uma vez.
            if not db_ocorrencia.historico_delegacia_flag:
                db_ocorrencia.historico_delegacia_flag = True
                db_ocorrencia.historico_delegacia_nome = update_data.get('delegacia_destino')

        # 2. Atualiza todos os campos "ao vivo" com os dados do formulário
        for key, value in update_data.items():
            setattr(db_ocorrencia, key, value)

        # 3. Regra de integridade: se o campo "ao vivo" foi desmarcado, limpa o destino "ao vivo"
        if not db_ocorrencia.para_delegacia:
            db_ocorrencia.delegacia_destino = None
        
        # 4. Lógica de timestamps (continua a mesma)
        if db_ocorrencia.viatura and db_ocorrencia.hora_visualizacao is None:
            db_ocorrencia.hora_visualizacao = datetime.utcnow()
        if db_ocorrencia.conclusao:
            db_ocorrencia.hora_conclusao = datetime.utcnow()
        else:
            db_ocorrencia.hora_conclusao = None
        
        db.commit()
        db.refresh(db_ocorrencia)
        
    return db_ocorrencia
    # Adicione esta função ao final de app/crud.py

def delete_all_ocorrencias(db: Session):
    # O método .delete() apaga todas as linhas da tabela especificada
    num_rows_deleted = db.query(models.Ocorrencia).delete()
    # Confirma a transação
    db.commit()
    # Retorna o número de linhas que foram apagadas
    return num_rows_deleted