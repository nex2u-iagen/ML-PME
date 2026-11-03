"""Página 03 — Torneio de Modelos (Fases 03, 04 e 05 CRISP-DM).

Vinculação do problema de negócio, preparação dos dados (Fase 03),
treinamento/avaliação (Fase 04) e seleção do modelo campeão (Fase 05).
"""

from pathlib import Path

import pandas as pd
import streamlit as st

from app_pages.componentes.graficos_modelagem import exibir_diagnosticos_modelos

from ui_comum import (
    garantir_estado,
    invalidar_cache_datasets,
    listar_problemas_cacheado,
    obter_cliente,
    painel_job,
    resumo_dataset,
    submeter_fase,
)

# Rótulos amigáveis das famílias de tarefa suportadas pela plataforma.
ROTULOS_TAREFA = {
    "classificacao": "Classificação",
    "regressao": "Regressão",
    "agrupamento": "Agrupamento",
    "deteccao_anomalias": "Detecção de anomalias",
}

# Métricas derivadas exibidas na tabela de cálculos (ordem de leitura).
COLUNAS_CALCULO = [
    "verdadeiro_positivo",
    "falso_positivo",
    "falso_negativo",
    "verdadeiro_negativo",
    "acuracia",
    "precisao",
    "recall",
    "f1_score",
    "especificidade",
    "roc_auc",
    "r2",
    "rmse",
    "mae",
    "mape",
    "silhueta",
    "inercia",
    "taxa_anomalia",
    "custo_liquido",
]

# Amostragem das colunas de cálculo na tabela comparativa.
ROTULOS_COLUNAS = {
    "verdadeiro_positivo": "VP",
    "falso_positivo": "FP",
    "falso_negativo": "FN",
    "verdadeiro_negativo": "TN",
    "f1_score": "F1",
    "custo_liquido": "Custo líquido (R$)",
}


def problema_vinculado(resumo: dict) -> dict | None:
    """Retorna o contrato de problema já vinculado ao dataset (ou None)."""
    return (resumo or {}).get("contrato")


