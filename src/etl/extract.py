import pandas as pd
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
import time
from pathlib import Path
from dotenv import load_dotenv 

dotenv_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path)

# %%

def obter_todos_os_jogadores():
    all_players = players.get_active_players()
    return all_players

# %%

def obter_estatisticas_carreira_jogador(player_id):
    try:
        career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
        df_stats = career_stats.get_data_frames()[0]
        return df_stats
    except Exception as e:
        print(f"Erro ao obter estatísticas para o jogador ID {player_id}: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    print("Iniciando a extração de jogadores da NBA")
    lista_de_jogadores = obter_todos_os_jogadores()

    if lista_de_jogadores:
        print(f"Total de jogadores ativos encontrados: {len(lista_de_jogadores)}")
        print(f"\nExtraindo estatísticas para todos os {len(lista_de_jogadores)} jogadores.")
        jogadores_selecionados = lista_de_jogadores

        todas_estatisticas = []
        for i, jogador in enumerate(jogadores_selecionados):
            player_id = jogador['id']
            player_name = jogador['full_name']
            print(f"Processando jogador {i+1}/{len(jogadores_selecionados)}: {player_name} (ID: {player_id})")

            stats_df = obter_estatisticas_carreira_jogador(player_id)
            if not stats_df.empty:
                stats_df['PLAYER_NAME'] = player_name
                todas_estatisticas.append(stats_df)

            time.sleep(0.3)

        if todas_estatisticas:
            df_final_estatisticas = pd.concat(todas_estatisticas, ignore_index=True)
            print("\nPrimeiras 5 linhas do DataFrame final de estatísticas:")
            print(df_final_estatisticas.head())

            output_path_raw = Path(__file__).resolve().parent.parent.parent / 'data' / 'raw' / 'nba_stats_brutas.csv'
            output_path_raw.parent.mkdir(parents=True, exist_ok=True) 
            df_final_estatisticas.to_csv(output_path_raw, index=False)
            print(f"\nDados de estatísticas salvos em '{output_path_raw}'")
        else:
            print("Nenhuma estatística de jogador foi extraída com sucesso.")
    else:
        print("Nenhum jogador ativo encontrado ou houve um erro na extração inicial.")

    print("\nExtração de dados concluída.")
     
    