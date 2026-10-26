"""Módulo Orquestrador do Raio-X Empresarial 360 Graus (Fase 02 Completa).

Coordena a execução unificada do diagnóstico estrutural de saúde de dados
e das análises exploratórias dos 10 departamentos de negócios da PME:
Comercial, Financeiro, Compras, Estoque, Contábil, Fiscal, Produção,
Logística, Pós-Venda e Recursos Humanos.
"""

# 'import logging' importa o sistema de rastreabilidade para auditoria técnica no
# console.
import logging

# 'from pathlib import Path' disponibiliza a manipulação portável de diretórios no
# sistema operacional.
from pathlib import Path

# 'from typing import Any, Dict' importa dicionários tipados da biblioteca padrão para
# documentação do prontuário[cite: 5].
from typing import Any

# Importa o especialista do departamento Comercial (d01) da pasta 'departamentos/'[cite:
# 5].
from src.etapas.fase_02_exploracao.departamentos.d01_comercial import (
    AnalisadorComercial,
)

# Importa o especialista do departamento Financeiro (d02) da pasta
# 'departamentos/'[cite: 5].
from src.etapas.fase_02_exploracao.departamentos.d02_financeiro import (
    AnalisadorFinanceiro,
)

# Importa o especialista do departamento de Compras (d03) da pasta
# 'departamentos/'[cite: 5].
from src.etapas.fase_02_exploracao.departamentos.d03_compras import (
    AnalisadorCompras,
)

# Importa o especialista do departamento de Estoque (d04) da pasta
# 'departamentos/'[cite: 5].
from src.etapas.fase_02_exploracao.departamentos.d04_estoque import (
    AnalisadorEstoque,
)

# Importa o especialista do departamento Contábil (d05) da pasta 'departamentos/'[cite:
# 5].
from src.etapas.fase_02_exploracao.departamentos.d05_contabil import (
    AnalisadorContabil,
)

# Importa o especialista do departamento Fiscal (d06) da pasta 'departamentos/'[cite:
# 5].
from src.etapas.fase_02_exploracao.departamentos.d06_fiscal import (
    AnalisadorFiscal,
)

# Importa o especialista do departamento de Produção (d07) da pasta
# 'departamentos/'[cite: 5].
from src.etapas.fase_02_exploracao.departamentos.d07_producao import (
    AnalisadorProducao,
)

# Importa o especialista do departamento de Logística (d08) da pasta
# 'departamentos/'[cite: 5].
from src.etapas.fase_02_exploracao.departamentos.d08_logistica import (
    AnalisadorLogistica,
)

# Importa o especialista do departamento de Pós-Venda (d09) da pasta
# 'departamentos/'[cite: 5].
from src.etapas.fase_02_exploracao.departamentos.d09_pos_venda import (
    AnalisadorPosVenda,
)

# Importa o especialista do departamento de Recursos Humanos (d10) da pasta
# 'departamentos/'[cite: 5].
from src.etapas.fase_02_exploracao.departamentos.d10_recursos_humanos import (
    AnalisadorRecursosHumanos,
)

# 'from src...' importa o auditor estrutural de tipos, nulos e duplicatas macro da Fase
# 02[cite: 5].
from src.etapas.fase_02_exploracao.etapa_02_diagnostico_geral import (
    AuditorSaudeDados,
)

