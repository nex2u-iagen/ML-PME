"""Especialista em Agrupamento Baseado em Densidade (DBSCAN).

Este módulo encapsula o estimador DBSCAN da biblioteca Scikit-Learn.
Ele cumpre o contrato estrutural 'ModeloBase' e agrupa amostras com base na
densidade espacial de pontos, rotulando outliers isolados como ruído (-1).
"""

# 'from typing' fornece suporte a tipagem estática para validar a interface da fábrica.
from typing import Any

# 'from sklearn.cluster' importa a implementação clássica de agrupamento espacial por
# densidade.
from sklearn.cluster import DBSCAN

# 'from src...' importa a classe base abstrata para assegurar polimorfismo e baixo
# acoplamento.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista DBSCAN herdando formalmente de 'ModeloBase'.
class AlgoritmoDBSCAN(ModeloBase):
    """Modelo não supervisionado baseado em conectividade por densidade e filtragem
    de ruído.
    """

    # 'def construir_estimador' instancia o agrupador densitário configurado.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador DBSCAN pronto para agrupamento espacial.

        Nota: O DBSCAN é um algoritmo determinístico baseado no cálculo exato de
        distâncias geométricas em vizinhanças, dispensando sementes pseudoaleatórias.
        O argumento 'semente_aleatoria' é preservado para satisfazer o contrato
        'ModeloBase'.

        Args:
            semente_aleatoria (int): Mantido para interoperabilidade polimórfica com
            ModeloBase.

        Returns:
            DBSCAN: Estimador configurado com parâmetros padrão de raio e vizinhança
            mínima.
        """
        # 'eps=0.5' define o raio esférico de busca ao redor de cada ponto.
        # 'min_samples=5' define a quantidade mínima de vizinhos para validar uma área
        # densa (Core Point).
        # 'metric="euclidean"' adota a distância em linha reta para medição geométrica.
        # 'n_jobs=-1' utiliza todos os núcleos de processamento para acelerar a busca de
        # vizinhos.
        return DBSCAN(eps=0.5, min_samples=5, metric="euclidean", n_jobs=-1)

    # 'def obter_grade_hiperparametros' expõe os intervalos críticos de raio e
    # densidade.
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca sistemática para exploração de hiperparâmetros no
        DBSCAN.

        Returns:
            Dict[str, list]: Dicionário com raios épsilon, limiares de amostras e
            métricas espaciais.
        """
        # 'eps': Distância máxima entre duas amostras para serem tratadas como da mesma
        # vizinhança.
        # 'min_samples': Número de amostras em uma vizinhança para formar um ponto
        # central (Core Point).
        # 'metric': Funções de distância matemática aplicadas no cálculo espacial.
        return {
            "eps": [0.1, 0.2, 0.3, 0.5, 0.7, 1.0],
            "min_samples": [3, 5, 10, 15],
            "metric": ["euclidean", "manhattan"],
        }
