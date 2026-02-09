import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="GEM Juncal - Alunos", layout="wide")

# Ajuste de Caminho
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_db = os.path.join(os.path.dirname(diretorio_atual), 'DATABASE.db')

def conectar_bd():
    return sqlite3.connect(caminho_db)

# Garante que a coluna ano_teste existe
def verificar_coluna_ano():
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ano_teste FROM Alunos LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE Alunos ADD COLUMN ano_teste INTEGER")
        conn.commit()
    finally:
        conn.close()

verificar_coluna_ano()

# --- CSS CUSTOMIZADO (MESMO ESTILO DA HOME) ---
st.markdown("""
<style>
    /* Estilização dos Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: var(--secondary-background-color);
        border-radius: 10px 10px 0px 0px;
        padding: 10px 20px;
        color: var(--text-color);
        border: 1px solid rgba(0, 204, 150, 0.2);
    }
    .stTabs [aria-selected="true"] {
        background-color: #00CC96 !important;
        color: white !important;
    }

    /* Estilização do Formulário (Card) */
    [data-testid="stForm"] {
        background: var(--secondary-background-color);
        padding: 30px;
        border-radius: 20px;
        border-left: 6px solid #00CC96;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    /* Estilização dos Botões */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #00CC96;
        color: white;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #009e74;
        transform: scale(1.02);
    }

    /* Títulos */
    h1, h2, h3 {
        color: var(--text-color);
    }
</style>
""", unsafe_allow_html=True)

OPCOES_TESTE = ["Nenhum", "RJM", "Culto Oficial", "Oficialização"]

def buscar_instrumentos_parametrizados():
    conn = conectar_bd()
    try:
        query = "SELECT DISTINCT instrumento FROM Parametros ORDER BY instrumento ASC"
        df_inst = pd.read_sql_query(query, conn)
        conn.close()
        return df_inst['instrumento'].tolist()
    except:
        conn.close()
        return []

st.title("👤 Gestão de Alunos - GEM Juncal")
lista_instrumentos = buscar_instrumentos_parametrizados()

aba1, aba2 = st.tabs(["✨ Cadastrar Novo Aluno", "📋 Lista de Alunos"])

with aba1:
    st.markdown("### Preencha os dados do músico")
    with st.form("novo_aluno"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo", placeholder="Ex: Natan Silva")
            inst = st.selectbox("Instrumento", lista_instrumentos)
        with col2:
            teste = st.selectbox("Preparando para:", OPCOES_TESTE)
            data_selecionada = st.date_input("Previsão do teste", datetime.now())
        
        # O botão do form agora segue o estilo verde
        submit = st.form_submit_button("CONCLUIR CADASTRO")
        
        if submit:
            if nome and inst:
                semana = data_selecionada.isocalendar()[1]
                ano = data_selecionada.year
                conn = conectar_bd()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Alunos (nome_aluno, instrumento, teste_para, semana_teste, ano_teste) 
                    VALUES (?, ?, ?, ?, ?)""", (nome, inst, teste, semana, ano))
                conn.commit()
                conn.close()
                st.success(f"✅ Músico {nome} adicionado ao pipeline do GEM!")
                st.rerun()

with aba2:
    conn = conectar_bd()
    df = pd.read_sql_query("SELECT id, nome_aluno as Nome, instrumento as Instrumento, teste_para as 'Preparação', semana_teste as Semana, ano_teste as Ano FROM Alunos", conn)
    conn.close()

    if not df.empty:
        # Tabela com visual adaptável
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("🛠️ Editar ou Remover")
        
        col_id, col_edit = st.columns([1, 3])
        with col_id:
            aluno_id = st.selectbox("ID do Aluno", df['id'].tolist())
        
        dados_originais = df[df['id'] == aluno_id].iloc[0]

        with st.expander(f"Modificar dados de {dados_originais['Nome']}"):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                novo_nome = st.text_input("Nome", value=dados_originais['Nome'])
                idx_inst = lista_instrumentos.index(dados_originais['Instrumento']) if dados_originais['Instrumento'] in lista_instrumentos else 0
                novo_inst = st.selectbox("Instrumento", lista_instrumentos, index=idx_inst)
            with col_e2:
                idx_teste = OPCOES_TESTE.index(dados_originais['Preparação']) if dados_originais['Preparação'] in OPCOES_TESTE else 0
                novo_teste = st.selectbox("Teste para", OPCOES_TESTE, index=idx_teste)
                nova_data = st.date_input("Nova data do teste")

            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("SALVAR ALTERAÇÕES"):
                    nova_semana = nova_data.isocalendar()[1]
                    novo_ano = nova_data.year
                    conn = conectar_bd()
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE Alunos SET nome_aluno=?, instrumento=?, teste_para=?, semana_teste=?, ano_teste=? 
                        WHERE id=?""", (novo_nome, novo_inst, novo_teste, nova_semana, novo_ano, aluno_id))
                    conn.commit()
                    conn.close()
                    st.success("Dados atualizados!")
                    st.rerun()
            
            with c_btn2:
                if st.button("EXCLUIR ALUNO", type="secondary"):
                    conn = conectar_bd()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Alunos WHERE id=?", (aluno_id,))
                    conn.commit()
                    conn.close()
                    st.error("Aluno removido.")
                    st.rerun()
    else:
        st.info("Nenhum músico cadastrado.")