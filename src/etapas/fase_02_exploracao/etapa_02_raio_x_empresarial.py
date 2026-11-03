# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro de auditoria e mensagens no console.
import logging

# 'import json' serializa o Prontuário Executivo 360° em disco (rastro recuperável
# para dashboards e consumidores externos — regra "nenhum resultado sem rastro").
import json

# 'from' indica a biblioteca de origem; 'pathlib' manipula caminhos e pastas no sistema operacional de forma orientada a objetos.
# 'import' traz a classe 'Path' para representar diretórios e caminhos compatíveis com Windows, Linux e macOS.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão para anotações formais de tipos estáticos (Type Hints).
# 'import' carrega 'Any' e 'Dict' para documentar saídas estruturadas.
from typing import Any, Dict

# Importação dos 10 analisadores especialistas departamentais da subpasta 'departamentos/'.
from src.etapas.fase_02_exploracao.departamentos.d01_comercial import AnalisadorComercial
from src.etapas.fase_02_exploracao.departamentos.d02_financeiro import AnalisadorFinanceiro
from src.etapas.fase_02_exploracao.departamentos.d03_compras import AnalisadorCompras
from src.etapas.fase_02_exploracao.departamentos.d04_estoque import AnalisadorEstoque
from src.etapas.fase_02_exploracao.departamentos.d05_contabil import AnalisadorContabil
from src.etapas.fase_02_exploracao.departamentos.d06_fiscal import AnalisadorFiscal
from src.etapas.fase_02_exploracao.departamentos.d07_producao import AnalisadorProducao
from src.etapas.fase_02_exploracao.departamentos.d08_logistica import AnalisadorLogistica
from src.etapas.fase_02_exploracao.departamentos.d09_pos_venda import AnalisadorPosVenda
from src.etapas.fase_02_exploracao.departamentos.d10_recursos_humanos import AnalisadorRecursosHumanos

# Importação do auditor estrutural macro de saúde de dados da Fase 02.
from src.etapas.fase_02_exploracao.etapa_02_diagnostico_geral import AuditorSaudeDados

# Importação do gerenciador de registro de datasets do núcleo compartilhado.
from src.nucleo.registro_datasets.gerenciador_datasets import GerenciadorDatasets

# 'logging.basicConfig' parametriza a formatação dos registros operacionais no terminal.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'def _serializador_json(...)' converte tipos científicos/exóticos em JSON válido.
def _serializador_json(objeto: Any) -> Any:
    """Converte Path, escalares NumPy/Pandas e datas em tipos nativos serializáveis.

    Args:
        objeto: Valor encontrado pelo ``json.dump`` que não é nativo do JSON.

    Returns:
        Any: Representação nativa (str/int/float/bool/None/list/dict).
    """
    # Caminhos de arquivo viram string.
    if isinstance(objeto, Path):
        return str(objeto)

    # Escalares NumPy (np.int64, np.bool_ etc.) expõem '.item()'.
    if hasattr(objeto, "item") and hasattr(objeto, "dtype"):
        return objeto.item()

    # Períodos e timestamps do pandas viram ISO 8601.
    if hasattr(objeto, "isoformat"):
        return objeto.isoformat()

    # Valores ausentes do pandas (NaT/NaN) viram null.
    if objeto is None:
        return None

    raise TypeError(f"Tipo não serializável em JSON: {type(objeto)!r}")


