# -*- coding: utf-8 -*-
"""
Página de Configuração de Parâmetros de Negócio por Dataset.

Etapa 1 do plano híbrido: Interface orientada a objetos com TDD.
Permite configurar parâmetros de negócio (CMV, ICMS, despesas, etc.)
por dataset, com persistência em JSON e validação de entrada.

A plataforma é agnóstica ao modelo de negócio: os parâmetros são
pré-fixados com médias de mercado e podem ser sobrescritos por dataset.
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime

from src.etapas.fase_02_exploracao.adaptadores.extrator_vendas import (
    carregar_parametros_negocio,
    salvar_parametros_negocio,
    PARAMETROS_NEGOCIO_DEFAULT,
    validar_parametros_negocio,
)


# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Parâmetros de Negócio",
    page_icon="⚙️",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Funções auxiliares da interface
# ---------------------------------------------------------------------------
def listar_datasets_disponiveis() -> list[str]:
    """Lista todos os datasets que têm pasta de registros."""
    pasta_registros = Path("dados/registros")
    if not pasta_registros.is_dir():
        return []
    return sorted(
        [d.name for d in pasta_registros.iterdir() if d.is_dir()]
    )


def exibir_metrica_parametro(
    chave: str,
    valor_atual: any,
    valor_padrao: any,
    tipo: str,
    descricao: str,
):
    """Exibe um campo de edição para um parâmetro com validação visual."""
    eh_padrao = valor_atual == valor_padrao
    badge = "🟢 Padrão" if eh_padrao else "🔵 Personalizado"

    with st.container():
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.caption(f"**{chave}**")
            st.caption(descricao)

        with col2:
            if tipo == "taxa":
                novo_valor = st.number_input(
                    f"Valor {chave}",
                    min_value=0.0,
                    max_value=1.0,
                    value=float(valor_atual),
                    step=0.01,
                    format="%.4f",
                    key=f"input_{chave}",
                    label_visibility="collapsed",
                )
            elif tipo == "monetario":
                novo_valor = st.number_input(
                    f"Valor {chave}",
                    min_value=0.0,
                    value=float(valor_atual),
                    step=100.0,
                    format="%.2f",
                    key=f"input_{chave}",
                    label_visibility="collapsed",
                )
            elif tipo == "prazo":
                novo_valor = st.number_input(
                    f"Valor {chave}",
                    min_value=1,
                    value=int(valor_atual),
                    step=1,
                    key=f"input_{chave}",
                    label_visibility="collapsed",
                )
            else:
                novo_valor = st.text_input(
                    f"Valor {chave}",
                    value=str(valor_atual),
                    key=f"input_{chave}",
                    label_visibility="collapsed",
                )

        with col3:
            st.caption(badge)

    return novo_valor


# ---------------------------------------------------------------------------
# Mapeamento de parâmetros para exibição
# ---------------------------------------------------------------------------
PARAMETROS_EXIBICAO = [
    {
        "chave": "cmv_taxa",
        "descricao": "Custo da Mercadoria Vendida sobre o faturamento",
        "tipo": "taxa",
    },
    {
        "chave": "despesas_variaveis_taxa",
        "descricao": "Despesas variáveis sobre o faturamento",
        "tipo": "taxa",
    },
    {
        "chave": "icms_aliquota",
        "descricao": "Alíquota de ICMS",
        "tipo": "taxa",
    },
    {
        "chave": "pis_aliquota",
        "descricao": "Alíquota de PIS",
        "tipo": "taxa",
    },
    {
        "chave": "cofins_aliquota",
        "descricao": "Alíquota de COFINS",
        "tipo": "taxa",
    },
    {
        "chave": "frete_taxa",
        "descricao": "Taxa de frete sobre o valor da mercadoria",
        "tipo": "taxa",
    },
    {
        "chave": "encargos_sociais_taxa",
        "descricao": "Encargos sociais sobre salário base",
        "tipo": "taxa",
    },
    {
        "chave": "refugo_taxa",
        "descricao": "Taxa de refugo/desperdício fabril",
        "tipo": "taxa",
    },
    {
        "chave": "custos_fixos_mensais",
        "descricao": "Custos fixos mensais (R$)",
        "tipo": "monetario",
    },
    {
        "chave": "prazo_pagamento_dias",
        "descricao": "Prazo padrão de pagamento (dias)",
        "tipo": "prazo",
    },
    {
        "chave": "prazo_entrega_dias_uteis",
        "descricao": "Prazo prometido de entrega (dias úteis)",
        "tipo": "prazo",
    },
]


# ---------------------------------------------------------------------------
# Lógica principal da página
# ---------------------------------------------------------------------------
def main():
    st.title("⚙️ Parâmetros de Negócio por Dataset")
    st.markdown(
        """
        Configure os parâmetros de negócio utilizados nas análises exploratórias
        e visões 360 de cada departamento. Os valores são específicos por dataset
        e podem ser ajustados conforme o modelo de negócio do seu ERP.
        """
    )

    # Inicializar session state
    if "parametros_salvos" not in st.session_state:
        st.session_state.parametros_salvos = False
    if "mensagem_sucesso" not in st.session_state:
        st.session_state.mensagem_sucesso = ""
    if "mensagem_erro" not in st.session_state:
        st.session_state.mensagem_erro = ""

    # Seleção do dataset
    datasets = listar_datasets_disponiveis()
    if not datasets:
        st.warning(
            "Nenhum dataset encontrado em `dados/registros/`. "
            "Execute primeiro a ingestão de dados (Fase 01)."
        )
        return

    dataset_selecionado = st.selectbox(
        "Selecione o dataset:",
        datasets,
        index=0,
        key="select_dataset",
    )

    # Carregar parâmetros atuais
    parametros_atuais = carregar_parametros_negocio(dataset_selecionado)

    st.divider()

    # Formulário de edição
    st.subheader(f"Parâmetros — {dataset_selecionado}")

    novos_valores = {}

    for info in PARAMETROS_EXIBICAO:
        chave = info["chave"]
        valor_atual = parametros_atuais.get(chave, PARAMETROS_NEGOCIO_DEFAULT.get(chave))
        valor_padrao = PARAMETROS_NEGOCIO_DEFAULT.get(chave)

        novo_valor = exibir_metrica_parametro(
            chave=chave,
            valor_atual=valor_atual,
            valor_padrao=valor_padrao,
            tipo=info["tipo"],
            descricao=info["descricao"],
        )
        novos_valores[chave] = novo_valor

    st.divider()

    # Botões de ação
    col_salvar, col_restaurar, col_status = st.columns([1, 1, 3])

    with col_salvar:
        if st.button("💾 Salvar Parâmetros", type="primary", use_container_width=True):
            # Validar antes de salvar
            resultado_validacao = validar_parametros_negocio(novos_valores)

            if not resultado_validacao["valido"]:
                st.session_state.mensagem_erro = (
                    "Erros de validação:\n"
                    + "\n".join(
                        f"• {campo}: {msg}"
                        for campo, msg in resultado_validacao["erros"].items()
                    )
                )
                st.session_state.mensagem_sucesso = ""
                st.session_state.parametros_salvos = False
            else:
                resultado_salvamento = salvar_parametros_negocio(
                    dataset_selecionado, novos_valores
                )

                if resultado_salvamento["sucesso"]:
                    st.session_state.mensagem_sucesso = (
                        f"Parâmetros salvos com sucesso em "
                        f"`{resultado_salvamento['caminho']}`"
                    )
                    st.session_state.mensagem_erro = ""
                    st.session_state.parametros_salvos = True
                else:
                    st.session_state.mensagem_erro = (
                        f"Erro ao salvar: {resultado_salvamento.get('erro', 'desconhecido')}"
                    )
                    st.session_state.mensagem_sucesso = ""
                    st.session_state.parametros_salvos = False

    with col_restaurar:
        if st.button("🔄 Restaurar Padrões", use_container_width=True):
            novos_valores_padrao = dict(PARAMETROS_NEGOCIO_DEFAULT)
            resultado_salvamento = salvar_parametros_negocio(
                dataset_selecionado, novos_valores_padrao
            )

            if resultado_salvamento["sucesso"]:
                st.session_state.mensagem_sucesso = (
                    "Parâmetros restaurados para os valores padrão."
                )
                st.session_state.mensagem_erro = ""
                st.session_state.parametros_salvos = True
                # Recarregar a página para refletir os valores padrão
                st.rerun()
            else:
                st.session_state.mensagem_erro = (
                    f"Erro ao restaurar: {resultado_salvamento.get('erro', 'desconhecido')}"
                )
                st.session_state.mensagem_sucesso = ""

    # Exibir mensagens
    with col_status:
        if st.session_state.mensagem_sucesso:
            st.success(st.session_state.mensagem_sucesso)
        if st.session_state.mensagem_erro:
            st.error(st.session_state.mensagem_erro)

    # Exibir valores atuais resumidos
    st.divider()
    st.subheader("Resumo dos Valores Atuais")

    col_resumo_1, col_resumo_2 = st.columns(2)

    for i, info in enumerate(PARAMETROS_EXIBICAO):
        chave = info["chave"]
        valor = novos_valores.get(chave, parametros_atuais.get(chave))
        col = col_resumo_1 if i % 2 == 0 else col_resumo_2

        with col:
            if info["tipo"] == "taxa":
                st.metric(chave, f"{float(valor):.1%}")
            elif info["tipo"] == "monetario":
                st.metric(chave, f"R$ {float(valor):,.2f}")
            elif info["tipo"] == "prazo":
                st.metric(chave, f"{int(valor)} dias")
            else:
                st.metric(chave, str(valor))


if __name__ == "__main__":
    main()
