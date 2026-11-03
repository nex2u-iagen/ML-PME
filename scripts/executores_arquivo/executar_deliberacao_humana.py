"""Script Executor de Deliberação Humana e Sign-off do Pódio Top 3 (Fase 5 - HITL).

Responsabilidade Única: Carregar os laudos consolidados do Pilar 1 (Técnico) e
do Pilar 2 (Financeiro), invocar o Portal de Deliberação Humana, colher a
chancela ativa do especialista e emitir o Termo Oficial de Homologação em disco[cite: 7, 13].
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro estruturado no console.
import logging

# 'from' acessa a biblioteca nativa 'pathlib'; 'import' traz a classe 'Path' para manipulação de rotas.
from pathlib import Path

# 'import' traz o módulo 'sys' nativo para manipulação dos caminhos de busca do interpretador.
import sys
import os

# RESOLUÇÃO CANÔNICA DA RAIZ DO REPOSITÓRIO:
DIRETORIO_RAIZ = Path(__file__).resolve().parents[2]
if str(DIRETORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_RAIZ))

# 'import' traz a biblioteca externa 'joblib' para desserializar os modelos finalistas.
import joblib

# 'import' traz a biblioteca externa 'pandas' para leitura ultra-rápida do teste Parquet[cite: 13].
import pandas as pd

# IMPORTAÇÃO DOS ORQUESTRADORES DOS PILARES 1 E 2 DA FASE 5[cite: 7]:
from src.etapas.fase_05_avaliacao.pilar_01_podio_top3.orquestrador_podio_top3 import (
    OrquestradorPodioTop3,
)
from src.etapas.fase_05_avaliacao.pilar_02_alinhamento_negocio.configuracao_custos import (
    ConfiguracaoCustoRisco,
)
from src.etapas.fase_05_avaliacao.pilar_02_alinhamento_negocio.orquestrador_alinhamento_negocio import (
    OrquestradorAlinhamentoNegocio,
)
from src.etapas.fase_05_avaliacao.pilar_04_governanca_homologacao.portal_deliberacao_humana import (
    PortalDeliberacaoHumana,
)

# Garantir logs em tempo real no terminal (sem bufferização do Python)
import sys
import os
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
os.environ['PYTHONUNBUFFERED'] = '1'

# 'logging.basicConfig' parametriza a formatação dos registros operacionais no terminal.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
    stream=sys.stdout,
)


def main() -> None:
    """Função executiva que orquestra a sessão interativa de validação humana da Fase 5[cite: 7]."""
    nome_cliente = "mercado_vencedor"
    pasta_modelos = DIRETORIO_RAIZ / "modelos" / nome_cliente
    pasta_ml = DIRETORIO_RAIZ / "dados" / "processados" / nome_cliente / "ml"
    pasta_relatorios = DIRETORIO_RAIZ / "relatorios" / nome_cliente / "fase_05_avaliacao"
    pasta_governanca = DIRETORIO_RAIZ / "relatorios" / nome_cliente / "governanca"

    caminho_top3 = pasta_modelos / "catalogo_top3_modelos.joblib"
    caminho_teste = pasta_ml / "teste_processado.parquet"

    # Verificação defensiva de integridade física dos artefatos em disco:
    if not caminho_top3.is_file() or not caminho_teste.is_file():
        logging.error("Artefatos necessários não encontrados! Certifique-se de que as Fases 3 e 4 foram executadas.")
        sys.exit(1)

    logging.info("Carregando o catálogo do Pódio Top 3 e a partição de teste retido...")
    catalogo_top3 = joblib.load(caminho_top3)
    df_teste = pd.read_parquet(caminho_teste)

    # Segregação da matriz preditora X e do vetor resposta y[cite: 13, 14]:
    coluna_alvo = "alvo_inadimplente"
    X_teste = df_teste.drop(columns=[coluna_alvo])
    y_teste = df_teste[coluna_alvo].to_numpy()

    # 1. Apuração das métricas técnicas do Pilar 1 (F1, Sensibilidade, Precisão, Latência)[cite: 7, 13]:
    orquestrador_p1 = OrquestradorPodioTop3(pasta_relatorios=pasta_relatorios / "pilar_01_top3")
    laudo_p1 = orquestrador_p1.executar_auditoria_completa(
        catalogo_top3=catalogo_top3,
        matriz_atributos_teste=X_teste,
        vetor_alvo_teste=y_teste,
        rotulos_classes=["Em Dia", "Inadimplente"],
    )
    scorecard_tecnico = laudo_p1["scorecard_tabular"]

    # 2. Apuração do impacto contábil do Pilar 2 (Custos de omissão vs alarmes falsos)[cite: 7]:
    config_custos = ConfiguracaoCustoRisco.perfil_conservador_saude_fraude()
    orquestrador_p2 = OrquestradorAlinhamentoNegocio(configuracao_custos=config_custos)
    leaderboard_financeiro = orquestrador_p2.gerar_leaderboard_financeiro(
        catalogo_top3=catalogo_top3,
        matriz_atributos_teste=X_teste,
        vetor_alvo_teste=y_teste,
    )

    # Identifica o modelo recomendado pela maior pontuação técnica e económica:
    modelo_recomendado = str(scorecard_tecnico.iloc[0]["Modelo"])

    # 3. Convocação da Mesa de Deliberação Humana no Circuito (HITL)[cite: 7]:
    portal_humano = PortalDeliberacaoHumana(pasta_governanca=pasta_governanca)
    portal_humano.conduzir_deliberacao_interativa(
        scorecard_tecnico=scorecard_tecnico,
        leaderboard_financeiro=leaderboard_financeiro,
        modelo_sugerido_maquina=modelo_recomendado,
    )


if __name__ == "__main__":
    main()