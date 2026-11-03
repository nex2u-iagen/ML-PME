"""Especialista em AdaBoost (Adaptive Boosting) para Classificação Binária.

Este módulo encapsula o estimador AdaBoostClassifier da biblioteca Scikit-Learn.
Ele implementa o contrato 'ModeloBase' e opera combinando sequencialmente
estimadores fracos (Decision Stumps), redistribuindo pesos analíticos para
priorizar instâncias classificadas incorretamente nas iterações anteriores[cite: 2, 3].
"""

# 'from typing' importa anotações de tipagem estática para validar a interface da
# fábrica.
from typing import Any

# 'from sklearn.ensemble' importa o classificador de impulsionamento adaptativo.
from sklearn.ensemble import AdaBoostClassifier

# 'from sklearn.tree' importa o estimador base padrão de decisão unitária (Stump)[cite:
# 2, 3].
from sklearn.tree import DecisionTreeClassifier

# 'from src...' importa a classe abstrata de referência para assegurar o Baixo
# Acoplamento.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista AdaBoost herdando as regras de ModeloBase.
class AlgoritmoAdaBoost(ModeloBase):
    """Modelo Ensemble sequencial baseado em aumento adaptativo de pesos
    residuais[cite: 2, 3].
    """

    # 'def construir_estimador' instancia a máquina matemática de aprendizado com
    # semente fixa.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o AdaBoostClassifier configurado com tocos de decisão.

        Args:
            semente_aleatoria (int): Semente para controlar a reprodutibilidade dos
            sorteios internos.

        Returns:
            AdaBoostClassifier: Estimador bruto pronto para ajuste e calibração fina.
        """
        # Instancia o aprendiz fraco clássico: árvore binária com apenas uma divisão
        # (profundidade 1)[cite: 2, 3].
        aprendiz_fraco = DecisionTreeClassifier(
            max_depth=1, random_state=semente_aleatoria
        )

        # Retorna o estimador Ensemble configurado com o toco de decisão.
        # 'estimator=aprendiz_fraco' estabelece a unidade básica de aprendizado
        # sequencial.
        # 'random_state=semente_aleatoria' garante convergência idêntica em múltiplas
        # execuções.
        return AdaBoostClassifier(
            estimator=aprendiz_fraco, random_state=semente_aleatoria
        )

    # 'def obter_grade_hiperparametros' expõe os intervalos de calibração para o
    # otimizador.
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca exaustiva (Grid Search) para o AdaBoost.

        Returns:
            Dict[str, list]: Dicionário com parâmetros de quantidade de árvores e taxa
            de aprendizado.
        """
        # Retorna o dicionário de opções para calibração no GridSearchCV:
        # 'n_estimators': Quantidade total de tocos de decisão que serão treinados em
        # sequência.
        # 'learning_rate': Taxa de aprendizado que encolhe a contribuição de cada toco
        # individual.
        # Valores menores exigem mais estimadores, prevenindo sobreajuste rápido.
        return {"n_estimators": [50, 100, 200], "learning_rate": [0.01, 0.1, 0.5, 1.0]}
