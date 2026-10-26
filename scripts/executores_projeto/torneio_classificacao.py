"""Script de Execução do Torneio de Modelos de Classificação Supervisionada.

Carrega os especialistas da fábrica, gera uma massa sintética com desbalanceamento
de classes e executa a validação cruzada de 5 dobras para eleger o modelo campeão.
"""

# 'import logging' gerencia as notificações de auditoria técnica no console.
import logging

# 'import numpy as np' gera a massa sintética de dados tabulares supervisionados[cite:
# 5, 6].
# 'from sklearn.datasets' importa o gerador de problemas de classificação
# controlados[cite: 6].
from sklearn.datasets import make_classification

# 'from sklearn.preprocessing' importa o padronizador estatístico para os modelos
# espaciais[cite: 4, 9].
from sklearn.preprocessing import StandardScaler

from scripts.bootstrap import configurar_ambiente
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_adaboost_classificador import (  # noqa: E501
    AlgoritmoAdaBoost,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_arvore_decisao import (  # noqa: E501
    AlgoritmoArvoreDecisao,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_knn_classificador import (  # noqa: E501
    AlgoritmoKNN,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_lda_classificador import (  # noqa: E501
    AlgoritmoLDA,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_naive_bayes_classificador import (  # noqa: E501
    AlgoritmoNaiveBayes,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_qda_classificador import (  # noqa: E501
    AlgoritmoQDA,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_random_forest import (  # noqa: E501
    AlgoritmoRandomForest,
)

# Importa os especialistas em classificação da nossa fábrica de modelos[cite: 3, 6].
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_regressao_logistica import (  # noqa: E501
    AlgoritmoRegressaoLogistica,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_sgd_classificador import (  # noqa: E501
    AlgoritmoSGD,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_svm_classificador import (  # noqa: E501
    AlgoritmoSVM,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_xgboost_classificador import (  # noqa: E501
    AlgoritmoXGBoost,
)

# Importa o motor orquestrador de torneio[cite: 6].
from src.etapas.fase_04_modelagem.orquestrador_torneio_classificacao import (
    OrquestradorTorneioClassificacao,
)

# Configura o layout textual dos registros de auditoria no terminal.
configurar_ambiente()

# Bloco de execução principal do script.
if __name__ == "__main__":
    logging.info("=== INICIANDO ETAPA DE TORNEIO E SELEÇÃO DE MODELOS (FASE 4) ===\n")

    # 1. PREPARAÇÃO DOS DADOS DE SIMULAÇÃO (Cenário de Diagnóstico Clínico)
    # Criamos 600 pacientes com 10 atributos clínicos, sendo 20% da classe de risco
    # (desbalanceado)[cite: 6, 13].
    x_bruto, y_alvo = make_classification(
        n_samples=600,
        n_features=10,
        n_informative=7,
        n_redundant=3,
        weights=[0.80, 0.20],
        random_state=42,
    )

    # Padronização estatística: Z-score necessário para KNN, SVM, LDA e SGD convergirem
    # com rigor[cite: 1, 4, 9].
    escalador = StandardScaler()
    x_processado = escalador.fit_transform(x_bruto)

    # 2. ESCALAÇÃO DO CATÁLOGO DE COMPETIDORES DA FÁBRICA
    corpo_clinico_concorrentes = {
        "Regressao_Logistica": AlgoritmoRegressaoLogistica(),
        "Arvore_Decisao": AlgoritmoArvoreDecisao(),
        "Random_Forest": AlgoritmoRandomForest(),
        "KNN": AlgoritmoKNN(),
        "SVM": AlgoritmoSVM(),
        "XGBoost": AlgoritmoXGBoost(),
        "LDA": AlgoritmoLDA(),
        "Naive_Bayes": AlgoritmoNaiveBayes(),
        "QDA": AlgoritmoQDA(),
        "AdaBoost": AlgoritmoAdaBoost(),
        "SGD_Classifier": AlgoritmoSGD(),
    }

    # 3. EXECUÇÃO DO TORNEIO COM VALIDAÇÃO CRUZADA ESTRATIFICADA (5 DOBRAS)
    orquestrador = OrquestradorTorneioClassificacao(
        numero_particoes=5, semente_aleatoria=42
    )
    tabela_classificacao = orquestrador.executar_torneio(
        catalogo_modelos=corpo_clinico_concorrentes,
        matriz_atributos=x_processado,
        vetor_alvo=y_alvo,
    )

    # 4. EXIBIÇÃO DO LEADERBOARD OFICIAL DE DESEMPENHO
    print("\n" + "=" * 105)
    print("🏆 TABELA CLASSIFICATÓRIA OFICIAL DO TORNEIO (LEADERBOARD DE CLASSIFICAÇÃO)")
    print("=" * 105)

    # Formata a exibição do pandas com 4 casas decimais para rigor estatístico[cite: 5,
    # 6].
    formatadores = {
        "F1_Score_Medio": "{:.4f}".format,
        "F1_Score_Desvio": "±{:.4f}".format,
        "ROC_AUC_Medio": "{:.4f}".format,
        "Sensibilidade_Media": "{:.4f}".format,
        "Precisao_Media": "{:.4f}".format,
        "Acuracia_Media": "{:.4f}".format,
        "Tempo_Treino_Medio_Seg": "{:.4f}s".format,
    }

    for coluna, formatador in formatadores.items():
        if coluna in tabela_classificacao.columns:
            tabela_classificacao[coluna] = tabela_classificacao[coluna].apply(
                formatador
            )

    print(tabela_classificacao.to_string(index=False))
    print("=" * 105)

    modelo_campeao = tabela_classificacao.iloc[0]["Modelo"]
    f1_campeao = tabela_classificacao.iloc[0]["F1_Score_Medio"]
    logging.info(
        "Vencedor do Torneio: %s com F1-Score médio de %s!", modelo_campeao, f1_campeao
    )
    logging.info("=== TORNEIO CONCLUÍDO COM SUCESSO! MODELO CAMPEÃO IDENTIFICADO ===")
