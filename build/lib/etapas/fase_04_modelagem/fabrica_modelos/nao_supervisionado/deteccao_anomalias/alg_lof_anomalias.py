"""Especialista em Fator de Discrepância Local (Local Outlier Factor - LOF).

Este módulo encapsula o estimador LocalOutlierFactor da biblioteca Scikit-Learn[cite:
1].
Ele cumpre o contrato 'ModeloBase' e mede o desvio de densidade local de uma amostra
em relação aos seus vizinhos mais próximos, configurado com novelty=True para permitir
predições[cite: 1].
"""

# 'from typing' fornece anotações de tipos para conformidade com a arquitetura.
from typing import Any

# 'from sklearn.neighbors' importa o algoritmo de anomalia baseado em densidade de
# vizinhança[cite: 1].
from sklearn.neighbors import LocalOutlierFactor

# 'from src...' importa o contrato universal da fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista LOF herdando de 'ModeloBase'.
class AlgoritmoLOF(ModeloBase):
    """Modelo não supervisionado baseado em comparação de densidades locais de
    vizinhança[cite: 1].
    """

    # 'def construir_estimador' instancia o estimador com suporte a inferência em novos
    # dados[cite: 1].
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador LocalOutlierFactor configurado para predição
        contínua[cite: 1].

        Nota: O LOF clássico é determinístico em distâncias.
        'novelty=True' é estritamente obrigatório para que o estimador exponha os
        métodos
        'predict' e 'decision_function', permitindo seu uso em pipelines e inferências
        futuras[cite: 1].

        Args:
            semente_aleatoria (int): Mantido para interoperabilidade polimórfica com
            ModeloBase.

        Returns:
            LocalOutlierFactor: Estimador pronto para avaliação de densidade
            relativa[cite: 1].
        """
        # 'n_neighbors=20' define o tamanho da vizinhança local para medir a
        # densidade[cite: 1].
        # 'contamination="auto"' delega a determinação do limiar estatístico de
        # corte[cite: 1].
        # 'novelty=True' habilita a interface de inferência 'predict' em novos
        # dados[cite: 1].
        # 'n_jobs=-1' acelera a busca geométrica de vizinhos no processador.
        return LocalOutlierFactor(
            n_neighbors=20, contamination="auto", novelty=True, n_jobs=-1
        )

    # 'def obter_grade_hiperparametros' expõe opções de vizinhança e métricas de
    # distância[cite: 1].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca exaustiva de hiperparâmetros para o LOF[cite: 1].

        Returns:
            Dict[str, list]: Dicionário com número de vizinhos e métricas
            espaciais[cite: 1].
        """
        # 'n_neighbors': Quantidade de vizinhos avaliados para calcular a densidade
        # local[cite: 1].
        # 'metric': Fórmula de distância para medir a proximidade geométrica entre
        # instâncias[cite: 1].
        return {
            "n_neighbors": [10, 20, 35],
            "contamination": ["auto", 0.01, 0.05, 0.1],
            "metric": ["euclidean", "manhattan"],
        }
