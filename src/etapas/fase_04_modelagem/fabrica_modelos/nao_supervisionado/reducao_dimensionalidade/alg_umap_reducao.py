"""Especialista em UMAP (Uniform Manifold Approximation and Projection).

Este módulo encapsula o estimador UMAP da biblioteca umap-learn[cite: 3].
Ele cumpre o contrato 'ModeloBase' e preserva simultaneamente as estruturas
locais e globais dos dados com altíssima eficiência computacional.
"""

# 'from typing' provê suporte a tipagem estática.
from typing import Any

# 'from src...' importa a classe base abstrata para assegurar o baixo acoplamento da
# fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista UMAP herdando formalmente de 'ModeloBase'.
class AlgoritmoUMAP(ModeloBase):
    """Modelo não-linear fundamentado em topologia de dados de alta
    dimensionalidade[cite: 3].
    """

    # 'def construir_estimador' instancia o algoritmo com importação defensiva.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador UMAP configurado.

        Args:
            semente_aleatoria (int): Semente para controlar a reprodutibilidade da
            variedade.

        Returns:
            Any: A instância da classe UMAP da biblioteca umap-learn[cite: 3].

        Raises:
            ImportError: Caso a biblioteca externa 'umap-learn' não esteja instalada no
            ambiente.
        """
        # Importação defensiva local: evita travamento do módulo se a biblioteca não
        # estiver no ambiente.
        try:
            import umap
        except ImportError as erro_importacao:
            raise ImportError(
                "A biblioteca 'umap-learn' não foi encontrada. "
                "Instale-a no seu ambiente virtual executando: 'uv add umap-learn' ou"
                "'pip install umap-learn'."
            ) from erro_importacao

        # 'n_neighbors=15' equilibra a ênfase entre estrutura local e global[cite: 12].
        # 'min_dist=0.1' controla a densidade de compactação dos pontos no espaço
        # projetado.
        # 'metric="euclidean"' define a métrica clássica para medição de distâncias.
        return umap.UMAP(
            n_components=2,
            n_neighbors=15,
            min_dist=0.1,
            metric="euclidean",
            random_state=semente_aleatoria,
        )

    # 'def obter_grade_hiperparametros' expõe opções de vizinhos e distâncias mínimas.
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca exaustiva de hiperparâmetros para o UMAP[cite: 3].

        Returns:
            Dict[str, list]: Dicionário com tamanho de vizinhança e dispersão espacial.
        """
        # 'n_neighbors': Quantidade de pontos vizinhos considerada para costurar a
        # variedade topológica[cite: 12].
        # 'min_dist': Distância mínima entre observações na projeção (valores baixos
        # agrupam mais).
        return {"n_neighbors": [5, 15, 30], "min_dist": [0.01, 0.1, 0.5]}
