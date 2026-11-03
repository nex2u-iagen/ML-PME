"""Especialista em Agrupamento por K-Médias (K-Means).

Este módulo encapsula o estimador KMeans da biblioteca Scikit-Learn.
Ele cumpre o contrato estrutural universal 'ModeloBase' e atua particionando
os dados em K grupos esféricos via convergência iterativa de centroides[cite: 8, 16].
"""

# 'from typing' fornece tipagem estática rigorosa para cumprir a interface contratual da
# fábrica.
from typing import Any

# 'from sklearn.cluster' importa a implementação clássica de particionamento por
# centroides[cite: 8, 16].
from sklearn.cluster import KMeans

# 'from src...' importa a classe base abstrata para assegurar polimorfismo e baixo
# acoplamento[cite: 8].
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista K-Means herdando formalmente de 'ModeloBase'.
class AlgoritmoKMeans(ModeloBase):
    """Modelo não supervisionado baseado em minimização da inércia intra-cluster
    (WCSS)[cite: 8, 16].
    """

    # 'def construir_estimador' instancia o agrupador particional com semente e
    # inicialização inteligente.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador KMeans pronto para a esteira não
        supervisionada.

        Args:
            semente_aleatoria (int): Semente para determinar o sorteio reprodutível dos
            centroides[cite: 16].

        Returns:
            KMeans: Estimador configurado com 'k-means++' para evitar mínimos locais
            desfavoráveis[cite: 16].
        """
        # 'n_clusters=8' estabelece a quantidade padrão inicial de agrupamentos do
        # Scikit-Learn[cite: 16].
        # 'init="k-means++"' espalha os centroides iniciais probabilisticamente para
        # acelerar a convergência[cite: 16].
        # 'n_init=10' roda o algoritmo 10 vezes com sementes diferentes e seleciona o
        # ajuste de menor inércia[cite: 16].
        # 'max_iter=300' estipula o número máximo de deslocamentos permitidos aos
        # centroides por execução.
        # 'random_state=semente_aleatoria' garante reprodutibilidade idêntica em
        # múltiplas execuções.
        return KMeans(
            n_clusters=8,
            init="k-means++",
            n_init=10,
            max_iter=300,
            random_state=semente_aleatoria,
        )

    # 'def obter_grade_hiperparametros' expõe os intervalos para calibração do Método do
    # Cotovelo e Silhueta.
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca sistemática de hiperparâmetros para exploração de
        clusters[cite: 8, 16].

        Returns:
            Dict[str, list]: Dicionário contendo números de grupos (k), esquemas de
            início e iterações.
        """
        # 'n_clusters': Quantidade de partições espaciais (k) a serem testadas (ex.: 2 a
        # 8 grupos).
        # 'init': Estratégias de semeadura dos centroides iniciais ('k-means++' ou
        # 'random')[cite: 16].
        # 'n_init': Quantidade de reinicializações completas para garantir o menor WCSS
        # global[cite: 16].
        # 'max_iter': Limite de épocas de movimentação dos centroides.
        return {
            "n_clusters": [2, 3, 4, 5, 6, 8],
            "init": ["k-means++", "random"],
            "n_init": [10, 20],
            "max_iter": [300, 500],
        }
