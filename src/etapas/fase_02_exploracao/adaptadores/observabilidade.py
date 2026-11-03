# -*- coding: utf-8 -*-
"""
Módulo de Observabilidade e Qualidade de Dados — Etapa 4.

Fornece métricas de qualidade de dados, alertas quando a qualidade está
abaixo de limiar configurável e logs estruturados para auditoria.

Agnóstico: não assume nomes específicos de coluna ou tabela.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd


logger = logging.getLogger(__name__)

# Limiar padrão para alerta de qualidade (50%)
LIMIAR_QUALIDADE_PADRAO = 50.0


# ===========================================================================
# FUNÇÃO — Calcular taxa de sucesso de extração de data
# ===========================================================================
def calcular_taxa_sucesso_data(
    df: pd.DataFrame,
    coluna_data: str = "data_emissao",
) -> float:
    """Calcula a taxa de sucesso de extração de data (percentual de registros
    com data válida).

    Args:
        df: DataFrame com dados
        coluna_data: Nome da coluna de data

    Returns:
        Percentual de registros com data válida (0.0 a 100.0)
    """
    if df.empty or coluna_data not in df.columns:
        return 0.0

    total = len(df)
    if total == 0:
        return 0.0

    datas_validas = df[coluna_data].notna().sum()
    taxa = (datas_validas / total) * 100.0
    return round(taxa, 2)


# ===========================================================================
# FUNÇÃO — Calcular taxa de integração entre departamentos
# ===========================================================================
def calcular_taxa_integracao(
    df_integrado: pd.DataFrame,
    extratos_originais: dict[str, pd.DataFrame],
    chave_comum: str,
    departamento_principal: str | None = None,
) -> float:
    """Calcula a taxa de integração entre departamentos.

    Percentual de registros do departamento principal que têm correspondência
    em pelo menos outro departamento.

    Args:
        df_integrado: DataFrame resultado da integração
        extratos_originais: Dict {nome_departamento: DataFrame original}
        chave_comum: Nome da coluna usada para join
        departamento_principal: Nome do departamento base

    Returns:
        Percentual de registros integrados (0.0 a 100.0)
    """
    if not extratos_originais or df_integrado.empty:
        return 0.0

    if departamento_principal is None:
        departamento_principal = list(extratos_originais.keys())[0]

    registros_principal = len(extratos_originais[departamento_principal])
    if registros_principal == 0:
        return 0.0

    # Contar registros com pelo menos uma coluna de outro departamento preenchida
    colunas_outros = [
        c for c in df_integrado.columns
        if c != chave_comum
        and not c.startswith(f"{departamento_principal}_")
    ]

    if not colunas_outros:
        return 0.0

    registros_com_correspondencia = df_integrado[
        df_integrado[colunas_outros].notna().any(axis=1)
    ]
    registros_integrados = len(registros_com_correspondencia)

    taxa = (registros_integrados / registros_principal) * 100.0
    return round(taxa, 2)


# ===========================================================================
# FUNÇÃO — Gerar alerta de qualidade
# ===========================================================================
def gerar_alerta_qualidade(
    taxa_sucesso_data: float,
    limiar: float = LIMIAR_QUALIDADE_PADRAO,
    nome_dataset: str | None = None,
    taxa_integracao: float | None = None,
) -> dict:
    """Gera alerta de qualidade quando taxa está abaixo do limiar.

    Níveis de alerta:
    - alto: taxa < limiar (crítico)
    - medio: limiar <= taxa < limiar + 20 (atenção)
    - baixo: taxa >= limiar + 20 (ok)

    Args:
        taxa_sucesso_data: Taxa de sucesso de extração de data (0-100)
        limiar: Limiar mínimo aceitável (0-100)
        nome_dataset: Nome do dataset (opcional)
        taxa_integracao: Taxa de integração entre departamentos (opcional)

    Returns:
        Dict com campos: alerta_ativo, nivel, mensagem, taxa, limiar
    """
    dataset_str = f" [dataset: {nome_dataset}]" if nome_dataset else ""

    alerta_ativo = False
    nivel = "baixo"
    partes_mensagem = []

    # Verificar taxa de sucesso de data
    if taxa_sucesso_data < limiar:
        alerta_ativo = True
        nivel = "alto"
        partes_mensagem.append(
            f"Taxa de sucesso de data ({taxa_sucesso_data:.1f}%) abaixo do limiar ({limiar:.1f}%){dataset_str}"
        )
    elif taxa_sucesso_data < limiar + 20:
        # Nível médio: acima do limiar mas próximo (dentro de 20 pontos)
        # Alerta ativo para níveis médios também
        alerta_ativo = True
        nivel = "medio"
        partes_mensagem.append(
            f"Taxa de sucesso de data ({taxa_sucesso_data:.1f}%) próxima do limiar ({limiar:.1f}%){dataset_str}"
        )

    # Verificar taxa de integração se fornecida
    if taxa_integracao is not None and taxa_integracao < limiar:
        alerta_ativo = True
        if nivel != "alto":
            nivel = "medio"
        partes_mensagem.append(
            f"Taxa de integração ({taxa_integracao:.1f}%) abaixo do limiar ({limiar:.1f}%){dataset_str}"
        )

    if not partes_mensagem:
        mensagem = f"Qualidade dentro do limiar{dataset_str}"
    else:
        mensagem = "; ".join(partes_mensagem)

    return {
        "alerta_ativo": alerta_ativo,
        "nivel": nivel,
        "mensagem": mensagem,
        "taxa_sucesso_data": taxa_sucesso_data,
        "limiar": limiar,
        "taxa_integracao": taxa_integracao,
        "dataset": nome_dataset,
    }


# ===========================================================================
# FUNÇÃO — Logger estruturado
# ===========================================================================
def logger_estruturado(
    nivel: str,
    mensagem: str,
    dados: dict | None = None,
    fonte: str | None = None,
) -> dict:
    """Gera um log estruturado em formato de dict para fácil serialização JSON.

    Args:
        nivel: Nível do log (INFO, WARNING, ERROR, DEBUG)
        mensagem: Mensagem descritiva
        dados: Dados adicionais opcionais
        fonte: Origem do log (opcional)

    Returns:
        Dict com campos: timestamp, nivel, mensagem, dados, fonte
    """
    entrada = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "nivel": nivel.upper(),
        "mensagem": mensagem,
        "dados": dados or {},
    }

    if fonte:
        entrada["fonte"] = fonte

    # Log também no sistema de logging padrão para compatibilidade
    nivel_log = getattr(logging, nivel.upper(), logging.INFO)
    logger.log(nivel_log, mensagem, extra={"estruturado": entrada})

    return entrada


# ===========================================================================
# CLASSE PRINCIPAL — Observabilidade
# ===========================================================================
class Observabilidade:
    """Especialista responsável por calcular métricas de qualidade de dados,
    gerar alertas e produzir logs estruturados para auditoria.

    Fornece visibilidade sobre a saúde dos dados extraídos e integrados,
    permitindo identificar problemas de qualidade antes que afetem as
    análises de negócio.
    """

    def __init__(
        self,
        limiar_qualidade: float = LIMIAR_QUALIDADE_PADRAO,
        nome_dataset: str | None = None,
    ):
        self.limiar_qualidade = limiar_qualidade
        self.nome_dataset = nome_dataset
        self._logs: list[dict] = []
        self._ultimas_metricas: dict | None = None

    def calcular_metricas(
        self,
        df_integrado: pd.DataFrame,
        extratos: dict[str, pd.DataFrame],
        chave_comum: str,
        departamento_principal: str | None = None,
        coluna_data: str | None = None,
    ) -> dict:
        """Calcula todas as métricas de qualidade de dados.

        Args:
            df_integrado: DataFrame resultado da integração
            extratos: Dict {nome_departamento: DataFrame original}
            chave_comum: Nome da coluna usada para join
            departamento_principal: Nome do departamento base
            coluna_data: Nome da coluna de dados para taxa de sucesso

        Returns:
            Dict com todas as métricas e alertas
        """
        # Calcular taxa de sucesso de data
        taxa_sucesso_data = 0.0
        if coluna_data and coluna_data in df_integrado.columns:
            taxa_sucesso_data = calcular_taxa_sucesso_data(
                df_integrado, coluna_data=coluna_data
            )

        # Calcular taxa de integração
        taxa_integracao = calcular_taxa_integracao(
            df_integrado=df_integrado,
            extratos_originais=extratos,
            chave_comum=chave_comum,
            departamento_principal=departamento_principal,
        )

        # Gerar alertas
        alerta = gerar_alerta_qualidade(
            taxa_sucesso_data=taxa_sucesso_data,
            limiar=self.limiar_qualidade,
            nome_dataset=self.nome_dataset,
            taxa_integracao=taxa_integracao,
        )

        metricas = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dataset": self.nome_dataset,
            "taxa_sucesso_data": taxa_sucesso_data,
            "taxa_integracao": taxa_integracao,
            "limiar_qualidade": self.limiar_qualidade,
            "alerta": alerta,
            "chave_comum": chave_comum,
            "departamento_principal": departamento_principal,
            "registros_integrado": len(df_integrado),
            "registros_principal": len(
                extratos.get(departamento_principal, pd.DataFrame())
            )
            if departamento_principal
            else 0,
        }

        self._ultimas_metricas = metricas

        # Log estruturado
        logger_estruturado(
            nivel="INFO" if not alerta["alerta_ativo"] else "WARNING",
            mensagem=alerta["mensagem"],
            dados={
                "taxa_sucesso_data": taxa_sucesso_data,
                "taxa_integracao": taxa_integracao,
                "limiar": self.limiar_qualidade,
                "dataset": self.nome_dataset,
            },
            fonte="observabilidade",
        )

        return metricas

    def obter_ultimas_metricas(self) -> dict | None:
        """Retorna as últimas métricas calculadas."""
        return self._ultimas_metricas

    def obter_logs(self) -> list[dict]:
        """Retorna todos os logs estruturados gerados."""
        return list(self._logs)

    def definir_limiar(self, limiar: float) -> None:
        """Define um novo limiar de qualidade (0-100)."""
        self.limiar_qualidade = limiar

    def definir_dataset(self, nome_dataset: str) -> None:
        """Define o nome do dataset para rastreabilidade."""
        self.nome_dataset = nome_dataset
