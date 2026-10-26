"""Construtor especializado do Data Mart Comercial para BI."""

# 'from' indica a biblioteca de origem; 'pathlib' manipula diretórios e arquivos
# orientados a objetos.
from pathlib import Path

# 'import' traz a biblioteca externa 'pandas' para manipulação relacional de dados.
# 'as' define o apelido clássico 'pd' para encurtar a sintaxe de comandos.
import pandas as pd

# 'from' acessa a ferramenta padronizada de leitura no núcleo compartilhado do projeto.
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares


# 'class' declara o molde especializado do construtor de vendas.
class ConstrutorMartComercial:
    """Classe responsável exclusiva pela transformação de pedidos e clientes para BI."""

    # 'def' define o método construtor '__init__'.
    # 'self' referencia a própria instância construída em memória.
    # 'pasta_brutos: Path' recebe o endereço onde residem as tabelas brutas do ERP.
    def __init__(self, pasta_brutos: Path) -> None:
        """Inicializa o construtor comercial acoplando o leitor de arquivos do núcleo.

        Args:
            pasta_brutos (Path): Diretório contendo os arquivos CSV brutos do ERP.
        """
        # Armazena o caminho da pasta bruta no atributo interno do objeto.
        self.pasta_brutos = pasta_brutos

        # Instancia a ferramenta de leitura desacoplada do núcleo compartilhado.
        self.leitor = LeitorArquivosTabulares()

    # 'def' define a função que executa a fusão e higienização das vendas.
    def processar(self) -> pd.DataFrame:
        """Carrega, cruza e renomeia os pedidos com semântica corporativa de negócios.

        Returns:
            pd.DataFrame: Tabela tratada pronta para alimentar painéis de vendas.
        """
        # Constrói o caminho dos arquivos de pedidos e clientes no disco.
        caminho_pedidos = self.pasta_brutos / "erp_pedidos_vendas.csv"
        caminho_clientes = self.pasta_brutos / "erp_clientes.csv"

        # Carrega ambas as tabelas na memória utilizando o leitor do núcleo.
        df_pedidos = self.leitor.carregar_tabela(caminho_pedidos)
        df_clientes = self.leitor.carregar_tabela(caminho_clientes)

        # Converte a coluna de data para o formato datetime oficial do pandas.
        df_pedidos["data_pedido"] = pd.to_datetime(df_pedidos["data_pedido"])

        # Realiza a junção relacional (INNER JOIN) pela chave 'id_cliente'.
        df_comercial = pd.merge(df_pedidos, df_clientes, on="id_cliente", how="inner")

        # Deriva a competência mensal no padrão 'AAAA-MM' para filtros cronológicos no
        # BI.
        df_comercial["competencia_ano_mes"] = (
            df_comercial["data_pedido"].dt.to_period("M").astype(str)
        )

        # Deriva o ano civil inteiro para comparações temporais no dashboard.
        df_comercial["ano_civil"] = df_comercial["data_pedido"].dt.year

        # Padroniza as métricas monetárias com duas casas decimais em reais (R$).
        df_comercial["valor_total"] = df_comercial["valor_total"].round(2)
        df_comercial["limite_credito"] = df_comercial["limite_credito"].round(2)

        # Mapeia cabeçalhos técnicos para termos amigáveis de negócios.
        colunas_amigaveis = {
            "id_pedido": "codigo_pedido",
            "id_cliente": "codigo_cliente",
            "nome_fantasia": "razao_social_cliente",
            "segmento": "segmento_mercado",
            "data_pedido": "data_transacao",
            "valor_total": "valor_faturado_reais",
            "limite_credito": "limite_credito_concedido_reais",
            "dias_prazo_pagamento": "prazo_pagamento_acordado_dias",
            "status_pagamento": "situacao_cobranca",
            "inadimplente": "indicador_inadimplencia_binario",
        }

        # Renomeia as colunas e retorna o DataFrame comercial tratado.
        return df_comercial.rename(columns=colunas_amigaveis)
