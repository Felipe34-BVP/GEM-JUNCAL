import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="GEM Juncal - Home", layout="wide")

# Ajuste de caminho do banco
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
diretorio_projeto = os.path.dirname(diretorio_atual)
caminho_db = os.path.join(diretorio_projeto, 'DATABASE.db')

def conectar_bd():
    return sqlite3.connect(caminho_db)

def obter_mes_por_semana(semana, ano):
    try:
        data_base = datetime.strptime(f'{int(ano)}-W{int(semana)}-1', "%Y-W%W-%w")
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        return meses[data_base.month - 1]
    except:
        return "Mês Indefinido"

# --- CSS ADAPTÁVEL (DARK/LIGHT) ---
st.markdown("""
<style>
    /* Faz as notas flutuarem independente do fundo */
    .stApp {
        background: transparent;
    }
    
    /* Container das notas no fundo */
    .music-background {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 0;
        pointer-events: none;
    }

    .note-anim {
        position: absolute;
        bottom: -100px;
        font-size: 50px;
        /* Cor das notas usa o verde tema com transparência */
        color: rgba(0, 204, 150, 0.2); 
        animation: floatUp 15s linear infinite;
    }

    @keyframes floatUp {
        0% { transform: translateY(0) rotate(0deg); opacity: 0; }
        20% { opacity: 1; }
        80% { opacity: 1; }
        100% { transform: translateY(-120vh) rotate(360deg); opacity: 0; }
    }

    /* Estilo do Título - Usando variáveis do Streamlit para as cores */
    .title-card {
        position: relative;
        z-index: 10;
        text-align: center;
        padding: 50px;
        /* Fundo sutil que se adapta ao tema */
        background: var(--secondary-background-color); 
        border-radius: 40px;
        border: 1px solid rgba(0, 204, 150, 0.4);
        margin-bottom: 50px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    .main-text {
        font-size: 4rem;
        font-weight: 900;
        color: var(--text-color); /* Cor de texto automática */
        margin: 0;
    }

    .sub-text {
        color: #00CC96; /* Verde fixo da marca */
        font-size: 1.2rem;
        letter-spacing: 5px;
        font-weight: bold;
    }

    /* Card dos Alunos Adaptável */
    .aluno-card {
        background: var(--secondary-background-color);
        padding: 25px;
        border-radius: 20px;
        border-left: 6px solid #00CC96;
        margin-bottom: 25px;
        position: relative;
        z-index: 10;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    
    .aluno-card:hover {
        transform: scale(1.02);
    }

    .aluno-nome {
        margin: 0;
        color: var(--text-color);
    }

    .aluno-meta {
        margin: 0;
        color: var(--text-color);
        opacity: 0.7;
        font-size: 14px;
    }
</style>

<div class="music-background">
    <div class="note-anim" style="left: 10%; animation-delay: 0s;">♩</div>
    <div class="note-anim" style="left: 25%; animation-delay: 4s;">♫</div>
    <div class="note-anim" style="left: 40%; animation-delay: 8s;">♬</div>
    <div class="note-anim" style="left: 55%; animation-delay: 2s;">♪</div>
    <div class="note-anim" style="left: 70%; animation-delay: 10s;">♫</div>
    <div class="note-anim" style="left: 85%; animation-delay: 5s;">♩</div>
</div>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
ano_hoje = datetime.now().year
st.markdown(f"""
    <div class="title-card">
        <div class="main-text">GEM JUNCAL</div>
        <div class="sub-text">GRUPO DE ESTUDO MUSICAL - {ano_hoje}</div>
    </div>
""", unsafe_allow_html=True)

# --- CRONOGRAMA DE TESTES ---
st.subheader("📅 Próximos Testes Agendados")

try:
    conn = conectar_bd()
    df_testes = pd.read_sql_query("""
        SELECT nome_aluno, instrumento, teste_para, semana_teste, ano_teste 
        FROM Alunos 
        WHERE semana_teste IS NOT NULL 
        ORDER BY ano_teste ASC, semana_teste ASC
    """, conn)
    conn.close()

    if not df_testes.empty:
        cols = st.columns(3)
        for index, row in df_testes.iterrows():
            ano_alvo = row['ano_teste'] if row['ano_teste'] else ano_hoje
            nome_mes = obter_mes_por_semana(row['semana_teste'], ano_alvo)
            
            with cols[index % 3]:
                st.markdown(f"""
                <div class="aluno-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <h3 class="aluno-nome">{row['nome_aluno']}</h3>
                        <span style="background:#00CC96; color:white; padding:2px 8px; border-radius:5px; font-size:10px; font-weight:bold;">
                            {ano_alvo}
                        </span>
                    </div>
                    <p style="margin:5px 0; color:#00CC96; font-weight:bold;">{row['instrumento']}</p>
                    <p class="aluno-meta">Objetivo: {row['teste_para']}</p>
                    <hr style="opacity: 0.2; margin: 15px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 13px; color: var(--text-color);">🗓️ Sem. {row['semana_teste']}</span>
                        <span style="background:rgba(0, 204, 150, 0.15); color:#00CC96; padding:2px 10px; border-radius:15px; font-size:12px; font-weight:bold; border: 1px solid #00CC96;">
                            {nome_mes.upper()}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Nenhum teste agendado no sistema.")

except Exception as e:
    st.error(f"Erro ao carregar cronograma: {e}")

st.divider()
st.markdown(f"<p style='text-align: center; opacity: 0.6; position: relative; z-index: 10;'>Gestão de Alunos • GEM Juncal {ano_hoje}</p>", unsafe_allow_html=True)