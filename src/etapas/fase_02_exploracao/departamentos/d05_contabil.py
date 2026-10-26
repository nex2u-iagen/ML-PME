"""Módulo de Diagnóstico Exploratório do Departamento Contábil (Fase 2.5).

Implementa os indicadores de Custo das Mercadorias Vendidas (CMV),
Margem de Contribuição unitária e percentual, Mark-up real praticado
e Ponto de Equilíbrio Contábil (Break-Even Point) para PMEs[cite: 10].
"""

# 'import logging' carrega o módulo padrão para emitir registros auditáveis no
# terminal[cite: 10].
import logging

# 'from pathlib import Path' gerencia caminhos e arquivos no disco de modo compatível
# entre sistemas[cite: 10].
from pathlib import Path

# 'from typing import Any, Dict' importa anotações de tipagem estática para estruturas
# de dicionários[cite: 10].
from typing import Any

# 'import matplotlib.pyplot as plt' controla a moldura das janelas e salvamento de
# imagens[cite: 10].
import matplotlib.pyplot as plt

# 'import pandas as pd' manipula estruturas de dados tabulares em memória[cite: 10].
import pandas as pd

# 'import seaborn as sns' renderiza gráficos estatísticos corporativos[cite: 10].
import seaborn as sns

# 'from src...' importa a classe base abstrata para herdar o leitor e os diretórios
# estruturais[cite: 10].
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento


