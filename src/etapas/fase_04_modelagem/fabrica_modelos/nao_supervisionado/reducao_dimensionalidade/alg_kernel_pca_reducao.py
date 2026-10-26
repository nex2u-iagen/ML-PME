"""Especialista em Kernel PCA para Redução de Dimensionalidade Não-Linear.

Este módulo encapsula o estimador KernelPCA da biblioteca Scikit-Learn[cite: 4].
Ele cumpre o contrato 'ModeloBase' e projeta os dados em espaços de Hilbert de dimensão
superior usando funções de Kernel, permitindo desdobrar superfícies não-lineares[cite:
12].
"""

# 'from typing' provê suporte a tipagem estática rigorosa.
from typing import Any

# 'from sklearn.decomposition' importa o redutor não-linear com truque do kernel[cite:
# 4, 12].
from sklearn.decomposition import KernelPCA

# 'from src...' importa a classe base abstrata para assegurar polimorfismo arquitetural.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' define o especialista Kernel PCA herdando de 'ModeloBase'.
class AlgoritmoKernelPCA(ModeloBase):
    """Modelo não-linear de componentes principais baseado em funções de núcleo
    (Kernels)[cite: 12].
    """

    # 'def construir_estimador' instancia a máquina matemática não linear.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador KernelPCA com Kernel RBF padrão[cite: 12].

        Args:
            semente_aleatoria (int): Semente para controlar solvers estocásticos
            internos.

        Returns:
            KernelPCA: Estimador pronto para projeções não-lineares complexas[cite: 12].
        """
        # 'n_components=2' estabelece a projeção em duas dimensões.
        # 'kernel="rbf"' ativa a função de base radial gaussiana para desdobrar dados
        # concêntricos[cite: 12].
        # 'n_jobs=-1' utiliza todos os núcleos para paralelizar o cálculo da matriz de
        # Gram[cite: 2].
        return KernelPCA(
            n_components=2, kernel="rbf", n_jobs=-1, random_state=semente_aleatoria
        )

    # 'def obter_grade_hiperparametros' expõe núcleos e fatores de escala gamma[cite:
    # 12].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca sistemática para exploração de geometrias e
        núcleos[cite: 12].

        Returns:
            Dict[str, list]: Dicionário com tipos de núcleos, coeficientes gamma e graus
            polinomiais[cite: 12].
        """
        # 'kernel': A função de conversão espacial ('rbf', 'poly', 'sigmoid' ou
        # 'cosine')[cite: 12].
        # 'gamma': O raio de influência de cada ponto nas funções RBF e Polinomial[cite:
        # 12].
        return {
            "n_components": [2, 3],
            "kernel": ["rbf", "poly", "cosine"],
            "gamma": [0.01, 0.1, 1.0, None],
        }
