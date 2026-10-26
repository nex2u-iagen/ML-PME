"""Construtor especializado do Data Mart de Estoque e Materiais para BI."""

# 'from' indica a biblioteca de origem; 'pathlib' manipula caminhos e pastas de forma
# orientada a objetos.
from pathlib import Path

# 'import' traz o 'pandas' para manipulação e agregações tabulares de estoque.
# 'as' define o atalho 'pd'.
import pandas as pd

# 'from' acessa o leitor padronizado no núcleo de acesso a dados do projeto.
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares


# 'class' declara o molde especializado do construtor de estoque.
class ConstrutorMartEstoque:
    """Classe responsável exclusiva pela classificação ABC e cobertura de materiais
    para BI.
    """

    # 'def' define o método construtor '__init__'.
    def __init__(self, pasta_brutos: Path) -> None:
        """Inicializa o construtor acoplando o leitor de arquivos do núcleo.

        Args:
            pasta_brutos (Path): Diretório contendo os arquivos CSV brutos do ERP.
        """
        # Armazena o endereço físico dos dados brutos no atributo do objeto.
        self.pasta_brutos = pasta_brutos

        # Instancia a ferramenta de leitura do núcleo compartilhado.
        self.leitor = LeitorArquivosTabulares()

    # 'def' define a função que processa a Curva ABC e autonomia do depósito.
    def processar(self) -> pd.DataFrame:
        """Aplica a classificação de Pareto (ABC) e cobertura em dias de inventário.

        Returns:
            pd.DataFrame: Tabela tratada pronta para alimentar painéis de estoque.
        """
        # Monta o caminho do arquivo de estoque no diretório de dados brutos.
        caminho_estoque = self.pasta_brutos / "erp_saldos_estoque.csv"

        # Checagem defensiva de contingência: cria os dados caso o arquivo ainda não
        # exista.
        if not caminho_estoque.is_file():
            dados_simulados = {
                "id_produto": [201, 202, 203, 204, 205, 206, 207, 208],
                "descricao_produto": [
                    "Mesa Jantar Carvalho",
                    "Cadeira Estofada Luxo",
                    "Verniz Poliuretano 5L",
                    "Parafuso Sextavado 50mm",
                    "Puxador Alumínio Escovado",
                    "Cola Madeira Industrial",
                    "Armário 2 Portas",
                    "Dobradiça com Amortecedor",
                ],
                "quantidade_saldo": [12, 48, 25, 1200, 350, 40, 5, 800],
                "custo_unitario": [850.0, 180.0, 120.0, 0.45, 15.0, 45.0, 1400.0, 6.50],
                "consumo_mensal_medio": [4, 16, 8, 300, 90, 15, 2, 220],
            }
            df_contingencia = pd.DataFrame(dados_simulados)
            df_contingencia["valor_imobilizado"] = (
                df_contingencia["quantidade_saldo"] * df_contingencia["custo_unitario"]
            ).round(2)
            df_contingencia.to_csv(caminho_estoque, index=False)

        # Carrega a tabela de estoque utilizando o leitor do núcleo.
        df_estoque = self.leitor.carregar_tabela(caminho_estoque)

        # Calcula o consumo diário dividindo a demanda mensal por 30.0 dias.
        consumo_diario = df_estoque["consumo_mensal_medio"] / 30.0

        # Calcula a autonomia em dias dividindo o saldo físico pelo consumo diário.
        df_estoque["dias_cobertura_estoque"] = (
            df_estoque["quantidade_saldo"] / consumo_diario
        ).round(1)

        # Ordena os produtos de forma decrescente pelo capital imobilizado para a Curva
        # ABC.
        df_estoque = df_estoque.sort_values(by="valor_imobilizado", ascending=False)

        # Calcula a soma cumulativa do capital imobilizado.
        soma_acumulada = df_estoque["valor_imobilizado"].cumsum()
        total_geral = df_estoque["valor_imobilizado"].sum()

        # Calcula o percentual acumulado sobre o total imobilizado da companhia.
        percentual_acumulado = (soma_acumulada / total_geral) * 100

        # Função interna com as faixas formais de Pareto para a Curva ABC.
        def rotular_classe(pct: float) -> str:
            if pct <= 80.0:
                return "Classe A (Alto Valor / 80% do Capital)"
            elif pct <= 95.0:
                return "Classe B (Valor Médio / 15% do Capital)"
            return "Classe C (Baixo Valor / 5% do Capital)"

        # Aplica a rotulagem de negócio sobre cada produto cadastrado.
        df_estoque["categoria_curva_abc"] = percentual_acumulado.apply(rotular_classe)

        # Mapeia cabeçalhos claros e descritivos para ferramentas de visualização.
        colunas_amigaveis_estoque = {
            "id_produto": "codigo_sku",
            "descricao_produto": "nome_material_produto",
            "quantidade_saldo": "saldo_fisico_prateleira",
            "custo_unitario": "custo_aquisicao_unitario_reais",
            "consumo_mensal_medio": "demanda_mensal_media_unidades",
            "valor_imobilizado": "capital_total_parado_reais",
        }

        # Renomeia as colunas e retorna a matriz tratada de estoque.
        return df_estoque.rename(columns=colunas_amigaveis_estoque)
