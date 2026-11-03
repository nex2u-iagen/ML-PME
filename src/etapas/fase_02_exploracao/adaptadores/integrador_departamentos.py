# -*- coding: utf-8 -*-
"""
Integrador de Departamentos — Camada de Integração para Visão 360.

Etapa 2 do plano híbrido: orientada a objetos com TDD.
Une extratos de múltiplos departamentos por chaves comuns descobertas
dinamicamente, permitindo análises cruzadas (visão 360 do cliente e negócio).

Agnóstico: não assume nomes específicos de coluna, tabela ou modelo de negócio.
"""

import logging
from pathlib import Path

import pandas as pd

from src.etapas.fase_02_exploracao.adaptadores.extrator_vendas import (
    _aplicar_recortes_temporais,
)

logger = logging.getLogger(__name__)


# ===========================================================================
# FUNÇÃO AUXILIAR — Descobrir chaves comuns entre múltiplos DataFrames
# ===========================================================================
def descobrir_chaves_comuns(dataframes: list[pd.DataFrame]) -> list[str]:
    """Descobre colunas comuns entre múltiplos DataFrames que podem servir
    como chaves de integração.

    Estratégia:
    1. Encontra a interseção de nomes de colunas entre todos os DataFrames
    2. Filtra apenas colunas que têm valores em comum (mesmo domínio de dados)
    3. Prioriza colunas com nomes de chave (id, nfe, cliente, produto, etc.)

    Args:
        dataframes: Lista de DataFrames para comparar

    Returns:
        Lista de nomes de colunas comuns ordenados por prioridade
    """
    if not dataframes:
        return []

    # Filtrar DataFrames vazios
    df_validos = [df for df in dataframes if not df.empty]
    if not df_validos:
        return []

    # Encontrar colunas comuns entre todos
    colunas_comuns = set(df_validos[0].columns)
    for df in df_validos[1:]:
        colunas_comuns = colunas_comuns.intersection(set(df.columns))

    if not colunas_comuns:
        return []

    # Verificar quais colunas comuns têm valores em comum (mesmo domínio)
    chaves_comuns = []
    for col in colunas_comuns:
        try:
            valores_primeiro = set(df_validos[0][col].dropna().astype(str))
            tem_valor_comum = False

            for df in df_validos[1:]:
                valores_outro = set(df[col].dropna().astype(str))
                if valores_primeiro.intersection(valores_outro):
                    tem_valor_comum = True
                    break

            if tem_valor_comum:
                chaves_comuns.append(col)
        except Exception:
            continue

    # Ordenar por prioridade: chaves com 'id', 'nfe', 'cliente', 'produto' primeiro
    def _prioridade(col: str) -> int:
        cl = col.lower().strip()
        if any(k in cl for k in ("idnfe", "id_nfe", "nfe")):
            return 0
        if any(k in cl for k in ("idcliente", "id_cliente", "cliente")):
            return 1
        if any(k in cl for k in ("idproduto", "id_produto", "produto")):
            return 2
        if cl.startswith("id"):
            return 3
        return 4

    chaves_comuns.sort(key=_prioridade)
    return chaves_comuns


