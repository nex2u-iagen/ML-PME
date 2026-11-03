"""Streamlit Frontend Operacional para o CRISP-DM projeto_ml.

Aplicação multipágina que separa cada fase CRISP-DM em uma página própria,
reduzindo acoplamento e evitando problemas de dependência entre componentes.

O dataset é selecionado uma única vez no sidebar e vale para todas as páginas.
"""

import streamlit as st

from ui_comum import (
    garantir_estado,
    nomes_datasets,
    obter_cliente,
    selecionar_dataset,
)

# Configuração inicial da página.
st.set_page_config(
    page_title="CRISP-DM Operacional",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estado compartilhado entre páginas (inicializado em um só lugar).
garantir_estado()


def sidebar_dataset() -> None:
    """Sidebar: status da API + seleção persistente de dataset."""
    cliente = obter_cliente()

    with st.sidebar:
        st.markdown("#### Plataforma CRISP-DM")

        # Status da API (detecção barata, já cacheada no cliente singleton).
        try:
            modo = cliente.detectar_modo()
        except Exception:
            modo = "local"

        if modo == "servico":
            st.success("API: operacional", icon=":material/check_circle:")
        else:
            st.warning(
                "API indisponível — modo local",
                icon=":material/wifi_off:",
            )

        st.divider()

        # --- Seleção de dataset (persiste imediatamente no estado) ---
        st.markdown("#### Dataset")
        nomes = nomes_datasets()

        if nomes:
            atual = st.session_state.dataset_nome
            opcoes = ["— Selecione —"] + nomes
            indice = opcoes.index(atual) if atual in nomes else 0

            escolha = st.selectbox(
                "Dataset ativo",
                options=opcoes,
                index=indice,
                label_visibility="collapsed",
                placeholder="Selecione um dataset",
            )

            if escolha.startswith("—"):
                # Volta para a seleção vazia sem reprocessar.
                if st.session_state.dataset_nome is not None:
                    selecionar_dataset(None)
            else:
                selecionar_dataset(escolha)
        else:
            st.info("Nenhum dataset registrado. Crie um na página de Ingestão.")

        # Mostra o dataset ativo de forma destacada.
        if st.session_state.dataset_nome:
            st.code(st.session_state.dataset_nome, language=None)

        st.divider()
        st.caption("Motor: CRISP-DM v6 · Fluxo: 4 fases")


# Definir navegação (uma página por fase).
paginas = [
    st.Page(
        "app_pages/pagina_01_ingestao.py",
        title="Ingestão",
        icon=":material/upload:",
        default=True,
    ),
    st.Page(
        "app_pages/pagina_02_raiox.py",
        title="Raio-X",
        icon=":material/analytics:",
    ),
    st.Page(
        "app_pages/pagina_03_torneio.py",
        title="Torneio",
        icon=":material/emoji_events:",
    ),
    st.Page(
        "app_pages/pagina_04_valor.py",
        title="Valor",
        icon=":material/attach_money:",
    ),
    st.Page(
        "app_pages/pagina_05_predicao.py",
        title="Predição",
        icon=":material/smart_toy:",
    ),
]

navegacao = st.navigation(paginas, position="top")

# Sidebar com status da API, seleção persistente de dataset e links cruzados.
sidebar_dataset()

with st.sidebar:
    st.divider()
    st.markdown("#### Navegação entre aplicações")
    st.page_link(
        "http://localhost:8503",
        label="Abrir vitrine CRISP-DM (fluxo, saúde 360°, relatórios)",
        icon=":material/description:",
        disabled=False,
    )
    st.caption("Vitrine executiva rodando na porta 8503.")

# Título da página atual (as páginas não repetem o título).
st.title(navegacao.title, icon=navegacao.icon)

# Renderizar página selecionada.
navegacao.run()
