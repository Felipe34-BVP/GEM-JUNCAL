import streamlit as st
import sqlite3
import pandas as pd
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="GEM Juncal - Lições", layout="wide")

# Ajuste de caminho para o seu DATABASE.db
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_db = os.path.join(os.path.dirname(diretorio_atual), 'DATABASE.db')

def conectar_bd():
    return sqlite3.connect(caminho_db)

# --- CSS CUSTOMIZADO (ALINHADO COM AS OUTRAS PÁGINAS) ---
st.markdown("""
<style>
    /* Estilização dos Cards e Informações */
    .stInfo {
        background-color: var(--secondary-background-color);
        border-left: 6px solid #00CC96 !important;
        border-radius: 10px;
        color: var(--text-color);
    }

    /* Estilização do Grid de Checkboxes */
    .stCheckbox {
        background: var(--secondary-background-color);
        padding: 5px;
        border-radius: 5px;
        border: 1px solid rgba(0, 204, 150, 0.2);
        transition: 0.3s;
        text-align: center;
    }
    
    .stCheckbox:hover {
        border-color: #00CC96;
        transform: translateY(-2px);
    }

    /* Títulos e Subtítulos */
    h1, h2, h3 {
        color: var(--text-color);
    }

    /* Expander de Hinos */
    .streamlit-expanderHeader {
        background-color: var(--secondary-background-color) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(0, 204, 150, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📖 Controle de Evolução - GEM Juncal")

# 1. Busca lista de alunos
conn = conectar_bd()
df_alunos = pd.read_sql_query("SELECT id, nome_aluno, instrumento, teste_para FROM Alunos", conn)
conn.close()

if not df_alunos.empty:
    col_aluno, col_meta = st.columns([2, 1])
    
    with col_aluno:
        nome_selecionado = st.selectbox("👤 Selecione o Aluno", df_alunos['nome_aluno'].tolist())
    
    # Dados do aluno selecionado
    dados_aluno = df_alunos[df_alunos['nome_aluno'] == nome_selecionado].iloc[0]
    id_aluno = int(dados_aluno['id'])
    instrumento = dados_aluno['instrumento']
    objetivo = dados_aluno['teste_para']

    st.info(f"🎻 **Instrumento:** {instrumento} | 🎯 **Objetivo:** {objetivo}")

    # 2. Busca Métodos na Parametrização
    conn = conectar_bd()
    query = "SELECT * FROM Parametros WHERE instrumento = ? OR instrumento = 'TEORIA'"
    df_metodos = pd.read_sql_query(query, conn, params=(instrumento,))
    conn.close()

    if not df_metodos.empty:
        metodo_nome = st.selectbox("📚 Selecione o Método ou Teoria", df_metodos['metodo'].tolist())
        info_metodo = df_metodos[df_metodos['metodo'] == metodo_nome].iloc[0]

        coluna_limite = "rjm" if objetivo == "RJM" else ("cultos_oficiais" if objetivo == "Culto Oficial" else "oficializacao")
        limite = int(info_metodo[coluna_limite])
        tipo_unidade = info_metodo['tipo'] 

        st.markdown(f"### Progresso: {metodo_nome}")
        st.caption(f"📍 **Unidade:** {tipo_unidade} | **Alvo:** {limite}")

        # 3. Carrega progresso
        conn = conectar_bd()
        df_progresso = pd.read_sql_query(
            "SELECT licao_passada FROM Progresso WHERE aluno_id = ? AND metodo = ?", 
            conn, params=(id_aluno, metodo_nome)
        )
        conn.close()
        itens_concluidos = df_progresso['licao_passada'].tolist()

        # 4. Grid de Quadradinhos
        st.write(f"Marque as {tipo_unidade}s concluídas:")
        
        # Container visual para as lições
        cols = st.columns(10)
        for i in range(1, limite + 1):
            label = str(i)
            ja_marcado = label in itens_concluidos
            
            with cols[(i-1) % 10]:
                if st.checkbox(label, key=f"it_{id_aluno}_{metodo_nome}_{i}", value=ja_marcado):
                    if not ja_marcado:
                        conn = conectar_bd()
                        conn.execute("INSERT INTO Progresso (aluno_id, metodo, licao_passada) VALUES (?, ?, ?)", 
                                    (id_aluno, metodo_nome, label))
                        conn.commit()
                        conn.close()
                        st.rerun()
                elif ja_marcado:
                    conn = conectar_bd()
                    conn.execute("DELETE FROM Progresso WHERE aluno_id = ? AND metodo = ? AND licao_passada = ?", 
                                (id_aluno, metodo_nome, label))
                    conn.commit()
                    conn.close()
                    st.rerun()
        
        # 5. Seção de Hinos
        st.divider()
        st.subheader("🎹 Hinário")
        inicio_hino = 431 if objetivo == "RJM" else 1
        
        conn = conectar_bd()
        hinos_concluidos = pd.read_sql_query(
            "SELECT licao_passada FROM Progresso WHERE aluno_id = ? AND metodo = 'HINARIO'", 
            conn, params=(id_aluno,)
        )['licao_passada'].tolist()
        conn.close()

        with st.expander("🎵 Ver Grade de Hinos (431-480 ou 1-480)"):
            h_cols = st.columns(12)
            for h in range(inicio_hino, 481):
                h_label = str(h)
                h_feito = h_label in hinos_concluidos
                with h_cols[(h-inicio_hino) % 12]:
                    if st.checkbox(f"H{h}", key=f"h_{id_aluno}_{h}", value=h_feito):
                        if not h_feito:
                            conn = conectar_bd()
                            conn.execute("INSERT INTO Progresso (aluno_id, metodo, licao_passada) VALUES (?, 'HINARIO', ?)", 
                                        (id_aluno, h_label))
                            conn.commit()
                            conn.close()
                            st.rerun()
                    elif h_feito:
                        conn = conectar_bd()
                        conn.execute("DELETE FROM Progresso WHERE aluno_id = ? AND metodo = 'HINARIO' AND licao_passada = ?", 
                                    (id_aluno, h_label))
                        conn.commit()
                        conn.close()
                        st.rerun()
    else:
        st.warning(f"⚠️ Configure os parâmetros para {instrumento} ou MSA primeiro.")
else:
    st.info("💡 Cadastre alunos primeiro para gerenciar a evolução.")