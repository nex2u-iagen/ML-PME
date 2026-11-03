"""Script Executor Oficial da Fase 05 do CRISP-DM: Avaliação e Governança do Pódio Top 3.

Responsabilidade Única: Ponto de entrada CLI que carrega o catálogo dos 3 melhores
modelos da Fase 4 e a base de teste cego da Fase 3, orquestrando em sequência:
1. Pilar 1: Pódio Técnico e Latência (Compara os 3 modelos e gera 3 figuras comparativas)[cite: 9].
2. Pilar 2: Alinhamento de Negócio (Calcula o retorno financeiro em R$ do Top 3)[cite: 9].
3. Pilar 3: Explicabilidade Forense SHAP (Abre a caixa-preta do modelo campeão)[cite: 9, 10].
4. Pilar 4: Governança, Regras de Aceite, Figuras Solo e Dossiê Markdown Executivo[cite: 9].
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registros profissionais no terminal[cite: 8].
import logging

# 'from' acessa a biblioteca nativa 'pathlib'; 'import' traz 'Path' para manipulação segura de diretórios[cite: 8].
from pathlib import Path

# 'import' traz o módulo 'sys' nativo para manipulação e garantia do caminho de busca de módulos no interpretador[cite: 8].
import sys

# RESOLUÇÃO CANÔNICA DA RAIZ DO REPOSITÓRIO:
DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent.parent
if str(DIRETORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_RAIZ))

# 'import' traz a biblioteca externa 'joblib' para desserializar o catálogo dos modelos finalistas.
import joblib

# 'import' traz a biblioteca externa 'numpy' para manipulação matemática de tensores.
import numpy as np

# 'import' traz a biblioteca externa 'pandas' para manipulação tabular[cite: 8, 12].
import pandas as pd

# IMPORTAÇÃO DAS FACHADAS OFICIAIS DOS 4 PILARES DA FASE 5[cite: 9]:
from src.etapas.fase_05_avaliacao.pilar_01_podio_top3.orquestrador_podio_top3 import (
    OrquestradorPodioTop3,
)
from src.etapas.fase_05_avaliacao.pilar_02_alinhamento_negocio.configuracao_custos import (
    ConfiguracaoCustoRisco,
)
from src.etapas.fase_05_avaliacao.pilar_02_alinhamento_negocio.orquestrador_alinhamento_negocio import (
    OrquestradorAlinhamentoNegocio,
)
from src.etapas.fase_05_avaliacao.pilar_03_explicabilidade_xai.orquestrador_explicabilidade import (
    OrquestradorExplicabilidadeShap,
)
from src.etapas.fase_05_avaliacao.pilar_04_governanca_homologacao.orquestrador_governanca import (
    OrquestradorGovernanca,
)

# Garantir logs em tempo real no terminal (sem bufferização do Python)
import sys
import os
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
os.environ['PYTHONUNBUFFERED'] = '1'

# 'logging.basicConfig' parametriza a formatação dos registros operacionais no terminal[cite: 8].
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
    stream=sys.stdout,
)


def main() -> None:
    """Função executiva que orquestra a sabatina dos 3 finalistas através dos 4 Pilares da Fase 5[cite: 9]."""
    print("\n" + "=" * 105)
    print("🚀 INICIANDO FASE 05: AVALIAÇÃO, CUSTO, EXPLICABILIDADE E GOVERNANÇA DO PÓDIO TOP 3")
    print("=" * 105 + "\n")

    # Identificação do cliente e configuração das pastas físicas de governança[cite: 8]:
    nome_cliente = "mercado_vencedor"
    pasta_ml = DIRETORIO_RAIZ / "dados" / "processados" / nome_cliente / "ml"
    pasta_modelos = DIRETORIO_RAIZ / "modelos" / nome_cliente

    # Subpastas dedicadas em 'relatorios/<cliente>/' para organização profissional[cite: 8, 9]:
    pasta_relatorios_fase5 = DIRETORIO_RAIZ / "relatorios" / nome_cliente / "fase_05_avaliacao"
    pasta_relatorios_p1 = pasta_relatorios_fase5 / "pilar_01_top3"
    pasta_relatorios_p3 = pasta_relatorios_fase5 / "pilar_03_xai"
    pasta_governanca = DIRETORIO_RAIZ / "relatorios" / nome_cliente / "governanca"

    # Rotas dos arquivos persistidos nas etapas anteriores[cite: 9, 12]:
    caminho_top3 = pasta_modelos / "catalogo_top3_modelos.joblib"
    caminho_treino = pasta_ml / "treino_processado.parquet"
    caminho_teste = pasta_ml / "teste_processado.parquet"

    # Verificação defensiva de existência física dos artefatos[cite: 9, 12]:
    if not caminho_top3.is_file():
        logging.error("Catálogo Top 3 não encontrado! Execute primeiro 'executar_fase_04_modelagem.py'.")
        sys.exit(1)

    logging.info("Carregando catálogo dos 3 finalistas e matrizes de teste cego...")
    catalogo_top3 = joblib.load(caminho_top3)
    df_treino = pd.read_parquet(caminho_treino)
    df_teste = pd.read_parquet(caminho_teste)

    coluna_alvo = "alvo_inadimplente"
    X_treino_df = df_treino.drop(columns=[coluna_alvo])
    X_teste_df = df_teste.drop(columns=[coluna_alvo])
    y_teste = df_teste[coluna_alvo].to_numpy()

    # Nomes descritivos das variáveis explicativas[cite: 8, 9]:
    nomes_features = list(X_teste_df.columns)

    logging.info(
        "Ambiente de teste montado: %d amostras de teste cego retido e %d features.",
        len(X_teste_df),
        len(nomes_features),
    )

    # ---------------------------------------------------------------------------------------------
    # PILAR 1: PÓDIO TÉCNICO E LATÊNCIA (Compara os 3 finalistas preservando nomes de atributos)[cite: 9]
    # ---------------------------------------------------------------------------------------------
    logging.info("--- [PILAR 1/4] AUDITORIA TÉCNICA E LATÊNCIA DO TOP 3 ---")
    orquestrador_p1 = OrquestradorPodioTop3(pasta_relatorios=pasta_relatorios_p1)
    laudo_p1 = orquestrador_p1.executar_auditoria_completa(
        catalogo_top3=catalogo_top3,
        matriz_atributos_teste=X_teste_df,  # Passa como DataFrame para não emitir UserWarning[cite: 9, 10]!
        vetor_alvo_teste=y_teste,
        rotulos_classes=["Em Dia", "Inadimplente"],
    )
    scorecard_tecnico = laudo_p1["scorecard_tabular"]

    # ---------------------------------------------------------------------------------------------
    # PILAR 2: ALINHAMENTO DE NEGÓCIO E IMPACTO FINANCEIRO (Leaderboard em Reais)[cite: 9]
    # ---------------------------------------------------------------------------------------------
    logging.info("--- [PILAR 2/4] AVALIAÇÃO ECONÔMICA E MATRIZ DE CUSTOS EM REAIS ---")
    config_custos = ConfiguracaoCustoRisco.perfil_conservador_saude_fraude()
    orquestrador_p2 = OrquestradorAlinhamentoNegocio(configuracao_custos=config_custos)
    leaderboard_financeiro = orquestrador_p2.gerar_leaderboard_financeiro(
        catalogo_top3=catalogo_top3,
        matriz_atributos_teste=X_teste_df,
        vetor_alvo_teste=y_teste,
    )

    # ---------------------------------------------------------------------------------------------
    # IDENTIFICAÇÃO DO MODELO CAMPEÃO DO PÓDIO:
    # ---------------------------------------------------------------------------------------------
    nome_campeao = str(scorecard_tecnico.iloc[0]["Modelo"])
    estimador_campeao = catalogo_top3[nome_campeao]
    logging.info("Modelo Vencedor do Pódio identificado: '%s'.", nome_campeao)

    # ---------------------------------------------------------------------------------------------
    # PILAR 3: EXPLICABILIDADE FORENSE (XAI COM SHAP SOBRE O CAMPEÃO)[cite: 9, 10]
    # ---------------------------------------------------------------------------------------------
    logging.info("--- [PILAR 3/4] ABERTURA DA CAIXA-PRETA DO CAMPEÃO COM SHAP ---")
    orquestrador_p3 = OrquestradorExplicabilidadeShap(
        pasta_relatorios=pasta_relatorios_p3,
        nomes_atributos=nomes_features,
        quantidade_amostras_fundo=30,
        semente_aleatoria=42,
    )

    # Função de probabilidade direcionada para a classe positiva (risco = 1)[cite: 9]:
    def funcao_probabilidade_campeao(X_lote: np.ndarray) -> np.ndarray:
        # Reconverte temporariamente para DataFrame com os nomes originais para alimentar o estimador[cite: 9, 10]:
        df_lote = pd.DataFrame(X_lote, columns=nomes_features)
        if hasattr(estimador_campeao, "predict_proba"):
            return estimador_campeao.predict_proba(df_lote)[:, 1]
        decision = estimador_campeao.decision_function(df_lote)
        return 1.0 / (1.0 + np.exp(-decision))

    # OTIMIZAÇÃO COMPUTACIONAL: Amostra representativa para cálculo ágil do KernelExplainer[cite: 9]:
    X_treino_np = X_treino_df.to_numpy()
    X_avaliacao_shap = X_teste_df.iloc[:50].to_numpy()

    laudo_p3 = orquestrador_p3.executar_auditoria_explicabilidade(
        funcao_predicao_probabilidade=funcao_probabilidade_campeao,
        dados_treinamento=X_treino_np,
        dados_avaliacao=X_avaliacao_shap,
        indice_amostra_individual=0,
    )

    # ---------------------------------------------------------------------------------------------
    # PILAR 4: GOVERNANÇA, REGRAS DE ACEITE E DOSSIÊ EXECUTIVO DE HOMOLOGAÇÃO[cite: 9]
    # ---------------------------------------------------------------------------------------------
    logging.info("--- [PILAR 4/4] CRITÉRIOS DE ACEITE E EMISSÃO DO DOSSIÊ DE HOMOLOGAÇÃO ---")
    orquestrador_p4 = OrquestradorGovernanca(pasta_relatorios=pasta_governanca)
    laudo_p4 = orquestrador_p4.gerar_dossie_executivo(
        scorecard_tecnico=scorecard_tecnico,
        leaderboard_financeiro=leaderboard_financeiro,
        laudo_explicabilidade=laudo_p3,
        estimador_campeao=estimador_campeao,
        x_teste=X_teste_df,  # Passa o DataFrame com colunas para as figuras limpas solo[cite: 9, 10]!
        y_teste=y_teste,
        rotulos_classes=["Em Dia", "Inadimplente"],
    )

    # ---------------------------------------------------------------------------------------------
    # EXIBIÇÃO DO PARECER CONSOLIDADO NO TERMINAL:
    # ---------------------------------------------------------------------------------------------
    print("\n" + "=" * 105)
    print("🏆 PILAR 1: SCORECARD TÉCNICO E LATÊNCIA DO PÓDIO TOP 3")
    print("=" * 105)
    print(scorecard_tecnico.to_string(index=False))

    print("\n" + "=" * 105)
    print("💰 PILAR 2: LEADERBOARD DE IMPACTO FINANCEIRO EM REAIS (R$)")
    print("=" * 105)
    print(leaderboard_financeiro.to_string(index=False))

    print("\n" + "=" * 105)
    print("📋 PILAR 4: PARECER FORMAL DE HOMOLOGAÇÃO INSTITUCIONAL")
    print("=" * 105)
    parecer = laudo_p4["parecer_homologacao"]
    print(f"• Modelo Avaliado: {parecer['modelo_avaliado']}")
    print(f"• Status de Homologação: {parecer['status_homologacao']}")
    print(f"• Sensibilidade Atendida: {'SIM' if parecer['criterio_sensibilidade_atendido'] else 'NÃO'}")
    print(f"• Latência em Tempo Real Atendida: {'SIM' if parecer['criterio_latencia_atendido'] else 'NÃO'}")
    print(f"• Retorno Financeiro Líquido Positivo: {'SIM' if parecer['criterio_financeiro_atendido'] else 'NÃO'}")
    print(f"\n> Parecer Pericial:\n{parecer['parecer_executivo']}")
    print("-" * 105)
    print(f"📄 Dossiê Markdown Executivo gravado em: {laudo_p4['caminho_dossie_arquivo']}")
    print("=" * 105 + "\n")


if __name__ == "__main__":
    main()