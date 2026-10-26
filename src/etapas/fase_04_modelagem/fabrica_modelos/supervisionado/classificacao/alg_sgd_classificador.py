"""Especialista em Descida do Gradiente Estocástico (SGD) para Classificação.

Este módulo encapsula o estimador SGDClassifier da biblioteca Scikit-Learn.
Ele cumpre o contrato estrutural 'ModeloBase' e implementa aprendizado linear
otimizado por gradiente estocástico, ideal para grandes volumes de dados (out-of-core).
"""

# 'from typing' fornece tipagem estática rigorosa para cumprir a interface abstrata.
from typing import Any

# 'from sklearn.linear_model' importa o estimador de gradiente estocástico linear.
from sklearn.linear_model import SGDClassifier

# 'from src...' importa a classe base abstrata para assegurar polimorfismo e baixo
# acoplamento.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista linear estocástico herdando obrigatoriamente de
# 'ModeloBase'.
class AlgoritmoSGD(ModeloBase):
    """Modelo discriminativo linear calibrado via otimização de gradiente
    estocástico.
    """

    # 'def construir_estimador' implementa a construção inicial do algoritmo.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador SGDClassifier configurado para probabilidade.

        Args:
            semente_aleatoria (int): Semente para controlar a ordem do sorteio das
            amostras.

        Returns:
            SGDClassifier: Estimador linear pronto para ajuste estocástico[cite: 1].
        """
        # 'loss="log_loss"' emula uma regressão logística, habilitando o método
        # 'predict_proba'[cite: 1].
        # 'penalty="l2"' aplica regularização de Ridge para limitar a magnitude dos
        # pesos[cite: 1].
        # 'max_iter=1000' estabelece a quantidade máxima de passadas (épocas) sobre os
        # dados[cite: 1].
        # 'random_state=semente_aleatoria' garante reprodutibilidade no embaralhamento
        # das instâncias[cite: 1].
        return SGDClassifier(
            loss="log_loss", penalty="l2", max_iter=1000, random_state=semente_aleatoria
        )

    # 'def obter_grade_hiperparametros' expõe os intervalos de calibração para o
    # otimizador[cite: 1].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de hiperparâmetros de ajuste para o GridSearchCV[cite: 1, 9].

        Returns:
            Dict[str, list]: Dicionário com opções de penalização e taxas de
            aprendizado[cite: 1].
        """
        # 'penalty': Tipo de regularização matemática aplicada aos coeficientes[cite:
        # 1].
        #   - 'l2': Encolhe os coeficientes proporcionalmente (Ridge)[cite: 1].
        # - 'l1': Zera coeficientes irrelevantes (Lasso / seleção de variáveis)[cite:
        # 1].
        #   - 'elasticnet': Combina a penalidade L1 e L2 simultaneamente[cite: 1].
        # 'alpha': Força da penalização matemática (valores altos impedem
        # sobreajuste)[cite: 1].
        # 'learning_rate': Estratégia de decaimento do tamanho do passo do
        # gradiente[cite: 1].
        return {
            "penalty": ["l2", "l1", "elasticnet"],
            "alpha": [1e-4, 1e-3, 1e-2, 1e-1],
            "learning_rate": ["optimal", "adaptive"],
            "eta0": [0.01, 0.1],
        }
