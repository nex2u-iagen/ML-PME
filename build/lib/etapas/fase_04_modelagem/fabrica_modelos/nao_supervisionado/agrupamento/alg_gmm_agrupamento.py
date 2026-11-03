"""Especialista em Modelos de Misturas Gaussianas (Gaussian Mixture Models - GMM).

Este módulo encapsula o estimador GaussianMixture da biblioteca Scikit-Learn.
Ele assina o contrato universal 'ModeloBase' e implementa agrupamento probabilístico
suave (Soft Clustering) através do algoritmo de Esperança-Maximização (EM).
"""

# 'from typing' importa anotações estáticas para garantir aderência ao contrato da
# fábrica.
from typing import Any

# 'from sklearn.mixture' importa a implementação probabilística baseada em misturas de
# densidade.
from sklearn.mixture import GaussianMixture

# 'from src...' importa a classe base abstrata para assegurar baixo acoplamento e reuso.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' define o especialista GMM herdando de 'ModeloBase'.
class AlgoritmoGMM(ModeloBase):
    """Modelo probabilístico que ajusta múltiplas distribuições normais aos dados."""

    # 'def construir_estimador' instancia a máquina matemática de densidade gaussiana.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador GaussianMixture em seu estado inicial.

        Args:
            semente_aleatoria (int): Semente para controlar a inicialização estocástica
            dos parâmetros EM.

        Returns:
            GaussianMixture: Estimador configurado com covariância irrestrita (full).
        """
        # 'n_components=3' define a quantidade base de distribuições gaussianas a serem
        # ajustadas.
        # 'covariance_type="full"' permite que cada gaussiana tenha formato elíptico e
        # rotação espacial livre.
        # 'max_iter=200' estabelece o teto de iterações do ciclo de
        # Esperança-Maximização (EM).
        # 'random_state=semente_aleatoria' garante reprodutibilidade nas sementes de
        # início do EM.
        return GaussianMixture(
            n_components=3,
            covariance_type="full",
            max_iter=200,
            random_state=semente_aleatoria,
        )

    # 'def obter_grade_hiperparametros' expõe a quantidade de componentes e tipos de
    # covariância.
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca exaustiva de hiperparâmetros para calibração do GMM.

        Returns:
            Dict[str, list]: Dicionário com quantidade de gaussianas e geometrias de
            dispersão.
        """
        # 'n_components': Quantidade de componentes gaussianas latentes a serem
        # ajustadas aos dados.
        # 'covariance_type': Restrições geométricas aplicadas à matriz de covariância:
        # - 'full': Cada grupo possui sua própria matriz de covariância simétrica e
        # irrestrita.
        # - 'tied': Todos os grupos compartilham rigorosamente a mesma matriz de
        # covariância.
        # - 'diag': A covariância é diagonal, alinhando as elipses paralelamente aos
        # eixos coordenados.
        # - 'spherical': Cada grupo é uma esfera perfeita (variância única
        # isotropicamente).
        return {
            "n_components": [2, 3, 4, 5],
            "covariance_type": ["full", "tied", "diag", "spherical"],
        }
