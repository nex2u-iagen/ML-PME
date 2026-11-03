"""Especialista em Naive Bayes Gaussiano para Classificação.

Este módulo encapsula o estimador GaussianNB da biblioteca Scikit-Learn.
Ele assina o contrato 'ModeloBase' e implementa a classificação probabilística
baseada no Teorema de Bayes, assumindo independência condicional entre os atributos.
"""

# 'from typing' importa os tipos estáticos necessários para cumprir o contrato abstrato
# da fábrica.
from typing import Any

# 'from sklearn.naive_bayes' importa a implementação do Naive Bayes para distribuições
# contínuas.
from sklearn.naive_bayes import GaussianNB

# 'from src...' importa a classe abstrata base garantindo o Baixo Acoplamento e
# Polimorfismo.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o novo especialista probabilístico herdando obrigatoriamente de
# 'ModeloBase'.
class AlgoritmoNaiveBayes(ModeloBase):
    """Modelo probabilístico supervisionado baseado no Teorema de Bayes e suposição
    ingênua.
    """

    # 'def construir_estimador' implementa a instanciação do algoritmo com as diretrizes
    # padrão.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador GaussianNB em estado bruto.

        Nota: O algoritmo GaussianNB calcula a média e a variância de forma analítica e
        fechada.
        Por esse motivo, não emprega sorteios aleatórios nem necessita do parâmetro
        'random_state'.

        Args:
            semente_aleatoria (int): Mantido na assinatura para manter o polimorfismo do
            ModeloBase.

        Returns:
            GaussianNB: Objeto do estimador pronto para receber os dados na etapa de
            ajuste.
        """
        # Retorna a instância pura do GaussianNB pronta para ser conectada ao
        # otimizador.
        return GaussianNB()

    # 'def obter_grade_hiperparametros' disponibiliza os parâmetros de ajuste para o
    # GridSearchCV.
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de hiperparâmetros destinada à calibração estatística do
        modelo.

        Returns:
            Dict[str, list]: Dicionário mapeando os parâmetros de estabilização numérica
            da variância.
        """
        # 'var_smoothing': Porção da maior variância de todos os atributos adicionada à
        # variância
        # para estabilizar o cálculo do denominador e evitar divisão por zero em
        # distribuições estreitas.
        return {"var_smoothing": [1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4]}
