"""Script Executor da Fase 02: Diagnóstico Macro e Raio-X Empresarial 360°.

Responsabilidade Única: Servir de ponto de entrada via linha de comando para
executar a Fase 02 do CRISP-DM, acionando o OrquestradorRaioXEmpresarial,
resolvendo a raiz física do repositório, disparando a perícia de saúde de todas
as tabelas do ERP e gerando os laudos e gráficos analíticos dos 10 departamentos.
"""

# 'from pathlib import Path' provê suporte a caminhos de arquivos de forma orientada a objetos.
from pathlib import Path

# 'import sys' viabiliza a injeção da raiz do projeto nas rotas de busca de módulos do Python[cite: 1].
import sys

# 'import logging' gerencia as mensagens de auditoria técnica estruturadas no terminal[cite: 5].
import logging


# -------------------------------------------------------------------------------------------------
# RESOLUÇÃO DINÂMICA E RESILIENTE DA RAIZ DO REPOSITÓRIO
# -------------------------------------------------------------------------------------------------
def localizar_raiz_repositorio(caminho_referencia: Path) -> Path:
    """Navega recursivamente pelos diretórios ancestrais até localizar a pasta raiz contendo 'src'[cite: 1].

    Args:
        caminho_referencia (Path): Caminho do arquivo atual em execução[cite: 1].

    Returns:
        Path: Caminho canônico da raiz do repositório ('projeto_ml/')[cite: 1].
    """
    for candidato in [caminho_referencia.parent] + list(caminho_referencia.parents):
        if (candidato / "src").is_dir():
            return candidato.resolve()
    raise RuntimeError("Não foi possível localizar a raiz do projeto contendo a pasta 'src'.")


# Localiza a raiz absoluta e a injeta no início de 'sys.path' para habilitar as importações de 'src'[cite: 1].
DIRETORIO_RAIZ = localizar_raiz_repositorio(Path(__file__).resolve())
if str(DIRETORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_RAIZ))

# Importa a classe oficial de orquestração do Raio-X construída na Fase 2[cite: 5].
from src.etapas.fase_02_exploracao.etapa_02_raio_x_empresarial import (
    OrquestradorRaioXEmpresarial,
)

# Importa o bootstrap parametrizado (G5) que unifica dataset, semente e problema.
from scripts.bootstrap import argumentos_comuns

# Importa o gerenciador de datasets para persistir o status da fase no registro.
from src.nucleo.registro_datasets.gerenciador_datasets import GerenciadorDatasets

# Garantir logs em tempo real no terminal (sem bufferização do Python)
import sys
import os
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
os.environ['PYTHONUNBUFFERED'] = '1'

# Configura o layout das mensagens de log corporativo[cite: 5].
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
    stream=sys.stdout,
)


def main() -> None:
    """Função principal que coordena o disparo do Raio-X 360° da Fase 02[cite: 5]."""
    print("\n" + "=" * 105)
    print("🔎 INICIANDO FASE 02 DO CRISP-DM: DIAGNÓSTICO GERAL E RAIO-X EMPRESARIAL 360°")
    print("=" * 105 + "\n")

    logging.info("Raiz do projeto ancorada dinamicamente em: %s", DIRETORIO_RAIZ)

    # 1. PARAMETRIZAÇÃO: o dataset alvo é informado pela camada de serviço (G6),
    # de modo que os laudos departamentais nunca se misturem entre PMEs.
    parser = argumentos_comuns("Fase 02 — Diagnóstico macro e Raio-X empresarial")
    argumentos = parser.parse_args()

    # Instancia o orquestrador oficial da Fase 02 passando a raiz do repositório[cite: 5].
    orquestrador_fase_02 = OrquestradorRaioXEmpresarial(
        raiz_projeto=DIRETORIO_RAIZ,
        nome_dataset=argumentos.dataset,
    )

    # Executa a triagem mecânica geral e os 10 departamentos analíticos[cite: 5].
    try:
        prontuario_final = orquestrador_fase_02.executar_raio_x_completo()
    except Exception as erro_execucao:
        logging.critical("Falha ao executar o Raio-X da Fase 02: %s", erro_execucao, exc_info=True)
        # Persiste no registro do dataset que a Fase 02 falhou: sem isto, a fase ficaria
        # presa em 'executando' para sempre, divergindo do estado real da plataforma.
        try:
            gerenciador = GerenciadorDatasets(diretorio_raiz=DIRETORIO_RAIZ)
            registro = gerenciador.obter_ou_criar(argumentos.dataset)
            registro.marcar_fase("02", "erro")
            registro.registrar_observacao(f"Fase 02 falhou: {erro_execucao}")
            gerenciador.salvar(registro)
        except Exception as erro_registro:
            logging.warning("Não foi possível persistir o status de erro da Fase 02: %s", erro_registro)
        sys.exit(1)

    # Persiste no registro do dataset que a Fase 02 foi concluída com sucesso.
    try:
        gerenciador = GerenciadorDatasets(diretorio_raiz=DIRETORIO_RAIZ)
        registro = gerenciador.obter_ou_criar(argumentos.dataset)
        registro.marcar_fase("02", "concluida")
        gerenciador.salvar(registro)
    except Exception as erro_registro:
        logging.warning("Não foi possível persistir o status da Fase 02: %s", erro_registro)

    # Exibição executiva do prontuário final compilado no terminal[cite: 5].
    print("\n" + "=" * 105)
    print("📋 PRONTUÁRIO EXECUTIVO CONSOLIDADO (FASE 02 CONCLUÍDA)")
    print("=" * 105)
    
    total_tabelas_auditadas = len(prontuario_final.get("saude_estrutural_dados", {}))
    print(f"📦 Total de Tabelas Periciadas pelo Auditor Geral: {total_tabelas_auditadas} tabelas[cite: 5]")
    print("🏢 Departamentos Auditados com Geração de Gráficos em 'relatorios/figuras/':")
    
    setores = [
        "comercial", "financeiro", "compras", "estoque", "contabil",
        "fiscal", "producao", "logistica", "pos_venda", "recursos_humanos"
    ]
    for setor in setores:
        if setor in prontuario_final:
            print(f"   • {setor.upper():<20} -> ✅ Diagnóstico Concluído e Laudo Registrado[cite: 5]")

    print("\n" + "=" * 105)
    print("✅ FASE 02 CONCLUÍDA COM SUCESSO! GRÁFICOS DISPONÍVEIS EM 'relatorios/figuras/'[cite: 5]")
    print("=" * 105 + "\n")


if __name__ == "__main__":
    main()