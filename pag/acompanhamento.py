import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="GEM Juncal - Lições", layout="wide")

# Ajuste de caminho
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_db = os.path.join(os.path.dirname(diretorio_atual), 'DATABASE.db')

def conectar_bd():
    return sqlite3.connect(caminho_db)

# --- CSS CUSTOMIZADO ---
st.markdown("""
<style>
    .stInfo { border-left: 6px solid #00CC96 !important; }
    .stCheckbox { background: var(--secondary-background-color); padding: 5px; border-radius: 5px; }
    /* Estilo para tarefas estudadas */
    .task-done { text-decoration: line-through; color: #00CC96; font-weight: bold; }
    .task-pending { color: #FFA500; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("📖 Controle de Evolução - GEM Juncal")

# 1. Busca lista de alunos
conn = conectar_bd()
df_alunos = pd.read_sql_query("SELECT id, nome_aluno, instrumento, teste_para FROM Alunos", conn)
conn.close()

if not df_alunos.empty:
    nome_selecionado = st.selectbox("👤 Selecione o Aluno", df_alunos['nome_aluno'].tolist())
    dados_aluno = df_alunos[df_alunos['nome_aluno'] == nome_selecionado].iloc[0]
    id_aluno = int(dados_aluno['id'])
    instrumento = dados_aluno['instrumento']
    objetivo = dados_aluno['teste_para']

    st.info(f"🎻 **Instrumento:** {instrumento} | 🎯 **Objetivo:** {objetivo}")

    # --- CRIAÇÃO DAS ABAS ---
    tab_plano, tab_historico = st.tabs(["📅 Próxima Aula (Metas)", "✅ Histórico Geral"])

    # --- ABA 1: PLANO DE ESTUDO (A sua nova solicitação) ---
    with tab_plano:
        st.subheader("🎯 O que estudar para a próxima aula?")
        
        # Interface para o Professor atribuir lições
        with st.expander("➕ Atribuir novas lições"):
            conn = conectar_bd()
            df_m = pd.read_sql_query("SELECT metodo FROM Parametros WHERE instrumento = ? OR instrumento = 'TEORIA'", conn, params=(instrumento,))
            conn.close()
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                met_atribuir = st.selectbox("Método", df_m['metodo'].tolist() + ["HINARIO"], key="at_met")
            with col2:
                lic_atribuir = st.text_input("Lição/Hino (ex: 5, 6, 7)", key="at_lic")
            with col3:
                st.write("##")
                if st.button("Adicionar"):
                    if lic_atribuir:
                        conn = conectar_bd()
                        for l in lic_atribuir.split(','):
                            conn.execute("INSERT INTO Tarefas (aluno_id, metodo, licao, data_atribuicao) VALUES (?, ?, ?, ?)",
                                        (id_aluno, met_atribuir, l.strip(), datetime.now().strftime('%Y-%m-%d')))
                        conn.commit()
                        conn.close()
                        st.success("Metas adicionadas!")
                        st.rerun()

        st.divider()

        # Exibição das tarefas pendentes
        conn = conectar_bd()
        df_tarefas = pd.read_sql_query("SELECT * FROM Tarefas WHERE aluno_id = ? AND estudado = 0", conn, params=(id_aluno,))
        df_concluidas = pd.read_sql_query("SELECT * FROM Tarefas WHERE aluno_id = ? AND estudado = 1", conn, params=(id_aluno,))
        conn.close()

        if not df_tarefas.empty:
            st.write("📝 **Suas tarefas para esta semana:**")
            for index, row in df_tarefas.iterrows():
                # Dividindo em 3 colunas para acomodar Texto, Check e Lixeira
                col_t1, col_t2, col_t3 = st.columns([3, 1, 1])
                
                with col_t1:
                    st.write(f"📖 **{row['metodo']}**: Lição {row['licao']}")
                
                with col_t2:
                    if st.button("✅", key=f"btn_{row['id']}", help="Marcar como estudado"):
                        conn = conectar_bd()
                        conn.execute("UPDATE Tarefas SET estudado = 1 WHERE id = ?", (row['id'],))
                        conn.commit()
                        conn.close()
                        st.balloons()
                        st.rerun()
                
                with col_t3:
                    if st.button("🗑️", key=f"del_{row['id']}", help="Excluir tarefa"):
                        conn = conectar_bd()
                        conn.execute("DELETE FROM Tarefas WHERE id = ?", (row['id'],))
                        conn.commit()
                        conn.close()
                        st.rerun()
        else:
            st.write("🌟 Nenhuma tarefa pendente.")

        # Exibição das tarefas concluídas
        if not df_concluidas.empty:
            st.write("---")
            with st.expander("✔ Ver tarefas já estudadas"):
                for index, row in df_concluidas.iterrows():
                    col_c1, col_c2, col_c3 = st.columns([3, 1, 1])
                    with col_c1:
                        st.write(f"~~{row['metodo']} - Lição {row['licao']}~~")
                    with col_c2:
                        if st.button("↩️", key=f"undo_{row['id']}", help="Desfazer"):
                            conn = conectar_bd()
                            conn.execute("UPDATE Tarefas SET estudado = 0 WHERE id = ?", (row['id'],))
                            conn.commit()
                            conn.close()
                            st.rerun()
                    with col_c3:
                        if st.button("🗑️", key=f"del_c_{row['id']}", help="Excluir permanentemente"):
                            conn = conectar_bd()
                            conn.execute("DELETE FROM Tarefas WHERE id = ?", (row['id'],))
                            conn.commit()
                            conn.close()
                            st.rerun()

    # --- ABA 2: HISTÓRICO GERAL (O código que você já tinha) ---
    with tab_historico:
        # 2. Busca Métodos na Parametrização
        conn = conectar_bd()
        query = "SELECT * FROM Parametros WHERE instrumento = ? OR instrumento = 'TEORIA'"
        df_metodos = pd.read_sql_query(query, conn, params=(instrumento,))
        conn.close()

        if not df_metodos.empty:
            metodo_nome = st.selectbox("📚 Selecione o Método", df_metodos['metodo'].tolist())
            info_metodo = df_metodos[df_metodos['metodo'] == metodo_nome].iloc[0]
            coluna_limite = "rjm" if objetivo == "RJM" else ("cultos_oficiais" if objetivo == "Culto Oficial" else "oficializacao")
            limite = int(info_metodo[coluna_limite])
            tipo_unidade = info_metodo['tipo'] 

            # Carrega progresso
            conn = conectar_bd()
            df_progresso = pd.read_sql_query("SELECT licao_passada FROM Progresso WHERE aluno_id = ? AND metodo = ?", 
                                            conn, params=(id_aluno, metodo_nome))
            conn.close()
            itens_concluidos = df_progresso['licao_passada'].tolist()

            # Grid de Quadradinhos
            cols = st.columns(10)
            for i in range(1, limite + 1):
                label = str(i)
                ja_marcado = label in itens_concluidos
                with cols[(i-1) % 10]:
                    if st.checkbox(label, key=f"it_{id_aluno}_{metodo_nome}_{i}", value=ja_marcado):
                        if not ja_marcado:
                            conn = conectar_bd()
                            conn.execute("INSERT INTO Progresso (aluno_id, metodo, licao_passada) VALUES (?, ?, ?)", (id_aluno, metodo_nome, label))
                            conn.commit(); conn.close()
                            st.rerun()
                    elif ja_marcado:
                        conn = conectar_bd()
                        conn.execute("DELETE FROM Progresso WHERE aluno_id = ? AND metodo = ? AND licao_passada = ?", (id_aluno, metodo_nome, label))
                        conn.commit(); conn.close()
                        st.rerun()
            
            # Hinário (dentro do histórico)
            st.divider()
            st.subheader("🎹 Hinário")
            inicio_hino = 431 if objetivo == "RJM" else 1
            conn = conectar_bd()
            hinos_concluidos = pd.read_sql_query("SELECT licao_passada FROM Progresso WHERE aluno_id = ? AND metodo = 'HINARIO'", 
                                               conn, params=(id_aluno,))['licao_passada'].tolist()
            conn.close()

            with st.expander("🎵 Ver Grade de Hinos"):
                h_cols = st.columns(12)
                for h in range(inicio_hino, 481):
                    h_label = str(h)
                    h_feito = h_label in hinos_concluidos
                    with h_cols[(h-inicio_hino) % 12]:
                        if st.checkbox(f"H{h}", key=f"h_{id_aluno}_{h}", value=h_feito):
                            if not h_feito:
                                conn = conectar_bd()
                                conn.execute("INSERT INTO Progresso (aluno_id, metodo, licao_passada) VALUES (?, 'HINARIO', ?)", (id_aluno, h_label))
                                conn.commit(); conn.close(); st.rerun()
                        elif h_feito:
                            conn = conectar_bd()
                            conn.execute("DELETE FROM Progresso WHERE aluno_id = ? AND metodo = 'HINARIO' AND licao_passada = ?", (id_aluno, h_label))
                            conn.commit(); conn.close(); st.rerun()
else:
    st.info("💡 Cadastre alunos primeiro.")