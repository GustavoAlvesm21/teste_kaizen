import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import LabelEncoder

st.set_page_config(
    page_title="Pokedex Analitica",
    layout="wide",
)


################importando dados#########################

combates = pd.read_csv('combats.csv')
pokemons = pd.read_csv('pokemons.csv')
pokemons_data = pd.read_csv('pokemons_data.csv')



###################funcoes#########################

def pega_nome(id):
    nome = pokemons.loc[pokemons['id'] == id, 'name'].values
    if len(nome) > 0:
        return nome[0]
    return 'Desconhecido'

def pega_atributos(id):
    atributos = pokemons_data.loc[pokemons_data['id'] == id]
    if len(atributos) > 0:
        return atributos
    return None

def pokemons_string(ids):
    nomes = []
    for id in ids:
        nome = pokemons.loc[pokemons['id'] == id, 'name'].values
        if len(nome) > 0:
            nomes.append(nome[0])
        else:
            nomes.append('Desconhecido')
    return ', '.join(nomes)

def soma_atributos_especificos(nomes, atributo):
    total = 0
    for nome in nomes:
        id = pokemons.loc[pokemons['name'] == nome, 'id'].values
        if len(id) > 0:
            atributos = pega_atributos(id[0])
            if atributos is not None:
                total += atributos[atributo].values[0]            
        else:
            return 0

    return int(total)

def media_atributos_especificos(nomes, atributo):
    total = 0
    for nome in nomes:
        id = pokemons.loc[pokemons['name'] == nome, 'id'].values
        if len(id) > 0:
            atributos = pega_atributos(id[0])
            if atributos is not None:
                total += atributos[atributo].values[0]            
        else:
            return 0

    return total / len(nomes) if len(nomes) > 0 else 0

def calcula_pontuacao(tickers):
    ataque = soma_atributos_especificos(tickers, 'attack')
    defesa = soma_atributos_especificos(tickers, 'defense')
    velocidade = soma_atributos_especificos(tickers, 'speed')
    vida = soma_atributos_especificos(tickers, 'hp')
    sp_ataque = soma_atributos_especificos(tickers, 'sp_attack')
    sp_defesa = soma_atributos_especificos(tickers, 'sp_defense')

    corr_ataque = corr.loc[corr['atributo'] == 'attack', 'correlacao'].iloc[0]
    corr_defesa = corr.loc[corr['atributo'] == 'defense', 'correlacao'].iloc[0]
    corr_velocidade = corr.loc[corr['atributo'] == 'speed', 'correlacao'].iloc[0]
    corr_vida = corr.loc[corr['atributo'] == 'hp', 'correlacao'].iloc[0]
    corr_sp_ataque = corr.loc[corr['atributo'] == 'sp_attack', 'correlacao'].iloc[0]
    corr_sp_defesa = corr.loc[corr['atributo'] == 'sp_defense', 'correlacao'].iloc[0]

    pontuacao = (
        ataque * corr_ataque +
        defesa * corr_defesa +
        velocidade * corr_velocidade +
        vida * corr_vida +
        sp_ataque * corr_sp_ataque +
        sp_defesa * corr_sp_defesa
    )

    return round(float(pontuacao), 0)



####################################### manipulacao de dados #########################################

pokemons_data['generation'] = pokemons_data['generation'].replace({'Gen1': 1, 'Gen2': 2, 'Gen3': 3, 'Gen4': 4, 'Gen5': 5, 'Gen6': 6, 'Gen7': 7, 'Gen8': 8})
pokemons_data['generation'] = pokemons_data['generation'].astype(int)

total_vitorias = combates['winner'].value_counts()
total_f = combates['first_pokemon'].value_counts()
total_s = combates['second_pokemon'].value_counts()
total_participacoes = total_f.add(total_s, fill_value=0)

total_participacoes = total_participacoes.reset_index()
total_participacoes.columns = ['id', 'participacoes']
total_participacoes = total_participacoes.merge(pokemons[['id','name']], on='id')
total_participacoes = total_participacoes.set_index('id')
total_participacoes = total_participacoes[['participacoes']]

