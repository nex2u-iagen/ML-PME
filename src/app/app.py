"""CRISP-DM Operacional — app de vitrine da plataforma.

Aplicação Streamlit com três vistas:
  1. **Início** — fluxograma SVG do pipeline CRISP-DM em 13 etapas;
  2. **Saúde 360°** — imagem única do dashboard de saúde da empresa
     (radar + KPIs + semáforo gerado pela Fase 02);
  3. **Relatórios** — PNGs e laudos departamentais da Fase 02.

Execução::

    streamlit run src/app/app.py
"""

# 'import sys' permite importar o pacote 'src.*' mesmo com o script fora da raiz.
import sys

# 'from pathlib import Path' resolve a raiz do projeto e as pastas de relatório.
from pathlib import Path

# 'import streamlit' traz a API da interface da aplicação.
import streamlit as st

# Raiz do projeto (src/app/app.py → 2 níveis acima) entra no caminho de importação.
RAIZ_PROJETO = Path(__file__).resolve().parents[2]
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

# Pasta deste módulo (onde vive o SVG do fluxograma).
PASTA_APP = Path(__file__).resolve().parent

# Departamentos da Fase 02: (pasta, nome exibido, ícone).
DEPARTAMENTOS = [
    ("comercial", "Comercial", ":material/trending_up:"),
    ("compras", "Compras", ":material/shopping_cart:"),
    ("estoque", "Estoque", ":material/inventory_2:"),
    ("contabil", "Contábil", ":material/calculate:"),
    ("financeiro", "Financeiro", ":material/account_balance:"),
    ("fiscal", "Fiscal", ":material/receipt_long:"),
    ("producao", "Produção", ":material/factory:"),
    ("logistica", "Logística", ":material/local_shipping:"),
    ("pos_venda", "Pós-Venda", ":material/support_agent:"),
    ("recursos_humanos", "RH", ":material/groups:"),
]

# As 13 etapas do pipeline real do projeto (mesma ordem do fluxograma SVG).
ETAPAS_PIPELINE = [
    ("Fase 01", "Ingestão", "Extração SQL → CSV isolada por PME, com validação das entidades do ERP."),
    ("Fase 02", "Raio-X Empresarial 360°", "Saúde dos dados + 10 diagnósticos departamentais + visão agnóstica de saúde."),
    ("Fase 03.1", "Data Marts para BI", "Tabelas analíticas prontas para painéis e relatórios gerenciais."),
    ("Fase 03.2", "ABT + Partições ML", "Partição 70/15/15 e pipeline de preparação de dados versionado."),
    ("Fase 04", "Modelagem (Torneio)", "Baseline → torneio de modelos → pódio Top 3 e campeão escolhido."),
    ("Fase 05.1", "Pilar 01 — Top 3", "Matrizes, curvas ROC/PR e métricas do pódio."),
    ("Fase 05.2", "Pilar 02 — Custo do erro", "Custo financeiro dos erros de previsão."),
    ("Fase 05.3", "Pilar 03 — SHAP (XAI)", "Explicabilidade global e local das predições."),
    ("Fase 05.4", "Pilar 04 — Governança", "Deliberação humana e dossiê de homologação."),
    ("Fase 06.1", "Pilar 01 — Persistência", "Artefato do campeão com manifesto SHA-256."),
    ("Fase 06.2", "Pilar 02 — Segurança", "Bearer JWT e validação isolada de entrada."),
    ("Fase 06.3", "Pilar 03 — Contratos", "OpenAPI e schemas de dados versionados."),
    ("Fase 06.4", "Pilar 04 — Motor de Inferência", "API REST de predição em produção para a PME."),
]


# 'def encontrar_pasta_fase_02(...)' localiza a pasta de relatórios da Fase 02.
def encontrar_pasta_fase_02(dataset: str) -> Path | None:
    """Testa os dois formatos de saída da Fase 02 e devolve o que existir.

    Args:
        dataset (str): Nome do dataset.

    Returns:
        Path | None: Pasta ``fase_02`` encontrada ou ``None``.
    """
    candidatos = [
        RAIZ_PROJETO / "relatorios" / dataset / dataset / "fase_02",
        RAIZ_PROJETO / "relatorios" / dataset / "fase_02",
    ]
    for candidato in candidatos:
        if candidato.is_dir():
            return candidato
    return None


# 'def datasets_com_relatorios(...)' lista os datasets que já têm Fase 02.
def datasets_com_relatorios() -> list[str]:
    """Varre ``relatorios/`` e devolve os datasets com pasta ``fase_02``.

    Returns:
        list[str]: Nomes ordenados (pastas de teste iniciadas por ``_`` ficam de fora).
    """
    raiz_relatorios = RAIZ_PROJETO / "relatorios"
    if not raiz_relatorios.is_dir():
        return []

    encontrados: list[str] = []
    for pasta in sorted(raiz_relatorios.iterdir()):
        if not pasta.is_dir() or pasta.name.startswith("_"):
            continue
        if encontrar_pasta_fase_02(pasta.name) is not None:
            encontrados.append(pasta.name)
    return encontrados


