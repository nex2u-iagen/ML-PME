"""Script Executável de Homologação do Pilar 1 (Auditoria Comparativa do Top 3).

Reconstrói a base de simulação clínica, aplica a padronização defensiva,
instancia os 3 finalistas oficiais eleitos na Fase 4 (SVM, XGBoost e KNN) e orquestra
o OrquestradorPodioTop3 para gerar o scorecard tabular e os gráficos comparativos em 300
DPI[cite: 18, 20, 22].
"""

# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo.
import logging

# 'from sklearn.datasets import make_classification' gera o problema de diagnóstico
# clínico simulado[cite: 18].
from sklearn.datasets import make_classification

# 'from sklearn.model_selection import train_test_split' separa os dados em treino e
# teste retido[cite: 18, 20].
from sklearn.model_selection import train_test_split

# 'from sklearn.preprocessing import StandardScaler' padroniza os atributos preditores
# com base em Z-score[cite: 18].
from sklearn.preprocessing import StandardScaler

from scripts.bootstrap import RAIZ_PROJETO, configurar_ambiente
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_knn_classificador import (  # noqa: E501
    AlgoritmoKNN,
)

# Importa os 3 finalistas oficiais eleitos no torneio da Fase 4[cite: 22].
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_svm_classificador import (  # noqa: E501
    AlgoritmoSVM,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_xgboost_classificador import (  # noqa: E501
    AlgoritmoXGBoost,
)

# Importa a fachada integradora do Pilar 1 da pasta oficial 'fase_05_avaliacao'[cite:
# 20].
from src.etapas.fase_05_avaliacao.pilar_01_podio_top3.orquestrador_podio_top3 import (
    OrquestradorPodioTop3,
)

# Configura o layout das mensagens de log no console corporativo.
configurar_ambiente()

# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    logging.info("=== INICIANDO SCRIPT DE HOMOLOGAÇÃO: PILAR 1 (AVALIAÇÃO TOP 3) ===\n")

    # 1. GERAÇÃO DOS DADOS SINTÉTICOS DE DIAGNÓSTICO CLÍNICO (600 pacientes, 10
    # variáveis, 20% de risco).
    x_bruto, y_alvo = make_classification(
        n_samples=600,
        n_features=10,
        n_informative=7,
        n_redundant=3,
        weights=[0.80, 0.20],
        random_state=42,
    )

    # 2. SEPARAÇÃO DEFENSIVA ENTRE TREINO (80%) E TESTE RETIDO / HOLDOUT (20%)[cite:
    # 20].
    x_treino, x_teste, y_treino, y_teste = train_test_split(
        x_bruto, y_alvo, test_size=0.20, stratify=y_alvo, random_state=42
    )

    # 3. PADRONIZAÇÃO ESTATÍSTICA CONTROLADA (Fit apenas no treino, transform no
    # teste)[cite: 18].
    escalador = StandardScaler()
    x_treino_escalado = escalador.fit_transform(x_treino)
    x_teste_escalado = escalador.transform(x_teste)

    # 4. INSTANCIAÇÃO E TREINAMENTO DOS 3 FINALISTAS DO TORNEIO DA FASE 4[cite: 22]
    logging.info(
        "Ajustando os 3 modelos concorrentes do pódio sobre a base de treino..."
    )

    # 1º Lugar: SVM Calibrado[cite: 22]
    modelo_svm = AlgoritmoSVM().construir_estimador(semente_aleatoria=42)
    modelo_svm.fit(x_treino_escalado, y_treino)

    # 2º Lugar: XGBoost Classifier[cite: 22]
    modelo_xgb = AlgoritmoXGBoost().construir_estimador(semente_aleatoria=42)
    modelo_xgb.fit(x_treino_escalado, y_treino)

    # 3º Lugar: KNN Classifier[cite: 20]
    modelo_knn = AlgoritmoKNN().construir_estimador(semente_aleatoria=42)
    modelo_knn.fit(x_treino_escalado, y_treino)

    catalogo_top3 = {
        "SVM_Calibrado": modelo_svm,
        "XGBoost_Classifier": modelo_xgb,
        "KNN_Classifier": modelo_knn,
    }

    # 5. EXECUÇÃO DA SABATINA COMPARATIVA DO PILAR 1 VIA FACHADA[cite: 20]
    pasta_destino_figuras = (
        RAIZ_PROJETO / "relatorios/figuras/fase_05_avaliacao/pilar_01_top3"
    )
    orquestrador_pilar1 = OrquestradorPodioTop3(pasta_relatorios=pasta_destino_figuras)

    # Dispara a sabatina completa unindo métricas escalares e as 3 figuras de 300
    # DPI[cite: 20].
    laudo_final = orquestrador_pilar1.executar_auditoria_completa(
        catalogo_top3=catalogo_top3,
        matriz_atributos_teste=x_teste_escalado,
        vetor_alvo_teste=y_teste,
        rotulos_classes=["Saudavel", "Risco"],
    )

    # 6. EXIBIÇÃO FORMATADA DO SCORECARD EXECUTIVO[cite: 20]
    print("\n" + "=" * 105)
    print("🏆 SCORECARD TÉCNICO COMPARATIVO DO PÓDIO (TOP 3 - TESTE RETIDO)")
    print("=" * 105)

    tabela_scorecard = laudo_final["scorecard_tabular"].copy()
    formatadores = {
        "F1_Score": "{:.4f}".format,
        "Sensibilidade_Recall": "{:.4f}".format,
        "Precisao": "{:.4f}".format,
        "ROC_AUC": "{:.4f}".format,
        "PR_AUC": "{:.4f}".format,
        "Latencia_Unit_ms": "{:.4f} ms".format,
    }
    for coluna, formata in formatadores.items():
        if coluna in tabela_scorecard.columns:
            tabela_scorecard[coluna] = tabela_scorecard[coluna].apply(formata)

    print(tabela_scorecard.to_string(index=False))
    print("=" * 105)

    print("\n" + "📊" * 38)
    print("🖼️ ARTEFATOS VISUAIS EXPORTADOS EM 300 DPI:")
    print(f"1. Matrizes de Confusão: {laudo_final['figura_matrizes_confusao']}")
    print(f"2. Curvas ROC Sobrepostas: {laudo_final['figura_curvas_roc']}")
    print(f"3. Curvas Precision-Recall: {laudo_final['figura_curvas_pr']}")
    print("📊" * 38 + "\n")

    logging.info("=== HOMOLOGAÇÃO DO PILAR 1 CONCLUÍDA COM SUCESSO! ===")