taxa_vitoria = total_vitorias / total_participacoes['participacoes']
taxa_vitoria = taxa_vitoria.reset_index()
taxa_vitoria.columns = ['id', 'win_rate']

taxa_vitoria = taxa_vitoria.set_index('id')
top_3 = total_vitorias.head(3)

df_para_corr = taxa_vitoria.merge(pokemons_data[['id','attack','defense','speed','hp', 'sp_attack', 'sp_defense', 'generation', 'legendary', 'types']], left_on='id', right_on='id', how='left')
infos_winrate = df_para_corr.copy()
df_para_corr['legendary'] = df_para_corr['legendary'].map({"true": 1, "false": 0})
df_para_corr = df_para_corr.drop(columns=['id'])

for col in df_para_corr.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    df_para_corr[col] = le.fit_transform(df_para_corr[col].astype(str))

corr = df_para_corr.corr(numeric_only=True)['win_rate'].sort_values(ascending=False)
corr = corr.reset_index()
corr.columns = ['atributo', 'correlacao']

nomes = pokemons['name'].tolist()

top_3 = top_3.reset_index()
top_3.columns = ['nome', 'vitorias']
top_3['nome'] = top_3['nome'].apply(pega_nome)

padrao = top_3.iloc[0:2]['nome'].tolist()

participacoes_win_rate = total_participacoes.merge(taxa_vitoria, left_on='id', right_on='id', how='left')
participacoes_win_rate = participacoes_win_rate.merge(pokemons[['id','name']], left_on='id', right_on='id', how='left')

geracoes_vitoriosas = pokemons_data.merge(taxa_vitoria, left_on='id', right_on='id', how='left')
geracoes_vitoriosas = geracoes_vitoriosas.groupby('generation')['win_rate'].mean().sort_values(ascending=False)

infos_winrate = infos_winrate.groupby('types')['win_rate'].mean().sort_values(ascending=False)
infos_winrate = infos_winrate.head(5)

pokemon_data_win_rate = pokemons_data.merge(taxa_vitoria, left_on='id', right_on='id', how='left')

########################### Layout #######################################

aba1, aba2 = st.tabs(["Analise", "Monte seu time"])

with aba1:

    """
    # :material/query_stats: Análise dos Pokémons
    
    """

    #Metrica exibidas no topo da aba 1
    with st.container(horizontal=True, gap="medium"):
        cols = st.columns(2, gap="medium", width=850, border=True)
        with cols[0]:
            st.metric(
                label="Maior Vencedor",
                value=top_3.iloc[0]['nome'],
                delta=f"Vitorias: {top_3.iloc[0]['vitorias']}",
                width="content"
            )
        with cols[1]:
            st.metric(
                label="Mais participações em lutas",
                value=participacoes_win_rate.loc[participacoes_win_rate['participacoes'].idxmax()]['name'],
                delta=f"Participações: {participacoes_win_rate['participacoes'].max()}",
                width="content"
            )
        cols = st.columns(2, gap="medium", width=820, border=True)
        with cols[0]:
            st.metric(
                label="Melhor taxa de vitória",
                value=participacoes_win_rate.loc[participacoes_win_rate['win_rate'].idxmax()]['name'],
                delta=f"Taxa de vitória: {participacoes_win_rate['win_rate'].max():.2%}",
                width="content"
            )
        with cols[1]:
            st.metric(
                label="Pior taxa de vitória",
                value=participacoes_win_rate.loc[participacoes_win_rate['win_rate'].idxmin()]['name'],
                delta=f"Taxa de vitória: {participacoes_win_rate['win_rate'].min():.2%}",
                width="content"
            )
    
    with st.container(horizontal=True, gap="medium"):
        cols = st.columns(2, gap="medium", width="stretch", border=True)
        with cols[0]:
            fig_corr = px.bar(corr.drop(index=0), x='atributo', y='correlacao', title='Correlação dos Atributos com a Taxa de Vitória', labels={'atributo': 'Atributo', 'correlacao': 'Correlação'})
            st.plotly_chart(fig_corr, use_container_width=True)
        with cols[1]:
            fig_winrate = px.bar(infos_winrate, x=infos_winrate.index, y='win_rate', title='Top 5 Tipos de Pokémons com Maior Taxa de Vitória', labels={'index': 'Tipo', 'win_rate': 'Taxa de Vitória'})
            st.plotly_chart(fig_winrate, use_container_width=True)
        with cols[0]:
            fig_geracoes = px.pie(geracoes_vitoriosas, values='win_rate', names=geracoes_vitoriosas.index, title='Taxa de Vitória Média por Geração', labels={'index': 'Geração', 'win_rate': 'Taxa de Vitória'})
            st.plotly_chart(fig_geracoes, use_container_width=True)
        with cols[1]:
            lendarios = infos_winrate = df_para_corr.groupby('legendary')['win_rate'].mean().sort_values(ascending=False)
            lendarios.index = lendarios.index.map({1: 'Lendário', 0: 'Não Lendário'})
            fig_lendarios = px.pie(lendarios, values='win_rate', names=lendarios.index, title='Taxa de Vitória Média: Lendários vs Não Lendários', labels={'index': 'Categoria', 'win_rate': 'Taxa de Vitória'})
            st.plotly_chart(fig_lendarios, use_container_width=True)

    """
    Dados Brutos dos Pokémons
    """

    pokemon_data_win_rate
