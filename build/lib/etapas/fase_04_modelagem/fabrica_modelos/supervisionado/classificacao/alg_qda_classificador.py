"""Especialista em Análise Discriminante Quadrática (QDA) para Classificação.

Este módulo encapsula o estimador QuadraticDiscriminantAnalysis do Scikit-Learn.
Ele assina o contrato 'ModeloBase' e atua estimando matrizes de covariância
independentes para cada classe, calibradas com regularização (shrinkage)[cite: 2].
"""

# 'from typing' provê suporte a tipagem estática rigorosa para validar a interface da
# fábrica.
from typing import Any

# 'from sklearn.discriminant_analysis' importa o classificador quadrático bayesiano.
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

# 'from src...' importa a classe base abstrata para assegurar polimorfismo e baixo
# acoplamento[cite: 4].
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista QDA herdando de 'ModeloBase'.
class AlgoritmoQDA(ModeloBase):
    """Modelo discriminante gerativo com covariâncias regulares e fronteiras
    curvas[cite: 2].
    """

    # 'def construir_estimador' instancia o estimador com regularização ativa.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador QuadraticDiscriminantAnalysis com
        regularização de covariância[cite: 2].

        Nota: O parâmetro 'reg_param=0.1' adiciona regularização proporcional à matriz
        identidade (Shrinkage), prevenindo matrizes singulares quando há
        multicolinearidade
        ou atributos redundantes (evita LinAlgError: not full rank)[cite: 1, 2, 5].

        Args:
            semente_aleatoria (int): Mantido para manter o polimorfismo da fábrica.

        Returns:
            QuadraticDiscriminantAnalysis: Estimador configurado com tolerância a dados
            redundantes[cite: 2].
        """
        # 'reg_param=0.1' regulariza as matrizes de covariância para garantir posto
        # completo (full rank).
        return QuadraticDiscriminantAnalysis(reg_param=0.1)

    # 'def obter_grade_hiperparametros' expõe os intervalos de regularização para o
    # otimizador[cite: 1, 2].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de hiperparâmetros de ajuste para o QDA[cite: 2].

        Returns:
            Dict[str, list]: Dicionário com coeficientes de encolhimento de
            covariância[cite: 1, 2].
        """
        # 'reg_param': Intensidade de encolhimento da matriz de covariância em direção à
        # esfera isotrópica[cite: 1, 2].
        return {"reg_param": [0.01, 0.05, 0.1, 0.2, 0.5], "tol": [1e-4, 1e-3, 1e-2]}
