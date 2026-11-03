"""Orquestrador de Avaliação e Benchmarking de Modelos de Agrupamento (Clustering).

Este componente avalia algoritmos não supervisionados através de métricas geométricas
intrínsecas, sem depender de gabaritos externos (y): Coeficiente de Silhueta,
Índice Davies-Bouldin e Índice Calinski-Harabasz (Critério da Razão de Variância).
"""

# 'from typing import ...' importa anotações de tipos estáticos para documentar a
# estrutura de retorno.
# 'import logging' importa o sistema de mensagens de auditoria técnica para o console.
import logging

# 'import time' importa a ferramenta de alta precisão para cronometrar a convergência
# dos agrupadores.
import time
from typing import Any

# 'import numpy as np' importa a biblioteca para indexação vetorial e filtragem de
# rótulos de ruído.
import numpy as np

# 'import pandas as pd' importa a manipulação tabular para construção do Leaderboard de
# Agrupamento.
import pandas as pd

# 'from sklearn.metrics import ...' importa os cálculos de coesão interna e
# separabilidade espacial.
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)

# 'from src...' importa o contrato universal da fábrica para preservar o polimorfismo
# arquitetural.
from src.etapas.fase_04_modelagem.fabrica_modelos.base_modelo import ModeloBase


# 'class OrquestradorAgrupamento' declara o maestro de avaliação para dados não
# rotulados.
class OrquestradorAgrupamento:
    """Motor de avaliação comparativa para algoritmos de agrupamento em dados não
    supervisionados.
    """

    # 'def __init__(...)' inicializa o orquestrador configurando a semente estocástica.
    def __init__(self, semente_aleatoria: int = 42) -> None:
        """Configura a semente para inicializações determinísticas dos centroides.

        Args:
            semente_aleatoria (int): Semente de aleatoriedade para algoritmos
            estocásticos (ex: K-Means).
        """
        # Armazena a semente de aleatoriedade na propriedade da instância para garantir
        # determinismo.
        self.semente_aleatoria = semente_aleatoria

    # 'def executar_benchmarking(...)' ajusta os agrupadores e extrai as métricas
    # geométricas espaciais.
    def executar_benchmarking(
        self, catalogo_modelos: dict[str, ModeloBase], matriz_atributos: np.ndarray
    ) -> pd.DataFrame:
        """Ajusta os agrupadores e extrai as métricas de coesão e dispersão espacial.

        Args:
            catalogo_modelos (Dict[str, ModeloBase]): Dicionário com os especialistas de
            agrupamento.
            matriz_atributos (np.ndarray): Matriz explicativa X padronizada sem
            variáveis-alvo (y).

        Returns:
            pd.DataFrame: Leaderboard de Agrupamento ranqueado pelo Coeficiente de
            Silhueta.
        """
        # Emite mensagem de log informando o início do benchmarking e a quantidade de
        # especialistas.
        logging.info(
            "Iniciando Benchmarking de Agrupamento com %d especialistas...",
            len(catalogo_modelos),
        )

        # Inicializa a lista vazia para armazenar as métricas de cada modelo avaliado.
        resultados_agrupamento: list[dict[str, Any]] = []

        # Itera por cada especialista registrado no catálogo de agrupamento.
        for nome_modelo, especialista in catalogo_modelos.items():
            # Informa no log qual especialista de clusterização está sob avaliação.
            logging.info("Avaliando agrupador: %s...", nome_modelo)

            # Instancia o estimador cru da biblioteca através do método padronizado da
            # fábrica.
            estimador = especialista.construir_estimador(
                semente_aleatoria=self.semente_aleatoria
            )

            # Registra a estampa de tempo de início em ponto flutuante de alta precisão.
            tempo_inicio = time.perf_counter()

            # Bloco de proteção contra agrupamentos vazios ou parâmetros inadequados ao
            # dataset.
            try:
                # Verifica se o estimador implementa o método unificado 'fit_predict'.
                if hasattr(estimador, "fit_predict"):
                    # Executa o ajuste espacial e extrai os rótulos de grupo atribuídos
                    # a cada observação.
                    rotulos = estimador.fit_predict(matriz_atributos)
                # Caso contrário (como no caso específico do GaussianMixture / GMM).
                else:
                    # Executa o ajuste de distribuição EM com 'fit'.
                    estimador.fit(matriz_atributos)
                    # Realiza a predição das gaussianas associadas via 'predict'.
                    rotulos = estimador.predict(matriz_atributos)

                # Calcula o tempo total decorrido subtraindo o tempo inicial da marcação
                # atual.
                tempo_processamento = time.perf_counter() - tempo_inicio

                # Identifica os índices dos pontos que NÃO são ruído (filtra o rótulo -1
                # do DBSCAN).
                indices_validos = np.where(rotulos != -1)[0]

                # Extrai apenas o subconjunto de rótulos válidos para cálculo das
                # métricas geométricas.
                rotulos_validos = rotulos[indices_validos]

                # Identifica a quantidade de grupos distintos formados descartando
                # rótulos repetidos.
                grupos_unicos = np.unique(rotulos_validos)

                # Armazena a contagem inteira de clusters legítimos formados.
                quantidade_grupos = len(grupos_unicos)

                # Se o algoritmo gerou menos de 2 grupos, métricas de separação não
                # podem ser computadas.
                if quantidade_grupos < 2:
                    # Emite um aviso de atenção no console informando a invalidação
                    # geométrica do modelo.
                    logging.warning(
                        "%s formou menos de 2 grupos válidos. Métricas invalidadas.",
                        nome_modelo,
                    )
                    # Pula para o próximo modelo do catálogo sem interromper o laço.
                    continue

                # Isola as coordenadas espaciais das amostras válidas excluindo os
                # pontos de ruído.
                x_validos = matriz_atributos[indices_validos]

                # Calcula a Silhueta: varia de -1 a +1; quanto maior, mais coeso é o
                # grupo e mais isolado do vizinho.
                score_silhueta = float(silhouette_score(x_validos, rotulos_validos))

                # Calcula o índice Davies-Bouldin: razão de similaridade; quanto mais
                # próximo de zero, melhor.
                score_davies_bouldin = float(
                    davies_bouldin_score(x_validos, rotulos_validos)
                )

                # Calcula o índice Calinski-Harabasz: razão de variância entre clusters;
                # quanto maior, melhor.
                score_calinski_harabasz = float(
                    calinski_harabasz_score(x_validos, rotulos_validos)
                )

                # Consolida as métricas intrínsecas e metadados no dicionário do
                # competidor.
                resumo_modelo = {
                    "Modelo": nome_modelo,
                    "Grupos_Formados": quantidade_grupos,
                    "Silhueta (Maior Melhor)": score_silhueta,
                    "Davies_Bouldin (Menor Melhor)": score_davies_bouldin,
                    "Calinski_Harabasz (Maior Melhor)": score_calinski_harabasz,
                    "Amostras_Ruido": int(np.sum(rotulos == -1)),
                    "Tempo_Treino_Seg": float(tempo_processamento),
                }

                # Adiciona o registro do agrupador à lista geral de resultados.
                resultados_agrupamento.append(resumo_modelo)

            # Caso ocorra alguma exceção matemática durante a convergência dos clusters.
            except Exception as erro_ajuste:
                # Registra o erro de forma explícita no log de auditoria técnica.
                logging.error(
                    "Falha ao avaliar agrupador %s: %s", nome_modelo, erro_ajuste
                )

        # Converte a lista consolidada em um DataFrame estruturado do pandas.
        tabela_classificacao = pd.DataFrame(resultados_agrupamento)

        # Verifica se o DataFrame contém dados antes de aplicar a ordenação.
        if not tabela_classificacao.empty:
            # Ordena os agrupadores pelo maior Coeficiente de Silhueta em ordem
            # decrescente.
            tabela_classificacao = tabela_classificacao.sort_values(
                by="Silhueta (Maior Melhor)", ascending=False
            ).reset_index(drop=True)

        # Retorna o Leaderboard de Agrupamento ordenado e formatado.
        return tabela_classificacao
