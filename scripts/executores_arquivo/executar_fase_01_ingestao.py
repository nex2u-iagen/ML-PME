"""Script Executor da Fase 01: Ingestão de Dados e Extração de Dumps de ERPs.

Responsabilidade Única: Ponto de entrada operacional via linha de comando (CLI)
localizado em 'scripts/executores_arquivo/' para disparar o OrquestradorIngestao,
resolver dinamicamente a raiz do repositório, validar a carga de backups SQL (.sql)
ou tabelas (.csv) e emitir a auditoria de volumetria das entidades na memória RAM.
"""

# 'from pathlib import Path' disponibiliza a manipulação orientada a objetos de caminhos no disco.
from pathlib import Path

# 'import sys' permite inspecionar e manipular as rotas internas de busca de módulos do interpretador Python.
import sys

# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo[cite: 2, 3, 4].
import logging

# 'import pandas as pd' permite calcular dimensões, memória e volumetria das tabelas retornadas[cite: 2, 4].
import pandas as pd


# -------------------------------------------------------------------------------------------------
# RESOLUÇÃO DINÂMICA E RESILIENTE DA RAIZ DO REPOSITÓRIO
# -------------------------------------------------------------------------------------------------
def localizar_raiz_repositorio(caminho_referencia: Path) -> Path:
    """Navega recursivamente pelos diretórios ancestrais até localizar a pasta raiz contendo 'src'.

    Args:
        caminho_referencia (Path): Caminho físico do arquivo atual em execução[cite: 3, 4].

    Returns:
        Path: Caminho absoluto canônico da raiz do projeto ('projeto_ml/').

    Raises:
        RuntimeError: Se a pasta 'src' não for localizada em nenhum diretório ancestral.
    """
    # Itera sobre o diretório do arquivo e todos os seus diretórios pais (árvore ascendente)[cite: 1, 3].
    for diretorio_candidato in [caminho_referencia.parent] + list(caminho_referencia.parents):
        # O critério de parada é a presença da pasta 'src' como filha direta do diretório.
        if (diretorio_candidato / "src").is_dir():
            return diretorio_candidato.resolve()

    # Caso a busca chegue na raiz do sistema operacional sem encontrar 'src', levanta exceção formal[cite: 1].
    raise RuntimeError(
        f"Não foi possível identificar a raiz do projeto a partir de: {caminho_referencia.resolve()}. "
        "Certifique-se de que a pasta 'src' existe na estrutura do projeto."
    )


# Localiza a raiz do projeto de forma robusta e independente da profundidade da subpasta[cite: 1].
DIRETORIO_RAIZ = localizar_raiz_repositorio(Path(__file__).resolve())

# Injeta a pasta raiz do projeto na primeira posição do 'sys.path' para habilitar 'from src...'[cite: 1].
if str(DIRETORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_RAIZ))

# Importa a classe oficial de orquestração construída na Fase 01 do projeto[cite: 1].
from src.etapas.fase_01_ingestao.etapa_01_extracao import OrquestradorIngestao

# Importa o bootstrap parametrizado (G5) que unifica dataset, semente e problema.
from scripts.bootstrap import argumentos_comuns

# Garantir logs em tempo real no terminal (sem bufferização do Python)
import sys
import os
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
os.environ['PYTHONUNBUFFERED'] = '1'

# 'logging.basicConfig' parametriza a formatação dos registros no console corporativo[cite: 1, 2, 3, 4].
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
    stream=sys.stdout,
)


# 'def emitir_painel_auditoria_entidades(...)' formata o relatório de volumetria no terminal[cite: 1].
def emitir_painel_auditoria_entidades(tabelas_ingeridas: dict[str, pd.DataFrame]) -> None:
    """Apresenta um relatório tabular formatado no terminal com as métricas de volumetria da ingestão[cite: 1].

    Args:
        tabelas_ingeridas (dict[str, pd.DataFrame]): Dicionário com as tabelas do ERP carregadas[cite: 1].
    """
    print("\n" + "=" * 95)
    print("📊 PAINEL DE CONTROLE DE INGESTÃO — AUDITORIA DE VOLUMETRIA (FASE 01 - CRISP-DM)")
    print("=" * 95)

    # Itera sobre cada entidade processada pelo OrquestradorIngestao[cite: 1].
    for nome_entidade, dataframe in tabelas_ingeridas.items():
        # Calcula a memória consumida pelo DataFrame em Kilobytes (KB).
        memoria_kb = dataframe.memory_usage(deep=True).sum() / 1024.0

        # Identifica a contagem total de valores ausentes (NaN / Nulos) em toda a tabela.
        total_nulos = int(dataframe.isna().sum().sum())

        print(f"📦 Entidade: '{nome_entidade.upper()}'")
        print(f"   • Dimensões: {dataframe.shape[0]} registros (linhas) × {dataframe.shape[1]} atributos (colunas)")
        print(f"   • Memória Alocada: {memoria_kb:.2f} KB na memória RAM")
        print(f"   • Células Nulas/Ausentes: {total_nulos}")
        print(f"   • Variáveis Identificadas: {list(dataframe.columns)}")
        print("   • Amostra dos Primeiros Registros:")

        # Formata os 2 primeiros registros como texto tabular com recuo visual limpo.
        linhas_amostra = dataframe.head(2).to_string(index=False)
        for linha in linhas_amostra.split("\n"):
            print(f"     {linha}")
        print("-" * 95)

    print(f"✅ Total de Entidades Homologadas para a Fase 02: {len(tabelas_ingeridas)}")
    print("=" * 95 + "\n")


# 'def main(...)' encapsula a execução do pipeline de ingestão via terminal[cite: 1].
def main() -> None:
    """Função principal que coordena o disparo da extração e a validação das entidades[cite: 1]."""
    logging.info("Raiz do projeto identificada dinamicamente em: %s", DIRETORIO_RAIZ)

    # 1. PARAMETRIZAÇÃO: o dataset alvo é informado pela camada de serviço (G6),
    # garantindo que a extração nunca contamine a base de outra PME.
    parser = argumentos_comuns("Fase 01 — Ingestão e extração de dados")
    argumentos = parser.parse_args()

    # Instancia o OrquestradorIngestao oficial passando a raiz calculada[cite: 1].
    orquestrador = OrquestradorIngestao(
        diretorio_raiz=DIRETORIO_RAIZ,
        nome_dataset=argumentos.dataset,
    )

    # 2. Executa o ciclo completo da Fase 01:
    #    - Se houver .sql em 'dados/brutos/sql/', restaura no SQLite e exporta para CSV em lotes[cite: 1, 3].
    #    - Se 'dados/brutos/csv/' estiver vazia, gera automaticamente dados sintéticos realistas[cite: 1].
    #    - Lê os CSVs com o LeitorArquivosTabulares e devolve os DataFrames[cite: 1, 4].
    try:
        tabelas_carregadas = orquestrador.executar_fase_ingestao()
    except Exception as erro_execucao:
        logging.critical("Falha crítica ao executar a Fase 01 de Ingestão: %s", erro_execucao, exc_info=True)
        sys.exit(1)

    # 3. Emite o laudo diagnóstico no console corporativo[cite: 1].
    emitir_painel_auditoria_entidades(tabelas_carregadas)

    logging.info("Fase 01 concluída com êxito! Dados tabulares prontos para a Fase 02 (Exploração).")


# Bloco de proteção para execução exclusiva via linha de comando[cite: 1].
if __name__ == "__main__":
    main()