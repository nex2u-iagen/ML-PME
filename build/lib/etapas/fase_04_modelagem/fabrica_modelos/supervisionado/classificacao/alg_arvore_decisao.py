"""Especialista em Árvore de Decisão (Decision Tree) para Classificação.

Este módulo encapsula o algoritmo DecisionTreeClassifier do Scikit-Learn.
Ele obedece ao contrato 'ModeloBase' e atua dividindo os dados sucessivamente
através de regras lógicas binárias, maximizando a pureza das classes em cada nó[cite:
2].
"""

# 'from typing' importa os tipos estáticos exigidos pelo nosso contrato (Interface).
from typing import Any

# 'from sklearn.tree' importa o estimador clássico baseado em estrutura de Árvore
# Binária[cite: 2].
from sklearn.tree import DecisionTreeClassifier

# 'from src...' importa o molde arquitetural que garante o Baixo Acoplamento do
# Orquestrador.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o nosso novo especialista lógico.
# Ao herdar de 'ModeloBase', o Python obriga a implementação dos métodos de estimador e
# grade.
class AlgoritmoArvoreDecisao(ModeloBase):
    """Modelo não-linear focado na extração de regras de negócio interpretáveis[cite:
    2].
    """

    # 'def construir_estimador' configura o equipamento de aprendizado antes do uso.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e configura o estado bruto da Árvore de Decisão.

        Args:
            semente_aleatoria (int): Controla o motor de estocasticidade para garantir
                                     que, a cada execução, a árvore inicie do mesmo
                                     ponto.

        Returns:
            DecisionTreeClassifier: Algoritmo configurado para balanceamento automático.
        """
        # Retorna a árvore instanciada.
        # 'class_weight="balanced"' ajusta os pesos matemáticos automaticamente para
        # penalizar mais severamente os erros cometidos na classe minoritária,
        # essencial para bases com desbalanceamento.
        return DecisionTreeClassifier(
            class_weight="balanced", random_state=semente_aleatoria
        )

    # 'def obter_grade_hiperparametros' expõe o manual de calibração clínica.
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define os parâmetros estruturais que limitam a memorização
        (Overfitting)[cite: 2].

        Returns:
            Dict[str, list]: Grade de busca para o GridSearchCV processar.
        """
        # Retorna os hiperparâmetros vitais da Decision Tree[cite: 2].
        # 'criterion': Qual matemática usaremos para avaliar se uma pergunta foi boa?
        #              'gini' foca na probabilidade de erro (pureza);
        #              'entropy' baseia-se na teoria da informação (desordem);
        # 'log_loss' penaliza probabilidades de classe muito erradas[cite: 2].
        # 'max_depth': O limite de andares da árvore. Sem isso, a árvore cresce até
        # ter 1 paciente por folha (100% de overfitting na base de treino)[cite: 2].
        # 'min_samples_leaf': Número mínimo de pacientes exigido para formar um grupo
        # final (folha).
        return {
            "criterion": ["gini", "entropy", "log_loss"],
            "max_depth": [3, 5, 7, 10, None],
            "min_samples_leaf": [5, 10, 20],
        }
