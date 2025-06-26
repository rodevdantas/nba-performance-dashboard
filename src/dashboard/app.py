import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path 
from dotenv import load_dotenv 
import os 
import sys 

# %%

script_dir = Path(__file__).resolve().parent 
src_dir = script_dir.parent                
project_root_dir = src_dir.parent          

if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

dotenv_path = project_root_dir / '.env'
load_dotenv(dotenv_path)

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
    st.error("Erro: Variáveis de ambiente do banco de dados não carregadas. Verifique o arquivo .env e o caminho.")
    st.stop() 

from dashboard.db_setup import engine, SessionLocal, Jogador, EstatisticaTemporada

# %%

st.markdown("""
<style>
    /* Titulo e subtitulo */
    .title-container {
        background-color: #2a3a52; 
        padding: 30px 0;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    }
    .title-container h1 {
        color: white !important;
        font-size: 3.5em;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        text-align: center !important;
    }
    .title-container p {
        color: #e0e0e0 !important;
        font-size: 1.2em;
        text-align: center !important;
    }

    /* Tabela (st.dataframe) */
    div[data-testid="stDataFrame"] {
        border: 2px solid #2a3a52;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stDataFrame"] .st-ag-header {
        background-color: #2a3a52;
        color: white;
        font-weight: bold;
    }
    div[data-testid="stDataFrame"] .st-ag-column-headers,
    div[data-testid="stDataFrame"] .st-ag-table-body {
        border-bottom: 1px solid #4b6a8e !important;
        border-right: 1px solid #4b6a8e !important;
    }
    div[data-testid="stDataFrame"] .st-ag-cell,
    div[data-testid="stDataFrame"] .st-ag-header-cell {
        border-right: 1px solid #4b6a8e !important;
        border-bottom: 1px solid #4b6a8e !important;
    }

    div[data-testid="stDataFrame"] .st-ag-row:hover {
        background-color: #e6f7ff;
    }
    div[data-testid="stDataFrame"] .st-ag-row-selected {
        background-color: #cceeff;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #2a3a52;
    }

</style>
""", unsafe_allow_html=True)

# %%

@st.cache_data
def get_player_evolution_data():
    session = SessionLocal()
    try:
        query = """
        WITH EstatisticasComTemporadaAnterior AS (
            SELECT
                et.id_jogador,
                j.nome_jogador,
                et.temporada,
                et.pontos,
                et.assistencias,
                et.rebotes,
                et.jogos_jogados,
                LAG(et.pontos, 1, 0) OVER (PARTITION BY et.id_jogador ORDER BY et.temporada ASC) AS pontos_anterior,
                LAG(et.assistencias, 1, 0) OVER (PARTITION BY et.id_jogador ORDER BY et.temporada ASC) AS assistencias_anterior,
                LAG(et.rebotes, 1, 0) OVER (PARTITION BY et.id_jogador ORDER BY et.temporada ASC) AS rebotes_anterior,
                LAG(et.jogos_jogados, 1, 0) OVER (PARTITION BY et.id_jogador ORDER BY et.temporada ASC) AS jogos_jogados_anterior
            FROM
                estatisticas_temporada et
            JOIN
                jogadores j ON et.id_jogador = j.id_jogador
        ),
        EvolucaoDesempenho AS (
            SELECT
                id_jogador,
                nome_jogador,
                temporada,
                pontos,
                assistencias,
                rebotes,
                jogos_jogados,
                jogos_jogados_anterior,
                pontos_anterior,
                assistencias_anterior,
                rebotes_anterior,
                (pontos - pontos_anterior) AS diferenca_pontos,
                (assistencias - assistencias_anterior) AS diferenca_assistencias,
                (rebotes - rebotes_anterior) AS diferenca_rebotes
            FROM
                EstatisticasComTemporadaAnterior
            WHERE
                jogos_jogados >= 50
                AND jogos_jogados_anterior >= 50
        )
        SELECT
            id_jogador,
            nome_jogador,
            temporada AS temporada_atual,
            jogos_jogados AS jogos_jogados_atual,
            jogos_jogados_anterior,
            pontos AS pontos_atual,
            pontos_anterior,
            diferenca_pontos,
            assistencias AS assistencias_atual,
            assistencias_anterior,
            diferenca_assistencias,
            rebotes AS rebotes_atual,
            rebotes_anterior,
            diferenca_rebotes
        FROM
            EvolucaoDesempenho
        WHERE
            diferenca_pontos > 0 OR diferenca_assistencias > 0 OR diferenca_rebotes > 0
        ORDER BY
            diferenca_pontos DESC, diferenca_assistencias DESC, diferenca_rebotes DESC
        LIMIT 20;
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Erro ao buscar dados de evolução de jogadores: {e}")
        return pd.DataFrame()
    finally:
        session.close()

# %%

@st.cache_data
def get_all_seasons_from_db():
    session = SessionLocal()
    try:
        seasons = session.query(EstatisticaTemporada.temporada).distinct().order_by(EstatisticaTemporada.temporada.desc()).all()
        return [s[0] for s in seasons]
    except Exception as e:
        st.error(f"Erro ao buscar temporadas: {e}")
        return []
    finally:
        session.close()

# %%

@st.cache_data
def get_seasonal_player_stats(season):
    session = SessionLocal()
    try:
        query = f"""
        SELECT
            j.id_jogador,
            j.nome_jogador,
            et.temporada,
            et.jogos_jogados,
            et.pontos,
            et.assistencias,
            et.rebotes
        FROM
            estatisticas_temporada et
        JOIN
            jogadores j ON et.id_jogador = j.id_jogador
        WHERE
            et.temporada = '{season}'
            AND et.jogos_jogados > 0
        """
        df = pd.read_sql(query, engine)

        df['pontos_por_jogo'] = df['pontos'] / df['jogos_jogados']
        df['assistencias_por_jogo'] = df['assistencias'] / df['jogos_jogados']
        df['rebotes_por_jogo'] = df['rebotes'] / df['jogos_jogados']

        return df
    except Exception as e:
        st.error(f"Erro ao buscar estatísticas da temporada {season}: {e}")
        return pd.DataFrame()
    finally:
        session.close()
        
# %%

st.set_page_config(layout="wide", page_title="Dashboard - NBA")
st.markdown("""
<div class="title-container">
    <h1>Análise de Desempenho de Jogadores da NBA 🏀</h1>
    <p>Este é um dashboard de análise de dados da NBA. Objetivo: explorar a evolução de jogadores e estatísticas por temporada.</p>
