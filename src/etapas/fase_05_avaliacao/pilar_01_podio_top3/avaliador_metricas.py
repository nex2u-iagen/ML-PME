"""Módulo Especialista em Cálculo de Métricas Técnicas e Latência (Pilar 1).

Responsabilidade Única: Executar inferências, computar métricas estatísticas
(F1-Score, Sensibilidade, Precisão, ROC-AUC, PR-AUC) e medir a latência
unitária por amostra em milissegundos para cada modelo do pódio.
"""

# 'from typing import ...' provê suporte a tipagem estática estrita para o design do
# pacote.
# 'import logging' gerencia as mensagens de auditoria técnica exibidas no console
# corporativo.
import logging

# 'import time' afere o tempo de resposta computacional com precisão de
# nanossegundos[cite: 18].
import time
from typing import Any

# 'import numpy as np' fornece manipulação de matrizes e funções sigmoides[cite: 17].
import numpy as np

# 'import pandas as pd' estrutura os resultados em DataFrames tabulares[cite: 18].
import pandas as pd

# 'from sklearn.metrics import ...' importa os cálculos de desempenho técnico[cite: 18,
# 20].
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


# 'class AvaliadorMetricasTabulares' isola unicamente as rotinas numéricas de
# avaliação[cite: 18, 20].
class AvaliadorMetricasTabulares:
    """Especialista responsável pela apuração de métricas estatísticas e latência de
    inferência[cite: 18].
    """

    # 'def comparar_modelos(...)' executa as inferências e tabula o scorecard técnico.
    def comparar_modelos(
        self,
        catalogo_top3: dict[str, Any],
        matriz_atributos_teste: np.ndarray,
        vetor_alvo_teste: np.ndarray,
    ) -> pd.DataFrame:
        """Calcula o scorecard de generalização e cronometra a latência média de
        inferência[cite: 18, 20].

        Args:
            catalogo_top3 (Dict[str, Any]): Dicionário com os 3 modelos
            concorrentes[cite: 20].
            matriz_atributos_teste (np.ndarray): Matriz X explicativa de teste
            retido[cite: 20].
            vetor_alvo_teste (np.ndarray): Vetor y com as classes reais de teste[cite:
            20].

        Returns:
            pd.DataFrame: Scorecard ordenado decrescentemente pelo F1-Score[cite: 20].
        """
        # Emite notificação no log de auditoria informando o início da compilação das
        # métricas.
        logging.info("Compilando scorecard técnico tabular para os 3 finalistas...")

        # Inicializa a lista que acumulará os registros analíticos de cada modelo
        # examinado.
        scorecard: list[dict[str, Any]] = []

        # Itera por cada modelo concorrente registrado no dicionário do pódio[cite: 20].
        for nome_modelo, estimador in catalogo_top3.items():
            # Marca a estampa de tempo inicial em alta precisão antes do lote de
            # inferência.
            tempo_inicio = time.perf_counter()

            # Gera as predições de classes discretas (0 ou 1) sobre todo o lote de
            # teste[cite: 18, 20].
            predicoes = estimador.predict(matriz_atributos_teste)

            # Calcula a latência unitária média dividindo o tempo total pela quantidade
            # de amostras[cite: 18].
            latencia_unitaria_ms = (
                (time.perf_counter() - tempo_inicio) / len(matriz_atributos_teste)
            ) * 1000.0

            # Extrai as probabilidades da classe de risco (classe positiva = 1)[cite:
            # 18].
            if hasattr(estimador, "predict_proba"):
                # Captura a segunda coluna que contém a probabilidade P(y = 1 | X)[cite:
                # 18].
                probabilidades = estimador.predict_proba(matriz_atributos_teste)[:, 1]
            else:
                # Caso use função de decisão, converte via sigmoide logística
                # padrão[cite: 18].
                probabilidades = 1.0 / (
                    1.0 + np.exp(-estimador.decision_function(matriz_atributos_teste))
                )

            # Consolida as métricas estatísticas essenciais no registro do modelo[cite:
            # 18, 20].
            scorecard.append(
                {
                    "Modelo": nome_modelo,
                    "F1_Score": float(
                        f1_score(vetor_alvo_teste, predicoes, zero_division=0)
                    ),
                    "Sensibilidade_Recall": float(
                        recall_score(vetor_alvo_teste, predicoes, zero_division=0)
                    ),
                    "Precisao": float(
                        precision_score(vetor_alvo_teste, predicoes, zero_division=0)
                    ),
                    "ROC_AUC": float(roc_auc_score(vetor_alvo_teste, probabilidades)),
                    "PR_AUC": float(
                        average_precision_score(vetor_alvo_teste, probabilidades)
                    ),
                    "Latencia_Unit_ms": latencia_unitaria_ms,
                }
            )

        # Retorna o DataFrame consolidado e ordenado pelo maior F1-Score[cite: 20].
        return (
            pd.DataFrame(scorecard)
            .sort_values(by="F1_Score", ascending=False)
            .reset_index(drop=True)
        )
