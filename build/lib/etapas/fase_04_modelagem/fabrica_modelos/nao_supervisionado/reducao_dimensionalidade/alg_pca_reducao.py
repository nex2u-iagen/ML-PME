"""Especialista em Análise de Componentes Principais (PCA) para Redução de
Dimensionalidade.

Este módulo encapsula o estimador PCA da biblioteca Scikit-Learn.
Ele cumpre o contrato 'ModeloBase' e projeta os dados em eixos ortogonais
não correlacionados que maximizam a variância estatística global capturada.
"""

# 'from typing' provê suporte a tipagem estática estrita para o design da fábrica.
from typing import Any

# 'from sklearn.decomposition' importa a decomposição clássica de componentes
# principais.
from sklearn.decomposition import PCA

# 'from src...' importa a interface contratual obrigatória para manter a modularidade.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista PCA herdando formalmente de 'ModeloBase'.
class AlgoritmoPCA(ModeloBase):
    """Modelo linear de projeção ortogonal focado em retenção de variância
    máxima[cite: 1].
    """

    # 'def construir_estimador' instancia a máquina matemática de decomposição por
    # autovalores/SVD[cite: 1, 2].
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador PCA configurado em seu estado
        fundamental[cite: 1].

        Args:
            semente_aleatoria (int): Semente para algoritmos de solução estocásticos
            (como 'randomized')[cite: 1].

        Returns:
            PCA: Estimador pronto para extração dos componentes principais[cite: 1].
        """
        # 'n_components=2' define o número padrão inicial de eixos a serem retidos
        # (ideal para gráficos 2D)[cite: 1].
        # 'svd_solver="auto"' delega a escolha entre SVD exato e aproximado com base no
        # tamanho da matriz[cite: 1, 2].
        # 'random_state=semente_aleatoria' garante reprodutibilidade quando o solver for
        # estocástico.
        return PCA(n_components=2, svd_solver="auto", random_state=semente_aleatoria)

    # 'def obter_grade_hiperparametros' expõe opções de retenção de eixos e
    # solvers[cite: 1].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de hiperparâmetros de ajuste para exploração da variância
        acumulada[cite: 1].

        Returns:
            Dict[str, list]: Dicionário contendo números inteiros de eixos ou frações de
            variância (ex.: 0.95)[cite: 1].
        """
        # 'n_components': Quantidade de dimensões finais (números inteiros) ou
        # percentual de variância (float)[cite: 1].
        # 'whiten': Se True, branqueia os dados (remove correlações lineares e fixa a
        # variância em 1).
        return {"n_components": [2, 3, 5, 0.80, 0.95], "whiten": [False, True]}