# 'def exibir_fluxo(...)' renderiza a aba de abertura com o fluxograma SVG.
def exibir_fluxo() -> None:
    """Aba 1 — landing page com o fluxograma CRISP-DM de 13 etapas."""
    st.markdown("#### Pipeline CRISP-DM em 13 etapas")
    st.caption(
        "Da base transacional de PME à API de inferência em produção — "
        "6 fases, 13 etapas executáveis, com laço de iteração."
    )

    # SVG lido do disco e passado como string (st.image aceita SVG nativamente).
    caminho_svg = PASTA_APP / "fluxo_crisp_dm.svg"
    if caminho_svg.is_file():
        st.image(
            caminho_svg.read_text(encoding="utf-8"),
            width="stretch",
            alt="Fluxograma do ciclo CRISP-DM com 13 etapas distribuídas em 6 fases",
        )
    else:
        st.error(f"Fluxograma não encontrado: `{caminho_svg.name}`")

    # Lista textual das 13 etapas (acessibilidade e consulta rápida).
    with st.expander("Ver a lista das 13 etapas"):
        for fase, titulo, descricao in ETAPAS_PIPELINE:
            st.markdown(f"**{fase} · {titulo}** — {descricao}")


# 'def exibir_saude_360(...)' renderiza a aba do dashboard de saúde da empresa.
def exibir_saude_360(dataset: str, pasta_fase_02: Path) -> None:
    """Aba 2 — imagem única do dashboard/radar de saúde 360°.

    Args:
        dataset (str): Dataset ativo.
        pasta_fase_02 (Path): Pasta da Fase 02 do dataset ativo.
    """
    st.markdown("#### Dashboard de Saúde 360°")
    st.caption(
        "Visão agnóstica da companhia: radar de saúde, KPIs executivos e "
        "semáforo de sinais — gerados pela Fase 02 a partir do prontuário executivo."
    )

    caminho_dashboard = pasta_fase_02 / "dashboard_saude_360.png"
    caminho_prontuario = pasta_fase_02 / "prontuario_executivo.json"

    if caminho_dashboard.is_file():
        st.image(
            str(caminho_dashboard),
            width="stretch",
            alt=(
                f"Dashboard de saúde 360° do dataset {dataset}, com radar de "
                "indicadores, cartões de KPI e semáforo de sinais"
            ),
        )
        st.caption(f"`{caminho_dashboard.relative_to(RAIZ_PROJETO)}`")
    else:
        st.info(
            "O dashboard ainda não foi gerado. Rode a Fase 02 (Raio-X) ou "
            "use o botão abaixo para gerar a partir do prontuário existente."
        )

    # Linha de ações: gerar/atualizar a placa + baixar o prontuário em JSON.
    with st.container(horizontal=True):
        if st.button(
            "Gerar/atualizar dashboard",
            icon=":material/refresh:",
            disabled=not caminho_prontuario.is_file(),
        ):
            with st.spinner("Gerando o dashboard de saúde 360°..."):
                try:
                    # Import tardio: só carrega matplotlib/JSON quando solicitado.
                    from src.etapas.fase_02_exploracao.visao_360_saude import (
                        gerar_dashboard_saude,
                    )

                    gerar_dashboard_saude(dataset=dataset, pasta_saida=pasta_fase_02)
                    st.rerun()
                except Exception as erro:
                    st.error(f"Falha ao gerar o dashboard: {erro}")

        if caminho_prontuario.is_file():
            st.download_button(
                "Baixar prontuário (JSON)",
                data=caminho_prontuario.read_bytes(),
                file_name="prontuario_executivo.json",
                mime="application/json",
                icon=":material/download:",
            )

    if not caminho_prontuario.is_file():
        st.caption(
            "Sem `prontuario_executivo.json` — execute a Fase 02 para criá-lo."
        )


