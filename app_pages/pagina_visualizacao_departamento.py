# -*- coding: utf-8 -*-
"""
Página de Visualização por Departamento — Etapa 3.

Funcionalidades:
- Geração de dados anuais (últimos 5 anos) e mensais (últimos 12 meses)
- Cálculo de métricas de negócio com parâmetros configuráveis
- Filtros por período (ano, mês), categoria e valor
- Preparação completa de dados para visualizações Streamlit

Agnóstico: não assume nomes específicos de coluna ou tabela.
"""

import logging
from pathlib import Path

import pandas as pd

from src.etapas.fase_02_exploracao.adaptadores.extrator_vendas import (
    carregar_parametros_negocio,
    PARAMETROS_NEGOCIO_DEFAULT,
)

logger = logging.getLogger(__name__)


# ===========================================================================
# FUNÇÕES DE GERAÇÃO DE DADOS TEMPORAIS
# ===========================================================================
def gerar_dados_anuais(
    df: pd.DataFrame,
    coluna_valor: str = "valor_total",
    coluna_data: str = "data_emissao",
) -> pd.DataFrame:
    """Gera dados agregados por ano nos últimos 5 anos.

    Args:
        df: DataFrame com dados de vendas
        coluna_valor: Nome da coluna de valor financeiro
        coluna_data: Nome da coluna de data

    Returns:
        DataFrame com colunas 'ano' e 'valor_total' (agregado por ano)
    """
    if df.empty or coluna_valor not in df.columns or coluna_data not in df.columns:
        return pd.DataFrame(columns=["ano", coluna_valor])

    df_copia = df.copy()
    df_copia[coluna_data] = pd.to_datetime(df_copia[coluna_data], errors="coerce")
    df_copia = df_copia.dropna(subset=[coluna_data])

    if df_copia.empty:
        return pd.DataFrame(columns=["ano", coluna_valor])

    # Adicionar coluna ano
    df_copia["ano"] = df_copia[coluna_data].dt.year

    # Recortar últimos 5 anos a partir da data máxima
    ano_maximo = df_copia["ano"].max()
    ano_corte = ano_maximo - 4  # 5 anos incluindo o atual
    df_5anos = df_copia[df_copia["ano"] >= ano_corte].copy()

    # Agregar por ano
    dados_anuais = (
        df_5anos.groupby("ano")[coluna_valor]
        .sum()
        .reset_index()
        .sort_values("ano")
    )

    return dados_anuais


def gerar_dados_mensais(
    df: pd.DataFrame,
    coluna_valor: str = "valor_total",
    coluna_data: str = "data_emissao",
) -> pd.DataFrame:
    """Gera dados agregados por mês nos últimos 12 meses.

    Args:
        df: DataFrame com dados de vendas
        coluna_valor: Nome da coluna de valor financeiro
        coluna_data: Nome da coluna de data

    Returns:
        DataFrame com colunas 'ano_mes' e 'valor_total' (agregado por mês)
    """
    if df.empty or coluna_valor not in df.columns or coluna_data not in df.columns:
        return pd.DataFrame(columns=["ano_mes", coluna_valor])

    df_copia = df.copy()
    df_copia[coluna_data] = pd.to_datetime(df_copia[coluna_data], errors="coerce")
    df_copia = df_copia.dropna(subset=[coluna_data])

    if df_copia.empty:
        return pd.DataFrame(columns=["ano_mes", coluna_valor])

    # Recortar últimos 12 meses a partir da data máxima
    data_maxima = df_copia[coluna_data].max()
    data_corte = data_maxima - pd.DateOffset(months=12)
    df_12m = df_copia[df_copia[coluna_data] >= data_corte].copy()

    # Adicionar coluna ano_mes
    df_12m["ano_mes"] = df_12m[coluna_data].dt.to_period("M").astype(str)

    # Agregar por ano_mes
    dados_mensais = (
        df_12m.groupby("ano_mes")[coluna_valor]
        .sum()
        .reset_index()
        .sort_values("ano_mes")
    )

    return dados_mensais


