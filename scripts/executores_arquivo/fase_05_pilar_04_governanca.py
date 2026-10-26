"""Script Executável de Homologação do Pilar 4 (Dossiê Executivo Limpo do Campeão).

Este script unifica o ciclo completo da Fase 5:
1. Executa a sabatina técnica do Top 3 (Pilar 1)[cite: 18, 20].
2. Executa a apuração da matriz de custo financeiro em reais (Pilar 2)[cite: 20].
3. Executa a explicabilidade com SHAP sobre o campeão (Pilar 3)[cite: 18, 20].
4. Orquestra a homologação oficial e gera o Dossiê Formal com evidências visuais
   limpas e exclusivas do modelo vencedor (Pilar 4)[cite: 17, 18, 20, 22].
"""

# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo.
import logging

# 'from sklearn.datasets import make_classification' gera o problema de diagnóstico
# simulado[cite: 18].
from sklearn.datasets import make_classification

# 'from sklearn.model_selection import train_test_split' separa treino e teste cego
# retido[cite: 18, 20].
from sklearn.model_selection import train_test_split

# 'from sklearn.pipeline import Pipeline' empacota escalador e estimador de forma
# reprodutível[cite: 17, 20].
from sklearn.pipeline import Pipeline

# 'from sklearn.preprocessing import StandardScaler' padroniza os atributos
# preditores[cite: 18].
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

# Importa as fachadas desacopladas dos 4 pilares da Fase 5[cite: 20].
from src.etapas.fase_05_avaliacao.pilar_01_podio_top3.orquestrador_podio_top3 import (
    OrquestradorPodioTop3,
)
from src.etapas.fase_05_avaliacao.pilar_02_alinhamento_negocio.orquestrador_alinhamento_negocio import (  # noqa: E501
    OrquestradorAlinhamentoNegocio,
)
from src.etapas.fase_05_avaliacao.pilar_03_explicabilidade_xai.orquestrador_explicabilidade import (  # noqa: E501
    OrquestradorExplicabilidadeShap,
)
from src.etapas.fase_05_avaliacao.pilar_04_governanca_homologacao.orquestrador_governanca import (  # noqa: E501
    OrquestradorGovernanca,
)

# Configura o layout das mensagens de log no console corporativo.
configurar_ambiente()

# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    logging.info("=== INICIANDO HOMOLOGAÇÃO COM DOSSIÊ LIMPO DO MODELO CAMPEÃO ===\n")

    # 1. GERAÇÃO DOS DADOS DE SIMULAÇÃO CLÍNICA (600 pacientes, 10 variáveis, 20% de
    # risco).
    x_bruto, y_alvo = make_classification(
        n_samples=600,
        n_features=10,
        n_informative=7,
        n_redundant=3,
        weights=[0.80, 0.20],
        random_state=42,
    )

    nomes_atributos_clinicos = [
        "Idade_Paciente",
        "Pressao_Sistolica",
        "Colesterol_Total",
        "Frequencia_Cardiaca",
        "Glicemia_Jejum",
        "Indice_Massa_Corporal",
        "Infradesnivel_ST",
        "Historico_Familiar",
        "Nivel_Sedentarismo",
        "Tempo_Internacao_Previo",
    ]

    # 2. SEPARAÇÃO DEFENSIVA ENTRE TREINO (80%) E TESTE RETIDO (20%)[cite: 20].
    x_treino, x_teste, y_treino, y_teste = train_test_split(
        x_bruto, y_alvo, test_size=0.20, stratify=y_alvo, random_state=42
    )

    # 3. PADRONIZAÇÃO E TREINAMENTO DOS FINALISTAS DO PÓDIO[cite: 18, 22]
    escalador = StandardScaler()
    x_treino_escalado = escalador.fit_transform(x_treino)
    x_teste_escalado = escalador.transform(x_teste)

    modelo_svm = AlgoritmoSVM().construir_estimador(semente_aleatoria=42)
    modelo_svm.fit(x_treino_escalado, y_treino)

    modelo_xgb = AlgoritmoXGBoost().construir_estimador(semente_aleatoria=42)
    modelo_xgb.fit(x_treino_escalado, y_treino)

    modelo_knn = AlgoritmoKNN().construir_estimador(semente_aleatoria=42)
    modelo_knn.fit(x_treino_escalado, y_treino)

    catalogo_top3 = {
        "SVM_Calibrado": modelo_svm,
        "XGBoost_Classifier": modelo_xgb,
        "KNN_Classifier": modelo_knn,
    }

    # 4. EXECUÇÃO INTEGRADA DOS PILARES 1, 2 E 3[cite: 18, 20]
    # Pilar 1: Scorecard Técnico do Top 3
    orq_pilar1 = OrquestradorPodioTop3(
        pasta_relatorios=RAIZ_PROJETO
        / "relatorios/figuras/fase_05_avaliacao/pilar_01_top3"
    )
    laudo_pilar1 = orq_pilar1.executar_auditoria_completa(
        catalogo_top3, x_teste_escalado, y_teste
    )

    # Pilar 2: Balancete Financeiro do Pódio
    orq_pilar2 = OrquestradorAlinhamentoNegocio()
    tabela_financeira = orq_pilar2.gerar_leaderboard_financeiro(
        catalogo_top3, x_teste_escalado, y_teste
    )

    # Pilar 3: Explicabilidade Forense com SHAP sobre o campeão (SVM)
    pipeline_campeao = Pipeline([("escalador", escalador), ("svm", modelo_svm)])

    def funcao_prob(dados):
        """Devolve a probabilidade contínua da classe positiva."""
        return pipeline_campeao.predict_proba(dados)[:, 1]

    orq_pilar3 = OrquestradorExplicabilidadeShap(
        pasta_relatorios=RAIZ_PROJETO
        / "relatorios/figuras/fase_05_avaliacao/pilar_03_xai",
        nomes_atributos=nomes_atributos_clinicos,
        quantidade_amostras_fundo=25,
        semente_aleatoria=42,
    )
    laudo_pilar3 = orq_pilar3.executar_auditoria_explicabilidade(
        funcao_prob, x_treino, x_teste[:30]
    )

    # 5. EXECUÇÃO DO PILAR 4: HOMOLOGAÇÃO COM TELEMETRIA VISUAL LIMPA DO CAMPEÃO[cite:
    # 18, 20, 22]
    pasta_governanca = RAIZ_PROJETO / "relatorios/governanca"
    orq_pilar4 = OrquestradorGovernanca(pasta_relatorios=pasta_governanca)

    dossie_final = orq_pilar4.gerar_dossie_executivo(
        scorecard_tecnico=laudo_pilar1["scorecard_tabular"],
        leaderboard_financeiro=tabela_financeira,
        laudo_explicabilidade=laudo_pilar3,
        estimador_campeao=modelo_svm,
        x_teste=x_teste_escalado,
        y_teste=y_teste,
        rotulos_classes=["Saudavel", "Risco"],
    )

    # 6. EXIBIÇÃO FORMATADA NO TERMINAL[cite: 20]
    parecer = dossie_final["parecer_homologacao"]
    print("\n" + "=" * 110)
    print(
        "📜 TERMO OFICIAL DE HOMOLOGAÇÃO EXECUTIVA — DOSSIÊ COM DADOS LIMPOS DO CAMPEÃO"
    )
    print("=" * 110)
    print(f"🎯 MODELO CERTIFICADO: {parecer['modelo_avaliado']}")
    print(f"⚖️ STATUS DA HOMOLOGAÇÃO: {parecer['status_homologacao']}")
    print(f"📝 PARECER PERICIAL: {parecer['parecer_executivo']}")
    print(
        f"📁 DOSSIÊ FÍSICO COM IMAGENS LIMPAS: {dossie_final['caminho_dossie_arquivo']}"
    )
    print("=" * 110 + "\n")

    logging.info("=== FASE 5 CONCLUÍDA! DOSSIÊ DO CAMPEÃO HOMOLOGADO COM SUCESSO ===")
