"""Módulo Orquestrador Mestre de Dados para Business Intelligence (Fase 3.1 Completa).

Coordena os 10 construtores departamentais especializados de Data Marts:
Comercial, Estoque, Financeiro, Compras, Contábil, Fiscal, Produção,
Logística, Pós-Venda e Recursos Humanos, exportando todas as tabelas
higienizadas e prontas para conexão com dashboards em dados/processados/bi/.
"""

# 'import' traz o módulo 'logging' nativo para registrar mensagens operacionais no
# console com data e hora.
import logging

# 'from' acessa 'pathlib'; 'import' traz 'Path' para gerenciamento de diretórios no
# sistema operacional.
from pathlib import Path

# 'from' acessa 'typing' da biblioteca padrão para anotação de tipos de dicionários
# estruturados.
# 'from' importa os 10 construtores especialistas desacoplados da subpasta 'marts_bi/'.
from src.etapas.fase_03_preparacao.marts_bi.mart_comercial import (
    ConstrutorMartComercial,
)
from src.etapas.fase_03_preparacao.marts_bi.mart_compras import ConstrutorMartCompras
from src.etapas.fase_03_preparacao.marts_bi.mart_contabil import ConstrutorMartContabil
from src.etapas.fase_03_preparacao.marts_bi.mart_estoque import ConstrutorMartEstoque
from src.etapas.fase_03_preparacao.marts_bi.mart_financeiro import (
    ConstrutorMartFinanceiro,
)
from src.etapas.fase_03_preparacao.marts_bi.mart_fiscal import ConstrutorMartFiscal
from src.etapas.fase_03_preparacao.marts_bi.mart_logistica import (
    ConstrutorMartLogistica,
)
from src.etapas.fase_03_preparacao.marts_bi.mart_pos_venda import ConstrutorMartPosVenda
from src.etapas.fase_03_preparacao.marts_bi.mart_producao import ConstrutorMartProducao
from src.etapas.fase_03_preparacao.marts_bi.mart_rh import ConstrutorMartRH

