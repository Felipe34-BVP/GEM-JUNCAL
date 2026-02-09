import streamlit as st
import sqlite3
import pandas as pd
import os
import math
import plotly.express as px
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="GEM Juncal - Situação", layout="wide")

# Ajuste de caminho do banco
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_db = os.path.join(os.path.dirname(diretorio_atual), 'DATABASE.db')

def conectar_bd():
    return sqlite3.connect(caminho_db)

# --- CSS CUSTOMIZADO (TEMA ADAPTÁVEL) ---
st.markdown("""
<style>
    /* Estilização das Métricas (Cards de cima) */
    [data-testid="stMetricValue"] {
        color: #00CC96 !important;
        font-weight: bold;
    }
    [data-testid="stMetric"] {
        background: var(--secondary-background-color);
        padding: 15px;
        border-radius: 15px;
        border-left: 5px solid #00CC96;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }

    /* Estilização das Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: var(--secondary-background-color);
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        border: 1px solid rgba(0, 204, 150, 0.1);
    }
    .stTabs [aria-selected="true"] {
        background-color: #00CC96 !important;
        color: white !important;
    }

    /* Barra de Progresso Customizada */
    .stProgress > div > div > div > div {
        background-color: #00CC96;
    }

    /* Estilização de Tabelas e Informações */
    .stTable {
        background: var(--secondary-background-color);
        border-radius: 15px;
        overflow: hidden;
    }
    
    .stInfo {
        border-left: 6px solid #00CC96 !important;
        background-color: var(--secondary-background-color) !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Acompanhamento e Predição - GEM Juncal")

# 1. Seleção do Aluno - Agora buscando também a coluna ano_teste
conn = conectar_bd()
df_alunos = pd.read_sql_query("SELECT id, nome_aluno, instrumento, teste_para, semana_teste, ano_teste FROM Alunos", conn)
conn.close()

if not df_alunos.empty:
    aluno_selecionado = st.selectbox("Selecione o Aluno", df_alunos['nome_aluno'].tolist())
    dados_aluno = df_alunos[df_alunos['nome_aluno'] == aluno_selecionado].iloc[0]
    
    id_aluno = int(dados_aluno['id'])
    instrumento = dados_aluno['instrumento']
    objetivo = dados_aluno['teste_para']
    semana_alvo = int(dados_aluno['semana_teste'])
    # Recupera o ano do banco ou assume o atual se estiver vazio
    ano_alvo = int(dados_aluno['ano_teste']) if dados_aluno['ano_teste'] else datetime.now().year

    # --- LÓGICA DE DATAS POR ANO E SEMANA ---
    hoje = datetime.now()
    semana_atual = hoje.isocalendar()[1]
    ano_atual = hoje.year

    # Cálculo preciso de semanas restantes entre anos diferentes
    if ano_alvo > ano_atual:
        # Semanas que faltam para acabar o ano atual + semanas dos anos inteiros no meio + semanas do ano alvo
        anos_de_diferenca = ano_alvo - ano_atual
        semanas_calendario = (52 - semana_atual) + (52 * (anos_de_diferenca - 1)) + semana_alvo
    else:
        # Se for no mesmo ano
        semanas_calendario = max(0, semana_alvo - semana_atual)

    # Regra padrão: 2 semanas de aula/mês (quinzenal) e -4 semanas de margem para revisão
    semanas_uteis_padrao = max(0, (semanas_calendario / 2) - 4)

    st.divider()
    aba_geral, aba_predicao, aba_simulacao, aba_kids = st.tabs([
        "📈 Histórico Semanal", 
        "🗓️ Metas e Cronograma", 
        "🧪 Simulação Personalizada",
        "🎨 Aventura Musical"
    ])

    # --- ABA 1: HISTÓRICO ---
    with aba_geral:
        st.subheader("Histórico de Evolução")
        conn = conectar_bd()
        df_historico = pd.read_sql_query("SELECT metodo, data_registro FROM Progresso WHERE aluno_id = ?", conn, params=(id_aluno,))
        conn.close()

        if not df_historico.empty:
            df_historico['data_registro'] = pd.to_datetime(df_historico['data_registro'])
            df_historico['Semana_Num'] = df_historico['data_registro'].dt.strftime('%U').astype(str)
            
            # Gráficos de Instrumento, MSA e Hinário
            def gerar_grafico(df_filtro, titulo, cor):
                if not df_filtro.empty:
                    st.write(f"### {titulo}")
                    df_plot = df_filtro.groupby('Semana_Num').size().reset_index(name='Qtd')
                    fig = px.bar(df_plot, x='Semana_Num', y='Qtd', text='Qtd', color_discrete_sequence=[cor],
                                 template="plotly_white" if st.get_option("theme.base") == "light" else "plotly_dark")
                    fig.update_xaxes(type='category') # Remove decimais indesejados
                    fig.update_traces(textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)

            gerar_grafico(df_historico[(df_historico['metodo'] != 'HINARIO') & (~df_historico['metodo'].str.contains('MSA', case=False))], "🎻 Lições de Instrumento", '#636EFA')
            gerar_grafico(df_historico[df_historico['metodo'].str.contains('MSA', case=False)], "📖 Evolução MSA", '#AB63FA')
            gerar_grafico(df_historico[df_historico['metodo'] == 'HINARIO'], "🎵 Hinos por Semana", '#00CC96')
        else:
            st.info("Ainda não há dados de progresso para este aluno.")

    # --- FUNÇÃO AUXILIAR DE LIMITES ---
    def buscar_limite_metodo(metodo_nome):
        if metodo_nome == 'HINARIO': return (50 if objetivo == "RJM" else 480), "Hino"
        conn = conectar_bd()
        df_meta = pd.read_sql_query("SELECT * FROM Parametros WHERE (instrumento = ? OR instrumento = 'TEORIA') AND metodo = ?", conn, params=(instrumento, metodo_nome))
        conn.close()
        if not df_meta.empty:
            col = "rjm" if objetivo == "RJM" else ("cultos_oficiais" if objetivo == "Culto Oficial" else "oficializacao")
            return int(df_meta.iloc[0][col]), df_meta.iloc[0]['tipo']
        return 100, "Lição"

    # --- ABA 2: PREDICAO ---
    with aba_predicao:
        st.subheader(f"🎯 Planejamento para o Teste em {ano_alvo}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Semanas Restantes", semanas_calendario)
        c2.metric("Aulas Úteis (Estimativa)", int(semanas_uteis_padrao))
        c3.metric("Margem", "1 Mês")

        st.divider()
        conn = conectar_bd()
        df_ativos = pd.read_sql_query("SELECT DISTINCT metodo FROM Progresso WHERE aluno_id = ?", conn, params=(id_aluno,))
        if not df_ativos.empty:
            for m in df_ativos['metodo'].tolist():
                limite, tipo = buscar_limite_metodo(m)
                concluidas = int(pd.read_sql_query("SELECT count(*) FROM Progresso WHERE aluno_id=? AND metodo=?", conn, params=(id_aluno, m)).iloc[0,0])
                faltam = max(0, limite - concluidas)
                meta = math.ceil(faltam / semanas_uteis_padrao) if semanas_uteis_padrao > 0 else faltam
                
                st.write(f"#### {m}")
                st.caption(f"**{int((concluidas/limite)*100)}% de 100%**")
                st.progress(min(concluidas/limite, 1.0))
                if faltam > 0:
                    st.warning(f"👉 Meta: {meta} {tipo}s por aula (Faltam {faltam})")
                else:
                    st.success("✅ Este método já foi concluído!")
        conn.close()

    # --- ABA 3: SIMULAÇÃO ---
    with aba_simulacao:
        st.subheader("🧪 Simulador de Plano de Estudo")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            data_sim = st.date_input("Data do teste (Simulação)", value=datetime(ano_alvo, 12, 1))
        with col_s2:
            aulas_por_mes_sim = st.number_input("Aulas por MÊS", min_value=1, value=2)
        
        # Diferença de meses considerando anos
        meses_dif = (data_sim.year - hoje.year) * 12 + data_sim.month - hoje.month
        total_aulas_sim = max(0, (meses_dif - 1) * aulas_por_mes_sim) # -1 mês de revisão
        
        st.info(f"Com {aulas_por_mes_sim} aulas mensais, restam **{total_aulas_sim} aulas** úteis até o teste.")

        conn = conectar_bd()
        df_ativos_sim = pd.read_sql_query("SELECT DISTINCT metodo FROM Progresso WHERE aluno_id = ?", conn, params=(id_aluno,))
        if not df_ativos_sim.empty:
            dados_sim = []
            for m in df_ativos_sim['metodo'].tolist():
                lim, tipo = buscar_limite_metodo(m)
                conc = int(pd.read_sql_query("SELECT count(*) FROM Progresso WHERE aluno_id=? AND metodo=?", conn, params=(id_aluno, m)).iloc[0,0])
                falta = max(0, lim - conc)
                ritmo = math.ceil(falta / total_aulas_sim) if total_aulas_sim > 0 else falta
                
                sit = "✅ Viável" if ritmo <= 4 else ("⚠️ Intenso" if ritmo <= 7 else "🚨 Crítico")
                dados_sim.append({"Método": m, "Faltam": falta, "Lições p/ Aula": ritmo, "Situação": sit})
            
            st.table(pd.DataFrame(dados_sim))
        conn.close()

    # --- ABA 4: KIDS ---
    with aba_kids:
        st.subheader(f"🚀 A Jornada Musical do(a) {aluno_selecionado}!")
        st.write("Complete seus estudos para tocar na orquestra!")
        conn = conectar_bd()
        df_ativos_k = pd.read_sql_query("SELECT DISTINCT metodo FROM Progresso WHERE aluno_id = ?", conn, params=(id_aluno,))
        for m in df_ativos_k['metodo'].tolist():
            lim, _ = buscar_limite_metodo(m)
            conc = int(pd.read_sql_query("SELECT count(*) FROM Progresso WHERE aluno_id=? AND metodo=?", conn, params=(id_aluno, m)).iloc[0,0])
            perc = int((conc/lim)*100)
            mapa = ["⚪"] * 10
            pos = min(9, int(perc/10))
            mapa[pos] = "🏃‍♂️" if perc < 100 else "🏆"
            #icone final é tocar na orquestra
            st.markdown(f"**{m}**\n## {'---'.join(mapa)} 🎶")
            st.write(f"✨ {perc}% concluído! Faltam {max(0, lim-conc)} lições.")
        conn.close()
else:
    st.warning("Cadastre alunos primeiro.")