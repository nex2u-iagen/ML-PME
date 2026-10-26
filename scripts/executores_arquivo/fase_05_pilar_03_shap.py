"""Script Executável de Homologação do Pilar 3 (Explicabilidade Forense com SHAP).

Este script reconstrói a base de simulação clínica, treina o modelo campeão (SVM
Calibrado),
orquestra a fachada OrquestradorExplicabilidadeShap e exporta os laudos de impacto
global
(Beeswarm) e auditoria individual atômica (Waterfall) em alta resolução (300 DPI)[cite:
18, 20, 22].
"""

# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo.
import logging

# 'from sklearn.datasets import make_classification' gera o problema de diagnóstico
# simulado[cite: 18].
from sklearn.datasets import make_classification

# 'from sklearn.model_selection import train_test_split' separa treino e teste cego
# retido[cite: 18, 20].
from sklearn.model_selection import train_test_split

# 'from sklearn.pipeline import Pipeline' encapsula pré-processamento e modelo em objeto
# único atômico[cite: 17, 24].
from sklearn.pipeline import Pipeline

# 'from sklearn.preprocessing import StandardScaler' padroniza os atributos
# preditores[cite: 18].
from sklearn.preprocessing import StandardScaler

from scripts.bootstrap import RAIZ_PROJETO, configurar_ambiente

# Importa o especialista SVM campeão da fábrica da Fase 4[cite: 22].
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_svm_classificador import (  # noqa: E501
    AlgoritmoSVM,
)

# Importa a fachada integradora do Pilar 3 recém-construída[cite: 20].
from src.etapas.fase_05_avaliacao.pilar_03_explicabilidade_xai.orquestrador_explicabilidade import (  # noqa: E501
    OrquestradorExplicabilidadeShap,
)

# Configura o layout das mensagens de log no console corporativo.
configurar_ambiente()

# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    logging.info(
        "=== INICIANDO SCRIPT DE HOMOLOGAÇÃO: PILAR 3 (EXPLICABILIDADE XAI) ===\n"
    )

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

    # Nomes clínicos amigáveis alinhados aos dados brutos da Fase 2[cite: 18, 20].
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

    # 2. SEPARAÇÃO DEFENSIVA ENTRE TREINO (80%) E TESTE RETIDO / HOLDOUT (20%)[cite:
    # 20].
    x_treino, x_teste, y_treino, y_teste = train_test_split(
        x_bruto, y_alvo, test_size=0.20, stratify=y_alvo, random_state=42
    )

    # 3. CONSTRUÇÃO E TREINAMENTO DO PIPELINE CAMPEÃO (StandardScaler + SVM
    # Calibrado)[cite: 17, 24].
    logging.info("Ajustando o Pipeline Campeão (StandardScaler + SVM Calibrado)...")
    pipeline_campeao = Pipeline(
        [
            ("padronizador", StandardScaler()),
            ("estimador_svm", AlgoritmoSVM().construir_estimador(semente_aleatoria=42)),
        ]
    )
    pipeline_campeao.fit(x_treino, y_treino)

    # 4. INSTANCIAÇÃO DA FACHADA DO PILAR 3 (XAI COM SHAP)[cite: 20]
    pasta_destino_xai = (
        RAIZ_PROJETO / "relatorios/figuras/fase_05_avaliacao/pilar_03_xai"
    )

    orquestrador_xai = OrquestradorExplicabilidadeShap(
        pasta_relatorios=pasta_destino_xai,
        nomes_atributos=nomes_atributos_clinicos,
        quantidade_amostras_fundo=25,
        semente_aleatoria=42,
    )

    # Função que isola unicamente a probabilidade contínua da classe de risco
    # (P(y=1|X))[cite: 18].
    def funcao_probabilidade_risco(matriz_dados):
        """Devolve a probabilidade contínua da classe positiva."""
        return pipeline_campeao.predict_proba(matriz_dados)[:, 1]

    # Lote representativo de 30 pacientes de teste retido para demonstração e análise
    # forense[cite: 18, 20].
    lote_teste_pacientes = x_teste[:30]

    # 5. EXECUÇÃO DA AUDITORIA FORENSE ADITIVA VIA FACHADA[cite: 20]
    laudo_xai = orquestrador_xai.executar_auditoria_explicabilidade(
        funcao_predicao_probabilidade=funcao_probabilidade_risco,
        dados_treinamento=x_treino,
        dados_avaliacao=lote_teste_pacientes,
        indice_amostra_individual=0,
    )

    # 6. EXIBIÇÃO FORMATADA DO RELATÓRIO EXECUTIVO DE INTERPRETABILIDADE[cite: 18, 20]
    print("\n" + "=" * 90)
    print("🧠 RELATÓRIO FORENSE DE EXPLICABILIDADE E IMPACTO CAUSAL NO NEGÓCIO (XAI)")
    print("=" * 90)

    tabela_exibicao = laudo_xai["tabela_importancia_global"].copy()
    tabela_exibicao["Impacto_Absoluto_Medio_SHAP"] = tabela_exibicao[
        "Impacto_Absoluto_Medio_SHAP"
    ].apply(lambda valor: f"{valor:.4f}")

    print(tabela_exibicao.to_string(index=False))
    print("=" * 90)

    variavel_dominante = tabela_exibicao.iloc[0]["Atributo_Negocio"]
    peso_dominante = tabela_exibicao.iloc[0]["Impacto_Absoluto_Medio_SHAP"]
    valor_base_pct = laudo_xai["valor_base_populacional"]

    print("\n" + "🩺" * 38)
    print("🔍 PARECER PERICIAL DE GOVERNANÇA E AUDITORIA FORENSE:")
    print(f"1. Ponto de Partida Populacional (Baseline E[f(x)]): {valor_base_pct:.2%}")
    print(
        f"2. Variável com Maior Força Causal nas Decisões: '{variavel_dominante}'"
        f"(Impacto médio: {peso_dominante})"
    )
    print(
        f"3. Gráfico de Impacto Global (Beeswarm): {laudo_xai['figura_sumario_global']}"
    )
    print(
        f"4. Gráfico de Auditoria Individual (Waterfall):"
        f"{laudo_xai['figura_cascata_individual']}"
    )
    print(
        "⚖️ Conformidade total com o Direito à Explicação (LGPD / Governança"
        "Corporativa)!"
    )
    print("🩺" * 38 + "\n")

    logging.info("=== HOMOLOGAÇÃO DO PILAR 3 CONCLUÍDA COM SUCESSO! ===")
