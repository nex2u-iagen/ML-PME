"""Script Executável de Homologação do Pilar 2 (Alinhamento de Negócio e Impacto
Financeiro).

Treina os 3 modelos finalistas do torneio (SVM, XGBoost e KNN) sobre o conjunto de
treino,
avalia as omissões e alarmes no teste retido e projeta o saldo líquido em reais (R$)
utilizando as classes desacopladas do Pilar 2 (ConfiguracaoCustoRisco e Orquestrador).
"""

# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo.
import logging

# 'from sklearn.datasets import make_classification' gera o problema de diagnóstico
# simulado[cite: 18].
from sklearn.datasets import make_classification

# 'from sklearn.model_selection import train_test_split' separa treino e teste cego
# retido[cite: 18, 20].
from sklearn.model_selection import train_test_split

# 'from sklearn.preprocessing import StandardScaler' padroniza os atributos preditores
# com base em Z-score[cite: 18].
from sklearn.preprocessing import StandardScaler

from scripts.bootstrap import configurar_ambiente
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_knn_classificador import (  # noqa: E501
    AlgoritmoKNN,
)

# Importa os 3 finalistas oficiais eleitos no torneio da Fase 4[cite: 26].
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_svm_classificador import (  # noqa: E501
    AlgoritmoSVM,
)
from src.etapas.fase_04_modelagem.fabrica_modelos.supervisionado.classificacao.alg_xgboost_classificador import (  # noqa: E501
    AlgoritmoXGBoost,
)

# Importa os componentes modulares do Pilar 2 recém-desacoplados[cite: 20].
from src.etapas.fase_05_avaliacao.pilar_02_alinhamento_negocio.configuracao_custos import (  # noqa: E501
    ConfiguracaoCustoRisco,
)
from src.etapas.fase_05_avaliacao.pilar_02_alinhamento_negocio.orquestrador_alinhamento_negocio import (  # noqa: E501
    OrquestradorAlinhamentoNegocio,
)

# Configura o layout das mensagens de log no console corporativo.
configurar_ambiente()

# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    logging.info(
        "=== INICIANDO SCRIPT DE HOMOLOGAÇÃO: PILAR 2 (IMPACTO FINANCEIRO) ===\n"
    )

    # 1. GERAÇÃO DOS DADOS DE SIMULAÇÃO (600 pacientes, 10 variáveis, 20% de risco).
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

    # 4. INSTANCIAÇÃO E TREINAMENTO DOS 3 FINALISTAS DO PÓDIO[cite: 26]
    logging.info("Treinando os 3 modelos concorrentes do pódio...")

    # 1º Lugar: SVM Calibrado[cite: 26]
    modelo_svm = AlgoritmoSVM().construir_estimador(semente_aleatoria=42)
    modelo_svm.fit(x_treino_escalado, y_treino)

    # 2º Lugar: XGBoost Classifier[cite: 26]
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

    # 5. EXECUÇÃO DO PILAR 2: SIMULAÇÃO FINANCEIRA VIA FACHADA MODULAR[cite: 20]
    # Instancia as premissas econômicas acordadas com a diretoria[cite: 20].
    contrato_custo = ConfiguracaoCustoRisco(
        custo_falso_negativo=12000.0,
        custo_falso_positivo=600.0,
        ganho_verdadeiro_positivo=4000.0,
        custo_verdadeiro_negativo=0.0,
    )

    # Instancia a fachada orquestradora injetando o contrato de custos ativo[cite: 20].
    orquestrador_negocio = OrquestradorAlinhamentoNegocio(
        configuracao_custos=contrato_custo
    )

    # Compila a tabela de impacto financeiro em reais sobre o conjunto de teste[cite:
    # 20].
    tabela_financeira = orquestrador_negocio.gerar_leaderboard_financeiro(
        catalogo_top3=catalogo_top3,
        matriz_atributos_teste=x_teste_escalado,
        vetor_alvo_teste=y_teste,
    )

    # 6. EXIBIÇÃO FORMATADA DO LEADERBOARD FINANCEIRO[cite: 20]
    print("\n" + "=" * 115)
    print("💼 LEADERBOARD FINANCEIRO E AVALIAÇÃO DE NEGLIGÊNCIA (TOP 3 - TESTE RETIDO)")
    print("=" * 115)

    formatadores = {
        "Prejuizo_Negligencia_R$": "R$ {:,.2f}".format,
        "Custo_Alarmes_R$": "R$ {:,.2f}".format,
        "Perda_Total_Erros_R$": "R$ {:,.2f}".format,
        "Valor_Preservado_R$": "R$ {:,.2f}".format,
        "Resultado_Liquido_R$": "R$ {:,.2f}".format,
    }
    tabela_exibicao = tabela_financeira.copy()
    for coluna, formata in formatadores.items():
        if coluna in tabela_exibicao.columns:
            tabela_exibicao[coluna] = tabela_exibicao[coluna].apply(formata)

    print(tabela_exibicao.to_string(index=False))
    print("=" * 115)

    campeao_financeiro = tabela_financeira.iloc[0]["Modelo"]
    saldo_campeao = tabela_financeira.iloc[0]["Resultado_Liquido_R$"]
    print("\n" + "💰" * 38)
    print(f"🥇 VENCEDOR PELO CRITÉRIO FINANCEIRO: {campeao_financeiro}")
    print(f"💵 Saldo Líquido Contábil Projetado: R$ {saldo_campeao:,.2f}")
    print("⚖️ Modelo com menor prejuízo acumulado de omissões (Falsos Negativos)!")
    print("💰" * 38 + "\n")

    logging.info("=== HOMOLOGAÇÃO DO PILAR 2 CONCLUÍDA COM SUCESSO! ===")