</div>
""", unsafe_allow_html=True)

st.header("Evolução de Desempenho de Jogadores entre Temporadas")
st.markdown("Essa tabela mostra quais jogadores tiveram maior crescimento em suas estatísticas individuais (pontos, assistências e rebotes) de uma temporada para outra, destacando quem mais evoluiu em desempenho. Para cada jogador, são apresentados os dados da temporada anterior, da temporada atual em que a evolução ocorreu, e a diferença calculada dessas métricas (pontos, assistências e rebotes). Ajuda a identificar o momento de ascensão de jogadores e o impacto positivo que podem ter gerado em suas equipes, ressaltando o valor de seu desempenho. Para evitar erros na análise, somente jogadores com, no mínimo, 50 jogos disputados em ambas as temporadas foram escolhidos. ")

df_evolucao = get_player_evolution_data()

if not df_evolucao.empty:
    st.dataframe(df_evolucao, use_container_width=True)

    fig_pontos = px.bar(
        df_evolucao.head(10),
        x='nome_jogador',
        y='diferenca_pontos',
        title='Jogadores que mais evoluíram em pontos entre duas temporadas consecutivas:',
        labels={'nome_jogador': '', 'diferenca_pontos': 'Diferença de Pontos'},
        hover_data=['temporada_atual', 'pontos_atual', 'pontos_anterior']
    )
    st.plotly_chart(fig_pontos, use_container_width=True)
else:
    st.warning("Não foi possível carregar os dados de evolução dos jogadores.")

st.markdown("---")

st.header("Análise Detalhada por Temporada")

todas_temporadas = get_all_seasons_from_db()
if todas_temporadas:
    selected_season = st.selectbox("Selecione a temporada:", todas_temporadas)
else:
    st.warning("Nenhuma temporada encontrada no banco de dados.")
    selected_season = None

if selected_season:
    df_temporada = get_seasonal_player_stats(selected_season)

    if not df_temporada.empty:
        st.subheader(f"Melhores da Temporada ({selected_season})")

        metric_choice = st.selectbox(
            "Selecione a Métrica:",
            ("Pontos p/ jogo", "Assistências p/ jogo", "Rebotes p/ jogo")
        )

        top_n = st.slider("Mostrar número selecionado de jogadores:", 5, 20, 10)

        title_phrases = {
            "Pontos p/ jogo": 'com mais pontos',
            "Assistências p/ jogo": 'com mais assistências',
            "Rebotes p/ jogo": 'com mais rebotes'
        }

        chart_title = f"Top {top_n} - Jogadores {title_phrases[metric_choice]} na temporada {selected_season}:"
        if metric_choice == "Pontos p/ jogo":
            df_top_players = df_temporada.sort_values(by='pontos_por_jogo', ascending=False).head(top_n)
            y_metric = 'pontos_por_jogo'
        elif metric_choice == "Assistências p/ jogo":
            df_top_players = df_temporada.sort_values(by='assistencias_por_jogo', ascending=False).head(top_n)
            y_metric = 'assistencias_por_jogo'
        else:
            df_top_players = df_temporada.sort_values(by='rebotes_por_jogo', ascending=False).head(top_n)
            y_metric = 'rebotes_por_jogo'

        st.dataframe(df_top_players[['nome_jogador', 'jogos_jogados', y_metric]], use_container_width=True) # Adicionado use_container_width

        fig_top_players = px.bar(
            df_top_players,
            x='nome_jogador',
            y=y_metric,
            title=chart_title,
            labels={'nome_jogador': '', y_metric: metric_choice},
            hover_data=['jogos_jogados']
        )
        st.plotly_chart(fig_top_players, use_container_width=True)

        st.subheader(f"Estatísticas Agregadas da Temporada {selected_season}")
        avg_points = df_temporada['pontos_por_jogo'].mean()
        std_dev_points = df_temporada['pontos_por_jogo'].std()

        avg_assists = df_temporada['assistencias_por_jogo'].mean()
        std_dev_assists = df_temporada['assistencias_por_jogo'].std()

        avg_rebounds = df_temporada['rebotes_por_jogo'].mean()
        std_dev_rebounds = df_temporada['rebotes_por_jogo'].std()

        total_jogadores_na_temporada = df_temporada['id_jogador'].nunique()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(label="Média de Pontos por Jogo (por jogador)", value=f"{avg_points:.2f}")
            st.metric(label="Desvio Padrão de Pontos por Jogo (por jogador)", value=f"{std_dev_points:.2f}")
        with col2:
            st.metric(label="Média de Assistências por Jogo (por jogador)", value=f"{avg_assists:.2f}")
            st.metric(label="Desvio Padrão de Assistências por Jogo (por jogador)", value=f"{std_dev_assists:.2f}")
        with col3:
            st.metric(label="Média de Rebotes por Jogo (por jogador)", value=f"{avg_rebounds:.2f}")
            st.metric(label="Desvio Padrão de Rebotes por Jogo (por jogador)", value=f"{std_dev_rebounds:.2f}")

        st.metric(label="Total de Jogadores com Estatísticas Válidas", value=f"{total_jogadores_na_temporada}")

        with st.expander("O que é o Desvio Padrão e por que ele é importante?"):
            st.markdown("""
            O Desvio Padrão é uma medida estatística que indica o quanto os valores de um conjunto de dados se desviam ou se espalham em relação à média.

            * **Desvio Padrão Baixo:** Significa que os pontos por jogo dos jogadores estão geralmente próximos da média. Há menos variação no desempenho.
            * **Desvio Padrão Alto:** Significa que os pontos por jogo dos jogadores estão mais espalhados em torno da média, com uma variação maior no desempenho. Você tem jogadores que pontuam muito acima e muito abaixo da média.

            Por que é importante?
            Ele te dá uma ideia da consistência ou da variedade de desempenho na liga. Uma média alta com um desvio padrão baixo pode indicar uma liga com muitos pontuadores consistentes, enquanto uma média similar com um desvio padrão alto pode indicar alguns "superstars" e muitos jogadores com pontuação baixa.
            """)

        st.subheader(f"Relação entre Pontos e Assistências por Jogo na Temporada {selected_season}")
        fig_scatter = px.scatter(
            df_temporada,
            x='pontos_por_jogo',
            y='assistencias_por_jogo',
            size='jogos_jogados',
            hover_name='nome_jogador',
            title=f'Pontos vs. Assistências por Jogo - Temporada {selected_season}',
            labels={'pontos_por_jogo': 'Pontos por Jogo', 'assistencias_por_jogo': 'Assistências por Jogo', 'jogos_jogados': 'Jogos'},
            height=820
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    else:
        st.warning(f"Não há dados disponíveis para a temporada {selected_season} ou ocorreu um erro.")
else:
    st.info("Selecione uma temporada para ver as análises detalhadas.")