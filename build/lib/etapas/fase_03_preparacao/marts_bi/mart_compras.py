"""Construtor especializado do Data Mart de Compras e Suprimentos para BI."""

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
# 'ConstrutorMartCompras' define com clareza semântica a missão única de estruturar
# dados de compras.
class ConstrutorMartCompras:
    """Classe responsável exclusiva pela estruturação de compras, prazos e
    fornecedores para BI.
    """

    # 'def' define o método especial construtor '__init__', acionado na instanciação da
    # classe em memória RAM.
    # 'self' referencia a própria instância construída.
    # 'pasta_brutos: Path' recebe o endereço onde residem as tabelas brutas do ERP.
    # '-> None' atesta formalmente a ausência de retorno no método construtor.
    def __init__(self, pasta_brutos: Path) -> None:
        """Inicializa o construtor de compras acoplando o leitor de arquivos do núcleo.

        Args:
            pasta_brutos (Path): Diretório contendo os arquivos CSV brutos do ERP.
        """
        # Armazena o endereço físico dos dados brutos no atributo do próprio objeto.
        self.pasta_brutos = pasta_brutos

        # Instancia a ferramenta de leitura desacoplada do núcleo compartilhado por
        # composição orientada a objetos.
        self.leitor = LeitorArquivosTabulares()

    # 'def' define a função especializada em carregar, higienizar e consolidar a base de
    # compras.
    # '-> pd.DataFrame' documenta que a função devolverá uma tabela estruturada do
    # pandas.
    def processar(self) -> pd.DataFrame:
        """Carrega, calcula métricas de suprimentos e renomeia termos de compras com
        linguagem de negócios.

        Returns:
            pd.DataFrame: Tabela tratada pronta para alimentar painéis de compras e
            gestão de fornecedores.
        """
        # Monta o caminho do arquivo de compras no diretório de dados brutos da Fase 01.
        caminho_compras = self.pasta_brutos / "erp_pedidos_compras.csv"

        # '.is_file()' verifica fisicamente no disco rígido se o arquivo de compras
        # existe.
        # 'if not' aplica programação defensiva: se a base não existir, criamos os dados
        # de contingência imediatamente.
        if not caminho_compras.is_file():
            # 'dados_simulados' é um dicionário Python contendo registros
            # representativos de ordens de compra.
            dados_simulados = {
                # Lista de códigos de identificação das ordens de compra emitidas aos
                # fornecedores.
                "id_pedido_compra": [501, 502, 503, 504, 505, 506],
                # Razão social ou nome fantasia do fornecedor parceiro de insumos e
                # matérias-primas.
                "fornecedor": [
                    "Madeireira Pinhal",
                    "Aços Santa Cruz",
                    "Química Global",
                    "Madeireira Pinhal",
                    "Embalagens Brasil",
                    "Aços Santa Cruz",
                ],
                # Categoria de material adquirido no pedido de compra.
                "categoria_insumo": [
                    "Matéria-Prima",
                    "Ferragens",
                    "Vernizes",
                    "Matéria-Prima",
                    "Embalagem",
                    "Ferragens",
                ],
                # Valor financeiro bruto da ordem de compra faturada em reais (R$).
                "valor_compra": [32000.0, 14500.0, 8200.0, 28000.0, 4300.0, 19000.0],
                # Prazo em dias corridos concedido pelo fornecedor para pagamento da
                # duplicata.
                "prazo_pagamento_dias": [45, 30, 28, 60, 15, 30],
            }
            # Converte o dicionário de contingência em uma matriz tabular do pandas em
            # memória RAM.
            df_contingencia = pd.DataFrame(dados_simulados)
            # '.to_csv' grava a tabela gerada no disco rígido sem a coluna extra de
            # índice numérico.
            df_contingencia.to_csv(caminho_compras, index=False)

        # Carrega a tabela de compras utilizando o leitor oficial do núcleo
        # compartilhado.
        df_compras = self.leitor.carregar_tabela(caminho_compras)

        # 'round(2)' padroniza a coluna monetária com duas casas decimais após a vírgula
        # (centavos em R$).
        df_compras["valor_compra"] = df_compras["valor_compra"].round(2)

        # 'dicionario_renomeacao' traduz nomes técnicos e códigos para termos semânticos
        # claros de negócios.
        dicionario_renomeacao = {
            # Traduz o identificador numérico da ordem de compra.
            "id_pedido_compra": "numero_ordem_compra",
            # Traduz a razão social do parceiro comercial.
            "fornecedor": "razao_social_fornecedor",
            # Traduz a classificação do material adquirido.
            "categoria_insumo": "categoria_material_insumo",
            # Traduz o valor financeiro do pedido para moeda corrente.
            "valor_compra": "valor_total_compra_reais",
            # Traduz a coluna de prazo concedido pelo parceiro.
            "prazo_pagamento_dias": "prazo_pagamento_concedido_dias",
        }

        # '.rename(columns=...)' aplica a tradução dos cabeçalhos na tabela de compras.
        df_compras = df_compras.rename(columns=dicionario_renomeacao)

        # 'return' devolve o DataFrame de compras higienizado e pronto para consumo.
        return df_compras
