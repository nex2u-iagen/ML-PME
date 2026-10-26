"""Especialista em Regressão ElasticNet (Regularização L1 + L2).

Este módulo encapsula o estimador ElasticNet da biblioteca Scikit-Learn.
Ele assina o contrato 'ModeloBase' e combina a penalidade de seleção esparsa do Lasso
(L1)
com o encolhimento suave da Ridge (L2) para solucionar problemas com variáveis
multicolineares.
"""

# 'from typing' provê suporte a tipagem estática para validar a interface da fábrica.
from typing import Any

# 'from sklearn.linear_model' importa a implementação do ElasticNet regularizado.
from sklearn.linear_model import ElasticNet

# 'from src...' importa a classe base abstrata para assegurar o baixo acoplamento.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista ElasticNet herdando do contrato 'ModeloBase'.
class AlgoritmoElasticNet(ModeloBase):
    """Modelo linear com regularização híbrida combinando penalidades L1 e L2."""

    # 'def construir_estimador' instancia o algoritmo em seu estado inicial configurado.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador ElasticNet em seu estado bruto.

        Args:
            semente_aleatoria (int): Semente para controlar o algoritmo de descida
            coordenada (Coordinate Descent)[cite: 9].

        Returns:
            ElasticNet: O estimador pronto para receber os parâmetros de
            calibração[cite: 9].
        """
        # 'fit_intercept=True' assegura o cálculo do termo independente (beta 0)[cite:
        # 9].
        # 'max_iter=5000' garante margem suficiente de épocas para convergência numérica
        # estável[cite: 9].
        # 'random_state=semente_aleatoria' garante reprodutibilidade exata em execuções
        # repetidas[cite: 3, 9].
        return ElasticNet(
            fit_intercept=True, max_iter=5000, random_state=semente_aleatoria
        )

    # 'def obter_grade_hiperparametros' expõe os intervalos de ajuste para o
    # otimizador[cite: 3].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de hiperparâmetros de ajuste para o GridSearchCV[cite: 3, 9].

        Returns:
            Dict[str, list]: Dicionário com a constante de penalidade total (alpha) e
            balanço (l1_ratio)[cite: 9].
        """
        # 'alpha': Intensidade global da regularização aplicada à função de perda[cite:
        # 9].
        # 'l1_ratio': O balanço da mistura: 0.0 equivale à Ridge pura (L2) e 1.0
        # equivale ao Lasso puro (L1)[cite: 9].
        # 'tol': Limiar de tolerância matemática para encerramento antecipado das
        # iterações[cite: 9].
        return {
            "alpha": [0.001, 0.01, 0.1, 1.0, 10.0],
            "l1_ratio": [0.1, 0.3, 0.5, 0.7, 0.9],
            "tol": [1e-4, 1e-3],
        }
