"""Especialista em Regressão Ridge (Regularização L2) para Variáveis Contínuas.

Este módulo encapsula o estimador Ridge da biblioteca Scikit-Learn.
Ele assina o contrato 'ModeloBase' e introduz uma penalidade quadrática sobre
a magnitude dos coeficientes para mitigar a multicolinearidade e o overfitting.
"""

from typing import Any

from sklearn.linear_model import Ridge

from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


class AlgoritmoRidge(ModeloBase):
    """Modelo linear com encolhimento de parâmetros via penalização quadrática L2."""

    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador Ridge em seu estado bruto.

        Args:
            semente_aleatoria (int): Semente de controle para solvers estocásticos (como
            'sag').

        Returns:
            Ridge: O modelo instanciado com cálculo automático de intercepto.
        """
        # 'random_state' garante reprodutibilidade de solvers baseados em
        # gradiente[cite: 1].
        return Ridge(fit_intercept=True, copy_X=True, random_state=semente_aleatoria)

    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca exaustiva para calibração do coeficiente de
        penalidade.

        Returns:
            Dict[str, list]: Dicionário com a constante de regularização alpha e métodos
            de resolução[cite: 1].
        """
        # 'alpha': Controla a força do encolhimento L2. Valores maiores = maior
        # restrição.
        # 'solver': Algoritmo matemático para resolver o sistema.
        #    - 'auto': Escolhe automaticamente com base no tipo de dado.
        # - 'cholesky': Decomposição matricial exata e rápida para matrizes densas[cite:
        # 1].
        # - 'saga': Gradiente estocástico otimizado, excelente para grandes bases[cite:
        # 1].
        return {
            "alpha": [0.01, 0.1, 1.0, 10.0, 100.0],
            "solver": ["auto", "cholesky", "saga"],
        }