# 'class OrquestradorRaioXEmpresarial' centraliza a coordenação unificada de toda a Fase 2 do CRISP-DM.
class OrquestradorRaioXEmpresarial:
    """Classe responsável por coordenar a triagem macro e os 10 departamentos analíticos na Fase 02."""

    # 'def __init__(...)' constrói a instância mapeando os diretórios oficiais e instanciando os especialistas.
    def __init__(self, raiz_projeto: Path, nome_dataset: str | None = None) -> None:
        """Inicializa o orquestrador resolvendo de forma determinística a base em análise.

        Args:
            raiz_projeto (Path): Caminho absoluto da raiz do projeto.
            nome_dataset (str | None, opcional): Nome do dataset específico a analisar.
                Quando ``None``, o GerenciadorDatasets resolve o dataset mais recente,
                eliminando a seleção frágil ``subpastas[0]`` da versão original.
        """
        # Armazena o endereço físico absoluto da pasta raiz do projeto de Machine Learning.
        self.raiz_projeto = raiz_projeto

        # RESOLUÇÃO CANÔNICA E DETERMINÍSTICA DO DIRETÓRIO DO BANCO DE DADOS ATIVO:
        # O GerenciadorDatasets substitui a heurística 'primeira subpasta encontrada'.
        self.gerenciador_datasets = GerenciadorDatasets(diretorio_raiz=raiz_projeto)
        try:
            self.pasta_dados_brutos = self.gerenciador_datasets.resolver_pasta_csv(nome_dataset)
        except FileNotFoundError:
            # Sem dataset disponível, ancora na pasta base para que os especialistas reportem vazio.
            pasta_csv_base = raiz_projeto / "dados" / "brutos" / "csv"
            pasta_csv_base.mkdir(parents=True, exist_ok=True)
            self.pasta_dados_brutos = pasta_csv_base

        self.nome_dataset = nome_dataset or self.pasta_dados_brutos.name
        self.nome_banco = self.nome_dataset

        # Constrói o caminho de saída raiz para a gravação dos laudos e figuras analíticas dos setores.
        # Os relatórios ficam isolados por dataset para evitar sobrescrita entre PMEs.
        self.pasta_relatorios = self.raiz_projeto / "relatorios" / self.nome_dataset
        self.pasta_relatorios.mkdir(parents=True, exist_ok=True)

        logging.info(
            "Orquestrador Raio-X conectado à base: '%s' (%s)",
            self.nome_banco,
            self.pasta_dados_brutos,
        )

        # 1. Auditor Estrutural Geral de Saúde de Dados:
        # Recebe o ponteiro exato da pasta onde residem as tabelas reais do banco.
        self.auditor_geral = AuditorSaudeDados(pasta_dados_brutos=self.pasta_dados_brutos)

        # 2. Bateria dos 10 Especialistas Departamentais (Composição Orientada a Objetos):
        self.analisador_comercial = AnalisadorComercial(self.pasta_dados_brutos, self.pasta_relatorios)
        self.analisador_financeiro = AnalisadorFinanceiro(self.pasta_dados_brutos, self.pasta_relatorios)
        self.analisador_compras = AnalisadorCompras(self.pasta_dados_brutos, self.pasta_relatorios)
        self.analisador_estoque = AnalisadorEstoque(self.pasta_dados_brutos, self.pasta_relatorios)
        self.analisador_contabil = AnalisadorContabil(self.pasta_dados_brutos, self.pasta_relatorios)
        self.analisador_fiscal = AnalisadorFiscal(self.pasta_dados_brutos, self.pasta_relatorios)
        self.analisador_producao = AnalisadorProducao(self.pasta_dados_brutos, self.pasta_relatorios)
        self.analisador_logistica = AnalisadorLogistica(self.pasta_dados_brutos, self.pasta_relatorios)
        self.analisador_pos_venda = AnalisadorPosVenda(self.pasta_dados_brutos, self.pasta_relatorios)
        self.analisador_rh = AnalisadorRecursosHumanos(self.pasta_dados_brutos, self.pasta_relatorios)

        logging.info("Orquestrador do Raio-X pronto com os 10 departamentos ativos para o banco '%s'.", self.nome_banco)

    # 'def executar_raio_x_completo(...)' executa em série a triagem geral e os diagnósticos setoriais.
    def executar_raio_x_completo(self) -> Dict[str, Any]:
        """Executa a triagem macro e as perícias departamentais completas da Fase 02 (CRISP-DM)."""
        logging.info("=================================================================")
        logging.info("=== INICIANDO EXECUÇÃO COMPLETA DO RAIO-X EMPRESARIAL 360° ===")
        logging.info("=================================================================")

        # 1. Executa o diagnóstico macro de volumetria, nulos, tipos e duplicatas via AuditorSaudeDados.
        laudo_estrutural = self.auditor_geral.executar_diagnostico_completo()

        # 2. Executa sequencialmente o diagnóstico completo de cada um dos 10 departamentos analíticos.
        # ISOLAÇÃO DE FALHAS: a quebra de um departamento não aborta os demais — os outros
        # setores ainda geram seus relatórios e a falha é reportada ao final, evitando que a
        # UI apresente uma pasta de relatórios pela metade como se fosse um resultado válido.
        departamentos = [
            ("comercial", self.analisador_comercial),
            ("financeiro", self.analisador_financeiro),
            ("compras", self.analisador_compras),
            ("estoque", self.analisador_estoque),
            ("contabil", self.analisador_contabil),
            ("fiscal", self.analisador_fiscal),
            ("producao", self.analisador_producao),
            ("logistica", self.analisador_logistica),
            ("pos_venda", self.analisador_pos_venda),
            ("recursos_humanos", self.analisador_rh),
        ]

        laudos_departamentais: Dict[str, Any] = {}
        falhas_departamentais: Dict[str, str] = {}

        for nome_departamento, analisador in departamentos:
            try:
                laudos_departamentais[nome_departamento] = analisador.executar_diagnostico_completo()
            except Exception as erro_departamento:
                falhas_departamentais[nome_departamento] = str(erro_departamento)
                logging.error(
                    "Departamento '%s' falhou na Fase 02 (os demais continuam): %s",
                    nome_departamento,
                    erro_departamento,
                    exc_info=True,
                )

        # 2.1. Se algum setor quebrou, a fase é considerada INCOMPLETA e o erro é propagado
        # só depois de todos os departamentos terem tido a chance de rodar.
        if falhas_departamentais:
            logging.error(
                "=== RAIO-X INCOMPLETO: %d de %d departamento(s) com falha: %s ===",
                len(falhas_departamentais),
                len(departamentos),
                ", ".join(sorted(falhas_departamentais)),
            )
            resumo_falhas = "; ".join(
                f"{nome}: {mensagem}" for nome, mensagem in sorted(falhas_departamentais.items())
            )
            raise RuntimeError(
                f"Fase 02 incompleta — {len(falhas_departamentais)} departamento(s) falharam: "
                f"{resumo_falhas}"
            )

        # 3. Consolidação do Prontuário Executivo 360 Graus integrando a saúde técnica e os 10 setores.
        prontuario_executivo: Dict[str, Any] = {
            "cliente_ativo": self.nome_banco,
            "saude_estrutural_dados": laudo_estrutural,
            "comercial": laudos_departamentais["comercial"],
            "financeiro": laudos_departamentais["financeiro"],
            "compras": laudos_departamentais["compras"],
            "estoque": laudos_departamentais["estoque"],
            "contabil": laudos_departamentais["contabil"],
            "fiscal": laudos_departamentais["fiscal"],
            "producao": laudos_departamentais["producao"],
            "logistica": laudos_departamentais["logistica"],
            "pos_venda": laudos_departamentais["pos_venda"],
            "recursos_humanos": laudos_departamentais["recursos_humanos"],
        }

        # 4. VISÃO AGNÓSTICA DE SAÚDE 360°: radar polar de notas 0–100 + KPIs
        # executivos + semáforo de sinais em uma placa única — a visão que
        # enxerga a companhia como um todo, independente do setor.
        # Bloco isolado em try/except: uma falha aqui não derruba a Fase 02,
        # que já concluiu os 10 departamentos com sucesso.
        pasta_fase_02 = self.pasta_relatorios / self.nome_banco / "fase_02"
        pasta_fase_02.mkdir(parents=True, exist_ok=True)
        try:
            from src.etapas.fase_02_exploracao.visao_360_saude import (
                gerar_dashboard_saude,
            )

            caminho_dashboard = gerar_dashboard_saude(
                dataset=self.nome_dataset,
                prontuario=prontuario_executivo,
                pasta_saida=pasta_fase_02,
            )
            prontuario_executivo["saude_360"] = {
                "grafico_dashboard_saude": str(caminho_dashboard),
                "natureza": (
                    "Visão agnóstica: radar de saúde + semáforo de sinais "
                    "sobre os KPIs dos 10 departamentos."
                ),
            }
        except Exception:
            logging.warning(
                "Falha ao gerar o Dashboard de Saúde 360° (visão agnóstica ignorada).",
                exc_info=True,
            )

        # 5. PERSISTÊNCIA DO PRONTUÁRIO: grava o dicionário completo em JSON na
        # mesma pasta dos relatórios departamentais, permitindo que dashboards
        # consumam os KPIs sem re-executar a fase (regra "sem rastro nenhum").
        caminho_prontuario = pasta_fase_02 / "prontuario_executivo.json"
        try:
            with caminho_prontuario.open("w", encoding="utf-8") as arquivo_prontuario:
                json.dump(
                    prontuario_executivo,
                    arquivo_prontuario,
                    ensure_ascii=False,
                    indent=2,
                    default=_serializador_json,
                )
            logging.info("Prontuário executivo persistido em: %s", caminho_prontuario)
        except Exception:
            # A persistência é um extra: uma falha de serialização não pode
            # derrubar a Fase 02 que já concluiu com sucesso.
            logging.warning(
                "Não foi possível persistir o prontuario_executivo.json.",
                exc_info=True,
            )

        logging.info("=================================================================")
        logging.info("=== RAIO-X CONCLUÍDO: 10 DEPARTAMENTOS AUDITADOS COM SUCESSO ===")
        logging.info("=== GRÁFICOS E LAUDOS DISPONÍVEIS EM relatorios/%s/fase_02/ ===", self.nome_banco)
        logging.info("=================================================================")

        return prontuario_executivo


# Bloco de execução direta via linha de comandos.
if __name__ == "__main__":
    caminho_raiz = Path(__file__).resolve().parent.parent.parent.parent
    maestro_fase_02 = OrquestradorRaioXEmpresarial(raiz_projeto=caminho_raiz)
    laudo_geral = maestro_fase_02.executar_raio_x_completo()