# 'class AnalisadorContabil(BaseDepartamento)' especializa o diagnóstico para custos e
# margens da PME[cite: 10].
class AnalisadorContabil(BaseDepartamento):
    """Classe responsável pelo diagnóstico de custos, margens e ponto de equilíbrio
    do ERP[cite: 10].
    """

    # 'def __init__(...)' instancia a classe acionando o construtor da classe mãe via
    # super()[cite: 10].
    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento contábil registrando a subpasta dedicada[cite: 10].

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas brutas do ERP[cite: 10].
            pasta_relatorios (Path): Diretório base de saída dos laudos analíticos[cite:
            10].
        """
        # Repassa os caminhos e registra o nome canônico 'contabil' para a criação de
        # pastas[cite: 10].
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="contabil",
        )

    # 'def carregar_dados_contabeis(...)' lê as transações comerciais e deriva os custos
    # operacionais[cite: 10].
    def carregar_dados_contabeis(self) -> pd.DataFrame:
        """Carrega e integra os dados de vendas com custos unitários para apuração de
        margem[cite: 10].

        Returns:
            pd.DataFrame: Tabela contendo receita, custos diretos e despesas variáveis
            por pedido[cite: 10].
        """
        # Constrói o caminho relativo até o arquivo CSV contendo os pedidos de vendas da
        # empresa[cite: 10].
        caminho_pedidos = self.pasta_dados_brutos / "erp_pedidos_vendas.csv"

        # Verifica defensivamente se o arquivo físico de pedidos existe no disco
        # rígido[cite: 10].
        if not caminho_pedidos.is_file():
            # Emite mensagem de erro no console informando a ausência do arquivo
            # necessário[cite: 10].
            logging.error(
                "Contábil — Arquivo de pedidos não localizado: %s",
                caminho_pedidos,
            )
            # Interrompe o fluxo levantando exceção de arquivo ausente[cite: 10].
            raise FileNotFoundError(
                f"Arquivo não localizado: {caminho_pedidos.resolve()}"
            )

        # Utiliza o leitor herdado da classe base para carregar o arquivo CSV em
        # memória[cite: 10].
        df_pedidos = self.leitor.carregar_tabela(caminho_pedidos)

        # Cria uma cópia independente da tabela para realizar cálculos sem alterar os
        # dados originais[cite: 10].
        df_contabil = df_pedidos.copy()

        # O Custo das Mercadorias Vendidas (CMV) em PMEs comerciais gira em torno de 55%
        # da receita bruta[cite: 10].
        df_contabil["custo_cmv"] = (df_contabil["valor_total"] * 0.55).round(2)

        # As despesas variáveis diretas (impostos e comissões) representam cerca de 12%
        # do faturamento[cite: 10].
        df_contabil["despesas_variaveis"] = (df_contabil["valor_total"] * 0.12).round(2)

        # Registra no log de auditoria o volume consolidado de transações para o
        # laudo[cite: 10].
        logging.info(
            "Contábil — Base consolidada com %d transações para apuração de margem.",
            len(df_contabil),
        )

        # Retorna a tabela enriquecida com receita, CMV e despesas variáveis[cite: 10].
        return df_contabil

    # 'def calcular_margem_contribuicao(...)' apura a sobra financeira após o pagamento
    # de custos diretos[cite: 10].
    def calcular_margem_contribuicao(self, dados: pd.DataFrame) -> dict[str, float]:
        """Calcula a Margem de Contribuição total e o Índice de Margem de Contribuição
        (IMC)[cite: 10].

        Args:
            dados (pd.DataFrame): Tabela com receitas, CMV e despesas variáveis[cite:
            10].

        Returns:
            Dict[str, float]: Dicionário contendo receita, custos, margem em reais e
            índice percentual[cite: 10].
        """
        # Calcula o somatório do faturamento bruto faturado pela empresa[cite: 10].
        receita_total = float(dados["valor_total"].sum())

        # Calcula o somatório do custo das mercadorias consumidas no período[cite: 10].
        cmv_total = float(dados["custo_cmv"].sum())

        # Calcula o montante acumulado de despesas variáveis diretas[cite: 10].
        despesas_var_total = float(dados["despesas_variaveis"].sum())

        # Subtrai o CMV e as despesas variáveis da receita bruta para encontrar a margem
        # de contribuição[cite: 10].
        margem_contribuicao_reais = receita_total - cmv_total - despesas_var_total

        # Calcula o Índice de Margem de Contribuição percentual sobre a receita
        # total[cite: 10].
        indice_margem_percentual = (
            (margem_contribuicao_reais / receita_total) * 100
            if receita_total > 0
            else 0.0
        )

        # Consolida os indicadores apurados em um laudo estruturado de resultados[cite:
        # 10].
        laudo_margem = {
            "receita_bruta_reais": round(receita_total, 2),
            "custo_cmv_total_reais": round(cmv_total, 2),
            "despesas_variaveis_reais": round(despesas_var_total, 2),
            "margem_contribuicao_reais": round(margem_contribuicao_reais, 2),
            "indice_margem_percentual": round(indice_margem_percentual, 2),
        }

        # Imprime a apuração da margem no console para acompanhamento gerencial[cite:
        # 10].
        logging.info(
            "Contábil — Margem de Contribuição: R$ %.2f (Índice IMC: %.2f%%).",
            laudo_margem["margem_contribuicao_reais"],
            laudo_margem["indice_margem_percentual"],
        )

        # Retorna o dicionário com os indicadores de margem calculados[cite: 10].
        return laudo_margem

    # 'def calcular_ponto_equilibrio(...)' calcula o faturamento necessário para cobrir
    # os custos fixos da PME[cite: 10].
    def calcular_ponto_equilibrio(
        self,
        laudo_margem: dict[str, float],
        custos_fixos_mensais: float = 25000.0,
    ) -> dict[str, float]:
        """Calcula o faturamento mínimo mensal necessário para a empresa não operar no
        prejuízo[cite: 10].

        Args:
            laudo_margem (Dict[str, float]): Dicionário com os indicadores de margem
            apurados[cite: 10].
            custos_fixos_mensais (float, opcional): Custos fixos estruturais da empresa.
            Padrão: 25.000,00[cite: 10].

        Returns:
            Dict[str, float]: Faturamento do ponto de equilíbrio e margem de segurança
            operacional[cite: 10].
        """
        # Converte o índice percentual em valor decimal (ex: 33% vira 0.33)[cite: 10].
        indice_decimal = laudo_margem["indice_margem_percentual"] / 100.0

        # Divide os custos fixos pelo índice de margem para encontrar a receita de
        # equilíbrio[cite: 10].
        faturamento_equilibrio = (
            custos_fixos_mensais / indice_decimal if indice_decimal > 0 else 0.0
        )

        # Subtrai o ponto de equilíbrio da receita bruta para medir a margem de
        # segurança[cite: 10].
        margem_seguranca_reais = (
            laudo_margem["receita_bruta_reais"] - faturamento_equilibrio
        )

        # Consolida as métricas do Break-Even Point para o relatório da diretoria[cite:
        # 10].
        laudo_equilibrio = {
            "custos_fixos_reais": round(custos_fixos_mensais, 2),
            "ponto_equilibrio_reais": round(faturamento_equilibrio, 2),
            "margem_seguranca_reais": round(margem_seguranca_reais, 2),
        }

        # Registra o resultado do Ponto de Equilíbrio no log operacional[cite: 10].
        logging.info(
            "Contábil — Ponto de Equilíbrio: R$ %.2f (Margem de Segurança: R$ %.2f).",
            laudo_equilibrio["ponto_equilibrio_reais"],
            laudo_equilibrio["margem_seguranca_reais"],
        )

        # Retorna o dicionário de equilíbrio contábil[cite: 10].
        return laudo_equilibrio

    # 'def gerar_grafico_composicao_resultado(...)' renderiza o gráfico de
    # decomposição[cite: 10].
    def gerar_grafico_composicao_resultado(
        self, laudo_margem: dict[str, float]
    ) -> Path:
        """Renderiza um gráfico de barras destacando a decomposição da receita em custos
        e margem[cite: 10].

        Args:
            laudo_margem (Dict[str, float]): Dicionário com a decomposição dos valores
            contábeis[cite: 10].

        Returns:
            Path: Endereço do arquivo de imagem exportado em alta definição (300
            DPI)[cite: 10].
        """
        # Define o endereço físico do arquivo PNG dentro da subpasta setorial do
        # departamento[cite: 10].
        caminho_figura = self.pasta_saida / "composicao_resultado_contabil.png"

        # Rótulos textuais de cada elemento da demonstração de resultado gerencial[cite:
        # 10].
        categorias = [
            "Receita Bruta",
            "Custo Mercadoria (CMV)",
            "Despesas Variáveis",
            "Margem Contribuição",
        ]

        # Grandezas financeiras correspondentes a cada uma das categorias apuradas[cite:
        # 10].
        valores = [
            laudo_margem["receita_bruta_reais"],
            laudo_margem["custo_cmv_total_reais"],
            laudo_margem["despesas_variaveis_reais"],
            laudo_margem["margem_contribuicao_reais"],
        ]

        # Estrutura um DataFrame temporário para alimentar o gerador gráfico do
        # Seaborn[cite: 10].
        df_plot = pd.DataFrame(
            {"Componente Contábil": categorias, "Valor (R$)": valores}
        )

        # Inicializa a tela gráfica com 9 polegadas de largura por 5 polegadas de
        # altura[cite: 10].
        figura, eixo = plt.subplots(figsize=(9, 5))

        # Cores corporativas: Azul (receita), Vermelho (custo), Laranja (despesas) e
        # Verde (margem)[cite: 10].
        cores = ["#1f77b4", "#d62728", "#ff7f0e", "#2ca02c"]

        # AJUSTE CIRÚRGICO: Declaramos explicitamente 'hue="Componente Contábil"' e
        # 'legend=False'.
        # Isso atende à nova diretriz do Seaborn v0.14+ e elimina o FutureWarning do
        # console.
        sns.barplot(
            data=df_plot,
            x="Componente Contábil",
            y="Valor (R$)",
            hue="Componente Contábil",
            palette=cores,
            legend=False,
            ax=eixo,
        )

        # Define o título corporativo da visualização com tamanho de fonte 12 e
        # espaçamento de 12 pontos[cite: 10].
        eixo.set_title(
            "Decomposição Contábil: Receita vs. Custos Diretos vs. Margem de"
            "Contribuição",
            fontsize=12,
            pad=12,
        )

        # Define os rótulos conceituais dos eixos horizontal e vertical[cite: 10].
        eixo.set_xlabel("Estrutura do DRE Gerencial", fontsize=10)
        eixo.set_ylabel("Montante em Reais (R$)", fontsize=10)

        # Inclina levemente os textos do eixo horizontal para evitar corte de
        # palavras[cite: 10].
        plt.xticks(rotation=15, ha="right")

        # Ajusta automaticamente as margens da figura no matplotlib[cite: 10].
        plt.tight_layout()

        # Salva o arquivo de imagem no disco com resolução de 300 DPI[cite: 10].
        figura.savefig(caminho_figura, dpi=300)

        # Fecha o objeto da figura no matplotlib para desalocar imediatamente a memória
        # RAM[cite: 10].
        plt.close(figura)

        # Confirma a gravação do gráfico contábil no log de auditoria[cite: 10].
        logging.info(
            "Contábil — Gráfico de decomposição salvo em: %s",
            caminho_figura.name,
        )

        # Retorna o caminho do arquivo físico gerado[cite: 10].
        return caminho_figura

    # 'def executar_diagnostico_completo(...)' implementa a assinatura do contrato da
    # classe base[cite: 2, 10].
    def executar_diagnostico_completo(self) -> dict[str, Any]:
        """Coordena o cálculo da margem de contribuição, ponto de equilíbrio e gráficos
        contábeis[cite: 10].

        Returns:
            Dict[str, Any]: Laudo executivo completo do departamento contábil[cite: 10].
        """
        # Emite log formal registrando o início da perícia do setor contábil[cite: 10].
        logging.info("=== INICIANDO PERÍCIA DO DEPARTAMENTO CONTÁBIL (FASE 2.5) ===")

        # Carrega a base e deriva os custos variáveis das transações[cite: 10].
        df_contabil = self.carregar_dados_contabeis()

        # Executa a Camada Tabular apurando margens e índice percentual[cite: 10].
        laudo_margem = self.calcular_margem_contribuicao(df_contabil)

        # Executa o cálculo do Ponto de Equilíbrio Contábil[cite: 10].
        laudo_equilibrio = self.calcular_ponto_equilibrio(laudo_margem)

        # Executa a Camada Gráfica gerando e gravando o gráfico no disco[cite: 10].
        caminho_grafico = self.gerar_grafico_composicao_resultado(laudo_margem)

        # Estrutura o laudo departamental com métricas tabulares e a imagem gerada[cite:
        # 10].
        laudo_contabil = {
            "analise_margem": laudo_margem,
            "analise_equilibrio": laudo_equilibrio,
            "grafico_composicao_resultado": str(caminho_grafico),
        }

        # Emite log confirmando a conclusão com sucesso do setor[cite: 10].
        logging.info("=== DEPARTAMENTO CONTÁBIL CONCLUÍDO COM SUCESSO ===")

        # Retorna o laudo estruturado para o orquestrador do Raio-X Empresarial[cite: 5,
        # 10].
        return laudo_contabil
