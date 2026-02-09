import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="GEM JUNCAL", layout="wide")

# --- CSS CUSTOMIZADO PARA O MENU (COMBINANDO COM A HOME) ---
st.markdown("""
    <style>
        /* Fundo da barra lateral para garantir integração total */
        [data-testid="stSidebar"] {
            background-color: #0e1117;
        }

        /* Estilização geral dos itens do menu */
        [data-testid="stSidebarNavItems"] li {
            border-radius: 8px;
            margin-bottom: 6px;
            margin-left: 10px;
            margin-right: 10px;
            transition: all 0.3s ease-in-out;
        }

        /* Efeito Hover: Degradê Verde (Combinando com a Home) */
        [data-testid="stSidebarNavItems"] li:hover {
            background: linear-gradient(90deg, rgba(0, 204, 150, 0.2) 0%, rgba(0, 204, 150, 0.05) 100%) !important;
            transform: translateX(5px);
            border-left: 4px solid #00CC96; /* Linha de destaque lateral */
        }

        /* Destaque para a página que está selecionada no momento */
        [data-testid="stSidebarNavItems"] li[aria-selected="true"] {
            background: linear-gradient(90deg, rgba(0, 204, 150, 0.3) 0%, rgba(0, 204, 150, 0.1) 100%) !important;
            border-left: 4px solid #00CC96;
        }

        /* Cor do ícone e texto */
        [data-testid="stSidebarNavItems"] li span {
            color: #ffffff !important;
            font-weight: 500;
        }

        /* Cor quando o mouse passa por cima (Hover) */
        [data-testid="stSidebarNavItems"] li:hover span {
            color: #00CC96 !important;
        }

        /* Estilização da Versão no rodapé do menu */
        .version-footer {
            position: fixed;
            bottom: 20px;
            left: 20px;
            font-size: 11px;
            color: #00CC96;
            opacity: 0.6;
            font-family: 'Courier New', monospace;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
# Mantendo os ícones Material que você escolheu
Menu = st.navigation([
    st.Page("pag/inicio.py", title="Início", icon=":material/home:"),
    st.Page("pag/Alunos.py", title="Alunos", icon=":material/group:"),
    st.Page("pag/acompanhamento.py", title="Lições", icon=":material/library_books:"),
    st.Page("pag/Situação.py", title="Situação", icon=":material/assessment:"),
])

# Adiciona a versão na barra lateral estilizada
st.sidebar.markdown('<p class="version-footer">GEM JUNCAL • FA01.00</p>', unsafe_allow_html=True)

Menu.run()