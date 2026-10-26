"""Especialista em Florestas de Isolamento (Isolation Forest) para Detecção de
Anomalias.

Este módulo encapsula o estimador IsolationForest da biblioteca Scikit-Learn.
Ele assina o contrato 'ModeloBase' e isola anomalias diretamente através de partições
aleatórias em árvores, aproveitando o fato de que outliers exigem menos cortes para
serem isolados[cite: 2, 5].
"""

# 'from typing' provê suporte a tipagem estática formal para validar a interface da
# fábrica.
from typing import Any

# 'from sklearn.ensemble' importa o estimador de conjunto para detecção de
# anomalias[cite: 1, 2].
from sklearn.ensemble import IsolationForest

# 'from src...' importa a classe base abstrata para assegurar polimorfismo e baixo
# acoplamento.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' declara o especialista Isolation Forest herdando formalmente de 'ModeloBase'.
class AlgoritmoIsolationForest(ModeloBase):
    """Modelo ensemble que isola anomalias medindo a profundidade média das folhas
    terminais[cite: 2, 5].
    """

    # 'def construir_estimador' instancia a máquina matemática com parâmetros padrão
    # robustos.
    def construir_estimador(self, semente_aleatoria: int = 42) -> Any:
        """Instancia e devolve o estimador IsolationForest configurado em seu estado
        fundamental[cite: 1].

        Args:
            semente_aleatoria (int): Semente para determinar o sorteio das quebras nas
            árvores[cite: 5].

        Returns:
            IsolationForest: Estimador pronto para calibrar o escore de anomalia[cite:
            1].
        """
        # 'n_estimators=100' constrói uma floresta de 100 árvores de isolamento
        # independentes[cite: 1, 5].
        # 'contamination="auto"' permite que o limiar de decisão seja determinado
        # automaticamente[cite: 1].
        # 'n_jobs=-1' utiliza todos os núcleos de processamento para acelerar a
        # construção da floresta.
        # 'random_state=semente_aleatoria' garante reprodutibilidade idêntica em
        # execuções repetidas[cite: 5].
        return IsolationForest(
            n_estimators=100,
            contamination="auto",
            n_jobs=-1,
            random_state=semente_aleatoria,
        )

    # 'def obter_grade_hiperparametros' expõe intervalos de contaminação e
    # subamostragem[cite: 1].
    def obter_grade_hiperparametros(self) -> dict[str, list]:
        """Define a grade de hiperparâmetros de ajuste para exploração sistemática[cite:
        1].

        Returns:
            Dict[str, list]: Dicionário contendo taxas de contaminação e volumes de
            árvores[cite: 1].
        """
        # 'contamination': Proporção estimada de outliers presentes na base de dados
        # (ex.: 1% a 10%)[cite: 1].
        # 'max_samples': Proporção ou número de observações sorteadas para treinar cada
        # árvore individual[cite: 1, 5].
        # 'n_estimators': Volume de árvores de isolamento a serem agregadas[cite: 1, 5].
        return {
            "n_estimators": [50, 100, 200],
            "contamination": ["auto", 0.01, 0.05, 0.1],
            "max_samples": ["auto", 0.8, 1.0],
        }
