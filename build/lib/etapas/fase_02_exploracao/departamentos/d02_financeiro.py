"""Módulo de Diagnóstico Exploratório do Departamento Financeiro (Fase 2.2 - CRISP-DM).

Responsabilidade Única: Auditar a saúde da tesouraria, calcular o volume e a taxa
percentual de inadimplência de títulos a receber e gerar o gráfico de distribuição
por situação de cobrança (Aging), consumindo dados reais via Adaptador Universal[cite: 5].
"""

# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo[cite: 5].
import logging

# 'from pathlib import Path' disponibiliza a manipulação orientada a objetos de caminhos e arquivos no disco[cite: 5].
from pathlib import Path

# 'from typing import Any, Dict' importa anotações de tipagem estática para estruturas heterogêneas de saída[cite: 5].
from typing import Any, Dict

# 'import matplotlib.pyplot as plt' importa o motor de criação e gravação de figuras gráficas[cite: 5].
import matplotlib.pyplot as plt

# 'import pandas as pd' manipula estruturas de dados tabulares, agregações e filtros em memória RAM[cite: 5].
import pandas as pd

# 'import seaborn as sns' renderiza gráficos estatísticos corporativos elegantes e padronizados[cite: 5].
import seaborn as sns

# Importação da classe base abstrata que injeta infraestrutura compartilhada e o Adaptador Universal[cite: 5].
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento


