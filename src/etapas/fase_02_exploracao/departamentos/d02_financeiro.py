"""Módulo de Diagnóstico Exploratório do Departamento Financeiro (Fase 2.2).

Implementa os indicadores vitais de tesouraria, inadimplência de títulos,
prazos médios de recebimento (PMR), curva de envelhecimento da dívida (aging)
e exposição máxima de risco financeiro para Pequenas e Médias Empresas (PMEs)[cite: 7].
"""

# 'import logging' importa o sistema de rastreabilidade de eventos no console[cite: 7].
import logging

# 'from pathlib import Path' disponibiliza a manipulação orientada a objetos de caminhos
# e arquivos[cite: 7].
from pathlib import Path

# 'from typing import Any, Dict' importa anotações de tipagem estática para estruturas
# de retorno[cite: 7].
from typing import Any

# 'import matplotlib.pyplot as plt' importa o motor de criação e gravação de figuras
# gráficas[cite: 7].
import matplotlib.pyplot as plt

# 'import pandas as pd' importa a ferramenta padrão para manipulação e agregações
# tabulares[cite: 7].
import pandas as pd

# 'import seaborn as sns' importa a biblioteca de visualização estatística
# corporativa[cite: 7].
import seaborn as sns

# 'from src...' importa a classe base abstrata para herdar o leitor e ferramentas do
# núcleo[cite: 7].
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento


