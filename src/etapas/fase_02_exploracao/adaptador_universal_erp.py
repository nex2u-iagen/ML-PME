# 'from' indica a biblioteca ou módulo de onde extrairemos uma ferramenta específica.
# 'pathlib' é o módulo padrão do Python para manipulação orientada a objetos de caminhos
# no sistema de arquivos.
# 'import' traz a classe 'Path' para representar diretórios e caminhos compatíveis com
# Windows, Linux e Mac.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão do Python para suporte a
# anotações de tipagem estática (Type Hints).
# 'import' carrega 'List' e 'Optional' para documentar parâmetros e retornos de métodos.
from typing import List, Optional

# 'import' traz o módulo 'logging' da biblioteca padrão do Python para registro de
# auditoria técnica e mensagens operacionais no console.
import logging

# 'import' traz a biblioteca externa 'pandas', padrão da indústria de dados para
# manipulação tabular de matrizes em memória RAM.
# 'as' define o apelido universal 'pd' para economizar digitação no código.
import pandas as pd

# 'from' navega até o pacote interno de adaptadores da Fase 02 de exploração.
# 'import' traz a classe 'ResolvedorSemantico', especialista em catálogo de sinônimos e
# casamento léxico de nomes de tabelas e colunas.
from src.etapas.fase_02_exploracao.adaptadores.resolvedor_semantico import (
    ResolvedorSemantico,
)

# 'from' acessa o módulo onde reside o leitor seguro e defensivo de tabelas.
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares

# 'from' acessa o módulo onde reside o extrator especialista em vendas e faturamento.
# 'import' traz a classe 'ExtratorVendas' que aplica o recorte temporal dos últimos 12
# meses e a categorização de varejo.
from src.etapas.fase_02_exploracao.adaptadores.extrator_vendas import (
    ExtratorVendas,
)

# 'from' acessa o módulo especialista em recebíveis e crédito da empresa.
# 'import' traz a classe 'ExtratorFinanceiro' que computa o Aging real e faixas de
# atraso de títulos a receber.
from src.etapas.fase_02_exploracao.adaptadores.extrator_financeiro import (
    ExtratorFinanceiro,
)

# 'from' acessa o módulo especialista em inventário, almoxarifado e materiais.
# 'import' traz a classe 'ExtratorEstoque' que desagrega os códigos de SKU e custos
# unitários reais.
from src.etapas.fase_02_exploracao.adaptadores.extrator_estoque import (
    ExtratorEstoque,
)

# 'from' acessa o módulo especialista em fornecedores e despesas com compras.
# 'import' traz a classe 'ExtratorCompras' que mapeia os credores e compras reais em
# contas a pagar.
from src.etapas.fase_02_exploracao.adaptadores.extrator_compras import (
    ExtratorCompras,
)

