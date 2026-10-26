"""Módulo de Diagnóstico Exploratório do Departamento de Compras (Fase 2.3).

Implementa os indicadores de suprimentos, Prazo Médio de Pagamento (PMP),
concentração de volume por fornecedor e volume de aquisição de insumos
para Pequenas e Médias Empresas (PMEs).
"""

# 'import' traz o módulo 'logging' da biblioteca padrão para registro e auditoria de
# execução.
import logging

# 'from' acessa 'pathlib'; 'import' traz 'Path' para gerenciamento de diretórios no
# sistema operacional.
from pathlib import Path

# 'from' acessa 'typing' da biblioteca padrão para anotação de tipos de dados de retorno
# e parâmetros.
from typing import Any

# 'import' traz o módulo 'pyplot' da biblioteca 'matplotlib' para montagem da moldura
# das figuras.
# 'as' define o apelido convencional 'plt'.
import matplotlib.pyplot as plt

# 'import' traz o 'pandas', biblioteca essencial para criação de tabelas e operações
# matemáticas vetorizadas.
# 'as' define o apelido reduzido 'pd'.
import pandas as pd

# 'import' traz a biblioteca 'seaborn' para criação de gráficos estatísticos com temas
# corporativos.
# 'as' define o apelido oficial 'sns'.
import seaborn as sns

# 'from' navega até o arquivo 'base_departamento.py' para reaproveitar a infraestrutura
# por herança.
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento


# 'class' declara o modelo orientado a objetos do departamento de suprimentos.
# '(BaseDepartamento)' herda o leitor de arquivos, ferramentas estatísticas e diretórios
# de relatórios.
class AnalisadorCompras(BaseDepartamento):
    """Classe responsável pelo diagnóstico de aquisição de insumos e prazos de
    fornecedores.
    """

    # 'def' define o método construtor '__init__', acionado ao instanciar o objeto na
    # memória.
    # 'self' referencia o próprio objeto departamento sendo construído.
    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento de compras configurando a pasta de saída dedicada.

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas brutas do ERP.
            pasta_relatorios (Path): Diretório base de saída dos laudos analíticos.
        """
        # 'super().__init__' chama o construtor da classe base, registrando o nome do
        # departamento como 'compras'.
        # Isso cria automaticamente a subpasta 'relatorios/figuras/compras/' no disco
        # rígido.
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="compras",
        )

    # 'def' define o método que carrega as compras do disco ou gera dados
    # representativos defensivamente.
    # '-> pd.DataFrame' documenta formalmente o retorno de uma tabela do pandas.
    def carregar_dados_compras(self) -> pd.DataFrame:
        """Carrega a tabela de pedidos de compra e notas fiscais de entrada do ERP.

        Returns:
            pd.DataFrame: Tabela contendo fornecedores, valores de compra e prazos
            concedidos.
        """
        # O operador '/' cria o caminho absoluto do arquivo de pedidos de compras dentro
        # da pasta de dados brutos.
        caminho_compras = self.pasta_dados_brutos / "erp_pedidos_compras.csv"

        # 'caminho_compras.is_file()' verifica fisicamente no disco se o arquivo existe.
        # 'if not' atua de forma defensiva: se a PME ainda não exportou as compras,
        # geramos dados representativos.
        if not caminho_compras.is_file():
            # 'logging.info' avisa no console que o gerador de contingência de compras
            # foi acionado.
            logging.info(
                "Compras — Base não localizada. Gerando dados representativos de"
                "suprimentos..."
            )

            # 'dados_simulados' é um dicionário Python com listas estruturadas simulando
            # notas de compras reais de insumos.
            dados_simulados = {
                "id_pedido_compra": [501, 502, 503, 504, 505, 506],
                "fornecedor": [
                    "Madeireira Pinhal",
                    "Aços Santa Cruz",
                    "Química Global",
                    "Madeireira Pinhal",
                    "Embalagens Brasil",
                    "Aços Santa Cruz",
                ],
                "categoria_insumo": [
                    "Matéria-Prima",
                    "Ferragens",
                    "Vernizes",
                    "Matéria-Prima",
                    "Embalagem",
                    "Ferragens",
                ],
                "valor_compra": [32000.0, 14500.0, 8200.0, 28000.0, 4300.0, 19000.0],
                "prazo_pagamento_dias": [45, 30, 28, 60, 15, 30],
            }

            # 'pd.DataFrame' converte o dicionário em uma matriz tabular do pandas em
            # memória RAM.
            df_compras = pd.DataFrame(dados_simulados)

            # '.to_csv' grava a tabela gerada no disco rígido para permitir inspeções
            # futuras.
            # 'index=False' impede que o pandas crie uma coluna extra de números
            # desnecessária no arquivo físico.
            df_compras.to_csv(caminho_compras, index=False)
        else:
            # Caso o arquivo já exista no disco, 'self.leitor.carregar_tabela' faz a
            # leitura segura do CSV.
            df_compras = self.leitor.carregar_tabela(caminho_compras)

        # 'logging.info' registra a quantidade de pedidos de compras carregados no
        # sistema.
        logging.info(
            "Compras — Base consolidada com %d ordens de compra.", len(df_compras)
        )

        # 'return' devolve a tabela de compras pronta para o cálculo dos KPIs
        # departamentais.
        return df_compras

    # KPI 21: Prazo Médio de Pagamento (PMP / DPO — Days Payable Outstanding).
    # Este indicador afere em média quantos dias a PME leva para pagar seus fornecedores
    # de suprimentos.
    def calcular_prazo_medio_pagamento(self, dados: pd.DataFrame) -> float:
        """Calcula o PMP ponderado pelo valor financeiro de cada ordem de compra.

        Args:
            dados (pd.DataFrame): Tabela de compras com valores e prazos.

        Returns:
            float: Prazo Médio de Pagamento ponderado em dias corridos.
        """
        # 'dados["valor_compra"].sum()' soma o valor financeiro total de todas as ordens
        # de compra emitidas.
        valor_total_compras = float(dados["valor_compra"].sum())

        # '(dados["valor_compra"] * dados["prazo_pagamento_dias"])' multiplica o valor
        # de cada compra pelo seu prazo concedido.
        # '.sum()' soma essa multiplicação, gerando o numerador da média ponderada
        # financeira.
        soma_ponderada = float(
            (dados["valor_compra"] * dados["prazo_pagamento_dias"]).sum()
        )

        # Divide a soma ponderada pelo valor total de compras para obter o prazo médio
        # real em dias.
        # 'round(..., 1)' arredonda o resultado com uma casa decimal (ex.: 38.5 dias).
        # O operador ternário 'if valor_total_compras > 0 else 0.0' previne erros de
        # divisão por zero caso a base esteja vazia.
        pmp_ponderado = (
            round(soma_ponderada / valor_total_compras, 1)
            if valor_total_compras > 0
            else 0.0
        )

        # 'logging.info' imprime o PMP ponderado no terminal para auditoria da diretoria
        # financeira e de suprimentos.
        logging.info(
            "Compras — Prazo Médio de Pagamento (PMP): %.1f dias.", pmp_ponderado
        )

        # 'return' devolve o prazo médio calculado em dias.
        return pmp_ponderado

    # KPI 25: Concentração de Compras por Fornecedor (Matriz de Dependência de
    # Suprimentos).
    def gerar_grafico_concentracao_fornecedores(self, dados: pd.DataFrame) -> Path:
        """Renderiza um gráfico de barras destacando os fornecedores de maior volume
        financeiro.

        Args:
            dados (pd.DataFrame): Tabela com registros de ordens de compra.

        Returns:
            Path: Endereço físico da imagem PNG exportada em 300 DPI.
        """
        # Agrupa pelo nome do fornecedor e soma o total em reais comprado de cada
        # parceiro.
        # '.reset_index()' converte a série agrupada de volta em uma tabela estruturada
        # com colunas convencionais.
        compras_por_fornecedor = (
            dados.groupby("fornecedor")["valor_compra"].sum().reset_index()
        )

        # '.sort_values()' ordena os fornecedores do maior volume financeiro para o
        # menor (ordenação decrescente).
        compras_por_fornecedor = compras_por_fornecedor.sort_values(
            by="valor_compra", ascending=False
        )

        # Define o caminho de salvamento do arquivo PNG dentro da subpasta
        # 'relatorios/figuras/compras/'.
        caminho_figura = self.pasta_saida / "concentracao_compras_fornecedores.png"

        # Cria a moldura da figura com 9 polegadas de largura por 5 polegadas de altura.
        figura, eixo = plt.subplots(figsize=(9, 5))

        # 'sns.barplot' desenha as barras comparativas de compras por parceiro
        # comercial.
        # 'color="#2ca02c"' aplica uma tonalidade verde floresta profissional.
        sns.barplot(
            data=compras_por_fornecedor,
            x="fornecedor",
            y="valor_compra",
            color="#2ca02c",
            ax=eixo,
        )

        # 'eixo.set_title' define o título principal do gráfico com espaçamento de 12
        # pontos.
        eixo.set_title(
            "Volume de Compras por Fornecedor (Matriz de Dependência)",
            fontsize=13,
            pad=12,
        )

        # 'eixo.set_xlabel' nomeia o eixo horizontal em português.
        eixo.set_xlabel("Fornecedor Parceiro", fontsize=10)

        # 'eixo.set_ylabel' nomeia o eixo vertical financeiro em reais.
        eixo.set_ylabel("Valor Total Comprado (R$)", fontsize=10)

        # 'plt.xticks(rotation=45, ha="right")' inclina os nomes dos fornecedores em 45
        # graus para evitar sobreposição de texto.
        plt.xticks(rotation=45, ha="right")

        # 'plt.tight_layout()' ajusta as margens da tela automaticamente.
        plt.tight_layout()

        # 'figura.savefig' grava a figura física no disco rígido com resolução
        # industrial de 300 DPI.
        figura.savefig(caminho_figura, dpi=300)

        # 'plt.close(figura)' limpa o buffer gráfico do matplotlib na memória RAM para
        # garantir performance contínua.
        plt.close(figura)

        # 'logging.info' confirma a persistência do gráfico de compras no terminal.
        logging.info(
            "Compras — Gráfico de fornecedores salvo em: %s", caminho_figura.name
        )

        # 'return' devolve o caminho do arquivo de imagem salvo.
        return caminho_figura

    # 'def' implementa a assinatura obrigatória herdada da classe base abstrata
    # 'BaseDepartamento'.
    def executar_diagnostico_completo(self) -> dict[str, Any]:
        """Coordena o cálculo de indicadores de suprimentos e persistência visual.

        Returns:
            Dict[str, Any]: Laudo executivo do departamento de compras.
        """
        # Emite log marcando o início da perícia de suprimentos da Fase 2.3.
        logging.info("=== INICIANDO PERÍCIA DO DEPARTAMENTO DE COMPRAS (FASE 2.3) ===")

        # Carrega as ordens de compra na memória RAM.
        df_compras = self.carregar_dados_compras()

        # Calcula o Prazo Médio de Pagamento ponderado em dias.
        pmp_dias = self.calcular_prazo_medio_pagamento(df_compras)

        # Renderiza e salva o gráfico de concentração de fornecedores no disco.
        caminho_grafico = self.gerar_grafico_concentracao_fornecedores(df_compras)

        # 'float(df_compras["valor_compra"].sum())' calcula o montante total financeiro
        # comprado no período.
        volume_total_comprado = round(float(df_compras["valor_compra"].sum()), 2)

        # 'int(df_compras["fornecedor"].nunique())' conta quantos fornecedores distintos
        # (cardinalidade) a PME possui.
        contagem_fornecedores_unicos = int(df_compras["fornecedor"].nunique())

        # Monta o dicionário consolidado do laudo de compras para subsidiar o comitê
        # executivo e o BI.
        laudo_compras = {
            "volume_total_comprado_reais": volume_total_comprado,
            "prazo_medio_pagamento_dias": pmp_dias,
            "total_fornecedores_ativos": contagem_fornecedores_unicos,
            "grafico_concentracao_fornecedores": str(caminho_grafico),
        }

        # Emite log registrando o encerramento do diagnóstico de compras.
        logging.info("=== DEPARTAMENTO DE COMPRAS CONCLUÍDO COM SUCESSO ===")

        # 'return' devolve o laudo consolidado de suprimentos.
        return laudo_compras