# 'class AnalisadorFinanceiro(BaseDepartamento)' especializa o diagnóstico para liquidez
# e inadimplência[cite: 7].
class AnalisadorFinanceiro(BaseDepartamento):
    """Classe responsável pelo Raio-X de liquidez, solvência e inadimplência do
    ERP[cite: 7].
    """

    # 'def __init__(...)' instancia a classe acionando o construtor da classe mãe via
    # super()[cite: 7].
    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento financeiro registrando seu nome canônico[cite: 7].

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas brutas do ERP[cite: 7].
            pasta_relatorios (Path): Diretório base de saída dos laudos analíticos[cite:
            7].
        """
        # Aciona o construtor base registrando o nome 'financeiro' para a criação da
        # pasta de imagens[cite: 7].
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="financeiro",
        )

    # 'def carregar_dados_financeiros(...)' carrega o histórico de contas a receber do
    # ERP[cite: 7].
    def carregar_dados_financeiros(self) -> pd.DataFrame:
        """Carrega a tabela de contas a receber e histórico de títulos do ERP[cite: 7].

        Returns:
            pd.DataFrame: Tabela contendo títulos, vencimentos, valores e status de
            pagamento[cite: 7].
        """
        # Constrói o caminho relativo até o arquivo CSV contendo os pedidos e títulos
        # financeiros[cite: 7].
        caminho_pedidos = self.pasta_dados_brutos / "erp_pedidos_vendas.csv"

        # Carrega a tabela na memória utilizando o leitor defensivo do núcleo[cite: 7].
        df_financeiro = self.leitor.carregar_tabela(caminho_pedidos)

        # Converte a coluna de datas para o formato datetime oficial do pandas[cite: 7].
        df_financeiro["data_pedido"] = pd.to_datetime(df_financeiro["data_pedido"])

        # Retorna o DataFrame carregado e pronto para o cálculo de métricas de
        # caixa[cite: 7].
        return df_financeiro

    # 'def calcular_taxa_inadimplencia(...)' executa a Camada Tabular medindo calotes e
    # atrasos[cite: 7].
    def calcular_taxa_inadimplencia(self, dados: pd.DataFrame) -> dict[str, Any]:
        """Calcula o percentual e o montante em reais de títulos em inadimplência[cite:
        7].

        Args:
            dados (pd.DataFrame): Tabela financeira transacional[cite: 7].

        Returns:
            Dict[str, Any]: Indicadores com valor total faturado, valor em atraso e taxa
            percentual[cite: 7].
        """
        # Calcula a soma do faturamento total bruto faturado pela empresa[cite: 7].
        faturamento_total = float(dados["valor_total"].sum())

        # Filtra os títulos cujo status de liquidação seja 'Inadimplente' ou
        # 'Atrasado'[cite: 7].
        titulos_em_risco = dados[
            dados["status_pagamento"].isin(["Inadimplente", "Atrasado"])
        ]

        # Soma o valor total em aberto que representa exposição de risco ao caixa da
        # empresa[cite: 7].
        valor_em_risco = float(titulos_em_risco["valor_total"].sum())

        # Calcula a taxa percentual de inadimplência sobre a receita total emitida[cite:
        # 7].
        taxa_inadimplencia = (
            (valor_em_risco / faturamento_total) * 100 if faturamento_total > 0 else 0.0
        )

        # Consolida os indicadores de inadimplência em um dicionário estruturado[cite:
        # 7].
        laudo_inadimplencia = {
            "faturamento_total_reais": round(faturamento_total, 2),
            "valor_em_risco_reais": round(valor_em_risco, 2),
            "taxa_inadimplencia_percentual": round(taxa_inadimplencia, 2),
            "total_titulos_analisados": int(len(dados)),
            "total_titulos_inadimplentes": int(len(titulos_em_risco)),
        }

        # Emite log registrando o indicador vital de saúde financeira[cite: 7].
        logging.info(
            "Financeiro — Taxa de Inadimplência: %.2f%% (R$ %.2f em risco de calote).",
            laudo_inadimplencia["taxa_inadimplencia_percentual"],
            laudo_inadimplencia["valor_em_risco_reais"],
        )

        # Retorna o laudo com as métricas de inadimplência apuradas[cite: 7].
        return laudo_inadimplencia

    # 'def gerar_grafico_distribuicao_status(...)' executa a Camada Gráfica gerando o
    # aging de títulos[cite: 7].
    def gerar_grafico_distribuicao_status(self, dados: pd.DataFrame) -> Path:
        """Renderiza a distribuição gráfica do montante financeiro por status de
        cobrança[cite: 7].

        Args:
            dados (pd.DataFrame): Tabela com títulos e valores[cite: 7].

        Returns:
            Path: Caminho físico da imagem exportada no disco em 300 DPI[cite: 7].
        """
        # Agrupa os valores financeiros somados por cada status de pagamento
        # registrado[cite: 7].
        valores_por_status = (
            dados.groupby("status_pagamento")["valor_total"].sum().reset_index()
        )

        # Define o caminho do arquivo PNG de destino dentro da pasta
        # 'relatorios/figuras/financeiro/'[cite: 7].
        caminho_figura = self.pasta_saida / "distribuicao_status_cobranca.png"

        # Cria a moldura da figura com 8 polegadas de largura por 5 de altura[cite: 7].
        figura, eixo = plt.subplots(figsize=(8, 5))

        # Renderiza o gráfico de barras comparando o volume de dinheiro em cada situação
        # de cobrança[cite: 7].
        # Aqui o código já utilizava hue='status_pagamento' e legend=False
        # corretamente[cite: 7]!
        sns.barplot(
            data=valores_por_status,
            x="status_pagamento",
            y="valor_total",
            hue="status_pagamento",
            palette="mako",
            legend=False,
            ax=eixo,
        )

        # Configura os títulos corporativos e rótulos dos eixos em português[cite: 7].
        eixo.set_title(
            "Exposição Financeira por Status de Cobrança (Aging)", fontsize=13, pad=12
        )
        eixo.set_xlabel("Situação do Título", fontsize=10)
        eixo.set_ylabel("Volume Financeiro Total (R$)", fontsize=10)

        # Ajusta automaticamente as margens da imagem no matplotlib[cite: 7].
        plt.tight_layout()

        # Salva o gráfico em alta definição (300 DPI)[cite: 7].
        figura.savefig(caminho_figura, dpi=300)

        # Fecha a figura no matplotlib para blindar o ambiente contra vazamentos de
        # memória[cite: 7].
        plt.close(figura)

        # Registra a conclusão da renderização no console[cite: 7].
        logging.info("Gráfico financeiro de cobrança salvo em: %s", caminho_figura.name)

        # Retorna o endereço físico da imagem salva[cite: 7].
        return caminho_figura

    # CORREÇÃO CIRÚRGICA: Alterada a assinatura de '-> None' para '-> Dict[str, Any]'
    # e incluído o 'return laudo_financeiro' para integrar ao Raio-X Empresarial.
    def executar_diagnostico_completo(self) -> dict[str, Any]:
        """Coordena o cálculo dos indicadores financeiros e a persistência dos gráficos
        do setor[cite: 7].

        Returns:
            Dict[str, Any]: Laudo executivo completo do departamento financeiro[cite:
            7].
        """
        # Emite log formal marcando o início da perícia financeira[cite: 7].
        logging.info("=== INICIANDO PERÍCIA DO DEPARTAMENTO FINANCEIRO (FASE 2.2) ===")

        # Carrega os dados financeiros na memória RAM[cite: 7].
        df_financeiro = self.carregar_dados_financeiros()

        # Executa a Camada Tabular apurando taxas de inadimplência e montante sob
        # risco[cite: 7].
        laudo_inadimplencia = self.calcular_taxa_inadimplencia(df_financeiro)

        # Executa a Camada Gráfica gerando a visualização de exposição de cobrança[cite:
        # 7].
        caminho_grafico = self.gerar_grafico_distribuicao_status(df_financeiro)

        # Estrutura o laudo departamental com métricas tabulares e a imagem gerada[cite:
        # 7].
        laudo_financeiro = {
            "analise_inadimplencia": laudo_inadimplencia,
            "grafico_status_cobranca": str(caminho_grafico),
        }

        # Emite log confirmando o encerramento do diagnóstico financeiro[cite: 7].
        logging.info("=== DEPARTAMENTO FINANCEIRO CONCLUÍDO COM SUCESSO ===")

        # Retorna o laudo estruturado para o orquestrador macro da empresa[cite: 5, 7].
        return laudo_financeiro