# 'def exibir_relatorios(...)' renderiza a aba dos relatórios departamentais.
def exibir_relatorios(dataset: str, pasta_fase_02: Path) -> None:
    """Aba 3 — PNGs e laudos departamentais (renderização preguiçosa).

    Args:
        dataset (str): Dataset ativo.
        pasta_fase_02 (Path): Pasta da Fase 02 do dataset ativo.
    """
    st.markdown("#### Relatórios por departamento")
    st.caption(
        "Cada departamento da Fase 02 publica seus gráficos (PNG) e laudos (MD) "
        "na própria pasta."
    )

    # Pastas reais existentes na Fase 02 (ordem fixa + extras dinâmicas).
    pastas_disponiveis = sorted(
        p.name for p in pasta_fase_02.iterdir() if p.is_dir()
    )
    mapa_depts = {pasta: (nome, icone) for pasta, nome, icone in DEPARTAMENTOS}

    # Mantém a ordem canônica dos 10 departamentos e acrescenta sobras.
    pastas_ordenadas = [p for p, _, _ in DEPARTAMENTOS if p in pastas_disponiveis]
    pastas_ordenadas += [p for p in pastas_disponiveis if p not in mapa_depts]

    if not pastas_ordenadas:
        st.warning("Nenhum departamento com relatórios. Execute a Fase 02.")
        return

    # Escolha do departamento (segmented control com render preguiçoso).
    def rotulo_opcao(pasta: str) -> str:
        """Monta o rótulo com ícone da opção do segmented control."""
        if pasta in mapa_depts:
            nome, icone = mapa_depts[pasta]
            return f"{icone} {nome}"
        return f":material/folder: {pasta.replace('_', ' ').title()}"

    opcoes = [rotulo_opcao(p) for p in pastas_ordenadas]
    escolha = st.segmented_control(
        "Departamento",
        options=opcoes,
        default=opcoes[0],
        label_visibility="collapsed",
    )
    if escolha is None:
        escolha = opcoes[0]

    pasta_escolhida = pastas_ordenadas[opcoes.index(escolha)]
    pasta_completa = pasta_fase_02 / pasta_escolhida

    imagens = sorted(pasta_completa.glob("*.png"))
    laudos = sorted(pasta_completa.glob("*.md"))

    if not imagens and not laudos:
        st.info("Este departamento ainda não possui gráficos.")
        return

    st.caption(
        f"{len(imagens)} gráfico(s) · {len(laudos)} laudo(s) — "
        f"`{pasta_completa.relative_to(RAIZ_PROJETO)}`"
    )

    # Gráficos do departamento.
    for img_path in imagens:
        titulo = img_path.stem.replace("_", " ").title()
        st.markdown(f"**{titulo}**")
        try:
            st.image(str(img_path), width="stretch", alt=titulo)
        except Exception as erro:
            st.error(f"Erro ao carregar `{img_path.name}`: {erro}")

    # Laudos em Markdown dentro de expansores.
    for laudo_path in laudos:
        with st.expander(f"Laudos — {laudo_path.stem}"):
            try:
                st.markdown(laudo_path.read_text(encoding="utf-8"))
            except Exception as erro:
                st.error(f"Erro ao carregar laudo: {erro}")


# -----------------------------------------------------------------------
# CORPO DA APLICAÇÃO
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="CRISP-DM Operacional",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar: seleção de dataset (somente quem tem relatórios da Fase 02) ---
with st.sidebar:
    st.markdown("#### Dataset com relatórios")
    datasets = datasets_com_relatorios()

    if not datasets:
        st.info(
            "Nenhum relatório da Fase 02 encontrado. Execute o Raio-X "
            "(Fase 02) para materializar os relatórios."
        )
        dataset_ativo = None
    else:
        dataset_ativo = st.selectbox(
            "Dataset",
            options=datasets,
            label_visibility="collapsed",
            placeholder="Selecione um dataset",
        )
        st.caption(
            "Relatórios lidos de `relatorios/<dataset>/…/fase_02/` "
            "(gerados pela execução da Fase 02)."
        )

    st.divider()
    st.markdown("#### Navegação entre aplicações")
    st.page_link(
        "http://localhost:8502",
        label="Abrir plataforma operacional (ingestão, raio-x, torneio, predição)",
        icon=":material/open_in_new:",
        disabled=False,
    )
    st.caption("Se a página não abrir, aguarde o processamento operacional na porta 8502.")

st.title("CRISP-DM Operacional", icon=":material/analytics:")
st.caption(
    "Pipeline completo de ciência de dados para PMEs — fluxo, saúde 360° "
    "e relatórios departamentais."
)

# --- Abas (render preguiçoso: só a aba aberta executa) ---
abas = st.tabs(
    ["Início — Fluxo CRISP-DM", "Saúde 360°", "Relatórios"],
    on_change="rerun",
)

with abas[0]:
    if abas[0].open:
        exibir_fluxo()

with abas[1]:
    if abas[1].open:
        if not dataset_ativo:
            st.warning("Selecione um dataset no sidebar para ver o dashboard.")
        else:
            pasta_fase_02 = encontrar_pasta_fase_02(dataset_ativo)
            if pasta_fase_02 is None:
                st.warning("Sem pasta da Fase 02 para o dataset selecionado.")
            else:
                exibir_saude_360(dataset_ativo, pasta_fase_02)

with abas[2]:
    if abas[2].open:
        if not dataset_ativo:
            st.warning("Selecione um dataset no sidebar para ver os relatórios.")
        else:
            pasta_fase_02 = encontrar_pasta_fase_02(dataset_ativo)
            if pasta_fase_02 is None:
                st.warning("Sem pasta da Fase 02 para o dataset selecionado.")
            else:
                exibir_relatorios(dataset_ativo, pasta_fase_02)
