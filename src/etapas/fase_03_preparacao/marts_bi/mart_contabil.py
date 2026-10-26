"""Construtor especializado do Data Mart Contábil e Controladoria para BI."""

# 'from' indica a biblioteca de origem; 'pathlib' manipula diretórios e arquivos de
# forma orientada a objetos.
# 'import' traz a classe 'Path' para gerenciar endereços de pastas compatíveis com
# Windows, Linux e macOS.
from pathlib import Path

# 'import' traz a biblioteca externa 'pandas', padrão mundial para manipulação de
# tabelas em memória.
# 'as' define o apelido clássico 'pd' para facilitar operações sobre matrizes e
# DataFrames.
import pandas as pd

# 'from' navega até o submódulo de acesso a dados do nosso núcleo compartilhado.
# 'import' traz a classe 'LeitorArquivosTabulares', garantindo o reaproveitamento de
# código e baixo acoplamento.
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares


# 'class' é a palavra-chave que declara um novo molde estrutural orientado a objetos.
# 'ConstrutorMartContabil' define com máxima clareza semântica a missão única de
# estruturar dados contábeis.
class ConstrutorMartContabil:
    """Classe responsável exclusiva pela estruturação de DRE, custos e margem de
    contribuição para BI.
    """

    # 'def' define o método especial construtor '__init__', acionado na instanciação da
    # classe em memória RAM.
    # 'self' referencia a própria instância acessando seus atributos internos.
    # 'pasta_brutos: Path' recebe o endereço onde residem as tabelas brutas do ERP.
    # '-> None' documenta formalmente que o método inicializador não retorna dados.
    def __init__(self, pasta_brutos: Path) -> None:
        """Inicializa o construtor contábil acoplando o leitor de arquivos do núcleo.

        Args:
            pasta_brutos (Path): Diretório contendo os arquivos CSV brutos do ERP.
        """
        # Armazena o endereço físico dos dados brutos no atributo do próprio objeto.
        self.pasta_brutos = pasta_brutos

        # Instancia a ferramenta de leitura desacoplada do núcleo compartilhado por
        # composição orientada a objetos.
        self.leitor = LeitorArquivosTabulares()

    # 'def' define o método principal que executa a apuração das margens e DRE
    # gerencial.
    # '-> pd.DataFrame' documenta que a função devolverá uma tabela estruturada do
    # pandas.
    def processar(self) -> pd.DataFrame:
        """Carrega transações, deriva CMV, despesas variáveis e apura a margem de
        contribuição.

        Returns:
            pd.DataFrame: Data Mart Contábil consolidado com estrutura de DRE gerencial
            em reais.
        """
        # Monta o caminho do arquivo de pedidos de venda no diretório de dados brutos.
        caminho_pedidos = self.pasta_brutos / "erp_pedidos_vendas.csv"

        # Carrega a tabela de pedidos utilizando o leitor oficial do núcleo
        # compartilhado.
        df_pedidos = self.leitor.carregar_tabela(caminho_pedidos)

        # '.copy()' cria uma cópia independente em memória para não alterar a tabela
        # original.
        df_contabil = df_pedidos.copy()

        # O Custo das Mercadorias Vendidas (CMV) em PMEs comerciais representa em média
        # 55% da receita bruta.
        # Multiplica o valor total por 0.55 e arredonda em centavos para derivar o custo
        # fabril/aquisição.
        df_contabil["custo_cmv_reais"] = (df_contabil["valor_total"] * 0.55).round(2)

        # As despesas variáveis com tributos sobre vendas e comissões representam cerca
        # de 12% da receita.
        # Multiplica o valor total por 0.12 para mapear os custos que só ocorrem quando
        # há venda.
        df_contabil["despesas_variaveis_reais"] = (
            df_contabil["valor_total"] * 0.12
        ).round(2)

        # Margem de Contribuição em Reais = Receita Bruta - Custo da Mercadoria (CMV) -
        # Despesas Variáveis.
        # É o montante líquido que sobra de cada pedido para ajudar a pagar as despesas
        # fixas da empresa.
        df_contabil["margem_contribuicao_reais"] = (
            df_contabil["valor_total"]
            - df_contabil["custo_cmv_reais"]
            - df_contabil["despesas_variaveis_reais"]
        ).round(2)

        # Índice de Margem de Contribuição (IMC %): percentual que a margem representa
        # sobre a receita bruta.
        df_contabil["indice_margem_percentual"] = (
            (df_contabil["margem_contribuicao_reais"] / df_contabil["valor_total"])
            * 100
        ).round(2)

        # 'pd.to_datetime' converte a coluna de data para formato oficial de data e hora
        # do pandas.
        df_contabil["data_pedido"] = pd.to_datetime(df_contabil["data_pedido"])

        # Mapeia os cabeçalhos para a nomenclatura padrão do DRE (Demonstrativo do
        # Resultado do Exercício).
        colunas_amigaveis_contabil = {
            # Identificação do pedido no faturamento.
            "id_pedido": "numero_documento_pedido",
            # Código do cliente comprador.
            "id_cliente": "codigo_cliente",
            # Data contábil da competência do faturamento.
            "data_pedido": "data_competencia_faturamento",
            # Receita bruta total faturada na nota.
            "valor_total": "receita_bruta_faturada_reais",
            # Custo direto das mercadorias vendidas.
            "custo_cmv_reais": "custo_mercadoria_vendida_cmv_reais",
            # Despesas variáveis com deduções e comissões.
            "despesas_variaveis_reais": "despesas_variaveis_venda_reais",
            # Margem bruta de contribuição unitária.
            "margem_contribuicao_reais": "margem_contribuicao_reais",
            # Margem de contribuição em escala percentual (%).
            "indice_margem_percentual": "indice_margem_contribuicao_pct",
        }

        # Renomeia as colunas selecionadas para consumo gerencial.
        df_contabil = df_contabil.rename(columns=colunas_amigaveis_contabil)

        # Lista com as colunas essenciais da visão contábil para compor o Data Mart
        # limpo.
        colunas_selecionadas = [
            "numero_documento_pedido",
            "codigo_cliente",
            "data_competencia_faturamento",
            "receita_bruta_faturada_reais",
            "custo_mercadoria_vendida_cmv_reais",
            "despesas_variaveis_venda_reais",
            "margem_contribuicao_reais",
            "indice_margem_contribuicao_pct",
        ]

        # Retorna apenas as colunas estruturadas do DRE gerencial.
        return df_contabil[colunas_selecionadas]
