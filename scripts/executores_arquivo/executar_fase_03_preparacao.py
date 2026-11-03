"""Script Executor Oficial da Fase 03 do CRISP-DM: Preparação dos Dados para ML.

Responsabilidade Única: Servir de ponto de entrada (CLI) para orquestrar a
construção da Tabela Base Analítica (ABT) guiada pelo **contrato de problema**,
a divisão estratificada anti-vazamento e a calibração do Pipeline matemático
do Scikit-Learn.

Exemplos de uso:

    uv run python -m scripts.executores_arquivo.executar_fase_03_preparacao \\
        --dataset mercado_vencedor --problema previsao_faturamento --semente 42
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro operacional do console.
import logging

# Importa o bootstrap parametrizado (G5) que unifica dataset, semente e problema.
from scripts.bootstrap import (
    argumentos_comuns,
    configurar_ambiente,
    resolver_contrato,
    resolver_pastas_dataset,
)

# Importação da classe orquestradora da Fase 3.2 após a garantia de ancoragem da raiz.
from src.etapas.fase_03_preparacao.etapa_03_02_dados_para_ml import (
    OrquestradorDadosML,
)

# Configura o ambiente de execução (sys.path + logging).
configurar_ambiente()


# 'def' define a função principal que comanda a execução do pipeline de preparação de dados[cite: 8].
def main() -> None:
    """Função executiva que localiza diretórios e inicializa o orquestrador de ML da Fase 3[cite: 8, 12]."""
    parser = argumentos_comuns("Fase 03 — Preparação dos dados para Machine Learning")
    argumentos = parser.parse_args()

    # Exibe cabeçalho informativo no console para demarcação da etapa atual do CRISP-DM[cite: 8].
    print("\n" + "=" * 95)
    print("🚀 INICIANDO FASE 03: PREPARAÇÃO DOS DADOS E ENGENHARIA DE ATRIBUTOS (ML)")
    print("=" * 95 + "\n")

    # 1. RESOLUÇÃO PARAMETRIZADA do dataset ativo e de suas pastas canônicas.
    pastas = resolver_pastas_dataset(argumentos.dataset)
    nome_cliente = pastas["nome"]
    pasta_cliente_ativo = pastas["brutos"]
    pasta_destino_ml = pastas["ml"]
    pasta_modelos = pastas["modelos"]

    # 2. RESOLUÇÃO do contrato de problema que dirigirá a construção da ABT.
    contrato = resolver_contrato(nome_cliente, argumentos.problema)
    if contrato is None:
        logging.error(
            "Nenhum problema de negócio definido para o dataset '%s'. "
            "Informe --problema com um dos 15 identificadores do catálogo.",
            nome_cliente,
        )
        raise SystemExit(1)

    logging.info(
        "Executor Fase 3 — Dataset: '%s' | Problema: '%s' | Tarefa: %s | Semente: %d",
        nome_cliente,
        contrato.id,
        contrato.tipo_tarefa.value,
        argumentos.semente,
    )

    # 3. Instancia o orquestrador de preparação matemática com o contrato vigente.
    orquestrador = OrquestradorDadosML(
        pasta_bi=pasta_cliente_ativo,
        pasta_saida_ml=pasta_destino_ml,
        pasta_modelos=pasta_modelos,
        semente_aleatoria=argumentos.semente,
        contrato=contrato,
    )

    # 4. Executa a preparação completa: ABT, partição 70/15/15 e pipeline Scikit-Learn.
    laudo_artefatos = orquestrador.executar_preparacao_ml_completa()

    # 5. Atualiza o registro do dataset com o contrato e o estado da fase.
    try:
        from src.nucleo.registro_datasets.gerenciador_datasets import GerenciadorDatasets
        from scripts.bootstrap import RAIZ_PROJETO

        gerenciador = GerenciadorDatasets(diretorio_raiz=RAIZ_PROJETO)
        registro = gerenciador.obter_ou_criar(nome_cliente)
        registro.contrato_problema = contrato
        registro.marcar_fase("03", "concluida")
        registro.registrar_observacao(
            f"Fase 03 concluída com o problema '{contrato.id}' ({contrato.tipo_tarefa.value})."
        )
        gerenciador.salvar(registro)
    except Exception as erro_registro:
        logging.warning("Não foi possível atualizar o registro do dataset: %s", erro_registro)

    # Emite mensagem afirmativa ao usuário confirmando o êxito operacional da fase[cite: 8].
    print("\n" + "=" * 95)
    print(f"✅ FASE 03 CONCLUÍDA COM SUCESSO PARA: '{nome_cliente.upper()}'")
    print(f"🧠 Problema aplicado: '{contrato.nome}' ({contrato.tipo_tarefa.value})")
    print(f"📁 Partições Parquet geradas em: {pasta_destino_ml.resolve()}")
    print(f"🧠 Pipeline Scikit-Learn gravado em: {pasta_modelos.resolve()}")
    print("=" * 95 + "\n")


# Bloco condicional para disparo direto via linha de comandos[cite: 8].
if __name__ == "__main__":
    main()
