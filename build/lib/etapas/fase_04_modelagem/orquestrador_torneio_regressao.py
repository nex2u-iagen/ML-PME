"""Orquestrador de Torneio de Modelos de Regressão Supervisionada.

Este módulo orquestra competições automatizadas entre estimadores contínuos.
Ele aplica Validação Cruzada K-Fold padrão e mensura simultaneamente:
Coeficiente de Determinação (R²), Raiz do Erro Quadrático Médio (RMSE) e Erro Médio
Absoluto (MAE).
"""

# 'from typing import ...' importa os tipos estáticos para documentar as coleções
# tabulares.
# 'import logging' importa o sistema de rastreamento de operações técnicas no terminal.
import logging

# 'import numpy as np' importa a biblioteca para cálculos de média, desvio padrão e
# conversões numéricas.
import numpy as np

# 'import pandas as pd' importa a estrutura tabular para montagem e ordenação do
# Leaderboard final.
import pandas as pd

# 'from sklearn.model_selection import ...' importa o divisor de dobras contínuo e a
# validação cruzada.
from sklearn.model_selection import KFold, cross_validate

# 'from src...' importa o contrato universal ModeloBase para garantir polimorfismo
# arquitetural.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class OrquestradorTorneioRegressao' declara o maestro de competição para problemas
# contínuos.
class OrquestradorTorneioRegressao:
    """Motor de execução comparativa para ranquear regressores sob condições
    idênticas de teste.
    """

    # 'def __init__(...)' instancia o particionamento K-Fold e mapeia as métricas
    # numéricas.
    def __init__(self, numero_particoes: int = 5, semente_aleatoria: int = 42) -> None:
        """Inicializa a infraestrutura de validação cruzada contínua.

        Args:
            numero_particoes (int): Quantidade de dobras (K) da validação cruzada.
            semente_aleatoria (int): Semente de controle para o embaralhamento
            determinístico das amostras.
        """
        # Atribui a quantidade de partições (K) à propriedade da instância.
        self.numero_particoes = numero_particoes

        # Atribui a semente de controle estocástico para garantir reprodutibilidade
        # experimental.
        self.semente_aleatoria = semente_aleatoria

        # Instancia o KFold com shuffle=True para embaralhar os dados antes de dividir
        # as dobras.
        self.validador_cruzado = KFold(
            n_splits=self.numero_particoes,
            shuffle=True,
            random_state=self.semente_aleatoria,
        )

        # Mapeia as métricas do Scikit-Learn: erros utilizam strings com prefixo 'neg_'
        # para maximização.
        self.metricas_avaliacao = {
            "r2": "r2",
            "rmse_neg": "neg_root_mean_squared_error",
            "mae_neg": "neg_mean_absolute_error",
        }

    # 'def executar_torneio(...)' itera por cada competidor e compila a tabela
    # classificatória.
    def executar_torneio(
        self,
        catalogo_modelos: dict[str, ModeloBase],
        matriz_atributos: np.ndarray,
        vetor_alvo_continuo: np.ndarray,
    ) -> pd.DataFrame:
        """Executa a validação cruzada para o catálogo e devolve a tabela de
        classificação.

        Args:
            catalogo_modelos (Dict[str, ModeloBase]): Dicionário com nomes e instâncias
            dos regressores.
            matriz_atributos (np.ndarray): Matriz X explicativa contendo as variáveis
            preditoras numéricas.
            vetor_alvo_continuo (np.ndarray): Vetor y contendo os valores contínuos
            reais a serem estimados.

        Returns:
            pd.DataFrame: Leaderboard de Regressão ordenado decrescentemente pelo R²
            médio.
        """
        # Emite mensagem de log informando a quantidade total de regressores inscritos
        # no torneio.
        logging.info(
            "Iniciando Torneio de Regressão com %d competidores...",
            len(catalogo_modelos),
        )

        # Inicializa a lista vazia que acumulará o resumo numérico de cada competidor
        # avaliado.
        resultados_torneio: list[dict[str, float]] = []

        # Itera por cada par (nome_modelo, especialista) registrado no catálogo de
        # modelos.
        for nome_modelo, especialista in catalogo_modelos.items():
            # Informa no log qual algoritmo específico está sendo processado no momento.
            logging.info("Avaliando regressor: %s...", nome_modelo)

            # Constrói o estimador cru da biblioteca chamando o método formal da fábrica
            # polimórfica.
            estimador = especialista.construir_estimador(
                semente_aleatoria=self.semente_aleatoria
            )

            # Bloco de proteção contra erros pontuais de convergência matemática do
            # algoritmo.
            try:
                # Executa o cross_validate computando simultaneamente R², RMSE e MAE nas
                # K dobras.
                resultados_cv = cross_validate(
                    estimator=estimador,
                    x=matriz_atributos,
                    y=vetor_alvo_continuo,
                    cv=self.validador_cruzado,
                    scoring=self.metricas_avaliacao,
                    n_jobs=-1,
                    return_train_score=False,
                )

                # Inverte o sinal negativo do RMSE retornado pelo Scikit-Learn para
                # expressar a perda real.
                rmse_real = -resultados_cv["test_rmse_neg"]

                # Inverte o sinal negativo do MAE retornado pelo Scikit-Learn para
                # expressar a perda real.
                mae_real = -resultados_cv["test_mae_neg"]

                # Coleta as pontuações do Coeficiente de Determinação R² de cada dobra
                # de teste.
                r2_real = resultados_cv["test_r2"]

                # Estrutura o dicionário consolidado com as médias e desvios de
                # desempenho do modelo.
                resumo_competidor = {
                    "Modelo": nome_modelo,
                    "R2_Medio": float(np.mean(r2_real)),
                    "R2_Desvio": float(np.std(r2_real)),
                    "RMSE_Medio": float(np.mean(rmse_real)),
                    "MAE_Medio": float(np.mean(mae_real)),
                    "Tempo_Treino_Medio_Seg": float(np.mean(resultados_cv["fit_time"])),
                }

                # Adiciona o registro individual do competidor à lista de resultados do
                # torneio.
                resultados_torneio.append(resumo_competidor)

            # Caso ocorra alguma instabilidade matricial ou incompatibilidade de dados.
            except Exception as erro_ajuste:
                # Registra o erro de forma explícita sem interromper a avaliação dos
                # outros competidores.
                logging.error(
                    "Falha ao avaliar regressor %s: %s", nome_modelo, erro_ajuste
                )

        # Converte a lista de dicionários em um DataFrame do pandas para manipulação
        # tabular.
        tabela_classificacao = pd.DataFrame(resultados_torneio)

        # Ordena a tabela classificatória pelo R² médio em ordem decrescente (mais
        # próximo de 1.0 é melhor).
        tabela_classificacao = tabela_classificacao.sort_values(
            by="R2_Medio", ascending=False
        ).reset_index(drop=True)

        # Retorna o Leaderboard final consolidado e devidamente classificado.
        return tabela_classificacao
