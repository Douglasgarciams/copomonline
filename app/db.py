# app/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .models import Base

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Pega a URL do banco de dados a partir da variável de ambiente
DATABASE_URL = os.getenv("DATABASE_URL")

# --- Linha de DEBUG que adicionamos ---
print(f"DEBUG: URL DO BANCO DE DADOS CARREGADA -> {DATABASE_URL}")
# ------------------------------------

# Cria o "motor" do SQLAlchemy.
engine = create_engine(DATABASE_URL)

# Cria uma classe SessionLocal para criar as sessões com o banco.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)