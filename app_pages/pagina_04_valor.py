"""Página 04 — Apuração de Valor (Fase CRISP-DM final).

Impacto financeiro, governança e valor entregue pelo modelo campeão.
"""

import streamlit as st

from ui_comum import garantir_estado, obter_cliente, resumo_dataset


def main() -> None:
    """Corpo principal da página."""
    garantir_estado()
    st.caption("Impacto financeiro, governança e valor entregue pelo modelo campeão")

    nome = st.session_state.dataset_nome

    if not nome:
        st.warning(
            "Nenhum dataset ativo. Selecione um no sidebar ou crie um na página de Ingestão."
        )
        if st.button("Ir para Ingestão", icon=":material/upload:"):
            st.switch_page("app_pages/pagina_01_ingestao.py")
        return

    st.info(f"Dataset ativo: **{nome}**")
    cliente = obter_cliente()

    # Pré-requisito: pódio existente.
    resumo = resumo_dataset(nome) or {}
    status_fases = resumo.get("status_fases") or {}
    top3 = (cliente.obter_top3(nome) or {}).get("top3") or []

    if not top3:
        st.warning(
            "Nenhum modelo no pódio ainda. Execute o **Torneio** (Fases 04/05) antes de apurar o valor."
        )
        if st.button("Ir para Torneio", icon=":material/emoji_events:"):
            st.switch_page("app_pages/pagina_03_torneio.py")
        return

    # --- Apuração ---
    st.markdown("#### Apurar valor do modelo campeão")
    st.caption(
        "A apuração lê os artefatos gerados nas fases anteriores "
        "(scorecard, contrato de problema, registros de governança)."
    )

    if st.button("Apurar valor", type="primary", icon=":material/calculate:"):
        st.session_state["valor_apurado"] = None
        try:
            with st.spinner("Apurando valor financeiro e governança..."):
                st.session_state["valor_apurado"] = cliente.apurar_valor(nome)
        except Exception as erro:
            st.error(f"Falha ao apurar valor: {erro}")

    resultado = st.session_state.get("valor_apurado")
    if not resultado:
        return

    # --- Campeão ---
    campeao = resultado.get("campeao")
    if campeao:
        st.success(f"Modelo campeão: **{campeao}**")
    else:
        st.warning(
            "Nenhum modelo campeão eleito ainda. Eleja no **Torneio** para completar a apuração."
        )

    # --- Impacto financeiro ---
    st.divider()
    st.markdown("#### Impacto financeiro")
    impacto = resultado.get("impacto_financeiro") or {}

    if impacto.get("disponivel"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Custo total apurado", f"R$ {impacto.get('total_apurado_R$', 0):,.2f}")
        with col2:
            st.metric(
                "Custo falso negativo",
                f"R$ {impacto.get('custo_falso_negativo', 0):,.2f}",
                help="Custo de perder uma oportunidade real.",
            )
        with col3:
            st.metric(
                "Custo falso positivo",
                f"R$ {impacto.get('custo_falso_positivo', 0):,.2f}",
                help="Custo de agir sobre uma falsa oportunidade.",
            )
        st.caption(
            f"Verdadeiro positivo (acerto): R$ {impacto.get('verdadeiro_positivo', 0):,.2f}"
        )
    else:
        st.info(
            "Contrato de problema com custos de negócio ainda não vinculado a este dataset."
        )

    # --- Métricas do campeão ---
    st.divider()
    st.markdown("#### Métricas de desempenho do campeão")
    metricas = resultado.get("metricas_top3") or {}

    if metricas:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("R² Score", f"{metricas.get('r2', 0):.4f}")
            st.caption("Coeficiente de determinação (maior melhor).")
        with col2:
            st.metric("RMSE", f"{metricas.get('rmse', 0):,.2f}")
            st.caption("Erro quadrático médio (menor melhor).")
        with col3:
            st.metric("MAE", f"{metricas.get('mae', 0):,.2f}")
            st.caption("Erro absoluto médio (menor melhor).")
    else:
        st.info("Métricas do campeão não disponíveis. Eleja um campeão no Torneio.")

    # --- Governança ---
    st.divider()
    st.markdown("#### Governança & rastreabilidade")

    hash_artefato = resultado.get("hash_artefato")
    if hash_artefato:
        st.metric("Hash do artefato (SHA-256)", f"`{hash_artefato}`")
        st.caption("Assinatura do registro do dataset — garante integridade e rastreabilidade.")
    else:
        st.info("Hash do artefato ainda não disponível.")

    diario = resultado.get("diario_observacoes") or []
    if diario:
        with st.expander("Diário de observações (últimas 10)"):
            for observacao in diario:
                st.markdown(f"- {observacao}")

    # --- Scorecard ---
    scorecard_path = resultado.get("scorecard_path")
    if scorecard_path:
        st.divider()
        st.markdown("#### Scorecard completo")
        st.code(f"Arquivo: {scorecard_path}", language=None)
        try:
            import pandas as pd

            df_scorecard = pd.read_csv(scorecard_path)
            st.dataframe(df_scorecard, width="stretch")
        except Exception as erro:
            st.warning(f"Erro ao carregar scorecard: {erro}")


if __name__ == "__main__":
    main()
