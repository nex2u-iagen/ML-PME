"""Especialista em Envelope Elíptico (Elliptic Envelope / FastMCD) para Detecção de
Outliers.

Este módulo encapsula o estimador EllipticEnvelope da biblioteca Scikit-Learn[cite: 1].
Ele cumpre o contrato 'ModeloBase' e ajusta uma distribuição gaussiana multivariada
robusta
baseada na Distância de Mahalanobis e no Determinante Mínimo de Covariância
(FastMCD)[cite: 1, 2].
"""

# 'from typing' fornece suporte a anotações estáticas para satisfazer a interface da
# fábrica.
from typing import Any

# 'from sklearn.covariance' importa o estimador robusto de covariância para dados
# gaussianos[cite: 1].
from sklearn.covariance import EllipticEnvelope

# 'from src...' importa a classe base abstrata para assegurar o baixo acoplamento.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista Envelope Elíptico herdando de 'ModeloBase'.
class AlgoritmoEnvelopeEliptico(ModeloBase):
    """Modelo paramétrico baseado em estimação robusta de covariância e Distância de
    Mahalanobis[cite: 1, 2].
    """

    # 'def construir_estimador' instancia o algoritmo configurado com semente
    # determinística[cite: 1].
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador EllipticEnvelope configurado[cite: 1].

        Args:
            semente_aleatoria (int): Semente para controlar a amostragem inicial do
            algoritmo FastMCD[cite: 1].

        Returns:
            EllipticEnvelope: Estimador robusto pronto para traçar a elipse de corte
            estatístico[cite: 1].
        """
        # 'contamination=0.05' assume preventivamente 5% de registros atípicos nos
        # dados[cite: 1].
        # 'random_state=semente_aleatoria' garante convergência idêntica nos sorteios de
        # subamostras do FastMCD[cite: 1].
        return EllipticEnvelope(contamination=0.05, random_state=semente_aleatoria)

    # 'def obter_grade_hiperparametros' expõe frações de suporte e taxas de
    # contaminação[cite: 1].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de busca exaustiva de hiperparâmetros para o
        EllipticEnvelope[cite: 1].

        Returns:
            Dict[str, list]: Dicionário com taxas de contaminação e frações de
            suporte[cite: 1].
        """
        # 'contamination': Percentual estipulado de contaminação por outliers no
        # conjunto[cite: 1].
        # 'support_fraction': Proporção de pontos incluídos para o cálculo da matriz de
        # covariância bruta[cite: 1].
        return {
            "contamination": [0.01, 0.05, 0.1, 0.15],
            "support_fraction": [None, 0.7, 0.85],
        }