# ===========================================================================
# FUNÇÃO AUXILIAR — Integrar extratos de departamentos
# ===========================================================================
def integrar_extratos_departamentos(
    extratos: dict[str, pd.DataFrame],
    chave_comum: str | None = None,
    departamento_principal: str | None = None,
    coluna_data: str | None = None,
    aplicar_recortes: bool = False,
) -> pd.DataFrame:
    """Integra extratos de múltiplos departamentos por uma chave comum.

    Realiza um join esquerdo a partir do departamento principal (ou do primeiro
    se não especificado), adicionando colunas dos outros departamentos com
    prefixo do nome do departamento para evitar colisões.

    Args:
        extratos: Dict {nome_departamento: DataFrame}
        chave_comum: Nome da coluna usada para join. Se None, tenta descobrir
            automaticamente via descobrir_chaves_comuns().
        departamento_principal: Nome do departamento base para o join esquerdo.
            Se None, usa o primeiro dicionário.
        coluna_data: Nome da coluna de data para recortes temporais.
        aplicar_recortes: Se True, aplica recortes de 5 anos + 12 meses.

    Returns:
        DataFrame integrado com colunas prefixadas por departamento.
    """
    if not extratos:
        return pd.DataFrame()

    nomes_departamentos = list(extratos.keys())

    # Determinar departamento principal
    if departamento_principal is None:
        departamento_principal = nomes_departamentos[0]

    if departamento_principal not in extratos:
        raise ValueError(
            f"Departamento principal '{departamento_principal}' não encontrado. "
            f"Disponíveis: {nomes_departamentos}"
        )

    df_principal = extratos[departamento_principal].copy()

    # Descobrir chave comum se não fornecida
    if chave_comum is None:
        chaves = descobrir_chaves_comuns(list(extratos.values()))
        if chaves:
            chave_comum = chaves[0]
        else:
            logger.warning(
                "Nenhuma chave comum encontrada entre departamentos. "
                "Retornando apenas o departamento principal."
            )
            return df_principal

    if chave_comum not in df_principal.columns:
        raise ValueError(
            f"Chave comum '{chave_comum}' não encontrada no departamento "
            f"'{departamento_principal}'. Colunas: {list(df_principal.columns)}"
        )

    # Começar com o departamento principal (renomear colunas com prefixo)
    resultado = df_principal.add_prefix(f"{departamento_principal}_")
    # Renomear a chave comum de volta para não ter prefixo (mantém como chave de join)
    resultado = resultado.rename(
        columns={f"{departamento_principal}_{chave_comum}": chave_comum}
    )

    # Fazer join esquerdo com cada departamento adicional
    for nome_depto in nomes_departamentos[1:]:
        if nome_depto == departamento_principal:
            continue

        df_depto = extratos[nome_depto].copy()

        # Renomear colunas do departamento com prefixo, exceto a chave comum
        colunas_renomeadas = {}
        for col in df_depto.columns:
            if col == chave_comum:
                continue
            colunas_renomeadas[col] = f"{nome_depto}_{col}"

        df_depto_renomeado = df_depto.rename(columns=colunas_renomeadas)

        # Fazer merge esquerdo
        try:
            resultado = resultado.merge(
                df_depto_renomeado,
                on=chave_comum,
                how="left",
            )
        except Exception as e:
            logger.warning(
                f"Falha ao integrar departamento '{nome_depto}': {e}"
            )
            continue

    # Aplicar recortes temporais se solicitado
    if aplicar_recortes and coluna_data:
        # Após o prefixo, a coluna de data se torna f"{departamento_principal}_{coluna_data}"
        coluna_data_resultado = coluna_data
        if f"{departamento_principal}_{coluna_data}" in resultado.columns:
            coluna_data_resultado = f"{departamento_principal}_{coluna_data}"
        elif coluna_data not in resultado.columns:
            # Procurar por qualquer coluna que termine com o nome da coluna de data
            for col in resultado.columns:
                if col.endswith(f"_{coluna_data}") or col == coluna_data:
                    coluna_data_resultado = col
                    break

        if coluna_data_resultado in resultado.columns:
            recortes = _aplicar_recortes_temporais(
                resultado, col_data=coluna_data_resultado
            )
            resultado = recortes["df_12m"].copy()
            resultado.attrs["recortes_temporais"] = recortes

    return resultado


