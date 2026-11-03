"""Módulo Especialista em Inferência Vetorizada e Aplicação de Limiar (Pilar 4 - Fase 6).

Responsabilidade Única: Extrair os atributos validados pelo Pydantic, estruturá-los
em DataFrame com as colunas corretas para o Pipeline completo do Scikit-Learn,
executar a predição probabilística, cronometrar a latência e aplicar o limiar[cite: 10, 19].
"""

# 'import' traz o módulo nativo para cronometragem de alta precisão em nanossegundos[cite: 10].
import time
from typing import Any

# 'import' traz a biblioteca 'numpy' para funções matemáticas e vetores[cite: 10].
import numpy as np

# 'import' traz o 'pandas' para manter os nomes de colunas exigidos pelo ColumnTransformer[cite: 10, 19].
import pandas as pd

# Importa o contrato formal de entrada do cliente[cite: 10].
from src.etapas.fase_06_implantacao.pilar_03_contratos_dados.esquema_entrada_cliente import (
    EsquemaEntradaCliente,
)


# 'class MotorPredicaoVetorizado' isola as rotinas de inferência e corte de probabilidade[cite: 10].
class MotorPredicaoVetorizado:
    """Motor de cálculo que transforma contratos de clientes em decisões probabilísticas[cite: 10]."""

    # 'def __init__(...)' constrói a instância registrando o limiar ótimo homologado[cite: 10].
    def __init__(self, limiar_corte: float = 0.50) -> None:
        """Inicializa o motor com a política de sensibilidade homologada[cite: 10].

        Args:
            limiar_corte (float): Ponto de corte ótimo de probabilidade[cite: 10].
        """
        self.limiar_corte = float(limiar_corte)

    # 'def prescrever_acao(...)' traduz a probabilidade em diretriz de negócio[cite: 10].
    @staticmethod
    def prescrever_acao(probabilidade: float) -> tuple[str, str, str]:
        """Mapeia a probabilidade contínua em rótulo, faixa e recomendação operacional[cite: 10]."""
        if probabilidade < 0.25:
            return (
                "BAIXO_RISCO_COMPROVADO",
                "BAIXO RISCO",
                "Liberar Faturamento / Manter Crédito Automático",
            )
        elif probabilidade < 0.60:
            return (
                "RISCO_MODERADO_MONITORAR",
                "MÉDIO RISCO",
                "Monitoramento Ativo / Alerta Preventivo ao Faturamento",
            )
        else:
            return (
                "ALTO_RISCO_INADIMPLENCIA",
                "ALTO RISCO (CRÍTICO)",
                "Bloquear Prazo / Exigir Pagamento à Vista ou Garantia",
            )

    # 'def executar_predicao_rapida(...)' processa os dados pelo Pipeline e afere a latência[cite: 10].
    def executar_predicao_rapida(
        self,
        cliente: EsquemaEntradaCliente,
        pipeline_modelo: Any,
    ) -> tuple[int, str, float, str, str, float]:
        """Estrutura os dados, calcula a probabilidade pelo Pipeline e cronometra a resposta[cite: 10].

        Args:
            cliente (EsquemaEntradaCliente): Objeto auditado pelo Pydantic[cite: 10].
            pipeline_modelo (Any): Pipeline completo (Pré-processador + Estimador Campeão)[cite: 10, 19].

        Returns:
            tuple: (Classe, Rótulo, Probabilidade, Faixa de Risco, Ação Prescritiva, Latência ms)[cite: 10].
        """
        # Inicia a cronometragem no hardware de maior resolução[cite: 10].
        tempo_inicio = time.perf_counter()

        # Extrai os dados do contrato Pydantic e formata como DataFrame de 1 linha com nomes de colunas[cite: 10].
        dicionario_cliente = cliente.exportar_dicionario_atributos()
        df_amostra = pd.DataFrame([dicionario_cliente])

        # Executa a predição probabilística através do Pipeline do Scikit-Learn[cite: 10, 19]:
        if hasattr(pipeline_modelo, "predict_proba"):
            probabilidade_risco = float(pipeline_modelo.predict_proba(df_amostra)[0, 1])
        else:
            decision = float(pipeline_modelo.decision_function(df_amostra)[0])
            probabilidade_risco = float(1.0 / (1.0 + np.exp(-decision)))

        # Calcula o tempo decorrido em milissegundos[cite: 10].
        latencia_ms = (time.perf_counter() - tempo_inicio) * 1000.0

        # Aplica a regra de decisão pelo limiar homologado[cite: 10]:
        classe_final = 1 if probabilidade_risco >= self.limiar_corte else 0
        rotulo, faixa, acao = self.prescrever_acao(probabilidade_risco)

        return classe_final, rotulo, probabilidade_risco, faixa, acao, latencia_ms