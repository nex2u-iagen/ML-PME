"""Módulo de Interface Contratual para a Fábrica de Modelos de Machine Learning.

Este arquivo utiliza o conceito de Classes Abstratas (ABC) para definir
um contrato de obrigatoriedade. Todos os algoritmos preditivos que forem
adicionados ao projeto deverão herdar desta classe e implementar seus métodos,
garantindo Baixo Acoplamento e Alta Coesão na arquitetura do software.
"""

# 'from' acessa o módulo 'abc' (Abstract Base Classes) nativo da biblioteca padrão do
# Python.
# 'ABC' é a classe raiz que transforma nossa classe em um contrato que não pode ser
# instanciado sozinho.
# 'abstractmethod' é um decorador que força as classes filhas a escreverem o código
# daquele método.
from abc import ABC, abstractmethod

# 'from' acessa o módulo 'typing' da biblioteca padrão para anotação estática de tipos.
# 'Any' indica que o retorno pode ser de qualquer tipo (pois o Scikit-Learn tem vários
# tipos de objetos).
# 'Dict' indica a construção de um dicionário (estrutura de chaves e valores).
from typing import Any


# 'class' declara o nosso molde estrutural.
# '(ABC)' entre parênteses indica herança: a 'ModeloBase' herda os poderes de contrato
# do Python.
class ModeloBase(ABC):
    """Contrato abstrato que padroniza a criação e calibração de modelos no sistema."""

    # '@abstractmethod' avisa ao Python: "Se algum programador criar um modelo novo e
    # esquecer
    # de escrever este método, proíba o código de rodar e acuse um erro imediatamente".
    @abstractmethod
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o algoritmo matemático bruto (Estimator) não treinado.

        Este método deve retornar a máquina de aprendizado (ex: LogisticRegression)
        com suas configurações padrão, pronta para receber os dados.

        Args:
            semente_aleatoria (int, opcional): Valor para controle de aleatoriedade
                                               garantindo a reprodutibilidade. Padrão:
                                               42.

        Returns:
            Any: A instância do modelo estatístico/matemático.
        """
        # 'pass' indica que esta classe abstrata não faz nada; a responsabilidade
        # de escrever a lógica é repassada para as classes filhas (os médicos
        # especialistas).
        pass

    # '@abstractmethod' força a implementação da grade de calibração para o otimizador.
    @abstractmethod
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Fornece o catálogo de hiperparâmetros (Parameter Grid) para a Sala de
        Calibração.

        Os hiperparâmetros são os 'botões de ajuste' pré-treinamento que controlam a
        complexidade matemática do modelo, fundamentais para evitar overfitting[cite:
        6].

        Returns:
            Dict[str, list]: Um dicionário onde a chave é o nome do parâmetro exato
                             exigido pelo modelo, e o valor é uma lista de opções a
                             testar.
        """
        # Novamente, 'pass' repassa a responsabilidade para a classe filha.
        pass
