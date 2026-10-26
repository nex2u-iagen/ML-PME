"""Construtor especializado do Data Mart de Marketing e Clientes para BI.

Cruza os dados transacionais de Vendas (Comercial), títulos em atraso (Financeiro)
e custos diretos (Controladoria) para gerar a segmentação RFV (Recência, Frequência e
Valor)
e classificar os clientes em grupos estratégicos de marketing e retenção.
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


# 'class' é a palavra-chave que declara um novo molde estrutural orientado a objetos.
# 'ConstrutorMartMarketing' define com máxima clareza semântica a missão única de
# estruturar dados para Marketing.
class ConstrutorMartMarketing:
    """Classe responsável por cruzar vendas, financeiro e margem para gerar
    inteligência de marketing.
    """

    # 'def' define o método especial construtor '__init__', acionado na alocação da
    # instância em memória RAM.
    # 'self' referencia a própria instância acessando seus atributos internos.
    # 'pasta_brutos: Path' exige receber o caminho onde estão as tabelas CSV do ERP.
    # '-> None' documenta formalmente que o método inicializador não retorna dados.
    def __init__(self, pasta_brutos: Path) -> None:
        """Inicializa o construtor acoplando o leitor de arquivos do núcleo.

        Args:
            pasta_brutos (Path): Diretório contendo os arquivos CSV brutos do ERP.
        """
        # Armazena o endereço da pasta de dados brutos no atributo do próprio objeto.
        self.pasta_brutos = pasta_brutos

        # Instancia a ferramenta de leitura desacoplada do núcleo compartilhado por
        # composição orientada a objetos.
        self.leitor = LeitorArquivosTabulares()

    # 'def' define o método principal que executa os cruzamentos interdepartamentais de
    # marketing.
    # '-> pd.DataFrame' atesta formalmente que o método retornará uma tabela estruturada
    # do pandas.
    def processar(self) -> pd.DataFrame:
        """Cruza dados comerciais, financeiros e cadastrais gerando a segmentação RFV e
        ações de marketing.

        Returns:
            pd.DataFrame: Data Mart de Marketing enriquecido com clusters acionáveis
            para campanhas.
        """
        # Monta os caminhos dos arquivos brutos de pedidos e clientes extraídos na Fase
        # 01.
        caminho_pedidos = self.pasta_brutos / "erp_pedidos_vendas.csv"
        caminho_clientes = self.pasta_brutos / "erp_clientes.csv"

        # Carrega ambas as tabelas na memória RAM utilizando o leitor padronizado do
        # núcleo.
        df_pedidos = self.leitor.carregar_tabela(caminho_pedidos)
        df_clientes = self.leitor.carregar_tabela(caminho_clientes)

        # 'pd.to_datetime' converte a coluna textual de data em carimbos temporais
        # legítimos (datetime64).
        df_pedidos["data_pedido"] = pd.to_datetime(df_pedidos["data_pedido"])

        # Define a data presente do sistema para cálculo dos dias corridos desde a
        # última compra (Recência).
        data_atual_referencia = pd.Timestamp.now()

        # Agrupa as transações de vendas por cliente para computar as métricas
        # fundamentais do modelo RFV.
        # 'ultima_compra': a data mais recente em que o cliente comprou da PME.
        # 'frequencia_compras': a quantidade total de pedidos emitidos no histórico.
        # 'faturamento_acumulado_reais': o valor monetário total gasto pelo cliente no
        # negócio.
        resumo_rfv = (
            df_pedidos.groupby("id_cliente")
            .agg(
                ultima_compra=("data_pedido", "max"),
                frequencia_compras=("id_pedido", "count"),
                faturamento_acumulado_reais=("valor_total", "sum"),
            )
            .reset_index()
        )

        # Calcula a Recência em dias corridos subtraindo a data da última compra da data
        # atual de referência.
        # '.dt.days' extrai apenas a contagem inteira de dias decorridos.
        resumo_rfv["recencia_dias"] = (
            data_atual_referencia - resumo_rfv["ultima_compra"]
        ).dt.days

        # Identifica o perfil de pontualidade de pagamento de cada cliente a partir das
        # transações.
        # 'inadimplente': verifica se o cliente possui algum título registrado com
        # calote/atraso severo.
        risco_cliente = (
            df_pedidos.groupby("id_cliente")
            .agg(
                total_titulos_inadimplentes=("inadimplente", "sum"),
                ticket_medio_reais=("valor_total", "mean"),
            )
            .reset_index()
        )

        # Cria um indicador booleano marcando clientes com histórico de títulos
        # atrasados.
        risco_cliente["possui_historico_atraso"] = (
            risco_cliente["total_titulos_inadimplentes"] > 0
        )

        # Realiza a primeira junção relacional (INNER JOIN) entre a tabela cadastral e o
        # resumo RFV.
        df_marketing = pd.merge(df_clientes, resumo_rfv, on="id_cliente", how="inner")

        # Realiza a segunda junção relacional integrando as variáveis de risco
        # financeiro calculadas.
        df_marketing = pd.merge(
            df_marketing, risco_cliente, on="id_cliente", how="inner"
        )

        # 'def' interna com regras de decisão de negócio para classificar cada cliente
        # em clusters de marketing.
        def atribuir_segmento_marketing(linha: pd.Series) -> str:
            # 1. Alerta Financeiro: Se o cliente compra muito mas dá calote, o marketing
            # NÃO deve gastar dinheiro com ele.
            if linha["possui_historico_atraso"]:
                return "01 - Bloqueio de Campanha (Alto Risco de Inadimplência)"

            # 2. Clientes Campeões (VIPs): Compraram nos últimos 45 dias e têm alta
            # frequência e faturamento.
            if linha["recencia_dias"] <= 45 and linha["frequencia_compras"] >= 2:
                return "02 - Clientes Campeões (Oferecer VIP / Cross-Selling)"

            # 3. Novos Promissores: Compraram recentemente pela primeira vez (potencial
            # de crescimento).
            if linha["recencia_dias"] <= 45 and linha["frequencia_compras"] == 1:
                return "03 - Novos Clientes (Ação de Boas-Vindas e 2ª Compra)"

            # 4. Clientes em Risco de Evasão (Churn): Costumavam comprar, mas estão há
            # mais de 45 dias sem pedir.
            if linha["recencia_dias"] > 45 and linha["frequencia_compras"] >= 2:
                return "04 - Em Risco de Churn (Enviar Cupom de Reativação)"

            # 5. Clientes Inativos / Dormentes: Compraram uma única vez há muito tempo e
            # sumiram.
            return "05 - Clientes Inativos (Campanha de Reengajamento)"

        # '.apply(..., axis=1)' avalia cada linha da tabela e aplica as regras de
        # segmentação estratégica.
        df_marketing["segmento_estrategico_marketing"] = df_marketing.apply(
            atribuir_segmento_marketing, axis=1
        )

        # 'round(2)' padroniza as métricas monetárias com precisão de duas casas
        # decimais em reais (R$).
        df_marketing["faturamento_acumulado_reais"] = df_marketing[
            "faturamento_acumulado_reais"
        ].round(2)
        df_marketing["ticket_medio_reais"] = df_marketing["ticket_medio_reais"].round(2)
        df_marketing["limite_credito"] = df_marketing["limite_credito"].round(2)

        # Mapeia os nomes das colunas para termos semânticos amigáveis para conexão com
        # ferramentas de BI.
        dicionario_renomeacao = {
            "id_cliente": "codigo_cliente",
            "nome_fantasia": "razao_social_cliente",
            "segmento": "nicho_atuacao_mercado",
            "limite_credito": "limite_credito_reais",
            "dias_prazo_pagamento": "prazo_pagamento_dias",
            "ultima_compra": "data_ultima_compra",
            "recencia_dias": "dias_sem_comprar_recencia",
            "frequencia_compras": "total_pedidos_historico_frequencia",
            "faturamento_acumulado_reais": "valor_total_gasto_reais",
        }

        # Renomeia os cabeçalhos e retorna a tabela consolidada pronta para dashboards
        # de marketing.
        return df_marketing.rename(columns=dicionario_renomeacao)
