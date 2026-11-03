"""Especialista em XGBoost (Extreme Gradient Boosting) para Classificação Binária e
Multiclasse.

Este módulo encapsula o algoritmo XGBClassifier da biblioteca xgboost.
Ele cumpre o contrato estrutural 'ModeloBase' e implementa boosting de gradiente
sequencial.
"""

# 'from typing' provê suporte a tipagem estática rigorosa para cumprir o contrato da
# fábrica.
from typing import Any

# 'import xgboost as xgb' importa a biblioteca de alta performance para Gradient
# Boosting.
import xgboost as xgb

# 'from src...' importa a classe base abstrata para assegurar o baixo acoplamento[cite:
# 4].
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista XGBoost moderno herdando de 'ModeloBase'.
class AlgoritmoXGBoost(ModeloBase):
    """Modelo Ensemble sequencial focado em minimização de gradientes e alta
    capacidade preditiva[cite: 9].
    """

    # 'def construir_estimador' instancia a máquina matemática base sem parâmetros
    # legados.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia o XGBClassifier em conformidade com as versões modernas da
        biblioteca.

        Args:
            semente_aleatoria (int): Semente para determinar reprodutibilidade nos
            sorteios[cite: 1].

        Returns:
            xgb.XGBClassifier: Estimador limpo pronto para calibração[cite: 1].
        """
        # 'eval_metric="logloss"' monitora a perda logarítmica durante o ajuste
        # sequencial[cite: 1].
        # 'random_state=semente_aleatoria' garante convergência idêntica em múltiplas
        # execuções[cite: 1].
        return xgb.XGBClassifier(eval_metric="logloss", random_state=semente_aleatoria)

    # 'def obter_grade_hiperparametros' expõe parâmetros de profundidade, árvores e taxa
    # de aprendizado.
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca exaustiva (Grid Search) para o XGBoost[cite: 6].

        Returns:
            Dict[str, list]: Dicionário com hiperparâmetros de controle de complexidade
            e encolhimento.
        """
        return {
            "n_estimators": [100, 200, 300],
            "max_depth": [3, 5, 7],
            "learning_rate": [0.01, 0.1, 0.2],
        }
