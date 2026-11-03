"""Especialista em Agrupamento Hierárquico Aglomerativo.

Este módulo encapsula o estimador AgglomerativeClustering do Scikit-Learn.
Ele assina o contrato universal 'ModeloBase' e atua através de uma abordagem
ascendente (bottom-up), fundindo sucessivamente os pares de clusters mais próximos.
"""

# 'from typing' provê suporte a tipagem estática para validar a interface abstrata da
# fábrica.
from typing import Any

# 'from sklearn.cluster' importa a implementação do agrupador hierárquico aglomerativo.
from sklearn.cluster import AgglomerativeClustering

# 'from src...' importa a classe base abstrata para assegurar polimorfismo e baixo
# acoplamento.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista hierárquico herdando formalmente de 'ModeloBase'.
class AlgoritmoHierarquico(ModeloBase):
    """Modelo não supervisionado baseado em fusão ascendente e análise taxonômica de
    dendrograma.
    """

    # 'def construir_estimador' instancia o agrupador com métrica euclidiana e critério
    # de Ward.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador AgglomerativeClustering configurado.

        Nota: O agrupamento hierárquico aglomerativo é um algoritmo puramente
        determinístico,
        baseado no cálculo exato de distâncias matriciais entre pares.
        O parâmetro 'semente_aleatoria' é mantido para honrar o polimorfismo de
        ModeloBase.

        Args:
            semente_aleatoria (int): Mantido para interoperabilidade polimórfica com a
            fábrica.

        Returns:
            AgglomerativeClustering: Estimador configurado pronto para processamento.
        """
        # 'n_clusters=2' define o ponto de corte inicial padrão para divisão em grupos.
        # 'metric="euclidean"' define a distância euclidiana para medição do afastamento
        # entre pontos.
        # 'linkage="ward"' minimiza a soma das variâncias ao quadrado dos clusters que
        # estão sendo fundidos.
        return AgglomerativeClustering(n_clusters=2, metric="euclidean", linkage="ward")

    # 'def obter_grade_hiperparametros' expõe critérios de ligação e quantidade de
    # partições.
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca sistemática de hiperparâmetros para exploração
        hierárquica.

        Returns:
            Dict[str, list]: Dicionário com opções de número de grupos e critérios de
            fusão (linkage).
        """
        # 'n_clusters': Quantidade de clusters desejada no corte final do dendrograma.
        # 'linkage': Critério matemático que define a distância entre dois conjuntos de
        # pontos:
        # - 'ward': Minimiza a variância total intra-cluster (exige metric='euclidean').
        #    - 'complete': Utiliza a distância máxima entre pontos dos dois conjuntos.
        # - 'average': Utiliza a média das distâncias entre todos os pontos dos dois
        # conjuntos.
        return {
            "n_clusters": [2, 3, 4, 5, 6],
            "linkage": ["ward", "complete", "average"],
        }