# ===========================================================================
# FUNÇÃO AUXILIAR — Relatório de integridade
# ===========================================================================
def gerar_relatorio_integridade(
    resultado_integrado: pd.DataFrame,
    extratos_originais: dict[str, pd.DataFrame],
    chave_comum: str,
) -> dict:
    """Gera relatório de integridade da integração.

    Calcula quantos registros do departamento principal foram integrados
    com sucesso (têm correspondência em pelo menos outro departamento)
    vs perdidos (apenas no departamento principal, sem correspondência).

    Args:
        resultado_integrado: DataFrame resultado da integração
        extratos_originais: Dict {nome_departamento: DataFrame original}
        chave_comum: Nome da coluna usada para join

    Returns:
        Dict com métricas de integridade
    """
    if not extratos_originais:
        return {
            "registros_principal": 0,
            "registros_integrados": 0,
            "registros_perdidos": 0,
            "taxa_integracao": 0.0,
            "departamentos": {},
        }

    departamento_principal = list(extratos_originais.keys())[0]
    df_principal = extratos_originais[departamento_principal]

    registros_principal = len(df_principal)
    registros_integrado = len(resultado_integrado)

    # Contar quantos registros do principal têm pelo menos uma coluna
    # preenchida de outro departamento (correspondência real)
    colunas_outros = [
        c for c in resultado_integrado.columns
        if c != chave_comum
        and not c.startswith(f"{departamento_principal}_")
    ]

    if colunas_outros:
        registros_com_correspondencia = resultado_integrado[
            resultado_integrado[colunas_outros].notna().any(axis=1)
        ]
        registros_integrados = len(registros_com_correspondencia)
    else:
        registros_integrados = registros_integrado

    registros_perdidos = registros_principal - registros_integrados

    taxa_integracao = (
        (registros_integrados / registros_principal * 100)
        if registros_principal > 0
        else 0.0
    )

    # Detalhe por departamento
    detalhes_departamentos = {}
    for nome, df in extratos_originais.items():
        detalhes_departamentos[nome] = {
            "registros": len(df),
            "colunas": list(df.columns),
        }

    return {
        "registros_principal": registros_principal,
        "registros_integrados": registros_integrados,
        "registros_perdidos": registros_perdidos,
        "taxa_integracao": round(taxa_integracao, 2),
        "chave_comum": chave_comum,
        "departamentos": detalhes_departamentos,
    }


# ===========================================================================
# CLASSE PRINCIPAL — IntegradorDepartamentos
# ===========================================================================
class IntegradorDepartamentos:
    """Especialista responsável pela integração de dados de múltiplos
    departamentos para visão 360.

    Descobre chaves comuns dinamicamente e realiza joins esquerdos
    preservando todos os registros do departamento principal.
    """

    def __init__(
        self,
        pasta_dados: str | Path | None = None,
        nome_dataset: str | None = None,
    ):
        self.pasta_dados = Path(pasta_dados) if pasta_dados else None
        self.nome_dataset = nome_dataset
        self._ultimo_resultado: pd.DataFrame | None = None
        self._ultimo_relatorio: dict | None = None

    def integrar(
        self,
        extratos: dict[str, pd.DataFrame],
        chave_comum: str | None = None,
        departamento_principal: str | None = None,
        coluna_data: str | None = None,
        aplicar_recortes: bool = False,
    ) -> pd.DataFrame:
        """Integra extratos de múltiplos departamentos.

        Args:
            extratos: Dict {nome_departamento: DataFrame}
            chave_comum: Nome da coluna para join (opcional, auto-descobre)
            departamento_principal: Departamento base para join esquerdo
            coluna_data: Coluna de data para recortes temporais
            aplicar_recortes: Se True, aplica recortes de 5 anos + 12 meses

        Returns:
            DataFrame integrado
        """
        resultado = integrar_extratos_departamentos(
            extratos=extratos,
            chave_comum=chave_comum,
            departamento_principal=departamento_principal,
            coluna_data=coluna_data,
            aplicar_recortes=aplicar_recortes,
        )

        # Gerar relatório de integridade
        if chave_comum is None:
            chaves = descobrir_chaves_comuns(list(extratos.values()))
            chave_usada = chaves[0] if chaves else None
        else:
            chave_usada = chave_comum

        if chave_usada:
            self._ultimo_relatorio = gerar_relatorio_integridade(
                resultado, extratos, chave_usada
            )

        self._ultimo_resultado = resultado
        return resultado

    def obter_relatorio_integridade(self) -> dict | None:
        """Retorna o relatório de integridade da última integração."""
        return self._ultimo_relatorio

    def obter_resultado(self) -> pd.DataFrame | None:
        """Retorna o DataFrame resultado da última integração."""
        return self._ultimo_resultado

    def descobrir_chaves(self, extratos: dict[str, pd.DataFrame]) -> list[str]:
        """Descobre chaves comuns entre os departamentos fornecidos."""
        return descobrir_chaves_comuns(list(extratos.values()))