# 'logging.basicConfig' parametriza a estética visual dos alertas e mensagens no console.
# 'level=logging.INFO' assegura que confirmações operacionais e avisos sejam exibidos.
# 'format' dita a máscara textual: carimbo de data/hora — [gravidade] — descrição do
# evento.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' é a palavra-chave reservada que declara uma nova classe orientada a objetos.
# 'AdaptadorUniversalERP' atua como a Fachada Unificada (Padrão de Projeto Facade).
# Sua responsabilidade única é prover uma porta de entrada limpa e consistente para os
# departamentos analíticos.
class AdaptadorUniversalERP:
    """Fachada unificada de dados de ERP com retrocompatibilidade total de métodos."""

    # 'def' define o método especial construtor '__init__', executado no momento da
    # instanciação da classe.
    # 'self' referencia a própria instância acessando seus atributos e ferramentas
    # internas.
    # 'pasta_dados_erp: Path' exige receber o caminho físico onde repousam os arquivos
    # CSV extraídos do ERP.
    # '-> None' atesta formalmente que o método inicializador não retorna dados.
    def __init__(self, pasta_dados_erp: Path) -> None:
        """Inicializa a fachada detectando automaticamente a subpasta do banco de dados

        e compondo os extratores de domínio.
        """
        # 'self.pasta_erp' armazena o caminho informado inicialmente na memória interna
        # do objeto.
        self.pasta_erp = pasta_dados_erp

        # Inspeciona se dentro do diretório fornecido existe uma subpasta isolada de
        # banco de dados real.
        # Filtra pastas ocultas iniciadas com ponto (.) e descarta a pasta de 'mocks'.
        subpastas = [
            p
            for p in self.pasta_erp.iterdir()
            if p.is_dir() and not p.name.startswith(".") and p.name != "mocks"
        ]

        # Se houver uma subpasta de banco de dados isolada (ex: 'mercado_vencedor/'),
        # ancora a busca nela.
        if subpastas:
            self.pasta_erp = subpastas[0]

        # Extrai o nome canônico do banco de dados/cliente para a governança de
        # relatórios e logs.
        self.nome_banco = self.pasta_erp.name

        # Instancia o especialista em casamento léxico e catálogo de sinônimos
        # compartilhado.
        self.resolvedor = ResolvedorSemantico()

        # COMPOSIÇÃO ORIENTADA A OBJETOS: Instancia cada um dos quatro especialistas de
        # negócio.
        # Passa como parâmetros o diretório físico dos arquivos CSV e o resolvedor
        # semântico.
        self._extrator_vendas = ExtratorVendas(
            pasta_dados=self.pasta_erp,
            resolvedor=self.resolvedor,
            leitor=LeitorArquivosTabulares(),
        )
        self._extrator_financeiro = ExtratorFinanceiro(
            self.pasta_erp, self.resolvedor
        )
        self._extrator_estoque = ExtratorEstoque(
            self.pasta_erp, self.resolvedor
        )
        self._extrator_compras = ExtratorCompras(
            self.pasta_erp, self.resolvedor
        )

        # Emite log informativo confirmando a inicialização da fachada unificada no
        # terminal.
        logging.info(
            "Fachada AdaptadorUniversalERP ativa. Banco: '%s' | Diretório: %s",
            self.nome_banco,
            self.pasta_erp.resolve(),
        )

    # -------------------------------------------------------------------------------------------------
    # MÉTODOS DE VENDAS E FATURAMENTO (COMERCIAL, CONTÁBIL, FISCAL, LOGÍSTICA,
    # PÓS-VENDA, RH)
    # -------------------------------------------------------------------------------------------------

    # 'def' define o método que atende à assinatura esperada pelos departamentos
    # analíticos.
    # '-> pd.DataFrame' documenta que o retorno desta função DEVE ser um DataFrame do
    # pandas.
    def obter_visao_vendas_comercial(self) -> pd.DataFrame:
        """Delega a extração das vendas canônicas com recorte de 12 meses para o

        ExtratorVendas.

        Método canônico que garante retrocompatibilidade com d01, d05, d06, d08, d09 e
        d10.
        """
        # Executa a chamada delegada diretamente para o método 'extrair_visao_canonica'
        # do especialista de vendas.
        return self._extrator_vendas.extrair_visao_canonica()

    # Método alternativo semântico que aponta para o mesmo procedimento de extração de
    # 12 meses.
    def obter_visao_vendas_ultimos_12_meses(self) -> pd.DataFrame:
        """Alias semântico explícito para a visão de vendas dos últimos 12 meses."""
        # Redireciona a chamada para o método canônico principal.
        return self.obter_visao_vendas_comercial()

    # -------------------------------------------------------------------------------------------------
    # MÉTODOS FINANCEIROS E RECEBÍVEIS (DEPARTAMENTO FINANCEIRO)
    # -------------------------------------------------------------------------------------------------

    # 'def' define o método de extração de títulos a receber canônicos.
    def obter_visao_financeira_receber(self) -> pd.DataFrame:
        """Delega a apuração de Aging real e títulos a receber para o

        ExtratorFinanceiro.
        """
        # Aciona o especialista de contas a receber retornando o DataFrame tratado com
        # faixas de atraso.
        return self._extrator_financeiro.extrair_visao_canonica()

    # Alias semântico para a visão de Aging financeiro real.
    def obter_visao_aging_financeiro_real(self) -> pd.DataFrame:
        """Alias semântico explícito para o cálculo de envelhecimento da dívida (Aging)."""
        # Redireciona a chamada para a função canônica financeira.
        return self.obter_visao_financeira_receber()

    # -------------------------------------------------------------------------------------------------
    # MÉTODOS DE ESTOQUE E MATERIAIS (DEPARTAMENTO DE ESTOQUE E PRODUÇÃO)
    # -------------------------------------------------------------------------------------------------

    # 'def' define o método de extração de produtos e saldos físicos.
    def obter_visao_estoque_materiais(self) -> pd.DataFrame:
        """Delega a desagregação física de SKUs e custos unitários para o

        ExtratorEstoque.
        """
        # Aciona o especialista de estoque retornando o inventário real ordenado por
        # capital imobilizado.
        return self._extrator_estoque.extrair_visao_canonica()

    # Alias semântico para a visão de Curva ABC com SKUs reais.
    def obter_visao_estoque_skus_reais(self) -> pd.DataFrame:
        """Alias semântico explícito para a Curva ABC com códigos de SKU e descrições

        reais.
        """
        # Redireciona a chamada para a função canônica de materiais.
        return self.obter_visao_estoque_materiais()

    # -------------------------------------------------------------------------------------------------
    # MÉTODOS DE COMPRAS E FORNECEDORES (DEPARTAMENTO DE COMPRAS)
    # -------------------------------------------------------------------------------------------------

    # 'def' define o método de extração de fornecedores reais e contas a pagar.
    def obter_visao_compras(self) -> pd.DataFrame:
        """Delega a extração de fornecedores e compras reais para o

        ExtratorCompras.
        """
        # Aciona o especialista de compras retornando as despesas reais com credores da
        # empresa.
        return self._extrator_compras.extrair_visao_canonica()

    # Alias semântico para a visão de fornecedores reais.
    def obter_visao_fornecedores_reais(self) -> pd.DataFrame:
        """Alias semântico explícito para a lista de fornecedores reais de contas a

        pagar.
        """
        # Redireciona a chamada para a função canônica de compras.
        return self.obter_visao_compras()

    # -------------------------------------------------------------------------------------------------
    # MÉTODOS DE APOIO E CONSULTA LÉXICA DELEGADA
    # -------------------------------------------------------------------------------------------------

    # 'def' define método utilitário para permitir busca de arquivos específicos por
    # departamentos de apoio.
    def _localizar_arquivo_por_sinonimos(
        self, entidade: str
    ) -> Optional[Path]:
        """Delega a busca de arquivos físicos no disco rígido ao ResolvedorSemantico."""
        # Transfere a responsabilidade para o resolvedor léxico.
        return self.resolvedor.localizar_arquivo_tabela(
            self.pasta_erp, entidade
        )

    # 'def' define método utilitário para permitir descoberta de nomes de colunas.
    def _resolver_coluna(
        self, colunas: List[str], papel: str
    ) -> Optional[str]:
        """Delega a identificação semântica de colunas ao ResolvedorSemantico."""
        # Transfere a responsabilidade para o resolvedor léxico.
        return self.resolvedor.resolver_coluna(colunas, papel)