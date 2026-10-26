"""Especialista em Floresta Aleatória (Random Forest) para Classificação Binária.

Este módulo encapsula o algoritmo RandomForestClassifier do Scikit-Learn.
Ele assina o contrato 'ModeloBase' e atua como um Método Ensemble, combinando
centenas de Árvores de Decisão para reduzir a variância e capturar relações
não lineares complexas nos dados, prevenindo o overfitting[cite: 2].
"""

# 'from typing import Any, Dict' garante a tipagem estática exigida pelo contrato
# abstrato.
from typing import Any

# 'from sklearn.ensemble' importa a classe que orquestra a "Junta Médica".
# O RandomForestClassifier cria um conjunto de múltiplas Decision Trees
# independentes[cite: 2].
from sklearn.ensemble import RandomForestClassifier

# 'from src...' importa a nossa interface padrão, garantindo o Baixo Acoplamento do
# sistema.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o novo médico especialista que fará parte do hospital (Fábrica).
class AlgoritmoRandomForest(ModeloBase):
    """Modelo Ensemble baseado em dezenas de Árvores de Decisão (Decision
    Trees)[cite: 2].
    """

    # 'def construir_estimador' implementa a regra obrigatória para entregar a máquina
    # médica.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e configura o estado inicial do Random Forest.

        Args:
            semente_aleatoria (int): Semente de reprodutibilidade para o sorteio
                                     das amostras e características das árvores[cite:
                                     2].

        Returns:
            RandomForestClassifier: O modelo bruto configurado para balancear as
            classes.
        """
        # Retorna a instância do modelo estatístico Ensemble.
        # 'class_weight="balanced_subsample"' é uma técnica avançada: ele calcula os
        # pesos
        # das classes (Inadimplente vs Bom Pagador) individualmente para a amostra
        # sorteada por cada árvore, lidando perfeitamente com desbalanceamentos severos.
        # 'random_state=semente_aleatoria' garante que a "aleatoriedade" gere sempre as
        # mesmas árvores a cada reexecução do código.
        return RandomForestClassifier(
            class_weight="balanced_subsample", random_state=semente_aleatoria
        )

    # 'def obter_grade_hiperparametros' expõe os botões que o Engenheiro Clínico
    # (GridSearchCV) pode testar.
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca exaustiva (Grid Search) específica para florestas.

        Returns:
            Dict[str, list]: Dicionário com hiperparâmetros de controle estrutural.
        """
        # Retorna as dimensões matemáticas que serão testadas via Validação Cruzada.
        # 'n_estimators': Quantidade de "médicos" (Árvores) na junta médica.
        # 'max_depth': Profundidade máxima de cada árvore. Limitar isso (ex: 5 ou 10)
        #              impede que a árvore decore os dados (overfitting), forçando-a
        #              a focar apenas nos padrões principais (explicabilidade).
        # 'min_samples_split': Número mínimo de pacientes que um nó precisa ter para
        # justificar a criação de uma nova regra (nova ramificação).
        return {
            "n_estimators": [100, 300, 500],
            "max_depth": [5, 10, 15, None],
            "min_samples_split": [2, 5, 10],
        }
