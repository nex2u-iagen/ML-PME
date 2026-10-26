"""Módulo Construtor da Tabela Analítica de Modelagem - ABT (Fase 3.2).

Responsável por ler os Data Marts consolidados de BI, executar agregações
transversais no grão atômico de cliente e consolidar a matriz de features
com a definição estrita da variável-alvo (target) de inadimplência.
"""

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


# 'class' declara o molde especializado do construtor de ABT orientado a objetos.
class ConstrutorABTCliente:
    """Classe responsável por consolidar os Data Marts em uma Tabela Analítica de
    Modelagem (ABT).
    """

    # 'def' define o método construtor '__init__', acionado na alocação da instância em
    # memória RAM.
    # 'self' referencia a própria instância construída.
    # 'pasta_bi: Path' recebe o endereço onde residem as tabelas consolidadas da trilha
    # de BI.
    def __init__(self, pasta_bi: Path) -> None:
        """Inicializa o construtor da ABT acoplando o leitor de arquivos do núcleo.

        Args:
            pasta_bi (Path): Diretório contendo os arquivos CSV higienizados dos Data
            Marts de BI.
        """
        # Armazena o endereço físico dos dados de BI no atributo do próprio objeto.
        self.pasta_bi = pasta_bi

        # Instancia a ferramenta de leitura desacoplada do núcleo compartilhado por
        # composição orientada a objetos.
        self.leitor = LeitorArquivosTabulares()

    # 'def' define o método principal que consolida as features transversais por
    # cliente.
    # '-> pd.DataFrame' documenta que a função devolverá uma tabela analítica plana do
    # pandas.
    def construir_abt(self) -> pd.DataFrame:
        """Cruza dados comerciais, financeiros e cadastrais consolidando uma linha por
        cliente.

        Returns:
            pd.DataFrame: Tabela Analítica de Modelagem contendo variáveis preditivas
            (X) e alvo (y).
        """
        # Monta os caminhos dos arquivos de Data Marts gerados na trilha de BI.
        caminho_comercial = self.pasta_bi / "data_mart_comercial.csv"
        # Constrói o caminho para a tabela de títulos financeiros em atraso.
        caminho_financeiro = self.pasta_bi / "data_mart_financeiro_titulos.csv"

        # Carrega os Data Marts higienizados utilizando o leitor do núcleo
        # compartilhado.
        df_comercial = self.leitor.carregar_tabela(caminho_comercial)
        # Carrega a tabela financeira de duplicatas.
        df_financeiro = self.leitor.carregar_tabela(caminho_financeiro)

        # 1. Agrupamento Comercial: consolida métricas transacionais no nível do cliente
        # (grão atômico).
        # 'faturamento_total_reais': soma de toda a receita faturada para o cliente.
        # 'ticket_medio_reais': valor médio desembolsado por pedido.
        # 'total_pedidos_comprados': quantidade de compras realizadas no histórico.
        # 'prazo_medio_acordado_dias': média de prazo de pagamento concedido nas vendas.
        agrupado_comercial = (
            df_comercial.groupby("codigo_cliente")
            .agg(
                faturamento_total_reais=("valor_faturado_reais", "sum"),
                ticket_medio_reais=("valor_faturado_reais", "mean"),
                total_pedidos_comprados=("codigo_pedido", "count"),
                prazo_medio_acordado_dias=("prazo_pagamento_acordado_dias", "mean"),
                razao_social_cliente=("razao_social_cliente", "first"),
                segmento_mercado=("segmento_mercado", "first"),
                limite_credito_reais=("limite_credito_concedido_reais", "first"),
            )
            .reset_index()
        )

        # 2. Agrupamento Financeiro: apura o histórico de inadimplência e títulos
        # vencidos por cliente.
        # 'alvo_inadimplente': verifica se o cliente possui algum título histórico
        # inadimplido (Target binário y).
        agrupado_financeiro = (
            df_financeiro.groupby("codigo_sacado_cliente")
            .agg(
                alvo_inadimplente=("flag_inadimplente_binario", "max"),
                total_titulos_emitidos=("numero_documento_titulo", "count"),
            )
            .reset_index()
        )

        # Renomeia a coluna chave do financeiro para viabilizar a junção relacional
        # perfeita.
        agrupado_financeiro = agrupado_financeiro.rename(
            columns={"codigo_sacado_cliente": "codigo_cliente"}
        )

        # Realiza a fusão relacional (INNER JOIN) unindo atributos comerciais ao
        # desfecho financeiro.
        df_abt = pd.merge(
            agrupado_comercial, agrupado_financeiro, on="codigo_cliente", how="inner"
        )

        # 'df_abt["alvo_inadimplente"].fillna(0).astype(int)' garante que clientes sem
        # atrasos tenham alvo 0.
        df_abt["alvo_inadimplente"] = df_abt["alvo_inadimplente"].fillna(0).astype(int)

        # Arredonda as variáveis numéricas contínuas para duas casas decimais.
        df_abt["faturamento_total_reais"] = df_abt["faturamento_total_reais"].round(2)
        df_abt["ticket_medio_reais"] = df_abt["ticket_medio_reais"].round(2)
        df_abt["prazo_medio_acordado_dias"] = df_abt["prazo_medio_acordado_dias"].round(
            1
        )

        # Retorna a Tabela Analítica de Modelagem (ABT) consolidada no grão de cliente.
        return df_abt
