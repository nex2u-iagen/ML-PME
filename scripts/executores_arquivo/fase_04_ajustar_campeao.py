"""Script de Calibração e Serialização do Modelo Campeão (SVM).

Executa a separação entre treino e teste retido (Holdout), padroniza os dados sem
vazamento (Data Leakage), calibra o SVM via GridSearchCV, afere métricas de teste
e serializa o Pipeline final treinado via joblib para uso na Fase 5 e implantação.
"""

# 'import logging' gerencia as mensagens de auditoria técnica no console.
import logging

# 'import joblib' é a ferramenta padrão recomendada pelo Scikit-Learn para persistência
# de modelos[cite: 1].
import joblib

# 'import numpy as np' manipula as matrizes numéricas sintéticas[cite: 1].
# 'from sklearn.datasets' importa o gerador de problemas de classificação
# sintéticos[cite: 1].
from sklearn.datasets import make_classification

# 'from sklearn.metrics' importa as métricas finais de validação cega[cite: 1].
from sklearn.metrics import classification_report, roc_auc_score

# 'from sklearn.model_selection' importa a divisão segura entre treino e teste
# retido[cite: 1].
from sklearn.model_selection import train_test_split

# 'from sklearn.pipeline' importa a infraestrutura de encapsulamento atômico[cite: 1].
from sklearn.pipeline import Pipeline

# 'from sklearn.preprocessing' importa a padronização Z-score[cite: 1, 3].
from sklearn.preprocessing import StandardScaler

from scripts.bootstrap import RAIZ_PROJETO, configurar_ambiente

# Importa o especialista SVM da fábrica e o motor de otimização de parâmetros[cite: 1,
# 3].
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_svm_classificador import (  # noqa: E501
    AlgoritmoSVM,
)
from src.etapas.fase_04_modelagem.otimizador_hiperparametros import (
    OtimizadorHiperparametros,
)

# Configura o layout das mensagens de log no console.
configurar_ambiente()

# Bloco de execução principal do script.
if __name__ == "__main__":
    logging.info("=== INICIANDO AFINAÇÃO DO MODELO CAMPEÃO (SVM) ===\n")

    # 1. GERAÇÃO DA BASE DE DADOS (Mesmo cenário clínico do torneio: 600 pacientes, 10
    # atributos)[cite: 1].
    x_bruto, y_alvo = make_classification(
        n_samples=600,
        n_features=10,
        n_informative=7,
        n_redundant=3,
        weights=[0.80, 0.20],
        random_state=42,
    )

    # 2. DIVISÃO ESTRATIFICADA ENTRE TREINO (80%) E TESTE RETIDO / HOLDOUT (20%)[cite:
    # 1].
    # O conjunto de teste retido permanece intocado e blindado para avaliação final
    # imparcial[cite: 1].
    x_treino, x_teste, y_treino, y_teste = train_test_split(
        x_bruto, y_alvo, test_size=0.20, stratify=y_alvo, random_state=42
    )

    # 3. PADRONIZAÇÃO NUMÉRICA CONTROLADA CONTRA VAZAMENTO DE DADOS (DATA LEAKAGE)[cite:
    # 1].
    # O escalador aprende a média e o desvio padrão unicamente com o conjunto de
    # TREINO[cite: 1].
    escalador = StandardScaler()
    x_treino_escalado = escalador.fit_transform(x_treino)
    # Transforma o teste retido usando os parâmetros aprendidos no treino[cite: 1].
    x_teste_escalado = escalador.transform(x_teste)

    # 4. EXECUÇÃO DO AJUSTE FINO (GRID SEARCH CV NO CONJUNTO DE TREINO)[cite: 1]
    especialista_svm = AlgoritmoSVM()
    otimizador = OtimizadorHiperparametros(
        metrica_alvo="f1", numero_dobras=5, semente_aleatoria=42
    )

    estimador_calibrado, melhores_parametros, score_treino = (
        otimizador.calibrar_especialista(
            especialista=especialista_svm,
            matriz_atributos_treino=x_treino_escalado,
            vetor_alvo_treino=y_treino,
        )
    )

    # 5. AVALIAÇÃO CEGA NO CONJUNTO DE TESTE RETIDO (HOLDOUT SET)[cite: 1]
    logging.info(
        "\nAvaliando desempenho do modelo calibrado nos dados de teste não vistos..."
    )
    previsoes_teste = estimador_calibrado.predict(x_teste_escalado)
    probabilidades_teste = estimador_calibrado.predict_proba(x_teste_escalado)[:, 1]

    roc_auc_final = roc_auc_score(y_teste, probabilidades_teste)

    print("\n" + "=" * 70)
    print("📋 RELATÓRIO TÉCNICO DE CLASSIFICAÇÃO NO CONJUNTO DE TESTE RETIDO")
    print("=" * 70)
    print(
        classification_report(
            y_teste,
            previsoes_teste,
            target_names=["Classe_Negativa", "Classe_Positiva_Risco"],
        )
    )
    print(f"ROC-AUC no Teste Retido: {roc_auc_final:.4f}")
    print("=" * 70)

    # 6. EMPACOTAMENTO E SERIALIZAÇÃO DO PIPELINE COMPLETO (ARTEFATO PRODUZIDO)[cite: 1]
    # Encapsulamos o escalador ajustado e o estimador calibrado em um único Pipeline
    # reprodutível[cite: 1].
    pipeline_producao = Pipeline(
        [("escalador_padrao", escalador), ("classificador_svm", estimador_calibrado)]
    )

    # Cria o diretório de destino caso não exista.
    caminho_artefato = RAIZ_PROJETO / "artefatos/modelos"
    caminho_artefato.mkdir(parents=True, exist_ok=True)
    arquivo_modelo = caminho_artefato / "modelo_campeao_svm.joblib"

    # Salva o pipeline completo em arquivo serializado.
    joblib.dump(pipeline_producao, arquivo_modelo)
    logging.info("Artefato empacotado e salvo com sucesso em: %s", arquivo_modelo)
    logging.info(
        "=== FASE 4 (MODELAGEM) CONCLUÍDA COM SUCESSO! MODELO PRONTO PARA XAI ==="
    )