# 'class AnalisadorFinanceiro(BaseDepartamento)' especializa o diagnóstico de tesouraria por herança[cite: 5].
class AnalisadorFinanceiro(BaseDepartamento):
    """Classe responsável pelo diagnóstico de solvência, liquidez e inadimplência real do ERP[cite: 5]."""

    # 'def __init__(...)' constrói a instância do analisador financeiro registrando a pasta setorial[cite: 5].
    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento financeiro registrando seu nome canônico para criação de pastas[cite: 5].

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas reais do ERP (ex: mercado_vencedor/)[cite: 5].
            pasta_relatorios (Path): Diretório base de saída onde a pasta 'financeiro/' será mantida[cite: 5].
        """
        # 'super().__init__(...)' aciona o construtor da classe base registrando 'financeiro' como nome canônico[cite: 5].
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="financeiro",
        )

    # 'def carregar_dados_financeiros(...)' aciona o Adaptador Universal para carregar Contas a Receber[cite: 5].
    def carregar_dados_financeiros(self) -> pd.DataFrame:
        """Solicita ao Adaptador Universal a tabela canônica de Contas a Receber reais[cite: 5].

        Returns:
            pd.DataFrame: Tabela financeira real contendo data_pedido, valor_total e status_pagamento[cite: 5].

        Raises:
            ValueError: Se o adaptador não localizar títulos a receber na base de dados do cliente[cite: 5].
        """
        # 'self.adaptador.obter_visao_financeira_receber()' busca e padroniza tabelas como 'erp_contasreceber.csv'.
        df_financeiro = self.adaptador.obter_visao_financeira_receber()

        # Validação defensiva: interrompe a execução caso a base financeira esteja indisponível ou vazia[cite: 5].
        if df_financeiro is None or df_financeiro.empty:
            logging.error("Financeiro — Falha crítica: Nenhum título a receber real localizado pelo Adaptador Universal.")
            raise ValueError("Dados financeiros reais de contas a receber não encontrados na base de dados sob perícia.")

        # 'logging.info' registra a confirmação do carregamento com a contagem exata de títulos auditados[cite: 5].
        logging.info("Financeiro — Base canônica carregada com sucesso contendo %d títulos a receber reais.", len(df_financeiro))

        # Devolve a matriz tabular canônica pronta para a apuração de solvência e risco[cite: 5].
        return df_financeiro

    # 'def calcular_taxa_inadimplencia(...)' calcula os valores monetários em atraso e a taxa percentual de calote[cite: 5].
    def calcular_taxa_inadimplencia(self, dados: pd.DataFrame) -> Dict[str, Any]:
        """Calcula o montante faturado, o volume em aberto e a taxa percentual de inadimplência da carteira[cite: 5].

        Args:
            dados (pd.DataFrame): Tabela financeira contendo as colunas 'valor_total' e 'status_pagamento'[cite: 5].

        Returns:
            Dict[str, Any]: Indicadores consolidando faturamento, valor sob risco e taxa percentual calculada[cite: 5].
        """
        # 'dados["valor_total"].sum()' calcula a soma monetária de todos os títulos emitidos pela empresa[cite: 5].
        faturamento_total = float(dados["valor_total"].sum())

        # 'dados["status_pagamento"].isin([...])' filtra os títulos que possuem pendência de quitação ou atraso[cite: 5].
        titulos_em_risco = dados[dados["status_pagamento"].isin(["Inadimplente", "Atrasado"])]

        # 'titulos_em_risco["valor_total"].sum()' calcula o total em reais exposto a risco de perda financeira[cite: 5].
        valor_em_risco = float(titulos_em_risco["valor_total"].sum())

        # Calcula a taxa percentual de inadimplência dividindo o valor em risco pelo total da carteira[cite: 5].
        # O operador ternário 'if faturamento_total > 0 else 0.0' previne erros de divisão por zero caso o saldo seja nulo[cite: 5].
        taxa_inadimplencia = (valor_em_risco / faturamento_total) * 100 if faturamento_total > 0 else 0.0

        # 'laudo_inadimplencia' consolida os sinais vitais da tesouraria em um dicionário estruturado[cite: 5].
        laudo_inadimplencia = {
            "faturamento_total_reais": round(faturamento_total, 2),
            "valor_em_risco_reais": round(valor_em_risco, 2),
            "taxa_inadimplencia_percentual": round(taxa_inadimplencia, 2),
            "total_titulos_analisados": int(len(dados)),
            "total_titulos_inadimplentes": int(len(titulos_em_risco)),
        }

        # 'logging.info' documenta o indicador de inadimplência no console para acompanhamento executivo[cite: 5].
        logging.info(
            "Financeiro — Taxa de Inadimplência: %.2f%% (R$ %.2f em risco de calote).",
            laudo_inadimplencia["taxa_inadimplencia_percentual"],
            laudo_inadimplencia["valor_em_risco_reais"],
        )

        # Devolve o dicionário com as métricas financeiras de inadimplência apuradas[cite: 5].
        return laudo_inadimplencia

    # 'def gerar_grafico_distribuicao_status(...)' desenha e exporta o gráfico comparativo de cobrança em 300 DPI[cite: 5].
    def gerar_grafico_distribuicao_status(self, dados: pd.DataFrame) -> Path:
        """Renderiza a distribuição gráfica do montante financeiro alocado por situação de liquidação[cite: 5].

        Args:
            dados (pd.DataFrame): Tabela financeira contendo títulos e valores monetários[cite: 5].

        Returns:
            Path: Rota física da imagem PNG salva no disco em alta resolução (300 DPI)[cite: 5].
        """
        # 'dados.groupby("status_pagamento")["valor_total"].sum().reset_index()' agrupa os valores por situação do título[cite: 5].
        valores_por_status = dados.groupby("status_pagamento")["valor_total"].sum().reset_index()

        # 'self.pasta_saida / "distribuicao_status_cobranca.png"' monta o caminho do arquivo PNG dentro de 'relatorios/figuras/financeiro/'[cite: 5].
        caminho_figura = self.pasta_saida / "distribuicao_status_cobranca.png"

        # 'plt.subplots(figsize=(8, 5))' inicializa a tela de desenho com 8 polegadas de largura por 5 de altura[cite: 5].
        figura, eixo = plt.subplots(figsize=(8, 5))

        # 'sns.barplot(...)' renderiza o gráfico de barras comparando o volume de dinheiro em cada situação de liquidação[cite: 5].
        # - 'hue="status_pagamento"' e 'legend=False': atende rigorosamente à diretriz do Seaborn moderno (v0.14+)[cite: 5].
        # - 'palette="mako"': aplica paleta cromática com transições contrastantes e corporativas[cite: 5].
        sns.barplot(
            data=valores_por_status,
            x="status_pagamento",
            y="valor_total",
            hue="status_pagamento",
            palette="mako",
            legend=False,
            ax=eixo,
        )

        # 'eixo.set_title(...)' configura o título principal com fonte 13 e espaçamento de 12 pontos[cite: 5].
        eixo.set_title("Exposição Financeira por Status de Cobrança (Aging)", fontsize=13, pad=12)

        # 'eixo.set_xlabel(...)' escreve a legenda do eixo horizontal em português[cite: 5].
        eixo.set_xlabel("Situação do Título de Cobrança", fontsize=10)

        # 'eixo.set_ylabel(...)' escreve a legenda financeira do eixo vertical em moeda corrente (R$)[cite: 5].
        eixo.set_ylabel("Volume Financeiro Total (R$)", fontsize=10)

        # 'plt.tight_layout()' ajusta automaticamente as margens do Matplotlib para evitar cortes de texto[cite: 5].
        plt.tight_layout()

        # 'figura.savefig(caminho_figura, dpi=300)' grava o arquivo físico no disco com resolução de 300 DPI[cite: 5].
        figura.savefig(caminho_figura, dpi=300)

        # 'plt.close(figura)' limpa o buffer gráfico da memória RAM, blindando o servidor contra vazamentos de memória[cite: 5].
        plt.close(figura)

        # 'logging.info' documenta a persistência da figura no console corporativo[cite: 5].
        logging.info("Financeiro — Gráfico de status de cobrança salvo com sucesso em: %s", caminho_figura.name)

        # Devolve a rota física da figura gravada no disco[cite: 5].
        return caminho_figura

    # 'def executar_diagnostico_completo(...)' implementa o contrato formal de execução da BaseDepartamento[cite: 5].
    def executar_diagnostico_completo(self) -> Dict[str, Any]:
        """Coordena o cálculo sequencial dos indicadores financeiros e a persistência das visualizações[cite: 5].

        Returns:
            Dict[str, Any]: Laudo executivo completo do departamento financeiro com métricas e caminho da imagem[cite: 5].
        """
        # Emite log formal marcando a abertura dos procedimentos do setor financeiro[cite: 5].
        logging.info("=== INICIANDO PERÍCIA DO DEPARTAMENTO FINANCEIRO (FASE 2.2) ===")

        # 1. Carrega os dados reais de títulos a receber utilizando o Adaptador Universal[cite: 5].
        df_financeiro = self.carregar_dados_financeiros()

        # 2. Executa a camada tabular apurando a taxa de inadimplência e o capital sob risco[cite: 5].
        laudo_inadimplencia = self.calcular_taxa_inadimplencia(df_financeiro)

        # 3. Executa a camada gráfica renderizando o gráfico de situação de cobrança e gravando a imagem[cite: 5].
        caminho_grafico = self.gerar_grafico_distribuicao_status(df_financeiro)

        # 'laudo_financeiro' consolida as métricas tabulares e a imagem gerada no dicionário oficial do setor[cite: 5].
        laudo_financeiro = {
            "analise_inadimplencia": laudo_inadimplencia,
            "grafico_status_cobranca": str(caminho_grafico),
        }

        # Emite log confirmando o encerramento bem-sucedido da perícia financeira[cite: 5].
        logging.info("=== DEPARTAMENTO FINANCEIRO CONCLUÍDO COM SUCESSO ===")

        # Devolve o laudo executivo financeiro para o orquestrador do Raio-X Empresarial[cite: 5].
        return laudo_financeiro