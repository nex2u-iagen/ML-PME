# -*- coding: utf-8 -*-
"""
Página de Visão 360 — Integração de Departamentos.

Etapa 2 do plano híbrido: orientada a objetos com TDD.
Permite visualizar dados integrados de múltiplos departamentos
por chaves comuns descobertas dinamicamente, gerando visão 360
do cliente e do negócio.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from src.etapas.fase_02_exploracao.adaptadores.extrator_vendas import ExtratorVendas
from src.etapas.fase_02_exploracao.adaptadores.integrador_departamentos import (
    IntegradorDepartamentos,
    descobrir_chaves_comuns,
    gerar_relatorio_integridade,
)
from src.etapas.fase_02_exploracao.adaptadores.resolvedor_semantico import ResolvedorSemantico
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares


# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Visão 360 — Integração de Departamentos",
    page_icon="🔗",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def listar_arquivos_vendas(pasta_dados: str) -> list[str]:
    """Lista arquivos CSV que podem ser tabelas de vendas/faturamento."""
    pasta = Path(pasta_dados)
    if not pasta.is_dir():
        return []
    arquivos = []
    for arquivo in pasta.glob("*.csv"):
        nome_lower = arquivo.name.lower()
        if any(p in nome_lower for p in ("nfetotal", "venda_total", "faturamento", "nfe", "venda")):
            arquivos.append(arquivo.name)
    return sorted(arquivos)


@st.cache_data(ttl=300)
def carregar_extrato_departamento(pasta_dados: str, nome_arquivo: str) -> pd.DataFrame:
    """Carrega um extrato de departamento."""
    leitor = LeitorArquivosTabulares()
    caminho = Path(pasta_dados) / nome_arquivo
    return leitor.carregar_tabela(caminho)


def detectar_colunas_relevantes(df: pd.DataFrame) -> dict:
    """Detecta colunas de ID, valor e data em um DataFrame."""
    resolvedor = ResolvedorSemantico()

    col_id = None
    col_valor = None
    col_data = None

    # ID
    for c in df.columns:
        cl = c.lower().strip()
        if "nfe" in cl or cl in ("id", "idnfe", "id_nfe"):
            col_id = c
            break

    # Valor
    for c in df.columns:
        cl = c.lower().strip()
        if cl.startswith("v") and len(cl) <= 6:
            continue
        if cl in ("vtotal", "valor", "total", "montante", "amount"):
            col_valor = c
            break
    if col_valor is None:
        for c in df.columns:
            cl = c.lower().strip()
            try:
                serie = pd.to_numeric(df[c], errors="coerce")
                if serie.notna().sum() > len(df) * 0.5:
                    col_valor = c
                    break
            except Exception:
                continue

    # Data
    for c in df.columns:
        cl = c.lower().strip()
        if any(k in cl for k in ("data", "emissao", "venc", "dt_", "datahora")):
            if not any(k in cl for k in ("id", "valor", "vtotal", "vprod")):
                col_data = c
                break

    return {"id": col_id, "valor": col_valor, "data": col_data}


# ---------------------------------------------------------------------------
# Lógica principal da página
# ---------------------------------------------------------------------------
def main():
    st.title("🔗 Visão 360 — Integração de Departamentos")
    st.markdown(
        """
        Integre dados de múltiplos departamentos por chaves comuns descobertas
        automaticamente. Obtenha visão consolidada do cliente e do negócio
        com análises cruzadas entre comercial, financeiro, estoque, compras,
        fiscal, logística, produção, contábil, pós-venda e RH.
        """
    )

    # Seleção da pasta de dados
    pasta_dados = st.text_input(
        "Pasta de dados (CSV):",
        value="dados/brutos/csv/mercadinho-t3",
        help="Caminho para a pasta contendo os arquivos CSV do ERP",
    )

    if not Path(pasta_dados).is_dir():
        st.error(f"Pasta não encontrada: {pasta_dados}")
        return

    # Listar arquivos disponíveis
    arquivos_disponiveis = listar_arquivos_vendas(pasta_dados)
    if not arquivos_disponiveis:
        st.warning(
            "Nenhum arquivo de vendas/faturamento encontrado na pasta. "
            "Verifique o caminho ou adicione arquivos CSV."
        )
        return

    # Seleção de departamentos para integrar
    st.subheader("1. Selecionar Departamentos para Integração")

    selecionados = st.multiselect(
        "Escolha os departamentos (arquivos CSV):",
        arquivos_disponiveis,
        default=arquivos_disponiveis[:2] if len(arquivos_disponiveis) >= 2 else arquivos_disponiveis,
        help="Selecione dois ou mais departamentos para integrar",
    )

    if len(selecionados) < 2:
        st.warning("Selecione pelo menos dois departamentos para integração.")
        return

    # Carregar extratos selecionados
    extratos = {}
    colunas_detectadas = {}

    with st.spinner("Carregando extratos..."):
        for nome_arquivo in selecionados:
            try:
                df = carregar_extrato_departamento(pasta_dados, nome_arquivo)
                nome_depto = nome_arquivo.replace(".csv", "").replace("erp_", "").replace("_", " ").title()
                extratos[nome_depto] = df
                colunas_detectadas[nome_depto] = detectar_colunas_relevantes(df)
            except Exception as e:
                st.error(f"Erro ao carregar {nome_arquivo}: {e}")

    if len(extratos) < 2:
        st.error("Não foi carregar pelo menos dois extratos válidos.")
        return

    # Exibir colunas detectadas por departamento
    with st.expander("🔍 Colunas detectadas por departamento"):
        for nome_depto, colunas in colunas_detectadas.items():
            st.write(f"**{nome_depto}:**")
            cols = []
            if colunas["id"]:
                cols.append(f"ID: `{colunas['id']}`")
            if colunas["valor"]:
                cols.append(f"Valor: `{colunas['valor']}`")
            if colunas["data"]:
                cols.append(f"Data: `{colunas['data']}`")
            if not cols:
                cols.append("Nenhuma coluna relevante detectada")
            st.write(" | ".join(cols))

    # Descobrir chaves comuns automaticamente
    st.divider()
    st.subheader("2. Chave Comum para Integração")

    df_primeiro = list(extratos.values())[0]
    chaves_sugeridas = descobrir_chaves_comuns(list(extratos.values()))

    if chaves_sugeridas:
        chave_sugerida = chaves_sugeridas[0]
        st.info(
            f"🔑 Chave comum sugerida: **{chave_sugerida}** "
            f"(encontrada em {len(extratos)} departamentos)"
        )
    else:
        chave_sugerida = None
        st.warning(
            "⚠️ Nenhuma chave comum encontrada automaticamente entre os departamentos. "
            "Selecione manualmente abaixo."
        )

    chave_comum = st.selectbox(
        "Chave de integração:",
        options=[chave_sugerida] + [c for c in df_primeiro.columns if c != chave_sugerida] if chave_sugerida else list(df_primeiro.columns),
        index=0,
        help="Coluna usada para fazer join entre os departamentos",
    )

    # Selecionar coluna de data para recortes temporais
    coluna_data = None
    colunas_com_data = [
        c for c in df_primeiro.columns
        if any(k in c.lower() for k in ("data", "emissao", "venc", "dt_", "datahora"))
        and not any(k in c.lower() for k in ("id", "valor"))
    ]
    if colunas_com_data:
        coluna_data = st.selectbox(
            "Coluna de data para recortes temporais (opcional):",
            options=["Nenhuma"] + colunas_com_data,
            index=0,
            help="Selecione uma coluna de data para aplicar recortes de 5 anos e 12 meses",
        )
        if coluna_data == "Nenhuma":
            coluna_data = None

    # Executar integração
    st.divider()
    st.subheader("3. Executar Integração")

    if st.button("🔗 Integrar Departamentos", type="primary", use_container_width=True):
        with st.spinner("Integrando departamentos..."):
            try:
                integrador = IntegradorDepartamentos()
                resultado = integrador.integrar(
                    extratos=extratos,
                    chave_comum=chave_comum,
                    departamento_principal=list(extratos.keys())[0],
                    coluna_data=coluna_data,
                    aplicar_recortes=(coluna_data is not None),
                )

                st.session_state["resultado_integracao"] = resultado
                st.session_state["relatorio_integridade"] = integrador.obter_relatorio_integridade()
                st.session_state["extratos_originais"] = extratos
                st.session_state["chave_comum_usada"] = chave_comum

                st.success("✅ Integração concluída com sucesso!")

            except Exception as e:
                st.error(f"Erro na integração: {e}")
                import traceback
                st.error(traceback.format_exc())

    # Exibir resultados da integração
    if "resultado_integracao" in st.session_state:
        resultado = st.session_state["resultado_integracao"]
        relatorio = st.session_state["relatorio_integridade"]
        extratos_originais = st.session_state["extratos_originais"]
        chave_usada = st.session_state["chave_comum_usada"]

        st.divider()
        st.subheader("4. Resultado da Integração")

        # Métricas de integridade
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Registros Principal", relatorio["registros_principal"])
        with col2:
            st.metric("Registros Integrados", relatorio["registros_integrados"])
        with col3:
            st.metric("Registros Perdidos", relatorio["registros_perdidos"])
        with col4:
            st.metric("Taxa de Integração", f"{relatorio['taxa_integracao']:.1f}%")

        # Tabela de resultado
        st.write(f"**Total de linhas integradas:** {len(resultado)}")
        st.write(f"**Colunas:** {len(resultado.columns)}")

        with st.expander("📊 Visualizar dados integrados"):
            st.dataframe(resultado.head(50), use_container_width=True)

        # Recortes temporais
        if "recortes_temporais" in resultado.attrs:
            st.divider()
            st.subheader("5. Recortes Temporais")

            recortes = resultado.attrs["recortes_temporais"]

            col_temp_1, col_temp_2 = st.columns(2)
            with col_temp_1:
                st.write("**Últimos 5 anos (ano a ano):**")
                st.write(f"Anos disponíveis: {recortes['anos_disponiveis']}")
                st.write(f"Registros: {len(recortes['df_5anos'])}")

            with col_temp_2:
                st.write("**Últimos 12 meses (mês a mês):**")
                st.write(f"Meses disponíveis: {recortes['meses_disponiveis']}")
                st.write(f"Registros: {len(recortes['df_12m'])}")

            # Gráfico de série temporal mensal
            df_12m = recortes["df_12m"]
            if not df_12m.empty and "ano_mes" in df_12m.columns:
                # Encontrar coluna de valor para agregação
                col_valor_resultado = [
                    c for c in df_12m.columns
                    if "valor" in c.lower()
                ]
                if col_valor_resultado:
                    col_valor = col_valor_resultado[0]
                    dados_mensais = df_12m.groupby("ano_mes")[col_valor].sum().reset_index()

                    st.subheader("📈 Faturamento Mensal (Últimos 12 Meses)")
                    st.line_chart(dados_mensais.set_index("ano_mes")[col_valor])

            # Gráfico anual
            if "ano" in df_12m.columns:
                col_valor_ano = [
                    c for c in df_12m.columns
                    if "valor" in c.lower()
                ]
                if col_valor_ano:
                    dados_anuais = df_12m.groupby("ano")[col_valor_ano[0]].sum().reset_index()
                    st.subheader("📊 Faturamento Anual (Últimos 5 Anos)")
                    st.bar_chart(dados_anuais.set_index("ano")[col_valor_ano[0]])

        # Relatório de integridade detalhado
        with st.expander("📋 Relatório Detalhado de Integridade"):
            st.json(relatorio)


if __name__ == "__main__":
    main()