def exibir_problema(nome: str, resumo: dict, cliente) -> str | None:
    """Seção de vínculo do problema de negócio. Devolve o id vigente (ou None)."""
    st.markdown("#### Problema de negócio")

    contrato = problema_vinculado(resumo)

    if contrato:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.success(
                f"Contrato vinculado: **{contrato.get('nome')}** "
                f"(`{contrato.get('id')}`) — {contrato.get('tipo_tarefa', '')}"
            )
            pergunta = contrato.get("pergunta_negocio")
            if pergunta:
                st.caption(f"Pergunta: {pergunta}")
        with col2:
            if st.button("Trocar problema", width="stretch"):
                st.session_state["mostrar_vinculo"] = True
                st.rerun()

        id_vigente = contrato.get("id")
    else:
        st.warning(
            "Nenhum problema vinculado. Escolha um dos 15 templates do catálogo "
            "para dirigir a preparação e a modelagem."
        )
        id_vigente = None
        st.session_state["mostrar_vinculo"] = True

    # Formulário de vínculo (aberto quando não há contrato ou pelo botão).
    if st.session_state.get("mostrar_vinculo"):
        problemas = listar_problemas_cacheado()
        if not problemas:
            st.error("Catálogo de problemas indisponível. Verifique a API.")
            return id_vigente

        opcoes = {p["id"]: p for p in problemas}
        ids = list(opcoes.keys())

        indice = ids.index(id_vigente) if id_vigente in ids else 0
        escolhido = st.selectbox(
            "Template de problema",
            options=ids,
            index=indice,
            format_func=lambda i: (
                f"{opcoes[i].get('nome', i)} · {opcoes[i].get('tipo_tarefa', '')}"
            ),
            help="Cada template define alvo, granularidade e métrica de otimização.",
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            vincular = st.button(
                "Vincular problema", type="primary", width="stretch"
            )
        with col2:
            if st.button("Cancelar", width="stretch"):
                st.session_state["mostrar_vinculo"] = False
                st.rerun()

        if vincular:
            try:
                with st.spinner("Vinculando problema ao dataset..."):
                    cliente.vincular_problema(nome, escolhido)
                invalidar_cache_datasets()
                st.session_state["mostrar_vinculo"] = False
                st.success(f"Problema `{escolhido}` vinculado com sucesso.")
                st.rerun()
            except Exception as erro:
                st.error(f"Falha ao vincular problema: {erro}")

    st.divider()
    return id_vigente


def exibir_fase_03(nome: str, status_fases: dict, problema_id: str | None) -> None:
    """Seção de execução da Fase 03 (preparação/ABT)."""
    st.markdown("#### Fase 03 — Preparação dos dados")

    fase_status = status_fases.get("03", "pendente")
    job_status = painel_job(nome, "03")

    col1, col2 = st.columns([3, 1])

    with col1:
        if fase_status == "concluida":
            st.success("Fase 03 concluída — ABT e partições (treino/val/teste) geradas.")
        elif job_status in ("executando", "pendente"):
            st.info("Fase 03 em execução. Acompanhe o painel acima.")
        else:
            st.caption(
                "A Fase 03 constrói a Tabela Analítica (ABT) e as partições "
                "treino/validação/teste, guiada pelo contrato de problema."
            )

    with col2:
        pode_executar = (
            fase_status != "concluida"
            and job_status not in ("executando", "pendente")
            and bool(problema_id)
        )
        if st.button(
            "Executar Fase 03",
            type="primary" if pode_executar else "secondary",
            disabled=not pode_executar,
            width="stretch",
        ):
            with st.spinner("Submetendo a Fase 03..."):
                submeter_fase(nome, "03", problema=problema_id)
            st.rerun()

    if not problema_id:
        st.warning("Vincule um problema de negócio antes de executar a Fase 03.")


def exibir_fase_04(nome: str, status_fases: dict, problema_id: str | None) -> None:
    """Seção de execução da Fase 04 (torneio), exigindo a Fase 03 concluída."""
    st.markdown("#### Fase 04 — Torneio de modelos")

    fase_status = status_fases.get("04", "pendente")
    job_status = painel_job(nome, "04")
    preparacao_ok = status_fases.get("03") == "concluida"

    col1, col2 = st.columns([3, 1])

    with col1:
        if fase_status == "concluida":
            st.success("Fase 04 concluída — modelos treinados e pódio Top 3 gerado.")
        elif job_status in ("executando", "pendente"):
            st.info(
                "Fase 04 em execução (treinamento pode demorar). "
                "Acompanhe o painel acima."
            )
        elif not preparacao_ok:
            st.warning(
                "Execute primeiro a **Fase 03 (Preparação)** — ela gera as "
                "partições necessárias ao treinamento."
            )
        else:
            st.caption("A Fase 04 treina múltiplos algoritmos e gera o pódio Top 3.")

    with col2:
        pode_executar = (
            fase_status != "concluida"
            and job_status not in ("executando", "pendente")
            and preparacao_ok
        )
        if st.button(
            "Executar Fase 04",
            type="primary" if pode_executar else "secondary",
            disabled=not pode_executar,
            width="stretch",
        ):
            with st.spinner("Submetendo a Fase 04..."):
                submeter_fase(nome, "04", problema=problema_id)
            st.rerun()


def _formatar_valor(valor, casas: int = 4) -> str:
    """Formata um número para exibição; devolve '—' para ausentes/inválidos."""
    if valor is None or isinstance(valor, bool):
        return "—"
    if isinstance(valor, (int, float)):
        try:
            if valor != valor or valor in (float("inf"), float("-inf")):
                return "—"
            return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (TypeError, ValueError):
            return "—"
    return str(valor)


def _formatar_moeda(valor) -> str:
    """Formata um valor em reais (R$ 1.234,56); '—' quando ausente."""
    if valor is None or isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return "—"
    if valor != valor or valor in (float("inf"), float("-inf")):
        return "—"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _avaliacao_de(top3_data: dict) -> dict:
    """Retorna o laudo de avaliação detalhada (ou dict vazio)."""
    avaliacao = (top3_data or {}).get("avaliacao") or {}
    return avaliacao if isinstance(avaliacao, dict) else {}


def _modelos_avaliados(avaliacao: dict) -> dict:
    """Retorna o mapa nome → detalhe do laudo (ou dict vazio)."""
    modelos = avaliacao.get("modelos") or {}
    return modelos if isinstance(modelos, dict) else {}


def exibir_leaderboard(top3_data: dict) -> None:
    """Seção de métricas: leaderboard completo do torneio (Fase 04)."""
    leaderboard = (top3_data or {}).get("leaderboard") or []
    if not leaderboard:
        st.caption(
            "Leaderboard ainda não disponível. Execute a **Fase 04** para gerar o placar."
        )
        return

    st.markdown("#### Métricas de avaliação — leaderboard do torneio")

    tipo = (top3_data or {}).get("tipo_tarefa")
    metrica = (top3_data or {}).get("metrica_otimizacao")
    if tipo or metrica:
        partes = []
        if tipo:
            partes.append(f"Tipo de problema: **{ROTULOS_TAREFA.get(tipo, tipo)}**")
        if metrica:
            partes.append(f"Métrica de otimização: **{metrica}**")
        st.caption(" · ".join(partes))

    df = pd.DataFrame(leaderboard)
    for coluna in df.columns:
        if pd.api.types.is_float_dtype(df[coluna]):
            df[coluna] = df[coluna].round(4)
    df = df.rename(columns={c: ROTULOS_COLUNAS.get(c, c.replace("_", " ").title()) for c in df.columns})

    st.dataframe(df, width="stretch", hide_index=True, height=min(380, 44 + 35 * len(df)))
    st.caption(
        f"{len(df)} modelo(s) avaliado(s) sobre a partição de validação cego "
        "(ordem do placar: melhor primeiro)."
    )


def exibir_diagnostico_por_tipo(top3_data: dict, top3: list) -> None:
    """Seção de diagnóstico: figuras + cálculos por família de problema.

    Para classificação exibe as **matrizes de confusão** com VP/FP/FN/TN e as
    métricas derivadas; para regressão, dispersão previsto × real; para
    agrupamento e anomalias, a distribuição detectada — sempre com os cálculos.
    """
    avaliacao = _avaliacao_de(top3_data)
    modelos_av = _modelos_avaliados(avaliacao)

    if not modelos_av:
        st.info(
            "Avaliação detalhada indisponível. Execute (ou reexecute) a **Fase 04** "
            "para gerar `avaliacao_top3.json` com as matrizes de confusão e os cálculos."
        )
        return

    tarefa = str(
        avaliacao.get("tipo_tarefa") or (top3_data or {}).get("tipo_tarefa") or ""
    ).lower()
    rotulo_tarefa = ROTULOS_TAREFA.get(tarefa, tarefa or "não identificado")
    particao = avaliacao.get("particao") or "validacao"
    total = avaliacao.get("total_amostras")

    st.markdown(f"#### Diagnóstico por tipo de problema — {rotulo_tarefa}")
    st.caption(
        f"Partição de **{particao}**"
        + (f" · **{total}** amostras avaliadas" if total else "")
        + " · figura e cálculos por finalista."
    )

    # --- FIGURAS lado a lado (uma por finalista) ---
    finais = [m for m in top3 if m in modelos_av] or list(modelos_av)
    cols = st.columns(min(3, len(finais)))

    for idx, nome_modelo in enumerate(finais[:3]):
        info = modelos_av.get(nome_modelo) or {}
        with cols[idx]:
            st.markdown(f"**{nome_modelo}**")
            caminho_figura = info.get("figura")
            if caminho_figura and Path(caminho_figura).is_file():
                st.image(str(caminho_figura), width="stretch")
            else:
                st.caption("Figura não disponível para este finalista.")
            if info.get("erro"):
                st.caption(f"⚠ {info['erro']}")

    # --- TABELA DE CÁLCULOS (contagens + métricas derivadas + custo) ---
    linhas = []
    for nome_modelo in finais:
        info = modelos_av.get(nome_modelo) or {}
        linha: dict = {"Modelo": nome_modelo}
        for chave, valor in (info.get("metricas") or {}).items():
            linha[chave] = valor
        matriz = info.get("matriz_confusao") or {}
        for chave in ("verdadeiro_positivo", "falso_positivo", "falso_negativo", "verdadeiro_negativo"):
            if chave in matriz:
                linha[chave] = matriz[chave]
        custos = info.get("custos_negocio") or {}
        if "custo_liquido" in custos:
            linha["custo_liquido"] = custos["custo_liquido"]
        linhas.append(linha)

    if linhas:
        st.markdown("**Cálculos por finalista**")
        df_calc = pd.DataFrame(linhas)
        ordenadas = ["Modelo"] + [c for c in COLUNAS_CALCULO if c in df_calc.columns]
        ordenadas += [c for c in df_calc.columns if c not in ordenadas]
        df_calc = df_calc[ordenadas]
        df_calc = df_calc.rename(
            columns={c: ROTULOS_COLUNAS.get(c, c.replace("_", " ").title()) for c in df_calc.columns}
        )
        for coluna in df_calc.columns:
            if coluna != "Modelo" and pd.api.types.is_float_dtype(df_calc[coluna]):
                df_calc[coluna] = df_calc[coluna].round(4)
        st.dataframe(df_calc, width="stretch", hide_index=True)

        if tarefa == "classificacao":
            st.caption(
                "**VP** = verdadeiro positivo · **FP** = falso positivo · "
                "**FN** = falso negativo (custo alto) · **TN** = verdadeiro negativo. "
                "Precisão = VP/(VP+FP) · Recall = VP/(VP+FN) · "
                "F1 = 2·(precisão·recall)/(precisão+recall) · "
                "Especificidade = TN/(TN+FP)."
            )


def exibir_analise_individual(top3_data: dict, top3: list) -> None:
    """Seção de análise individual de cada um dos 3 finalistas (seletor segmentado)."""
    avaliacao = _avaliacao_de(top3_data)
    modelos_av = _modelos_avaliados(avaliacao)

    st.markdown("#### Análise individual dos finalistas")

    if not top3:
        st.caption("Sem finalistas para analisar.")
        return

    if not modelos_av:
        st.info(
            "Avaliação detalhada indisponível. Execute (ou reexecute) a **Fase 04** "
            "para gerar o laudo por finalista."
        )
        return

    metricas_gerais = (top3_data or {}).get("metricas") or {}
    campeao_atual = (top3_data or {}).get("campeao")
    metrica_otimizacao = (top3_data or {}).get("metrica_otimizacao")
    tarefa = str(
        avaliacao.get("tipo_tarefa") or (top3_data or {}).get("tipo_tarefa") or ""
    ).lower()

    # --- Seletor do finalista (um por vez) ---
    escolhido = st.segmented_control(
        "Finalista",
        options=top3,
        default=top3[0],
        format_func=lambda m: f"{top3.index(m) + 1}º — {m}",
        key="seg_finalista_avaliacao",
        width="stretch",
    )

    nome_modelo = escolhido or top3[0]
    info = modelos_av.get(nome_modelo) or {}
    posicao = top3.index(nome_modelo) + 1 if nome_modelo in top3 else 0

    with st.container(border=True):
        cabecalho = [f"🏅 {posicao}º lugar — **{nome_modelo}**"]
        if campeao_atual == nome_modelo:
            cabecalho.append("✅ **Campeão atual**")
        if metrica_otimizacao and metrica_otimizacao in (info.get("metricas") or {}):
            valor_metrica = info["metricas"][metrica_otimizacao]
            cabecalho.append(
                f"Métrica de otimização `{metrica_otimizacao}` = "
                f"**{_formatar_valor(valor_metrica)}**"
            )
        st.markdown(" · ".join(cabecalho))

        if info.get("erro"):
            st.error(f"Falha ao avaliar este finalista: {info['erro']}")
            return

        # --- FIGURA do finalista ---
        caminho_figura = info.get("figura")
        if caminho_figura and Path(caminho_figura).is_file():
            st.image(str(caminho_figura), width="stretch")

        # --- MÉTRICAS da família de tarefa ---
        metricas = info.get("metricas") or {}
        metricas_exibir = metricas or metricas_gerais.get(nome_modelo) or {}
        if metricas_exibir:
            st.markdown("**Métricas**")
            cols = st.columns(min(4, max(1, len(metricas_exibir))))
            for idx, (chave, valor) in enumerate(metricas_exibir.items()):
                with cols[idx % len(cols)]:
                    st.metric(chave.replace("_", " ").title(), _formatar_valor(valor))

        # --- CLASSIFICAÇÃO: matriz de confusão + cálculos + custos ---
        matriz = info.get("matriz_confusao") or {}
        if matriz:
            st.markdown("**Matriz de confusão (contagens)**")
            contagens = [
                ("Verdadeiros positivos (VP)", matriz.get("verdadeiro_positivo")),
                ("Falsos positivos (FP)", matriz.get("falso_positivo")),
                ("Falsos negativos (FN)", matriz.get("falso_negativo")),
                ("Verdadeiros negativos (TN)", matriz.get("verdadeiro_negativo")),
            ]
            cols = st.columns(4)
            for idx, (rotulo, valor) in enumerate(contagens):
                with cols[idx]:
                    st.metric(rotulo, valor if valor is not None else "—")
            classes = matriz.get("classes")
            if classes:
                st.caption(
                    f"Classes: {classes} (linha = real, coluna = previsto; "
                    "a matriz é [[TN, FP], [FN, TP]] para a classe positiva {classes[-1]})."
                )

        custos = info.get("custos_negocio") or {}
        if custos:
            st.markdown("**Custo de negócio dos erros**")
            cols = st.columns(4)
            with cols[0]:
                st.metric("Perda por FN", _formatar_moeda(custos.get("perda_falsos_negativos")))
            with cols[1]:
                st.metric("Perda por FP", _formatar_moeda(custos.get("perda_falsos_positivos")))
            with cols[2]:
                st.metric("Ganho por VP", _formatar_moeda(custos.get("ganho_verdadeiros_positivos")))
            with cols[3]:
                st.metric(
                    "Custo líquido",
                    _formatar_moeda(custos.get("custo_liquido")),
                    help="Perda_FN + Perda_FP − Ganho_VP sobre a partição avaliada.",
                )
            st.caption(
                f"Unitários: FN = {_formatar_moeda(custos.get('custo_falso_negativo_unit'))} · "
                f"FP = {_formatar_moeda(custos.get('custo_falso_positivo_unit'))} · "
                f"VP = {_formatar_moeda(custos.get('ganho_verdadeiro_positivo_unit'))}"
            )

        # --- NÃO SUPERVISIONADOS: distribuições ---
        distribuicao = info.get("distribuicao_grupos") or info.get("distribuicao_anomalias") or {}
        if distribuicao:
            st.markdown("**Distribuição detectada**")
            df_dist = pd.DataFrame(
                [{"Grupo": chave, "Amostras": valor} for chave, valor in distribuicao.items()]
            )
            st.dataframe(df_dist, width="stretch", hide_index=True, height=min(260, 44 + 35 * len(df_dist)))

        if tarefa not in ("classificacao",) and not metricas:
            st.caption("Sem métricas detalhadas para este finalista.")


def exibir_top3(nome: str, cliente) -> bool:
    """Exibe o pódio Top 3, métricas, diagnóstico e a eleição do campeão.

    Returns:
        bool: ``True`` quando há finalistas no pódio.
    """
    try:
        top3_data = cliente.obter_top3(nome)
    except Exception as erro:
        st.warning(f"Erro ao consultar Top 3: {erro}")
        return False

    top3 = (top3_data or {}).get("top3") or []
    metricas_por_modelo = (top3_data or {}).get("metricas") or {}
    campeao_atual = (top3_data or {}).get("campeao")

    if not top3:
        st.info(
            "Top 3 ainda não disponível. Execute as Fases 04 e 05 para gerar os modelos."
        )
        return False

    st.success(f"Top 3 disponível — {len(top3)} finalista(s).")

    # Pódio em cards (top3 é lista de nomes; métricas vêm em dicionário à parte).
    cols = st.columns(min(3, len(top3)))
    emojis = ["🥇", "🥈", "🥉"]

    for idx, nome_modelo in enumerate(top3[:3]):
        with cols[idx]:
            with st.container(border=True):
                st.markdown(f"### {emojis[idx]} {idx + 1}º lugar")
                st.markdown(f"**{nome_modelo}**")

                metricas = metricas_por_modelo.get(nome_modelo) or {}
                for chave, valor in metricas.items():
                    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
                        st.metric(chave.replace("_", " ").title(), _formatar_valor(valor))

                if campeao_atual == nome_modelo:
                    st.success("Campeão atual")

    # --- Métricas de avaliação (leaderboard completo) ---
    st.divider()
    exibir_leaderboard(top3_data)

    # --- Diagnóstico por tipo (matriz de confusão / dispersão / distribuição) ---
    st.divider()
    exibir_diagnostico_por_tipo(top3_data, top3)

    # --- Análise individual de cada finalista ---
    st.divider()
    exibir_analise_individual(top3_data, top3)

    # Eleição.
    st.divider()
    st.markdown("#### Eleger campeão")

    if campeao_atual:
        st.info(f"Campeão atual: **{campeao_atual}**")

    nomes_modelos = [m for m in top3 if isinstance(m, str) and m]
    if not nomes_modelos:
        return True

    modelo_selecionado = st.selectbox(
        "Modelo campeão",
        options=nomes_modelos,
        index=(
            nomes_modelos.index(campeao_atual)
            if campeao_atual in nomes_modelos
            else 0
        ),
        key="select_campeao_torneio",
    )

    if st.button("Confirmar eleição", type="primary"):
        try:
            cliente.eleger_campeao(nome, modelo_selecionado)
            st.success(f"Modelo **{modelo_selecionado}** eleito como campeão!")
            st.rerun()
        except Exception as erro:
            st.error(f"Falha na eleição: {erro}")

    return True


def exibir_fase_05(
    nome: str, status_fases: dict, problema_id: str | None, tem_top3: bool
) -> None:
    """Seção da Fase 05 (avaliação final), quando ainda não concluída."""
    fase_status = status_fases.get("05", "pendente")

    if fase_status == "concluida":
        return

    job_status = painel_job(nome, "05")
    if job_status in ("executando", "pendente"):
        st.info("Fase 05 em execução. Acompanhe o painel acima.")
        return

    # A Fase 05 audita o pódio gerado pela Fase 04.
    if not tem_top3 and status_fases.get("04") != "concluida":
        return

    st.divider()
    st.markdown("#### Fase 05 — Avaliação final do pódio")

    if st.button(
        "Executar Fase 05 — avaliação final",
        width="stretch",
        disabled=not bool(problema_id) and not tem_top3,
    ):
        with st.spinner("Submetendo a Fase 05..."):
            submeter_fase(nome, "05", problema=problema_id)
        st.rerun()


def _ler_parquet_leve(caminho: Path) -> tuple[int, int] | None:
    """Lê apenas as dimensões (linhas, colunas) de um parquet sem carregar dados."""
    try:
        import pyarrow.parquet as pq

        pf = pq.ParquetFile(caminho)
        return pf.metadata.num_rows, pf.schema_ntypes.names and len(
            pf.schema_ntypes.names
        ) or 0
    except Exception:
        return None


def exibir_base_modelagem(nome: str) -> None:
    """Painel de validação de tamanho: ABT + partições treino/val/teste."""
    pasta_ml = Path("dados") / "processados" / nome / "ml"
    abt = pasta_ml / "abt_cliente_bruta.parquet"
    treino = pasta_ml / "treino_processado.parquet"
    validacao = pasta_ml / "validacao_processada.parquet"
    teste = pasta_ml / "teste_processado.parquet"

    st.markdown("#### Base para modelagem (validação de tamanho do dataset)")

    if not pasta_ml.is_dir():
        st.info(
            "Ainda não há base de modelagem para este dataset. "
            "Execute a **Fase 03 (Preparação)** para gerar a ABT e as partições."
        )
        return

    col1, col2, col3, col4 = st.columns(4)

    dim_abt = _ler_parquet_leve(abt) if abt.is_file() else None
    with col1:
        if dim_abt:
            st.metric("ABT — linhas", f"{dim_abt[0]:,}".replace(",", "."))
            st.caption(f"colunas: {dim_abt[1]}")
        else:
            st.metric("ABT — linhas", "—")
            st.caption("Execute a Fase 03.")

    # Partições.
    dims = {}
    for chave, caminho in [("treino", treino), ("validação", validacao), ("teste", teste)]:
        if caminho.is_file():
            d = _ler_parquet_leve(caminho)
            if d:
                dims[chave] = d

    total_particoes = sum(d[0] for d in dims.values())
    with col2:
        st.metric("Partições — total", f"{total_particoes:,}".replace(",", "."))
        st.caption("treino + validação + teste")
    with col3:
        if dims.get("treino"):
            st.metric("Treino (70%)", f"{dims['treino'][0]:,}".replace(",", "."))
        else:
            st.metric("Treino (70%)", "—")
    with col4:
        if dims.get("validação") and dims.get("teste"):
            st.metric("Val. (15%) / Teste (15%)", f"{dims['validação'][0]:,} / {dims['teste'][0]:,}".replace(",", "."))
        else:
            st.metric("Val. (15%) / Teste (15%)", "—")

    st.caption(
        "Partição canônica 70/15/15 (treino / validação / teste) gerada pela Fase 03. "
        "Use esses números para confirmar que o dataset tem volume suficiente para treinar os modelos."
    )
    """Corpo principal da página."""
    garantir_estado()
    st.caption("Preparação, treinamento, avaliação e seleção do modelo campeão")

    nome = st.session_state.dataset_nome

def main() -> None:
    """Corpo principal da página."""
    garantir_estado()
    st.caption("Preparação, treinamento, avaliação e seleção do modelo campeão")

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

    resumo = resumo_dataset(nome) or {}
    status_fases = resumo.get("status_fases") or {}

    # Pré-requisito: Fase 02 concluída (recomendado, não bloqueante).
    if status_fases.get("02") != "concluida":
        st.warning(
            "Recomendado executar primeiro a **Fase 02 (Raio-X)** para validar os dados."
        )
        if st.button("Ir para Raio-X", icon=":material/analytics:"):
            st.switch_page("app_pages/pagina_02_raiox.py")
        st.divider()

    # --- Problema de negócio (contrato que dirige as fases 03/04/05) ---
    problema_id = exibir_problema(nome, resumo, cliente)

    # --- Base para modelagem (tamanho ABT + partições) ---
    exibir_base_modelagem(nome)
    st.divider()

    # --- Fase 03 (preparação) ---
    exibir_fase_03(nome, status_fases, problema_id)
    st.divider()

    # --- Fase 04 (torneio) ---
    exibir_fase_04(nome, status_fases, problema_id)
    st.divider()

    # --- Top 3 / campeão ---
    st.markdown("#### Pódio Top 3 & campeão")
    tem_top3 = exibir_top3(nome, cliente)

    # --- Diagnósticos granulares dos modelos (Fase 05) ---
    st.divider()
    exibir_diagnosticos_modelos(nome)

    # --- Fase 05 (avaliação final), se necessário ---
    exibir_fase_05(nome, status_fases, problema_id, tem_top3)

    # Navegação para a apuração de valor quando há pódio.
    if tem_top3:
        st.divider()
        if st.button(
            "Ir para Apuração de Valor →",
            type="primary",
            width="stretch",
            icon=":material/arrow_forward:",
        ):
            st.switch_page("app_pages/pagina_04_valor.py")


if __name__ == "__main__":
    main()
