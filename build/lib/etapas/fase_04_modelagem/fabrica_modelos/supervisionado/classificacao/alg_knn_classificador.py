"""Especialista em K-Vizinhos Mais Próximos (KNN) para Classificação.

Este módulo encapsula o algoritmo KNeighborsClassifier do Scikit-Learn.
Ele assina o contrato 'ModeloBase' e atua classificando novos dados
com base na similaridade (distância matemática) em relação aos
exemplos mais próximos do conjunto de treinamento.
"""

# 'from typing' importa as anotações estáticas para garantirmos a obediência ao contrato
# da fábrica.
from typing import Any

# 'from sklearn.neighbors' importa o algoritmo baseado em cálculo de distância espacial.
from sklearn.neighbors import KNeighborsClassifier

# 'from src...' importa a Classe Abstrata (o Contrato do nosso Hospital de Dados).
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o nosso Especialista em Similaridade.
# Ele herda de 'ModeloBase', obrigando-se a ter os métodos de construção e grade.
class AlgoritmoKNN(ModeloBase):
    """Modelo não-paramétrico focado em classificação por similaridade espacial."""

    # 'def construir_estimador' prepara a máquina de calcular distâncias.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o algoritmo KNN em seu estado bruto.

        Nota: O KNN tradicional não possui o parâmetro 'random_state' na sua
        inicialização básica, pois ele não faz sorteios internos durante o treino,
        ele apenas calcula distâncias absolutas.

        Args:
            semente_aleatoria (int): Mantido na assinatura para respeitar o Polimorfismo
                                     do contrato ModeloBase, mas não utilizado no KNN.

        Returns:
            KNeighborsClassifier: A instância do modelo pronta para calibração.
        """
        # Retorna o estimador puro.
        # 'n_jobs=-1' orienta o algoritmo a usar todos os núcleos do processador
        # para acelerar o cálculo de distâncias (que costuma ser computacionalmente
        # pesado).
        return KNeighborsClassifier(n_jobs=-1)

    # 'def obter_grade_hiperparametros' entrega o manual de calibração ao
    # GridSearchCV[cite: 5].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define os hiperparâmetros de ajuste para a busca exaustiva (Grid Search).

        Returns:
            Dict[str, list]: Dicionário com os limites de calibração que controlam
                             quantos vizinhos olhar e como medir a distância[cite: 5].
        """
        # Retorna as opções para o Engenheiro Clínico (GridSearchCV) testar:
        # 'n_neighbors' (O valor de K): Quantos vizinhos próximos devo consultar?
        #     - Valores muito baixos (ex: 1) causam overfitting (memorização de ruído).
        #     - Valores muito altos causam underfitting (borrão na decisão).
        # 'weights': Como o peso do voto de um vizinho é calculado?
        #     - 'uniform': Todos os K vizinhos têm peso igual no voto.
        # - 'distance': Vizinhos fisicamente mais próximos têm um voto com peso
        # maior[cite: 2].
        # 'metric': Qual fórmula matemática usar para calcular a distância?
        #     - 'euclidean': Distância em linha reta (Teorema de Pitágoras).
        # - 'manhattan': Distância em blocos (como andar de carro quarteirão por
        # quarteirão)[cite: 5].
        return {
            "n_neighbors": [3, 5, 7, 9, 11],
            "weights": ["uniform", "distance"],
            "metric": ["euclidean", "manhattan"],
        }
