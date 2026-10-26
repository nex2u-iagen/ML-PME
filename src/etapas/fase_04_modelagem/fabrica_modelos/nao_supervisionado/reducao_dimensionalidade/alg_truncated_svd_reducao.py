"""Especialista em SVD Truncado (Truncated Singular Value Decomposition).

Este módulo encapsula o estimador TruncatedSVD da biblioteca Scikit-Learn.
Ele cumpre o contrato 'ModeloBase' e opera eficientemente sobre matrizes esparsas,
sendo a base da Análise Semântica Latente (LSA) sem exigir a centralização na média.
"""

# 'from typing' fornece anotações de tipos para conformidade com a arquitetura.
from typing import Any

# 'from sklearn.decomposition' importa o redutor matricial para grandes volumes
# esparsos[cite: 2, 4].
from sklearn.decomposition import TruncatedSVD

# 'from src...' importa o contrato universal da fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista SVD Truncado herdando de 'ModeloBase'.
class AlgoritmoTruncatedSVD(ModeloBase):
    """Modelo de fatoração matricial truncada adaptado para estruturas esparsas."""

    # 'def construir_estimador' instancia o algoritmo configurado com semente
    # reprodutível.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador TruncatedSVD em estado bruto[cite: 2].

        Args:
            semente_aleatoria (int): Semente para controlar o sorteio no algoritmo de
            Lanczos/Randomized[cite: 2].

        Returns:
            TruncatedSVD: O estimador pronto para decomposição linear direta[cite: 2].
        """
        # 'n_components=2' define a dimensionalidade alvo padrão inicial.
        # 'algorithm="randomized"' acelera a aproximação dos valores singulares
        # dominantes[cite: 2].
        # 'random_state=semente_aleatoria' garante convergência idêntica em múltiplas
        # execuções.
        return TruncatedSVD(
            n_components=2, algorithm="randomized", random_state=semente_aleatoria
        )

    # 'def obter_grade_hiperparametros' expõe intervalos de componentes e números de
    # iterações.
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca exaustiva de hiperparâmetros para o TruncatedSVD.

        Returns:
            Dict[str, list]: Dicionário com número de componentes e algoritmos de
            decomposição[cite: 2].
        """
        # 'n_components': Dimensões truncadas a serem preservadas na fatoração[cite: 2].
        # 'n_iter': Quantidade de iterações do solver para refinar a precisão singular.
        return {"n_components": [2, 3, 5, 10], "n_iter": [5, 7, 10]}
