"""Especialista em Árvore de Decisão para Regressão Contínua.

Este módulo encapsula o estimador DecisionTreeRegressor da biblioteca Scikit-Learn[cite:
2].
Ele cumpre o contrato estrutural 'ModeloBase' e particiona o espaço de atributos
em regiões homogêneas através de divisões binárias, prevendo médias locais.
"""

# 'from typing' fornece suporte a anotações estáticas para o contrato abstrato.
from typing import Any

# 'from sklearn.tree' importa o estimador clássico de árvore binária para
# regressão[cite: 2].
from sklearn.tree import DecisionTreeRegressor

# 'from src...' importa a interface contratual obrigatória para manter a modularidade.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' define o especialista em árvore de regressão herdando de 'ModeloBase'.
class AlgoritmoArvoreRegressao(ModeloBase):
    """Modelo não-linear estruturado em partições binárias para regressão numérica."""

    # 'def construir_estimador' instancia o algoritmo configurando sua semente
    # estocástica.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador DecisionTreeRegressor em estado bruto[cite:
        2].

        Args:
            semente_aleatoria (int): Semente para determinar empates no sorteio de
            divisões[cite: 2].

        Returns:
            DecisionTreeRegressor: Estimador pronto para calibração com dados
            tabulares[cite: 2].
        """
        # 'random_state=semente_aleatoria' garante determinação reprodutível em nós
        # empatados[cite: 2].
        return DecisionTreeRegressor(random_state=semente_aleatoria)

    # 'def obter_grade_hiperparametros' expõe os limitadores de sobreajuste
    # (overfitting)[cite: 2].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca em grade para controle de profundidade e pureza dos
        nós[cite: 2].

        Returns:
            Dict[str, list]: Dicionário com critérios de perda e limites de
            complexidade[cite: 2].
        """
        # 'criterion': Função que mede a qualidade da divisão nos dados contínuos:
        # - 'squared_error': Redução da variância via média dos resíduos ao
        # quadrado[cite: 2].
        # - 'absolute_error': Redução do erro absoluto médio através da mediana
        # local[cite: 2].
        # 'max_depth': Limita a profundidade máxima para impedir memorização de ruído
        # (overfitting)[cite: 2].
        # 'min_samples_split': Mínimo de observações necessárias para permitir uma nova
        # ramificação[cite: 2].
        # 'min_samples_leaf': Quantidade mínima de dados que devem residir em cada folha
        # terminal[cite: 2].
        return {
            "criterion": ["squared_error", "absolute_error"],
            "max_depth": [3, 5, 7, 10, None],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 5],
        }