# ===========================================================================
# FUNÇÕES DE CÁLCULO DE MÉTRICAS DE NEGÓCIO
# ===========================================================================
def calcular_metricas_negocio(
    df: pd.DataFrame,
    parametros: dict,
    coluna_valor: str = "valor_total",
) -> dict:
    """Calcula métricas de negócio com base em parâmetros configuráveis.

    Métricas calculadas:
    - cmv: Custo da Mercadoria Vendida = valor_total * cmv_taxa
    - despesas_variaveis: valor_total * despesas_variaveis_taxa
    - margem_bruta: valor_total - cmv
    - imc: Índice de Margem de Contribuição = (receita - cmv - despesas) / receita
    - break_even: custos fixos / margem fracionária

    Args:
        df: DataFrame com dados de vendas
        parametros: Dict com parâmetros de negócio (cmv_taxa, etc.)
        coluna_valor: Nome da coluna de valor financeiro

    Returns:
        Dict com as métricas calculadas
    """
    if df.empty or coluna_valor not in df.columns or not parametros:
        return {}

    receita_total = df[coluna_valor].sum()
    metricas = {}

    # CMV
    cmv_taxa = parametros.get("cmv_taxa")
    if cmv_taxa is not None:
        metricas["cmv"] = receita_total * float(cmv_taxa)

    # Despesas variáveis
    despesas_taxa = parametros.get("despesas_variaveis_taxa")
    if despesas_taxa is not None:
        metricas["despesas_variaveis"] = receita_total * float(despesas_taxa)

    # Margem bruta
    if "cmv" in metricas:
        metricas["margem_bruta"] = receita_total - metricas["cmv"]

    # IMC (Índice de Margem de Contribuição)
    if "cmv" in metricas and "despesas_variaveis" in metricas:
        margem_fracionaria = 1 - float(cmv_taxa) - float(despesas_taxa)
        if receita_total > 0:
            metricas["imc"] = margem_fracionaria
        else:
            metricas["imc"] = 0.0

    # Break-Even Point
    custos_fixos = parametros.get("custos_fixos_mensais")
    if custos_fixos is not None and "cmv" in metricas and "despesas_variaveis" in metricas:
        margem_fracionaria = 1 - float(cmv_taxa) - float(despesas_taxa)
        if margem_fracionaria > 0:
            metricas["break_even"] = float(custos_fixos) / margem_fracionaria
        else:
            metricas["break_even"] = 0.0

    return metricas


# ===========================================================================
# FUNÇÕES DE FILTRO
# ===========================================================================
def filtrar_por_periodo(
    df: pd.DataFrame,
    coluna_data: str = "data_emissao",
    ano: int | None = None,
    mes: int | None = None,
) -> pd.DataFrame:
    """Filtra DataFrame por ano e/ou mês.

    Args:
        df: DataFrame com dados
        coluna_data: Nome da coluna de data
        ano: Ano para filtrar (opcional)
        mes: Mês para filtrar (opcional)

    Returns:
        DataFrame filtrado
    """
    if df.empty or coluna_data not in df.columns:
        return df.copy()

    df_copia = df.copy()
    df_copia[coluna_data] = pd.to_datetime(df_copia[coluna_data], errors="coerce")
    df_copia = df_copia.dropna(subset=[coluna_data])

    if ano is not None:
        df_copia = df_copia[df_copia[coluna_data].dt.year == ano]

    if mes is not None:
        df_copia = df_copia[df_copia[coluna_data].dt.month == mes]

    return df_copia


def filtrar_por_categoria(
    df: pd.DataFrame,
    coluna_categoria: str = "categoria",
    valor_categoria: str | None = None,
) -> pd.DataFrame:
    """Filtra DataFrame por categoria.

    Args:
        df: DataFrame com dados
        coluna_categoria: Nome da coluna de categoria
        valor_categoria: Valor da categoria para filtrar (opcional)

    Returns:
        DataFrame filtrado
    """
    if df.empty or coluna_categoria not in df.columns:
        return df.copy()

    if valor_categoria is None:
        return df.copy()

    return df[df[coluna_categoria] == valor_categoria].copy()


def filtrar_por_valor(
    df: pd.DataFrame,
    coluna_valor: str = "valor_total",
    valor_minimo: float | None = None,
    valor_maximo: float | None = None,
) -> pd.DataFrame:
    """Filtra DataFrame por intervalo de valor.

    Args:
        df: DataFrame com dados
        coluna_valor: Nome da coluna de valor
        valor_minimo: Valor mínimo (inclusive)
        valor_maximo: Valor máximo (inclusive)

    Returns:
        DataFrame filtrado
    """
    if df.empty or coluna_valor not in df.columns:
        return df.copy()

    df_copia = df.copy()
    df_copia[coluna_valor] = pd.to_numeric(df_copia[coluna_valor], errors="coerce")

    if valor_minimo is not None:
        df_copia = df_copia[df_copia[coluna_valor] >= valor_minimo]

    if valor_maximo is not None:
        df_copia = df_copia[df_copia[coluna_valor] <= valor_maximo]

    return df_copia