with aba2:

    """
    # :crossed_swords: Monte seu time de Pokémons e compare suas estatísticas!
    
    """

    colunas = st.columns(2)

    if "tickers_input" not in st.session_state:
        st.session_state.tickers_input = st.query_params.get("pokemons", padrao)
    else:
        st.query_params.pop("pokemons", None)

    esq_1 = colunas[0].container(border=True, height="stretch", vertical_alignment="center")

    with esq_1:
        tickers = st.multiselect(
            "Selecione os Pokémons (Esquerda)",
            options=nomes,
            default=st.session_state.tickers_input,
            placeholder="Selecione os Pokémons para analisar",
            accept_new_options=True,
            key="multiselect_esq"
        )

    esq_2 = colunas[0].container(
        border=True, height="stretch", vertical_alignment="center"
    )


    dir_1 = colunas[1].container(border=True, height="stretch", vertical_alignment="center")

    with dir_1:
        tickers_2 = st.multiselect(
            "Selecione os Pokémons (Direita)",
            options=nomes,
            default=st.session_state.tickers_input,
            placeholder="Selecione os Pokémons para analisar",
            accept_new_options=True,
            key="multiselect_dir"
        )

    dir_2 = colunas[1].container(
        border=True, height="stretch", vertical_alignment="center"
    )

    with esq_2:
        cols_esq_2 = st.columns(2)
        cols_esq_2[0].metric(
            label="Ataque do(s) Pokémon(s) Selecionado(s)",
            value=soma_atributos_especificos(tickers, 'attack'),
            delta=soma_atributos_especificos(tickers, 'attack') - soma_atributos_especificos(tickers_2,'attack'),
        )
        cols_esq_2[1].metric(
            label="Defesa do(s) Pokémon(s) Selecionado(s)",
            value=soma_atributos_especificos(tickers, 'defense'),
            delta=soma_atributos_especificos(tickers, 'defense') - soma_atributos_especificos(tickers_2,'defense'),
        )
        cols_esq_2[0].metric(
            label="Velocidade do(s) Pokémon(s) Selecionado(s)",
            value=soma_atributos_especificos(tickers, 'speed'),
            delta=soma_atributos_especificos(tickers, 'speed') - soma_atributos_especificos(tickers_2,'speed'),
        )
        cols_esq_2[1].metric(
            label="Vida do(s) Pokémon(s) Selecionado(s)",
            value=soma_atributos_especificos(tickers, 'hp'),
            delta=soma_atributos_especificos(tickers, 'hp') - soma_atributos_especificos(tickers_2,'hp'),
        )
        cols_esq_2[0].metric(
            label="Ataque especial do(s) Pokémon(s) Selecionado(s)",
            value=soma_atributos_especificos(tickers, 'sp_attack'),
            delta=soma_atributos_especificos(tickers, 'sp_attack') - soma_atributos_especificos(tickers_2,'sp_attack'),
        )
        cols_esq_2[1].metric(
            label="Defesa especial do(s) Pokémon(s) Selecionado(s)",
            value=soma_atributos_especificos(tickers, 'sp_defense'),
            delta=soma_atributos_especificos(tickers, 'sp_defense') - soma_atributos_especificos(tickers_2,'sp_defense'),
        )
        cols_esq_2[0].metric(
            label="Media da Geração do(s) Pokémon(s) Selecionado(s)",
            value=media_atributos_especificos(tickers, 'generation'),
            delta=media_atributos_especificos(tickers, 'generation') - media_atributos_especificos(tickers_2,'generation'),
        )
        cols_esq_2[1].metric(
            label="Pontuação Total do(s) Pokémon(s) Selecionado(s)",
            value=int(calcula_pontuacao(tickers)),
            delta=int(calcula_pontuacao(tickers)) - int(calcula_pontuacao(tickers_2)),
        )



    with dir_2:
        cols_dir_2 = st.columns(2)
        cols_dir_2[0].metric(
            label="Ataque do(s) Pokémon(s) Selecionado(s)",
            value=soma_atributos_especificos(tickers_2, 'attack'),
            delta=soma_atributos_especificos(tickers_2, 'attack') - soma_atributos_especificos(tickers, 'attack'),
        )
        cols_dir_2[1].metric(
            label="Defesa do(s) Pokémon(s) Selecionado(s)",
            value=soma_atributos_especificos(tickers_2, 'defense'),
            delta=soma_atributos_especificos(tickers_2, 'defense') - soma_atributos_especificos(tickers, 'defense'),
        )
        cols_dir_2[0].metric(
            label="Velocidade do(s) Pokémon(s) Selecionado(s)",
            value=soma_atributos_especificos(tickers_2, 'speed'),
            delta=soma_atributos_especificos(tickers_2, 'speed') - soma_atributos_especificos(tickers, 'speed'),
        )
        cols_dir_2[1].metric(
            label="Vida do(s) Pokémon(s) Selecionado(s)",
            value=soma_atributos_especificos(tickers_2, 'hp'),
            delta=soma_atributos_especificos(tickers_2, 'hp') - soma_atributos_especificos(tickers, 'hp'),
        )
        cols_dir_2[0].metric(
            label="Ataque especial do(s) Pokémon(s) Selecionado(s)",
            value=soma_atributos_especificos(tickers_2, 'sp_attack'),
            delta=soma_atributos_especificos(tickers_2, 'sp_attack') - soma_atributos_especificos(tickers, 'sp_attack'),
        )
        cols_dir_2[1].metric(
            label="Defesa especial do(s) Pokémon(s) Selecionado(s)",
            value=soma_atributos_especificos(tickers_2, 'sp_defense'),
            delta=soma_atributos_especificos(tickers_2, 'sp_defense') - soma_atributos_especificos(tickers, 'sp_defense'),
        )
        cols_dir_2[0].metric(
            label="Media da Geração do(s) Pokémon(s) Selecionado(s)",
            value=media_atributos_especificos(tickers_2, 'generation'),
            delta=media_atributos_especificos(tickers_2, 'generation') - media_atributos_especificos(tickers, 'generation'),
        )
        cols_dir_2[1].metric(
            label="Pontuação Total do(s) Pokémon(s) Selecionado(s)",
            value=int(calcula_pontuacao(tickers_2)),
            delta=int(calcula_pontuacao(tickers_2)) - int(calcula_pontuacao(tickers)),
        )

    """
    Pokemons Disponíveis para Seleção
    """


    pokemon_data_win_rate