# 'logging.basicConfig' configura a formatação e a severidade dos logs exibidos no
# terminal.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara o orquestrador mestre dos 10 departamentos de BI.
class OrquestradorDadosBI:
    """Classe responsável por coordenar a exportação de todos os 10 Data Marts de BI
    da PME.
    """

    # 'def' define o método construtor '__init__'.
    def __init__(self, pasta_dados_brutos: Path, pasta_saida_bi: Path) -> None:
        """Inicializa o orquestrador configurando pastas e instanciando os 10
        especialistas.

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas brutas do ERP.
            pasta_saida_bi (Path): Diretório onde os Data Marts de BI serão gravados.
        """
        # Armazena o endereço da pasta de saída no atributo do próprio objeto.
        self.pasta_saida_bi = pasta_saida_bi

        # Garante a criação física da pasta 'dados/processados/bi/' no disco rígido.
        self.pasta_saida_bi.mkdir(parents=True, exist_ok=True)

        # Injeta os 10 construtores especialistas passando o diretório de dados brutos
        # por composição orientada a objetos.
        self.mart_comercial = ConstrutorMartComercial(pasta_dados_brutos)
        self.mart_estoque = ConstrutorMartEstoque(pasta_dados_brutos)
        self.mart_financeiro = ConstrutorMartFinanceiro(pasta_dados_brutos)
        self.mart_compras = ConstrutorMartCompras(pasta_dados_brutos)
        self.mart_contabil = ConstrutorMartContabil(pasta_dados_brutos)
        self.mart_fiscal = ConstrutorMartFiscal(pasta_dados_brutos)
        self.mart_producao = ConstrutorMartProducao(pasta_dados_brutos)
        self.mart_logistica = ConstrutorMartLogistica(pasta_dados_brutos)
        self.mart_pos_venda = ConstrutorMartPosVenda(pasta_dados_brutos)
        self.mart_rh = ConstrutorMartRH(pasta_dados_brutos)

        # Emite log confirmando a prontidão do orquestrador mestre de BI.
        logging.info(
            "Orquestrador de BI pronto com todos os 10 departamentos ativos. Destino:"
            "%s",
            self.pasta_saida_bi,
        )

    # 'def' define o método que dispara a execução sequencial completa dos 10 Data
    # Marts.
    def executar_preparacao_bi_completa(self) -> dict[str, Path]:
        """Coordena a geração e a persistência dos 10 Data Marts analíticos de BI da
        companhia.

        Returns:
            Dict[str, Path]: Dicionário com os nomes dos Data Marts e seus respectivos
            arquivos gravados no disco.
        """
        logging.info(
            "================================================================="
        )
        logging.info(
            "=== INICIANDO FASE 3.1: ORQUESTRAÇÃO COMPLETA DOS 10 DATA MARTS ==="
        )
        logging.info(
            "================================================================="
        )

        # 1. Processa o Data Mart Comercial de Vendas e Clientes.
        df_comercial = self.mart_comercial.processar()
        caminho_comercial = self.pasta_saida_bi / "data_mart_comercial.csv"
        df_comercial.to_csv(caminho_comercial, index=False)
        logging.info("BI — 01. Comercial gravado: %d linhas.", len(df_comercial))

        # 2. Processa o Data Mart de Estoque e Armazenagem (Curva ABC).
        df_estoque = self.mart_estoque.processar()
        caminho_estoque = self.pasta_saida_bi / "data_mart_estoque_materiais.csv"
        df_estoque.to_csv(caminho_estoque, index=False)
        logging.info("BI — 02. Estoque gravado: %d SKUs.", len(df_estoque))

        # 3. Processa o Data Mart Financeiro de Títulos e Cobrança.
        df_financeiro = self.mart_financeiro.processar()
        caminho_financeiro = self.pasta_saida_bi / "data_mart_financeiro_titulos.csv"
        df_financeiro.to_csv(caminho_financeiro, index=False)
        logging.info("BI — 03. Financeiro gravado: %d títulos.", len(df_financeiro))

        # 4. Processa o Data Mart de Compras e Fornecedores.
        df_compras = self.mart_compras.processar()
        caminho_compras = self.pasta_saida_bi / "data_mart_compras_suprimentos.csv"
        df_compras.to_csv(caminho_compras, index=False)
        logging.info("BI — 04. Compras gravado: %d ordens.", len(df_compras))

        # 5. Processa o Data Mart Contábil de Margem e DRE Gerencial.
        df_contabil = self.mart_contabil.processar()
        caminho_contabil = self.pasta_saida_bi / "data_mart_contabil_margem.csv"
        df_contabil.to_csv(caminho_contabil, index=False)
        logging.info("BI — 05. Contábil gravado: %d apurações.", len(df_contabil))

        # 6. Processa o Data Mart Fiscal de Tributos e Alíquotas Efetivas.
        df_fiscal = self.mart_fiscal.processar()
        caminho_fiscal = self.pasta_saida_bi / "data_mart_fiscal_tributos.csv"
        df_fiscal.to_csv(caminho_fiscal, index=False)
        logging.info("BI — 06. Fiscal gravado: %d notas fiscais.", len(df_fiscal))

        # 7. Processa o Data Mart de Produção Industrial e Chão de Fábrica.
        df_producao = self.mart_producao.processar()
        caminho_producao = self.pasta_saida_bi / "data_mart_producao_operacoes.csv"
        df_producao.to_csv(caminho_producao, index=False)
        logging.info("BI — 07. Produção gravado: %d ordens fabris.", len(df_producao))

        # 8. Processa o Data Mart de Logística, Fretes e Nível de Serviço OTIF.
        df_logistica = self.mart_logistica.processar()
        caminho_logistica = self.pasta_saida_bi / "data_mart_logistica_expedicao.csv"
        df_logistica.to_csv(caminho_logistica, index=False)
        logging.info("BI — 08. Logística gravada: %d despachos.", len(df_logistica))

        # 9. Processa o Data Mart de Pós-Venda, Suporte e Satisfação CSAT.
        df_pos_venda = self.mart_pos_venda.processar()
        caminho_pos_venda = self.pasta_saida_bi / "data_mart_pos_venda_sac.csv"
        df_pos_venda.to_csv(caminho_pos_venda, index=False)
        logging.info("BI — 09. Pós-Venda gravado: %d tickets.", len(df_pos_venda))

        # 10. Processa o Data Mart de Recursos Humanos, Folha e Assiduidade.
        df_rh = self.mart_rh.processar()
        caminho_rh = self.pasta_saida_bi / "data_mart_recursos_humanos_folha.csv"
        df_rh.to_csv(caminho_rh, index=False)
        logging.info("BI — 10. Recursos Humanos gravado: %d colaboradores.", len(df_rh))

        # Consolida os 10 artefatos gerados em um dicionário para governança da esteira
        # analítica.
        artefatos: dict[str, Path] = {
            "mart_comercial": caminho_comercial,
            "mart_estoque": caminho_estoque,
            "mart_financeiro": caminho_financeiro,
            "mart_compras": caminho_compras,
            "mart_contabil": caminho_contabil,
            "mart_fiscal": caminho_fiscal,
            "mart_producao": caminho_producao,
            "mart_logistica": caminho_logistica,
            "mart_pos_venda": caminho_pos_venda,
            "mart_recursos_humanos": caminho_rh,
        }

        logging.info(
            "================================================================="
        )
        logging.info(
            "=== FASE 3.1 CONCLUÍDA COM SUCESSO: 10 DATA MARTS DISPONÍVEIS ==="
        )
        logging.info("=== DESTINO: %s ===", self.pasta_saida_bi)
        logging.info(
            "================================================================="
        )

        # Retorna o dicionário com os 10 caminhos consolidados.
        return artefatos


# Bloco padrão para execução direta via terminal como script Python.
if __name__ == "__main__":
    # Localiza a raiz do repositório subindo 4 níveis a partir deste arquivo.
    raiz_do_projeto = Path(__file__).resolve().parent.parent.parent.parent

    # Aponta para a pasta onde a Fase 01 descarregou os arquivos CSV brutos do ERP.
    caminho_brutos = raiz_do_projeto / "dados" / "brutos" / "csv"

    # Aponta para o diretório oficial de BI dentro de dados processados.
    caminho_bi = raiz_do_projeto / "dados" / "processados" / "bi"

    # Instancia o orquestrador mestre e executa a esteira dos 10 departamentos de BI.
    orquestrador_bi = OrquestradorDadosBI(
        pasta_dados_brutos=caminho_brutos,
        pasta_saida_bi=caminho_bi,
    )
    tabelas_geradas = orquestrador_bi.executar_preparacao_bi_completa()