# 'logging.basicConfig' parametriza a formatação dos logs de auditoria técnica no
# console[cite: 5].
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class OrquestradorRaioXEmpresarial' declara a classe de orquestração mestre da Fase 2
# do CRISP-DM[cite: 5].
class OrquestradorRaioXEmpresarial:
    """Classe responsável por coordenar a triagem e os 10 departamentos analíticos na
    Fase 02[cite: 5].
    """

    # 'def __init__(...)' instancia o orquestrador configurando os caminhos oficiais e
    # compondo os especialistas[cite: 5].
    def __init__(self, raiz_projeto: Path) -> None:
        """Inicializa o orquestrador configurando os caminhos oficiais de dados e
        relatórios[cite: 5].

        Args:
            raiz_projeto (Path): Caminho absoluto da pasta raiz do projeto de Machine
            Learning[cite: 5].
        """
        # Armazena o endereço absoluto da pasta raiz do repositório no sistema
        # operacional[cite: 5].
        self.raiz_projeto = raiz_projeto

        # Constrói o caminho oficial onde residem os arquivos CSV brutos extraídos do
        # ERP[cite: 5].
        self.pasta_dados_brutos = self.raiz_projeto / "dados" / "brutos" / "csv"

        # Constrói o caminho de saída raiz para a gravação dos laudos e figuras
        # analíticas dos setores[cite: 5].
        self.pasta_relatorios = self.raiz_projeto / "relatorios" / "figuras"

        # Garante a criação da pasta física de relatórios no disco caso ainda não
        # exista[cite: 5].
        self.pasta_relatorios.mkdir(parents=True, exist_ok=True)

        # 1. Auditor Estrutural Geral de Saúde de Dados (Validação mecânica macro)[cite:
        # 4, 5]
        self.auditor_geral = AuditorSaudeDados(
            pasta_dados_brutos=self.pasta_dados_brutos
        )

        # 2. Bateria dos 10 Especialistas Departamentais (Composição Orientada a
        # Objetos)[cite: 5]
        # Instancia o especialista Comercial configurando suas pastas de trabalho[cite:
        # 5].
        self.analisador_comercial = AnalisadorComercial(
            self.pasta_dados_brutos, self.pasta_relatorios
        )
        # Instancia o especialista Financeiro configurando suas pastas de trabalho[cite:
        # 5].
        self.analisador_financeiro = AnalisadorFinanceiro(
            self.pasta_dados_brutos, self.pasta_relatorios
        )
        # Instancia o especialista de Compras configurando suas pastas de trabalho[cite:
        # 5].
        self.analisador_compras = AnalisadorCompras(
            self.pasta_dados_brutos, self.pasta_relatorios
        )
        # Instancia o especialista de Estoque configurando suas pastas de trabalho[cite:
        # 5].
        self.analisador_estoque = AnalisadorEstoque(
            self.pasta_dados_brutos, self.pasta_relatorios
        )
        # Instancia o especialista Contábil configurando suas pastas de trabalho[cite:
        # 5].
        self.analisador_contabil = AnalisadorContabil(
            self.pasta_dados_brutos, self.pasta_relatorios
        )
        # Instancia o especialista Fiscal configurando suas pastas de trabalho[cite: 5].
        self.analisador_fiscal = AnalisadorFiscal(
            self.pasta_dados_brutos, self.pasta_relatorios
        )
        # Instancia o especialista de Produção configurando suas pastas de
        # trabalho[cite: 5].
        self.analisador_producao = AnalisadorProducao(
            self.pasta_dados_brutos, self.pasta_relatorios
        )
        # Instancia o especialista de Logística configurando suas pastas de
        # trabalho[cite: 5].
        self.analisador_logistica = AnalisadorLogistica(
            self.pasta_dados_brutos, self.pasta_relatorios
        )
        # Instancia o especialista de Pós-Venda configurando suas pastas de
        # trabalho[cite: 5].
        self.analisador_pos_venda = AnalisadorPosVenda(
            self.pasta_dados_brutos, self.pasta_relatorios
        )
        # Instancia o especialista de Recursos Humanos configurando suas pastas de
        # trabalho[cite: 5].
        self.analisador_rh = AnalisadorRecursosHumanos(
            self.pasta_dados_brutos, self.pasta_relatorios
        )

        # Emite log confirmando a prontidão do orquestrador com os 10 departamentos
        # ativos[cite: 5].
        logging.info("Orquestrador do Raio-X pronto com os 10 departamentos ativos.")

    # 'def executar_raio_x_completo(...)' coordena a execução serial dos diagnósticos
    # setoriais[cite: 5].
    def executar_raio_x_completo(self) -> dict[str, Any]:
        """Executa a triagem macro e as perícias departamentais completas da Fase 02
        (CRISP-DM)[cite: 5].

        Returns:
            Dict[str, Any]: Prontuário executivo integrado de 360 graus da
            organização[cite: 5].
        """
        # Emite linha delimitadora visual para abertura dos registros no console[cite:
        # 5].
        logging.info(
            "================================================================="
        )
        # Registra no log o início oficial do processamento unificado da Fase 2[cite:
        # 5].
        logging.info("=== INICIANDO EXECUÇÃO COMPLETA DO RAIO-X EMPRESARIAL 360° ===")
        # Emite linha delimitadora visual no console[cite: 5].
        logging.info(
            "================================================================="
        )

        # 1. Executa o diagnóstico macro de volumetria, nulos, tipos e duplicatas via
        # AuditorSaudeDados[cite: 4, 5].
        laudo_estrutural = self.auditor_geral.executar_diagnostico_completo()

        # 2. Executa sequencialmente o diagnóstico completo de cada um dos 10
        # departamentos de negócios[cite: 5].
        # Captura o laudo do departamento Comercial contendo métricas tabulares e
        # caminhos de figuras[cite: 5].
        laudo_comercial = self.analisador_comercial.executar_diagnostico_completo()

        # Captura o laudo do departamento Financeiro (ajuste da linha órfã
        # corrigida)[cite: 5].
        laudo_financeiro = self.analisador_financeiro.executar_diagnostico_completo()

        # Captura o laudo do departamento de Compras[cite: 5].
        laudo_compras = self.analisador_compras.executar_diagnostico_completo()

        # Captura o laudo do departamento de Estoque[cite: 5].
        laudo_estoque = self.analisador_estoque.executar_diagnostico_completo()

        # Captura o laudo do departamento Contábil[cite: 5].
        laudo_contabil = self.analisador_contabil.executar_diagnostico_completo()

        # Captura o laudo do departamento Fiscal[cite: 5].
        laudo_fiscal = self.analisador_fiscal.executar_diagnostico_completo()

        # Captura o laudo do departamento de Produção[cite: 5].
        laudo_producao = self.analisador_producao.executar_diagnostico_completo()

        # Captura o laudo do departamento de Logística[cite: 5].
        laudo_logistica = self.analisador_logistica.executar_diagnostico_completo()

        # Captura o laudo do departamento de Pós-Venda[cite: 5].
        laudo_pos_venda = self.analisador_pos_venda.executar_diagnostico_completo()

        # Captura o laudo do departamento de Recursos Humanos[cite: 5].
        laudo_rh = self.analisador_rh.executar_diagnostico_completo()

        # 3. Consolidação do Prontuário Executivo 360 Graus integrando a saúde técnica e
        # os 10 setores[cite: 5].
        prontuario_executivo: dict[str, Any] = {
            "saude_estrutural_dados": laudo_estrutural,
            "comercial": laudo_comercial,
            # Chave restabelecida para garantir a integridade dos 10 setores[cite: 5].
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

        # Emite linha delimitadora visual para encerramento dos registros[cite: 5].
        logging.info(
            "================================================================="
        )
        # Registra a confirmação da auditoria completa dos 10 departamentos de
        # negócios[cite: 5].
        logging.info("=== RAIO-X CONCLUÍDO: 10 DEPARTAMENTOS AUDITADOS COM SUCESSO ===")
        # Informa o local físico onde os gráficos vetoriais foram disponibilizados[cite:
        # 5].
        logging.info(
            "=== GRÁFICOS E LAUDOS DISPONÍVEIS EM relatorios/figuras/      ==="
        )
        # Emite linha delimitadora visual no console[cite: 5].
        logging.info(
            "================================================================="
        )

        # Retorna o dicionário com o prontuário executivo unificado da organização[cite:
        # 5].
        return prontuario_executivo


# Bloco de execução direta via linha de comandos para testes manuais do módulo[cite: 5].
if __name__ == "__main__":
    # Obtém o caminho absoluto da raiz do repositório subindo 4 níveis no sistema de
    # arquivos[cite: 4, 5].
    caminho_raiz = Path(__file__).resolve().parent.parent.parent.parent

    # Instancia o maestro orquestrador passando o endereço raiz do projeto[cite: 5].
    maestro_fase_02 = OrquestradorRaioXEmpresarial(raiz_projeto=caminho_raiz)

    # Dispara a auditoria de 360 graus e captura o prontuário executivo da Fase 2[cite:
    # 5].
    laudo_geral = maestro_fase_02.executar_raio_x_completo()
