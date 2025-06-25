import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from pathlib import Path
from dotenv import load_dotenv
import sys

# %%

script_dir = Path(__file__).resolve().parent
src_dir = script_dir.parent
project_root_dir = src_dir.parent

if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

dotenv_path = project_root_dir / '.env'
load_dotenv(dotenv_path)

from dashboard.db_setup import engine, SessionLocal, Jogador, EstatisticaTemporada

# %%

def carregar_para_mysql(df):
    if df.empty:
        print("DataFrame vazio, sem dados para carregar.")
        return

    session = SessionLocal()
    try:
        session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        session.execute(text(f"TRUNCATE TABLE {EstatisticaTemporada.__tablename__};"))
        session.execute(text(f"TRUNCATE TABLE {Jogador.__tablename__};"))
        session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        session.commit()
        print("Tabelas limpas com sucesso.")
    except Exception as e:
        session.rollback()
        print(f"Erro ao limpar tabelas: {e}")

    print("\nCarregando dados para a tabela 'jogadores'...")
    df_jogadores = df[['id_jogador', 'nome_jogador']].drop_duplicates().copy()

    jogadores_processados = 0
    for index, row in df_jogadores.iterrows():
        jogador = Jogador(id_jogador=row['id_jogador'], nome_jogador=row['nome_jogador'])
        try:
            session.merge(jogador)
            jogadores_processados += 1
        except IntegrityError:
            session.rollback()
            print(f"Erro de integridade ao adicionar jogador {row['nome_jogador']}.")
            
    session.commit()
    print(f"Total de {jogadores_processados} jogadores processados (inseridos/atualizados) em 'jogadores'.")
    print("\nCarregando dados para a tabela 'estatisticas_temporada'...")
    estatisticas_para_adicionar = []
    for index, row in df.iterrows():
        stat = EstatisticaTemporada(
            id_jogador=row['id_jogador'],
            temporada=row['temporada'],
            id_time=row['id_time'],
            sigla_time=row['sigla_time'],
            jogos_jogados=row['jogos_jogados'],
            pontos=row['pontos'],
            assistencias=row['assistencias'],
            rebotes=row['rebotes'],
            perc_arremessos_quadra=row['perc_arremessos_quadra'],
            perc_arremessos_3pts=row['perc_arremessos_3pts'],
            perc_lances_livres=row['perc_lances_livres']
        )
        estatisticas_para_adicionar.append(stat)
    
    try:
        session.add_all(estatisticas_para_adicionar)
        session.commit()
        print(f"Total de {len(estatisticas_para_adicionar)} estatísticas inseridas em 'estatisticas_temporada'.")
    except IntegrityError as e:
        session.rollback()
        print(f"Erro de integridade ao carregar estatísticas: {e}. Revertendo.")
    except Exception as e:
        session.rollback()
        print(f"Erro inesperado ao carregar estatísticas: {e}. Revertendo.")
    finally:
        session.close()

if __name__ == "__main__":
    nome_arquivo_csv_transformado = project_root_dir / 'data' / 'processed' / 'nba_stats_transformadas.csv'

    try:
        df_transformado = pd.read_csv(nome_arquivo_csv_transformado)
        print(f"Dados transformados carregados de: {nome_arquivo_csv_transformado}")
        print(f"Número de linhas carregadas: {len(df_transformado)}")
    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo_csv_transformado}' não foi encontrado.")
        df_transformado = pd.DataFrame()
    except Exception as e:
        print(f"Erro ao carregar o arquivo CSV: {e}")
        df_transformado = pd.DataFrame()

    if not df_transformado.empty:
        carregar_para_mysql(df_transformado)
    else:
        print("DataFrame transformado está vazio. Carga no MySQL não realizada.")

    print("\nProcesso de carga no MySQL concluído.")