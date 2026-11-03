"""Página 02 — Raio-X Empresarial (Fase CRISP-DM 02).

Execução da Fase 02 e exibição dos relatórios por departamento.
Usa renderização lazy: apenas o departamento selecionado é carregado,
evitando reprocessar os 10 conjuntos de imagens a cada interação.
"""

from pathlib import Path

import streamlit as st

from ui_comum import (
    garantir_estado,
    obter_cliente,
    painel_job,
    resumo_dataset,
    submeter_fase,
)

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


def encontrar_pasta_fase_02(dataset_nome: str) -> Path | None:
    """Localiza a pasta de relatórios da Fase 02 (testa os dois formatos)."""
    candidatos = [
        Path("relatorios") / dataset_nome / dataset_nome / "fase_02",
        Path("relatorios") / dataset_nome / "fase_02",
    ]
    for candidato in candidatos:
        if candidato.is_dir():
            return candidato
    return None


def exibir_execucao(nome: str) -> None:
    """Seção de execução da Fase 02 com painel de job não-bloqueante."""
    resumo = resumo_dataset(nome) or {}
    status_fases = resumo.get("status_fases") or {}
    fase_02_status = status_fases.get("02", "pendente")
    job_status = painel_job(nome, "02")

    col1, col2 = st.columns([3, 1])

    with col1:
        if fase_02_status == "concluida":
            st.success("Fase 02 concluída — relatórios disponíveis abaixo.")
        elif job_status in ("executando", "pendente"):
            st.info("Fase 02 em execução. Acompanhe o painel acima.")
        else:
            st.caption(
                "A Fase 02 gera relatórios analíticos para os 10 departamentos "
                "(gráficos em `relatorios/`)."
            )

    with col2:
        pode_executar = (
            fase_02_status != "concluida"
            and job_status not in ("executando", "pendente")
        )
        if st.button(
            "Executar Fase 02",
            type="primary" if pode_executar else "secondary",
            disabled=not pode_executar,
            width="stretch",
        ):
            with st.spinner("Submetendo a Fase 02..."):
                submeter_fase(nome, "02")
            st.rerun()


def exibir_departamento(pasta_base: Path, pasta_dep: str, nome_dep: str) -> None:
    """Renderiza somente o departamento escolhido (lazy)."""
    pasta_completa = pasta_base / pasta_dep

    if not pasta_completa.is_dir():
        st.info(
            f"O departamento **{nome_dep}** ainda não possui relatórios. "
            "Execute a Fase 02 para gerá-los."
        )
        return

    imagens = sorted(pasta_completa.glob("*.png"))
    laudos = sorted(pasta_completa.glob("*.md"))

    if not imagens and not laudos:
        st.info(f"O departamento **{nome_dep}** ainda não possui gráficos.")
        return

    st.caption(
        f"{len(imagens)} gráfico(s) · {len(laudos)} laudo(s) — `{pasta_completa}`"
    )

    for img_path in imagens:
        titulo = img_path.stem.replace("_", " ").title()
        st.markdown(f"**{titulo}**")
        try:
            st.image(str(img_path), width="stretch", alt=titulo)
        except Exception as erro:
            st.error(f"Erro ao carregar `{img_path.name}`: {erro}")

    for laudo_path in laudos:
        with st.expander(f"Laudos — {laudo_path.stem}"):
            try:
                st.markdown(laudo_path.read_text(encoding="utf-8"))
            except Exception as erro:
                st.error(f"Erro ao carregar laudo: {erro}")


def main() -> None:
    """Corpo principal da página."""
    garantir_estado()
    st.caption("Diagnóstico completo por departamento")

    nome = st.session_state.dataset_nome

    if not nome:
        st.warning(
            "Nenhum dataset ativo. Selecione um no sidebar ou crie um na página de Ingestão."
        )
        if st.button("Ir para Ingestão", icon=":material/upload:"):
            st.switch_page("app_pages/pagina_01_ingestao.py")
        return

    st.info(f"Dataset ativo: **{nome}**")

    # --- Execução ---
    st.markdown("#### Fase 02")
    exibir_execucao(nome)
    st.divider()

    pasta_fase_02 = encontrar_pasta_fase_02(nome)

    # --- Visão 360°: dashboard de saúde gerado pela própria Fase 02 ---
    # (radar de saúde + KPIs executivos + semáforo de sinais)
    if pasta_fase_02 is not None:
        dashboard = pasta_fase_02 / "dashboard_saude_360.png"
        if dashboard.is_file():
            st.markdown("#### Visão 360° — Saúde da empresa")
            st.image(
                str(dashboard),
                width="stretch",
                alt="Dashboard de saúde 360° com radar de indicadores, KPIs executivos e semáforo de sinais",
            )
            st.caption("`dashboard_saude_360.png` — regenerado a cada execução da Fase 02.")
            st.divider()

    # --- Relatórios (só o departamento ativo é renderizado) ---
    st.markdown("#### Relatórios por departamento")

    if pasta_fase_02 is None:
        st.warning(
            "Nenhum relatório da Fase 02 encontrado. Execute a fase acima para gerar."
        )
        return

    # Escolha do departamento (segmented control com lazy render).
    opcoes = [f"{icone} {dep_nome}" for _, dep_nome, icone in DEPARTAMENTOS]
    escolha = st.segmented_control(
        "Departamento",
        options=opcoes,
        default=opcoes[0],
        label_visibility="collapsed",
    )

    if escolha is None:
        escolha = opcoes[0]

    # Mapeia a opção de volta para a pasta.
    pasta_dep, nome_dep = next(
        (p, n) for p, n, i in DEPARTAMENTOS if f"{i} {n}" == escolha
    )

    with st.container(border=True):
        exibir_departamento(pasta_fase_02, pasta_dep, nome_dep)

    # --- Navegação para a próxima fase ---
    resumo = resumo_dataset(nome) or {}
    status_fases = resumo.get("status_fases") or {}

    if status_fases.get("02") == "concluida":
        st.divider()
        if st.button(
            "Ir para Torneio (Fases 04 + 05) →",
            type="primary",
            width="stretch",
            icon=":material/arrow_forward:",
        ):
            st.switch_page("app_pages/pagina_03_torneio.py")


if __name__ == "__main__":
    main()