# ===========================================================================
# FUNÇÃO PRINCIPAL — Preparar dados para visualização
# ===========================================================================
def preparar_dados_visualizacao(
    df: pd.DataFrame,
    coluna_valor: str = "valor_total",
    coluna_data: str = "data_emissao",
    coluna_categoria: str | None = None,
    parametros_negocio: dict | None = None,
) -> dict:
    """Prepara dados completos para visualização por departamento.

    Gera:
    - dados_anuais: agregação por ano (últimos 5 anos)
    - dados_mensais: agregação por mês (últimos 12 meses)
    - metricas_negocio: CMV, despesas, IMC, break-even
    - dados_filtrados: dados após aplicação de filtros

    Args:
        df: DataFrame com dados brutos
        coluna_valor: Nome da coluna de valor financeiro
        coluna_data: Nome da coluna de data
        coluna_categoria: Nome da coluna de categoria (opcional)
        parametros_negocio: Dict com parâmetros de negócio (opcional)

    Returns:
        Dict com todos os dados preparados para visualização
    """
    if df.empty:
        return {
            "dados_anuais": pd.DataFrame(columns=["ano", coluna_valor]),
            "dados_mensais": pd.DataFrame(columns=["ano_mes", coluna_valor]),
            "metricas_negocio": {},
            "dados_filtrados": pd.DataFrame(),
        }

    if parametros_negocio is None:
        parametros_negocio = {}

    # Gerar dados temporais
    dados_anuais = gerar_dados_anuais(df, coluna_valor=coluna_valor, coluna_data=coluna_data)
    dados_mensais = gerar_dados_mensais(df, coluna_valor=coluna_valor, coluna_data=coluna_data)

    # Calcular métricas de negócio
    metricas_negocio = calcular_metricas_negocio(df, parametros_negocio, coluna_valor=coluna_valor)

    # Dados filtrados (sem filtro inicial = todos os dados)
    dados_filtrados = df.copy()

    resultado = {
        "dados_anuais": dados_anuais,
        "dados_mensais": dados_mensais,
        "metricas_negocio": metricas_negocio,
        "dados_filtrados": dados_filtrados,
        "coluna_valor": coluna_valor,
        "coluna_data": coluna_data,
        "coluna_categoria": coluna_categoria,
    }

    return resultado


# ===========================================================================
# FUNÇÃO DE FILTRAGEM COMBINADA
# ===========================================================================
def aplicar_filtros(
    df: pd.DataFrame,
    coluna_data: str | None = None,
    ano: int | None = None,
    mes: int | None = None,
    coluna_categoria: str | None = None,
    valor_categoria: str | None = None,
    coluna_valor: str | None = None,
    valor_minimo: float | None = None,
    valor_maximo: float | None = None,
) -> pd.DataFrame:
    """Aplica múltiplos filtros sequencialmente.

    Args:
        df: DataFrame com dados
        coluna_data: Nome da coluna de data
        ano: Ano para filtrar
        mes: Mês para filtrar
        coluna_categoria: Nome da coluna de categoria
        valor_categoria: Valor da categoria
        coluna_valor: Nome da coluna de valor
        valor_minimo: Valor mínimo
        valor_maximo: Valor máximo

    Returns:
        DataFrame filtrado
    """
    resultado = df.copy()

    if coluna_data and (ano is not None or mes is not None):
        resultado = filtrar_por_periodo(
            resultado, coluna_data=coluna_data, ano=ano, mes=mes
        )

    if coluna_categoria and valor_categoria is not None:
        resultado = filtrar_por_categoria(
            resultado, coluna_categoria=coluna_categoria, valor_categoria=valor_categoria
        )

    if coluna_valor and (valor_minimo is not None or valor_maximo is not None):
        resultado = filtrar_por_valor(
            resultado,
            coluna_valor=coluna_valor,
            valor_minimo=valor_minimo,
            valor_maximo=valor_maximo,
        )

    return resultado
