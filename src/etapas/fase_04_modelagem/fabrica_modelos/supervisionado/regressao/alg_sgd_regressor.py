"""Especialista em Regressão Linear por Gradiente Estocástico (SGD Regressor).

Este módulo encapsula o estimador SGDRegressor da biblioteca Scikit-Learn[cite: 9].
Ele assina o contrato 'ModeloBase' e implementa aprendizado linear iterativo amostra a
amostra,
sendo o algoritmo ideal para regressão em grandes volumes de dados (Out-of-Core)[cite:
9].
"""

# 'from typing' importa os tipos estáticos para satisfazer a interface polimórfica.
from typing import Any

# 'from sklearn.linear_model' importa o estimador estocástico para problemas de
# regressão contínua[cite: 9].
from sklearn.linear_model import SGDRegressor

# 'from src...' importa a interface contratual obrigatória da nossa arquitetura.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista SGD Regressor herdando de 'ModeloBase'.
class AlgoritmoSGDRegressor(ModeloBase):
    """Modelo linear iterativo otimizado por descida do gradiente estocástico
    contínuo[cite: 9].
    """

    # 'def construir_estimador' instancia a máquina com valores padrão robustos.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador SGDRegressor configurado[cite: 9].

        Args:
            semente_aleatoria (int): Semente para controlar o embaralhamento estocástico
            das amostras[cite: 3, 9].

        Returns:
            SGDRegressor: Estimador pronto para calibração com dados numéricos
            contínuos[cite: 9].
        """
        # 'loss="squared_error"' configura a função de perda clássica dos mínimos
        # quadrados[cite: 9].
        # 'penalty="l2"' aplica regularização Ridge padrão para manter os pesos
        # controlados[cite: 9].
        # 'max_iter=2000' define o limite máximo de passadas completas pelo conjunto de
        # dados[cite: 9].
        # 'random_state=semente_aleatoria' assegura determinismo nos sorteios das
        # amostras[cite: 3, 9].
        return SGDRegressor(
            loss="squared_error",
            penalty="l2",
            max_iter=2000,
            random_state=semente_aleatoria,
        )

    # 'def obter_grade_hiperparametros' expõe a grade de ajuste fino de perdas e taxas
    # de aprendizado[cite: 3].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca exaustiva (Grid Search) para o SGDRegressor[cite: 3,
        9].

        Returns:
            Dict[str, list]: Dicionário com funções de custo, regularizações e taxas de
            aprendizado[cite: 9].
        """
        # 'loss': Função de perda matemática que mede o erro residual:
        #    - 'squared_error': Erro quadrático clássico (sensível a outliers)[cite: 9].
        # - 'huber': Combinação suave de erro quadrático e erro absoluto (robusto a
        # outliers)[cite: 9].
        # 'penalty': Tipo de penalidade sobre os coeficientes ('l2', 'l1' ou
        # 'elasticnet')[cite: 9].
        # 'alpha': Constante de multiplicação da regularização[cite: 9].
        # 'learning_rate': Modo de ajuste da taxa de descida do gradiente[cite: 9].
        return {
            "loss": ["squared_error", "huber"],
            "penalty": ["l2", "l1", "elasticnet"],
            "alpha": [1e-4, 1e-3, 1e-2],
            "learning_rate": ["optimal", "adaptive"],
            "eta0": [0.01, 0.05],
        }
