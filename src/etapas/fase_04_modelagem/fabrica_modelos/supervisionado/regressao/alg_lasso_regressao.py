"""Especialista em Regressão Lasso (Regularização L1) para Variáveis Contínuas.

Este módulo encapsula o estimador Lasso da biblioteca Scikit-Learn[cite: 1].
Ele assina o contrato 'ModeloBase' e introduz uma penalidade linear absoluta,
capaz de zerar coeficientes e atuar como seletor automático de variáveis (Feature
Selection)[cite: 1].
"""

from typing import Any

from sklearn.linear_model import Lasso

from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


class AlgoritmoLasso(ModeloBase):
    """Modelo linear com seleção esparsa de atributos via penalização absoluta
    L1[cite: 1].
    """

    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador Lasso em seu estado bruto.

        Args:
            semente_aleatoria (int): Controla a aleatoriedade do solver Coordinate
            Descent[cite: 1].

        Returns:
            Lasso: O estimador pronto para penalizar coeficientes irrelevantes.
        """
        # O Lasso do scikit-learn utiliza o algoritmo 'Coordinate Descent'[cite: 1].
        # 'max_iter=5000' é elevado preventivamente, pois a otimização L1
        # pode demorar a convergir em bases não normalizadas.
        return Lasso(fit_intercept=True, max_iter=5000, random_state=semente_aleatoria)

    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de hiperparâmetros para calibração da esparsidade[cite: 1].

        Returns:
            Dict[str, list]: Dicionário focado na intensidade da penalidade
            'alpha'[cite: 1].
        """
        # 'alpha': Quanto maior o valor, mais variáveis terão o peso exatamente igual a
        # zero[cite: 1].
        # 'tol': Limite numérico de tolerância para o solver declarar convergência
        # alcançada.
        return {"alpha": [0.001, 0.01, 0.1, 1.0, 10.0], "tol": [1e-4, 1e-3]}
