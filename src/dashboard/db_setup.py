
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, ForeignKey, text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from dotenv import load_dotenv 
from pathlib import Path
import os
import streamlit as st 
# %%

dotenv_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path)

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("Erro: Variáveis de ambiente do banco de dados não carregadas. Verifique o arquivo .env e o caminho.")

Base = declarative_base()

class Jogador(Base):
    __tablename__ = 'jogadores'
    id_jogador = Column(Integer, primary_key=True)
    nome_jogador = Column(String(255), nullable=False) # Aumentei para 255 (VARCHAR no MySQL)
    estatisticas = relationship("EstatisticaTemporada", back_populates="jogador")

class EstatisticaTemporada(Base):
    __tablename__ = 'estatisticas_temporada'
    id_estatistica = Column(Integer, primary_key=True, autoincrement=True)
    id_jogador = Column(Integer, ForeignKey('jogadores.id_jogador'), nullable=False)
    temporada = Column(String(10), nullable=False)
    id_time = Column(Integer, nullable=False)
    sigla_time = Column(String(10))
    jogos_jogados = Column(Integer, nullable=False)
    pontos = Column(Integer, nullable=False)
    assistencias = Column(Integer, nullable=False)
    rebotes = Column(Integer, nullable=False)
    perc_arremessos_quadra = Column(DECIMAL(5,3), nullable=False)
    perc_arremessos_3pts = Column(DECIMAL(5,3), nullable=False)
    perc_lances_livres = Column(DECIMAL(5,3), nullable=False)
    jogador = relationship("Jogador", back_populates="estatisticas")

try:
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as connection:
        pass 

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print(f"Conectado ao servidor MySQL em '{DB_HOST}' via SQLAlchemy (Módulo db_setup).")
except Exception as e:
    raise ConnectionError(f"Erro CRÍTICO ao conectar ao banco de dados no módulo db_setup: {e}")