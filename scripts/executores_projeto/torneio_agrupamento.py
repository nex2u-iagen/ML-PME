"""Script de Execução e Homologação do Torneio de Agrupamento Não Supervisionado.

Este script executa o benchmarking comparativo entre os 5 especialistas da ala de
clustering,
aplica padronização estatística Z-score e avalia a qualidade geométrica das partições.
Ao final, extrai o modelo campeão com base no indicador principal (Coeficiente de
Silhueta)
e exibe um relatório consolidado com suas métricas complementares de suporte.
"""

# 'import logging' gerencia as mensagens de auditoria técnica exibidas no console do
import logging

# 'from sklearn.datasets import make_blobs' importa o gerador de grupos espaciais
# gaussianos sintéticos.
from sklearn.datasets import make_blobs

# 'from sklearn.preprocessing import StandardScaler' importa o padronizador estatístico
# para média zero e desvio unitário.
from sklearn.preprocessing import StandardScaler

from scripts.bootstrap import configurar_ambiente

# Importa o especialista em DBSCAN baseado em densidade espacial e filtragem automática
# de ruído (-1).
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.agrupamento.alg_dbscan_agrupamento import (  # noqa: E501
    AlgoritmoDBSCAN,
)

# Importa o especialista em GMM baseado em densidades de probabilidade e distribuições
# gaussianas elípticas.
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.agrupamento.alg_gmm_agrupamento import (  # noqa: E501
    AlgoritmoGMM,
)

# Importa o especialista em Agrupamento Hierárquico baseado em fusões ascendentes com
# critério de Ward.
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.agrupamento.alg_hierarquico_agrupamento import (  # noqa: E501
    AlgoritmoHierarquico,
)

# Importa o especialista em K-Means baseado em convergência de centroides e inércia
# intra-cluster.
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.agrupamento.alg_kmeans_agrupamento import (  # noqa: E501
    AlgoritmoKMeans,
)

# Importa o especialista em Mean Shift baseado em janelas deslizantes e localização de
# modas espaciais.
from src.etapas.fase_04_modelagem.fabrica_modelos.nao_supervisionado.agrupamento.alg_mean_shift_agrupamento import (  # noqa: E501
    AlgoritmoMeanShift,
)

# Importa o motor maestro de avaliação geométrica comparativa para modelos não
# supervisionados.
from src.etapas.fase_04_modelagem.orquestrador_agrupamento import (
    OrquestradorAgrupamento,
)

# Configura o layout das mensagens de log no console, incluindo horário, nível de
# criticidade e mensagem.
configurar_ambiente()

# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    # Registra no log o início do benchmarking da ala não supervisionada da fábrica de
    # modelos.
    logging.info("=== INICIANDO BENCHMARKING OFICIAL DE AGRUPAMENTO (FASE 4) ===\n")

    # 1. GERAÇÃO E PREPARAÇÃO DOS DADOS NÃO SUPERVISIONADOS
    # Gera 400 amostras sintéticas com 5 atributos preditores contínuos distribuídas em
    # 3 centros espaciais distintos.
    matriz_atributos_bruta, _ = make_blobs(
        n_samples=400, n_features=5, centers=3, cluster_std=1.2, random_state=42
    )

    # Instancia o padronizador estatístico Z-score para colocar todas as 5 variáveis na
    # mesma escala de dispersão.
    padronizador_zscore = StandardScaler()

    # Ajusta o padronizador calculando média e desvio padrão, gerando a matriz com média
    # 0 e variância 1.
    matriz_atributos_escalada = padronizador_zscore.fit_transform(
        matriz_atributos_bruta
    )

    # 2. ESCALAÇÃO DO CATÁLOGO DE COMPETIDORES NÃO SUPERVISIONADOS
    # Instancia os 5 algoritmos especialistas de agrupamento registrados na fábrica em
    # um catálogo padronizado.
    catalogo_competidores_agrupamento = {
        "KMeans": AlgoritmoKMeans(),
        "DBSCAN": AlgoritmoDBSCAN(),
        "Hierarquico": AlgoritmoHierarquico(),
        "GMM": AlgoritmoGMM(),
        "MeanShift": AlgoritmoMeanShift(),
    }

    # Calibra pontualmente o estimador KMeans para procurar exatamente k=3 agrupamentos
    # estruturais.
    catalogo_competidores_agrupamento["KMeans"].construir_estimador = (
        lambda semente_aleatoria=42: (
            AlgoritmoKMeans()
            .construir_estimador(semente_aleatoria)
            .set_params(n_clusters=3)
        )
    )

    # Calibra pontualmente o estimador Hierárquico para realizar o corte do dendrograma
    # em 3 partições.
    catalogo_competidores_agrupamento["Hierarquico"].construir_estimador = (
        lambda semente_aleatoria=42: (
            AlgoritmoHierarquico()
            .construir_estimador(semente_aleatoria)
            .set_params(n_clusters=3)
        )
    )

    # Calibra pontualmente o estimador GMM para ajustar uma mistura contendo 3
    # componentes gaussianas.
    catalogo_competidores_agrupamento["GMM"].construir_estimador = (
        lambda semente_aleatoria=42: (
            AlgoritmoGMM()
            .construir_estimador(semente_aleatoria)
            .set_params(n_components=3)
        )
    )

    # 3. EXECUÇÃO DO BENCHMARKING GEOMÉTRICO
    # Instancia o orquestrador de agrupamento passando a semente pseudoaleatória para
    # controle determinístico.
    orquestrador_clusters = OrquestradorAgrupamento(semente_aleatoria=42)

    # Executa os ajustes espaciais em todos os modelos e extrai o DataFrame com os
    # escores geométricos calculados.
    tabela_classificacao_clusters = orquestrador_clusters.executar_benchmarking(
        catalogo_modelos=catalogo_competidores_agrupamento,
        matriz_atributos=matriz_atributos_escalada,
    )

    # 4. EXTRAÇÃO DO CAMPEÃO E DO INDICADOR PRINCIPAL
    # O DataFrame retornado pelo orquestrador já vem ordenado decrescentemente pelo
    # Coeficiente de Silhueta.
    # Extrai o nome do algoritmo vencedor posicionado na linha de índice 0 do
    # Leaderboard.
    nome_agrupador_campeao = tabela_classificacao_clusters.iloc[0]["Modelo"]

    # Extrai a pontuação numérica exata do Coeficiente de Silhueta do modelo campeão
    # (indicador principal).
    valor_silhueta_campeao = float(
        tabela_classificacao_clusters.iloc[0]["Silhueta (Maior Melhor)"]
    )

    # Extrai o índice Davies-Bouldin do modelo campeão para avaliação de sobreposição de
    # fronteiras.
    valor_davies_bouldin_campeao = float(
        tabela_classificacao_clusters.iloc[0]["Davies_Bouldin (Menor Melhor)"]
    )

    # Extrai o critério Calinski-Harabasz do modelo campeão para avaliação da razão de
    # variância global.
    valor_calinski_campeao = float(
        tabela_classificacao_clusters.iloc[0]["Calinski_Harabasz (Maior Melhor)"]
    )

    # Extrai a quantidade inteira de grupos legítimos que o campeão formou nos dados.
    total_grupos_campeao = int(tabela_classificacao_clusters.iloc[0]["Grupos_Formados"])

    # 5. EXIBIÇÃO FORMATADA DO LEADERBOARD OFICIAL
    # Imprime uma linha horizontal de 115 caracteres para separação estética do bloco de
    # resultados.
    print("\n" + "=" * 115)
    # Imprime o título oficial da tabela classificatória de modelos de agrupamento.
    print("🏆 TABELA CLASSIFICATÓRIA OFICIAL DO TORNEIO (LEADERBOARD DE AGRUPAMENTO)")
    # Imprime a linha de fechamento do cabeçalho da tabela no console.
    print("=" * 115)

    # Cria uma cópia independente do DataFrame para fins de formatação de exibição
    # textual.
    tabela_formatada = tabela_classificacao_clusters.copy()

    # Define o dicionário de funções de formatação numérica com a precisão decimal
    # necessária para cada coluna.
    formatadores_exibicao = {
        "Silhueta (Maior Melhor)": "{:.4f}".format,
        "Davies_Bouldin (Menor Melhor)": "{:.4f}".format,
        "Calinski_Harabasz (Maior Melhor)": "{:.2f}".format,
        "Tempo_Treino_Seg": "{:.4f}s".format,
    }

    # Itera sobre cada coluna formatável aplicando as máscaras de casas decimais
    # correspondentes.
    for coluna, funcao_formatadora in formatadores_exibicao.items():
        # Verifica se o nome da coluna existe na tabela antes de invocar a formatação.
        if coluna in tabela_formatada.columns:
            # Aplica a função de conversão textual para cada registro contido na coluna
            # alvo.
            tabela_formatada[coluna] = tabela_formatada[coluna].apply(
                funcao_formatadora
            )

    # Imprime a tabela alinhada e estruturada sem exibir o índice padrão numérico do
    # pandas.
    print(tabela_formatada.to_string(index=False))
    # Imprime a linha inferior de fechamento da tabela visual.
    print("=" * 115)

    # 6. DECLARAÇÃO EXPLÍCITA DO CAMPEÃO E SEUS INDICADORES
    # Imprime o bloco de destaque informando as métricas do modelo vencedor.
    print("\n" + "⭐" * 5)
    # Exibe o nome do especialista que venceu o torneio de agrupamento.
    print(f"🏆 CAMPEÃO DO TORNEIO DE AGRUPAMENTO: {nome_agrupador_campeao}")
