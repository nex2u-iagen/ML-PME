"""Script de Execução do Torneio Oficial de Regressão Supervisionada.

Instancia os 10 especialistas da ala de regressão da fábrica, cria uma base sintética
de estimativa contínua e aplica validação cruzada K-Fold para ranquear o campeão
contínuo.
"""

# 'import logging' importa o sistema de registro de mensagens operacionais no console.
import logging

# 'import numpy as np' importa a biblioteca para criação e manipulação dos arrays
# sintéticos.
# 'from sklearn.datasets import make_regression' importa o gerador de problemas
# contínuos lineares.
from sklearn.datasets import make_regression

# 'from sklearn.preprocessing import StandardScaler' importa o padronizador estatístico
# Z-score.
from sklearn.preprocessing import StandardScaler

from scripts.bootstrap import configurar_ambiente

# Importa o especialista Árvore de Decisão para regressão não-linear da fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_arvore_regressao import (  # noqa: E501
    AlgoritmoArvoreRegressao,
)

# Importa o especialista ElasticNet combinando L1 e L2 da fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_elasticnet_regressao import (  # noqa: E501
    AlgoritmoElasticNet,
)

# Importa o especialista Huber Regressor blindado contra outliers da fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_huber_regressor import (  # noqa: E501
    AlgoritmoHuber,
)

# Importa o especialista Lasso com regularização linear absoluta L1 da fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_lasso_regressao import (  # noqa: E501
    AlgoritmoLasso,
)

# Importa o especialista Random Forest Regressor baseado em ensemble bagging da fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_random_forest_regressao import (  # noqa: E501
    AlgoritmoRandomForestRegressor,
)

# Importa o especialista Regressão Linear Simples/Múltipla (OLS) da fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_regressao_linear import (  # noqa: E501
    AlgoritmoRegressaoLinear,
)

# Importa o especialista Ridge com regularização quadrática L2 da fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_ridge_regressao import (  # noqa: E501
    AlgoritmoRidge,
)

# Importa o especialista SGD Regressor para aprendizado estocástico iterativo da
# fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_sgd_regressor import (  # noqa: E501
    AlgoritmoSGDRegressor,
)

# Importa o especialista SVR baseado em margem de erro épsilon e kernel da fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_svr_regressor import (  # noqa: E501
    AlgoritmoSVR,
)

# Importa o especialista XGBoost Regressor baseado em boosting sequencial da fábrica.
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.regressao.alg_xgboost_regressao import (  # noqa: E501
    AlgoritmoXGBoostRegressor,
)

# Importa a classe do orquestrador de competição de modelos de regressão.
from src.etapas.fase_04_modelagem.orquestrador_torneio_regressao import (
    OrquestradorTorneioRegressao,
)

# Configura o layout das mensagens de log no console.
configurar_ambiente()

# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    # Registra no log o início oficial da execução do torneio de regressão.
    logging.info("=== INICIANDO TORNEIO OFICIAL DE REGRESSÃO (FASE 4) ===\n")

    # 1. GERAÇÃO DOS DADOS SINTÉTICOS DE REGRESSÃO
    # Gera 500 amostras com 10 atributos preditores numéricos contínuos e ruído
    # gaussiano controlado.
    matriz_bruta, vetor_alvo_continuo = make_regression(
        n_samples=500, n_features=10, n_informative=6, noise=15.0, random_state=42
    )

    # Instancia o padronizador para transformar as variáveis para média 0 e desvio
    # padrão 1.
    escalador = StandardScaler()

    # Ajusta o escalador e transforma a matriz de atributos de entrada.
    matriz_escalada = escalador.fit_transform(matriz_bruta)

    # 2. CATÁLOGO DOS 10 COMPETIDORES DE REGRESSÃO
    # Registra os 10 especialistas da ala de regressão em um dicionário estruturado.
    concorrentes_regressao = {
        "Regressao_Linear_OLS": AlgoritmoRegressaoLinear(),
        "Ridge_L2": AlgoritmoRidge(),
        "Lasso_L1": AlgoritmoLasso(),
        "ElasticNet": AlgoritmoElasticNet(),
        "SGD_Regressor": AlgoritmoSGDRegressor(),
        "Huber_Regressor": AlgoritmoHuber(),
        "Arvore_Decisao_Reg": AlgoritmoArvoreRegressao(),
        "Random_Forest_Reg": AlgoritmoRandomForestRegressor(),
        "SVR": AlgoritmoSVR(),
        "XGBoost_Reg": AlgoritmoXGBoostRegressor(),
    }

    # 3. EXECUÇÃO DO TORNEIO VIA VALIDAÇÃO K-FOLD
    # Instancia o orquestrador configurado com 5 dobras de validação contínua.
    orquestrador = OrquestradorTorneioRegressao(
        numero_particoes=5, semente_aleatoria=42
    )

    # Dispara a avaliação comparativa para todos os 10 algoritmos de regressão.
    tabela_leaderboard = orquestrador.executar_torneio(
        catalogo_modelos=concorrentes_regressao,
        matriz_atributos=matriz_escalada,
        vetor_alvo_continuo=vetor_alvo_continuo,
    )

    # 4. EXIBIÇÃO FORMATADA DO LEADERBOARD OFICIAL
    # Imprime linha separadora visual no console.
    print("\n" + "=" * 95)
    # Imprime o cabeçalho do pódio oficial de regressão.
    print("🏆 TABELA CLASSIFICATÓRIA OFICIAL DO TORNEIO (LEADERBOARD DE REGRESSÃO)")
    # Imprime linha separadora visual no console.
    print("=" * 95)

    # Define o dicionário de formatação com 4 casas decimais para cada coluna numérica.
    formatadores = {
        "R2_Medio": "{:.4f}".format,
        "R2_Desvio": "±{:.4f}".format,
        "RMSE_Medio": "{:.4f}".format,
        "MAE_Medio": "{:.4f}".format,
        "Tempo_Treino_Medio_Seg": "{:.4f}s".format,
    }

    # Itera por cada coluna formatando as saídas numéricas do DataFrame.
    for coluna, formata in formatadores.items():
        # Verifica se a coluna está presente na tabela de resultados antes de formatar.
        if coluna in tabela_leaderboard.columns:
            # Aplica a função de formatação textual em todos os registros da coluna.
            tabela_leaderboard[coluna] = tabela_leaderboard[coluna].apply(formata)

    # Imprime a tabela completa alinhada sem a coluna de índice do pandas.
    print(tabela_leaderboard.to_string(index=False))
    # Imprime linha de fechamento visual no console.
    print("=" * 95)

    # Extrai o nome do algoritmo vencedor na primeira linha da tabela classificada.
    campeao = tabela_leaderboard.iloc[0]["Modelo"]
    # Extrai o Coeficiente de Determinação R² alcançado pelo campeão.
    r2_campeao = tabela_leaderboard.iloc[0]["R2_Medio"]
    # Registra no log o anúncio oficial do modelo campeão contínuo.
    logging.info(
        "Regressão finalizada com sucesso! Campeão: %s com R² de %s",
        campeao,
        r2_campeao,
    )
