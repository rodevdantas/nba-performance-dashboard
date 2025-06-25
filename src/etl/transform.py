# src/etl/transform.py
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv 

dotenv_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path)

# %%

def carregar_dados_brutos(caminho_arquivo):
    try:
        df = pd.read_csv(caminho_arquivo)
        print(f"Dados brutos carregados de: {caminho_arquivo}")
        print(f"Número de linhas carregadas: {len(df)}")
        return df
    except FileNotFoundError:
        print(f"Erro: o arquivo '{caminho_arquivo}' não foi encontrado. Certifique-se de que a extração foi executada primeiro.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Erro ao carregar o arquivo CSV: {e}")
        return pd.DataFrame()
    
# %%

def transformar_dados_evolucao_jogador(df_bruto):
    if df_bruto.empty:
        print("O DataFrame bruto está vazio, sem dados para transformar.")
        return pd.DataFrame()

    print("\nIniciando a transformação dos dados...")

    colunas_originais = [
        'PLAYER_ID', 'PLAYER_NAME',
        'SEASON_ID', 'TEAM_ID',
        'TEAM_ABBREVIATION', 'GP',
        'PTS', 'AST', 'REB',
        'FG_PCT', 'FG3_PCT', 'FT_PCT'
    ]

    colunas_presentes = [col for col in colunas_originais if col in df_bruto.columns]
    df_transformado = df_bruto[colunas_presentes].copy()

    novos_nomes = {
        'PLAYER_ID': 'id_jogador',
        'PLAYER_NAME': 'nome_jogador',
        'SEASON_ID': 'temporada',
        'TEAM_ID': 'id_time',
        'TEAM_ABBREVIATION': 'sigla_time',
        'GP': 'jogos_jogados',
        'PTS': 'pontos',
        'AST': 'assistencias',
        'REB': 'rebotes',
        'FG_PCT': 'perc_arremessos_quadra',
        'FG3_PCT': 'perc_arremessos_3pts',
        'FT_PCT': 'perc_lances_livres'
    }
    df_transformado.rename(columns=novos_nomes, inplace=True)

    numeric_cols_to_check = ['jogos_jogados', 'pontos', 'assistencias', 'rebotes', 'perc_arremessos_quadra', 'perc_arremessos_3pts', 'perc_lances_livres']
    for col in numeric_cols_to_check:
        if col in df_transformado.columns:
            df_transformado[col] = pd.to_numeric(df_transformado[col], errors='coerce')

    if 'id_time' in df_transformado.columns:
        df_transformado['id_time'] = pd.to_numeric(df_transformado['id_time'], errors='coerce')

    df_transformado.dropna(subset=['id_jogador', 'temporada'], inplace=True)

    df_transformado.sort_values(by=['id_jogador', 'temporada', 'id_time'], ascending=[True, True, True], inplace=True)

    df_transformado.drop_duplicates(subset=['id_jogador', 'temporada'], keep='first', inplace=True)

    print("Dados transformados com sucesso!")
    print("\nPrimeiras 5 linhas do DataFrame transformado:")
    print(df_transformado.head())

    print("\nVerificando tipos de dados após a transformação:")
    print(df_transformado.info())

    return df_transformado

if __name__ == "__main__":
    nome_arquivo_csv_bruto = Path(__file__).resolve().parent.parent.parent / 'data' / 'raw' / 'nba_stats_brutas.csv'
    df_bruto = carregar_dados_brutos(nome_arquivo_csv_bruto)

    if not df_bruto.empty:
        df_transformado = transformar_dados_evolucao_jogador(df_bruto)

        if not df_transformado.empty:
            output_path_transformed = Path(__file__).resolve().parent.parent.parent / 'data' / 'processed' / 'nba_stats_transformadas.csv'
            output_path_transformed.parent.mkdir(parents=True, exist_ok=True) 
            df_transformado.to_csv(output_path_transformed, index=False)
            print(f"\nDados transformados salvos em '{output_path_transformed}'")
    else:
        print("DataFrame bruto está vazio. Transformação não realizada.")

    print("\nProcesso de transformação concluído.")
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            