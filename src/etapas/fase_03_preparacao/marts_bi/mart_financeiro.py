"""Construtor especializado do Data Mart Financeiro para BI."""

# 'from' indica a biblioteca de origem; 'pathlib' manipula diretórios e arquivos de
# forma orientada a objetos.
from pathlib import Path

# 'import' traz a biblioteca externa 'pandas' para manipulação tabular de títulos e
# cobranças.
# 'as' define o apelido clássico 'pd'.
import pandas as pd

# 'from' acessa o leitor padronizado no núcleo de acesso a dados do projeto.
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares


# 'class' declara o molde especializado do construtor financeiro.
class ConstrutorMartFinanceiro:
    """Classe responsável exclusiva pela estruturação de títulos, aging e liquidez
    para BI.
    """

    # 'def' define o método construtor '__init__'.
    def __init__(self, pasta_brutos: Path) -> None:
        """Inicializa o construtor financeiro acoplando o leitor de arquivos do núcleo.

        Args:
            pasta_brutos (Path): Diretório contendo os arquivos CSV brutos do ERP.
        """
        # Armazena o endereço físico dos dados brutos no atributo do objeto.
        self.pasta_brutos = pasta_brutos

        # Instancia a ferramenta de leitura do núcleo compartilhado.
        self.leitor = LeitorArquivosTabulares()

    # 'def' define a função que estrutura as duplicatas e réguas de cobrança.
    def processar(self) -> pd.DataFrame:
        """Estrutura as contas a receber com réguas de aging e termos de tesouraria.

        Returns:
            pd.DataFrame: Tabela tratada pronta para dashboards de fluxo de caixa e
            inadimplência.
        """
        # Monta o caminho do arquivo de títulos e vendas no diretório de dados brutos.
        caminho_pedidos = self.pasta_brutos / "erp_pedidos_vendas.csv"

        # Carrega os dados utilizando o leitor oficial do núcleo.
        df_titulos = self.leitor.carregar_tabela(caminho_pedidos)

        # Converte a coluna de data para o formato datetime oficial do pandas.
        df_titulos["data_pedido"] = pd.to_datetime(df_titulos["data_pedido"])

        # Função interna de categorização do envelhecimento da dívida (Aging List).
        def categorizar_faixa(status: str) -> str:
            if status == "Pago":
                return "00 - Título Liquidado / Em Dia"
            elif status == "Atrasado":
                return "01 - Atraso Leve (Abaixo de 30 dias)"
            return "02 - Inadimplência Crítica (Risco de Calote)"

        # Aplica a categorização de régua de cobrança em cada linha da tabela.
        df_titulos["faixa_envelhecimento_divida"] = df_titulos[
            "status_pagamento"
        ].apply(categorizar_faixa)

        # Arredonda o valor nominal do título para duas casas decimais em centavos.
        df_titulos["valor_total"] = df_titulos["valor_total"].round(2)

        # Traduz os nomes das colunas técnicas para termos de gestão de cobrança e
        # tesouraria.
        colunas_amigaveis_financeiro = {
            "id_pedido": "numero_documento_titulo",
            "id_cliente": "codigo_sacado_cliente",
            "data_pedido": "data_emissao_titulo",
            "valor_total": "valor_nominal_titulo_reais",
            "status_pagamento": "status_posicao_cobranca",
            "inadimplente": "flag_inadimplente_binario",
        }

        # Renomeia as colunas e retorna o DataFrame financeiro tratado.
        return df_titulos.rename(columns=colunas_amigaveis_financeiro)
