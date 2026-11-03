# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro de auditoria e mensagens no console.
import logging

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

# 'logging.basicConfig' parametriza a formatação dos registros operacionais no terminal.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class OrquestradorRaioXEmpresarial' centraliza a coordenação unificada de toda a Fase 2 do CRISP-DM.
class OrquestradorRaioXEmpresarial:
    """Classe responsável por coordenar a triagem macro e os 10 departamentos analíticos na Fase 02."""

    # 'def __init__(...)' constrói a instância mapeando os diretórios oficiais e instanciando os especialistas.
    def __init__(self, raiz_projeto: Path) -> None:
        """Inicializa o orquestrador identificando dinamicamente a subpasta do banco de dados real."""
        # Armazena o endereço físico absoluto da pasta raiz do projeto de Machine Learning.
        self.raiz_projeto = raiz_projeto

        # RESOLUÇÃO CANÔNICA DO DIRETÓRIO DO BANCO DE DADOS ATIVO:
        # Aponta para o diretório de arquivos delimitados CSV.
        pasta_csv_base = self.raiz_projeto / "dados" / "brutos" / "csv"

        # Detecta dinamicamente as subpastas isoladas existentes (ex: 'mercado_vencedor/'), ignorando 'mocks'.
        subpastas_bancos = [
            p for p in pasta_csv_base.iterdir()
            if p.is_dir() and not p.name.startswith(".") and p.name != "mocks"
        ]

        # Se houver subpasta de banco de dados, ancora a esteira diretamente nela para consumo dos dados reais.
        self.pasta_dados_brutos = subpastas_bancos[0] if subpastas_bancos else pasta_csv_base
        self.nome_banco = self.pasta_dados_brutos.name

        # Constrói o caminho de saída raiz para a gravação dos laudos e figuras analíticas dos setores.
        self.pasta_relatorios = self.raiz_projeto / "relatorios"
        self.pasta_relatorios.mkdir(parents=True, exist_ok=True)

        logging.info("Orquestrador Raio-X conectado à base: '%s' (%s)", self.nome_banco, self.pasta_dados_brutos)

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
        laudo_comercial = self.analisador_comercial.executar_diagnostico_completo()
        laudo_financeiro = self.analisador_financeiro.executar_diagnostico_completo()
        laudo_compras = self.analisador_compras.executar_diagnostico_completo()
        laudo_estoque = self.analisador_estoque.executar_diagnostico_completo()
        laudo_contabil = self.analisador_contabil.executar_diagnostico_completo()
        laudo_fiscal = self.analisador_fiscal.executar_diagnostico_completo()
        laudo_producao = self.analisador_producao.executar_diagnostico_completo()
        laudo_logistica = self.analisador_logistica.executar_diagnostico_completo()
        laudo_pos_venda = self.analisador_pos_venda.executar_diagnostico_completo()
        laudo_rh = self.analisador_rh.executar_diagnostico_completo()

        # 3. Consolidação do Prontuário Executivo 360 Graus integrando a saúde técnica e os 10 setores.
        prontuario_executivo: Dict[str, Any] = {
            "cliente_ativo": self.nome_banco,
            "saude_estrutural_dados": laudo_estrutural,
            "comercial": laudo_comercial,
            "financeiro": laudo_financeiro,
            "compras": laudo_compras,
            "estoque": laudo_estoque,
            "contabil": laudo_contabil,
            "fiscal": laudo_fiscal,
            "producao": laudo_producao,
            "logistica": laudo_logistica,
            "pos_venda": laudo_pos_venda,
            "recursos_humanos": laudo_rh,
        }

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