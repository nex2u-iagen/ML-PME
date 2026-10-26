"""Orquestrador de Torneio de Modelos de Classificação Supervisionada (AutoML Baseline).

Este módulo gerencia a execução de torneios competitivos entre múltiplos estimadores
fornecidos pela fábrica de modelos. Ele implementa Validação Cruzada K-Fold
Estratificada
e calcula métricas essenciais (Acurácia, Precisão, Sensibilidade/Recall, F1-Score e
ROC-AUC).
"""

# 'from typing' fornece anotações de tipagem estática para parâmetros e retornos
# formais.

# 'import logging' gerencia as mensagens de auditoria técnica no console de modelagem.
import logging

# 'import numpy as np' fornece manipulação de matrizes e cálculos de desvio padrão[cite:
# 5].
import numpy as np

# 'import pandas as pd' estrutura os resultados em DataFrames para o Leaderboard
# final[cite: 5, 6].
import pandas as pd

# 'from sklearn.model_selection' importa o motor de validação cruzada e a partição
# estratificada.
from sklearn.model_selection import StratifiedKFold, cross_validate

# 'from src...' importa a interface contratual obrigatória da nossa arquitetura[cite:
# 4].
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class' define o maestro de treinamento comparativo da fábrica.
class OrquestradorTorneioClassificacao:
    """Motor de execução comparativa para ranquear modelos supervisionados sob as
    mesmas condições.
    """

    # 'def __init__' inicializa o orquestrador configurando o particionamento
    # estratificado.
    def __init__(self, numero_particoes: int = 5, semente_aleatoria: int = 42) -> None:
        """Configura a infraestrutura de validação cruzada do torneio.

        Args:
            numero_particoes (int): Quantidade de dobras (K) da validação cruzada[cite:
            6].
            semente_aleatoria (int): Semente para controlar o embaralhamento
            determinístico das dobras[cite: 6].
        """
        self.numero_particoes = numero_particoes
        self.semente_aleatoria = semente_aleatoria

        # 'StratifiedKFold' garante que a proporção da classe alvo (y) seja idêntica em
        # todas as dobras[cite: 6].
        self.validador_cruzado = StratifiedKFold(
            n_splits=self.numero_particoes,
            shuffle=True,
            random_state=self.semente_aleatoria,
        )

        # Dicionário de métricas técnicas padronizadas para classificação binária[cite:
        # 6, 12].
        self.metricas_avaliacao = {
            "acuracia": "accuracy",
            "precisao": "precision",
            "sensibilidade": "recall",
            "f1_score": "f1",
            "roc_auc": "roc_auc",
        }

    # 'def executar_torneio' itera pelos especialistas e extrai o desempenho médio de
    # cada competidor.
    def executar_torneio(
        self,
        catalogo_modelos: dict[str, ModeloBase],
        matriz_atributos: np.ndarray,
        vetor_alvo: np.ndarray,
    ) -> pd.DataFrame:
        """Executa a validação cruzada para cada modelo do catálogo e compila o
        Leaderboard[cite: 6].

        Args:
            catalogo_modelos (Dict[str, ModeloBase]): Dicionário com nomes e instâncias
            dos especialistas.
            matriz_atributos (np.ndarray): Matriz explicativa X (pré-processada)[cite:
            4, 6].
            vetor_alvo (np.ndarray): Vetor de gabarito supervisionado y[cite: 4, 6].

        Returns:
            pd.DataFrame: Tabela classificatória ordenada decrescentemente pelo F1-Score
            médio[cite: 6].
        """
        logging.info(
            "Iniciando Torneio com %d modelos concorrentes...", len(catalogo_modelos)
        )
        resultados_torneio: list[dict[str, float]] = []

        # Itera por cada especialista registrado na fábrica.
        for nome_modelo, especialista in catalogo_modelos.items():
            logging.info("Avaliando competidor: %s...", nome_modelo)

            # Instancia o estimador cru da biblioteca via contrato ModeloBase.
            estimador = especialista.construir_estimador(
                semente_aleatoria=self.semente_aleatoria
            )

            try:
                # 'cross_validate' roda o ciclo K-Fold completo de treino e teste em
                # cada dobra[cite: 6].
                resultados_cv = cross_validate(
                    estimator=estimador,
                    x=matriz_atributos,
                    y=vetor_alvo,
                    cv=self.validador_cruzado,
                    scoring=self.metricas_avaliacao,
                    n_jobs=-1,
                    return_train_score=False,
                )

                # Compila as médias e desvios das métricas avaliadas nas K dobras[cite:
                # 6, 12].
                resumo_competidor = {
                    "Modelo": nome_modelo,
                    "F1_Score_Medio": float(np.mean(resultados_cv["test_f1_score"])),
                    "F1_Score_Desvio": float(np.std(resultados_cv["test_f1_score"])),
                    "ROC_AUC_Medio": float(np.mean(resultados_cv["test_roc_auc"])),
                    "Sensibilidade_Media": float(
                        np.mean(resultados_cv["test_sensibilidade"])
                    ),
                    "Precisao_Media": float(np.mean(resultados_cv["test_precisao"])),
                    "Acuracia_Media": float(np.mean(resultados_cv["test_acuracia"])),
                    "Tempo_Treino_Medio_Seg": float(np.mean(resultados_cv["fit_time"])),
                }
                resultados_torneio.append(resumo_competidor)

            except Exception as erro_ajuste:
                logging.error("Falha ao avaliar %s: %s", nome_modelo, erro_ajuste)

        # Converte a lista de dicionários em DataFrame do pandas para análise
        # tabular[cite: 5, 6].
        tabela_classificacao = pd.DataFrame(resultados_torneio)

        # Ordena os concorrentes com foco no F1-Score médio (melhor equilíbrio entre
        # precisão e sensibilidade)[cite: 6].
        tabela_classificacao = tabela_classificacao.sort_values(
            by="F1_Score_Medio", ascending=False
        ).reset_index(drop=True)

        return tabela_classificacao
