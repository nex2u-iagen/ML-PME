"""Módulo Especialista em Cálculo dos Valores de Shapley (Pilar 3).

Responsabilidade Única: Resumir o espaço estatístico de referência via shap.sample,
inicializar o KernelExplainer agnóstico, extrair a matriz de Shapley aditiva e compilar
a tabela de importância média global dos atributos em linguagem de negócios.
"""

# 'from typing import ...' importa os tipos estáticos formais para a interface do
# módulo[cite: 18].
# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo.
import logging
from collections.abc import Callable

# 'import numpy as np' fornece suporte para tensores e operações matriciais[cite: 17].
import numpy as np

# 'import pandas as pd' estrutura os rankings de importância em DataFrames
# tabulares[cite: 18].
import pandas as pd

# 'import shap' importa a biblioteca matemática de Inteligência Artificial Explicável.
import shap

# Importa a classe de configuração de metadados do Pilar 3.
from src.etapas.fase_05_avaliacao.pilar_03_explicabilidade_xai.configuracao_shap import (  # noqa: E501
    ConfiguracaoShap,
)


# 'class CalculadoraValoresShap' centraliza estritamente os cálculos de Shapley.
class CalculadoraValoresShap:
    """Motor de cálculo estatístico para decomposição aditiva de probabilidade com
    SHAP[cite: 20].
    """

    # 'def __init__(...)' injeta a dependência das configurações operacionais[cite: 20].
    def __init__(self, configuracao: ConfiguracaoShap) -> None:
        """Inicializa a calculadora de Shapley associando as regras de amostragem[cite:
        20].

        Args:
            configuracao (ConfiguracaoShap): Objeto de domínio com nomes de colunas e
            baseline[cite: 20].
        """
        self.config = configuracao

    # 'def construir_explicador(...)' instancia o KernelExplainer com dados de fundo
    # amostrados[cite: 20].
    def construir_explicador(
        self,
        funcao_predicao_probabilidade: Callable[[np.ndarray], np.ndarray],
        dados_treinamento: np.ndarray,
    ) -> shap.KernelExplainer:
        """Resume os dados de treino via amostragem e compila o explicador agnóstico.

        Args:
            funcao_predicao_probabilidade (Callable): Função que recebe matriz X e
            devolve probabilidades 1D[cite: 18].
            dados_treinamento (np.ndarray): Matriz X de treino para cálculo da população
            basal[cite: 20].

        Returns:
            shap.KernelExplainer: Estimador configurado com a distribuição de referência
            populacional[cite: 20].
        """
        logging.info(
            "Resumindo espaço estatístico basal com %d amostras de fundo...",
            self.config.quantidade_fundo,
        )

        # CORREÇÃO CIRÚRGICA: O argumento oficial de contagem de amostras é 'nsamples'
        # (não 'npatterns').
        dados_fundo_resumidos = shap.sample(
            dados_treinamento,
            nsamples=self.config.quantidade_fundo,
            random_state=self.config.semente_aleatoria,
        )

        logging.info("Inicializando shap.KernelExplainer sobre o modelo campeão...")

        # Constrói o explicador aditivo agnóstico baseado na Teoria dos Jogos
        # Cooperativos[cite: 20].
        return shap.KernelExplainer(
            model=funcao_predicao_probabilidade,
            data=dados_fundo_resumidos,
        )

    # 'def calcular_matriz_shap(...)' computa as contribuições marginais e o valor
    # base[cite: 20].
    def calcular_matriz_shap(
        self,
        explicador: shap.KernelExplainer,
        dados_avaliacao: np.ndarray,
    ) -> tuple[np.ndarray, float]:
        """Calcula a matriz de Shapley para o conjunto avaliado e extrai o valor
        esperado basal[cite: 20].

        Args:
            explicador (shap.KernelExplainer): Estimador de Shapley previamente
            ajustado[cite: 20].
            dados_avaliacao (np.ndarray): Matriz X contendo os indivíduos a serem
            auditados[cite: 18, 20].

        Returns:
            Tuple[np.ndarray, float]: (Matriz de valores SHAP, Probabilidade Basal
            Esperada E[f(x)])[cite: 20].
        """
        logging.info(
            "Calculando Valores de Shapley para %d observações de teste...",
            len(dados_avaliacao),
        )

        # Extrai os valores aditivos de Shapley para cada amostra e cada atributo
        # preditor[cite: 18, 20].
        valores_shap = np.array(explicador.shap_values(dados_avaliacao))

        # Trata o valor esperado populacional basal como float escalar independente do
        # formato retornado[cite: 18, 20].
        valor_base = float(np.atleast_1d(explicador.expected_value)[0])

        return valores_shap, valor_base

    # 'def compilar_importancia_global(...)' gera o ranking tabular de magnitude de
    # negócio[cite: 20].
    def compilar_importancia_global(self, valores_shap: np.ndarray) -> pd.DataFrame:
        """Calcula a média do impacto absoluto (|SHAP|) de cada variável sobre as
        decisões[cite: 20].

        Args:
            valores_shap (np.ndarray): Matriz 2D contendo as forças marginais
            computadas[cite: 20].

        Returns:
            pd.DataFrame: Ranking de importância global ordenado decrescentemente pelo
            impacto[cite: 18, 20].
        """
        # Calcula a média da magnitude absoluta (|SHAP|) em cada coluna da matriz de
        # impacto[cite: 18, 20].
        impacto_medio_absoluto = np.mean(np.abs(valores_shap), axis=0)

        # Monta a tabela associando o nome do atributo ao seu peso causal no
        # modelo[cite: 18, 20].
        tabela = pd.DataFrame(
            {
                "Atributo_Negocio": self.config.nomes_atributos,
                "Impacto_Absoluto_Medio_SHAP": impacto_medio_absoluto,
            }
        )

        # Ordena os atributos posicionando a variável com maior peso causal no
        # topo[cite: 18, 20].
        return tabela.sort_values(
            by="Impacto_Absoluto_Medio_SHAP", ascending=False
        ).reset_index(drop=True)
