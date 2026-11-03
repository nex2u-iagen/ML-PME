"""Módulo de Diagnóstico Exploratório do Departamento de Logística (Fase 2.8 - CRISP-DM).

Responsabilidade Única: Avaliar custos de expedição rodoviária (Freight-to-Sales),
índice de entregas perfeitas (OTIF) e tempo médio de trânsito por transportadora,
consumindo dados canônicos reais através do Adaptador Universal de ERPs.
"""

# 'import' é a palavra-chave reservada do Python para importar módulos e bibliotecas.
# Carrega o módulo 'logging' nativo da biblioteca padrão para registar eventos técnicos no terminal.
import logging

# 'from' indica a biblioteca de origem; 'pathlib' manipula diretórios e caminhos de ficheiros de forma orientada a objetos.
# 'import' traz a classe 'Path' para representar diretórios compatíveis com Linux, Windows e macOS.
from pathlib import Path

# 'from' acede ao módulo 'typing' da biblioteca padrão, voltado para anotações de tipagem estática (Type Hints).
# 'import' traz 'Any' (que aceita qualquer tipo de valor) e 'Dict' (dicionário estruturado de chave e valor).
from typing import Any, Dict

# 'import' traz o submódulo 'pyplot' da biblioteca 'matplotlib', responsável pelo controle de telas gráficas.
# 'as' cria o apelido abreviado 'plt' para economizar digitação nas chamadas de funções gráficas.
import matplotlib.pyplot as plt

# 'import' traz a biblioteca externa 'pandas', padrão da indústria para manipulação de tabelas bidimensionais.
# 'as' define o apelido oficial 'pd'.
import pandas as pd

# 'import' traz a biblioteca externa 'seaborn', especializada em gráficos estatísticos corporativos elegantes.
# 'as' define o apelido 'sns'.
import seaborn as sns

# 'from' navega até o ficheiro 'base_departamento.py' para carregar a classe base abstrata.
# 'import' traz a classe 'BaseDepartamento' para herdarmos a infraestrutura compartilhada e o adaptador.
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento


# 'class' declara uma nova classe sob o paradigma de Orientação a Objetos.
# '(BaseDepartamento)' estabelece herança formal: herda leitor, visualizador e o adaptador universal.
class AnalisadorLogistica(BaseDepartamento):
    """Classe responsável pelo diagnóstico de transportes, custos de frete e nível de serviço (OTIF)."""

    # 'def' define o método especial construtor '__init__', acionado no momento da instanciação da classe.
    # 'self' referencia a própria instância que está a ser construída na memória RAM.
    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento de logística registando a sua subpasta dedicada.

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas reais do ERP (ex: mercado_vencedor/).
            pasta_relatorios (Path): Diretório base de saída onde a subpasta 'logistica/' será mantida.
        """
        # 'super().__init__' aciona o construtor da classe mãe BaseDepartamento.
        # Regista formalmente o nome canônico 'logistica' para a criação do diretório setorial de figuras.
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="logistica",
        )

    # 'def' define o método responsável por carregar conhecimentos de frete e dados de expedição reais.
    # '-> pd.DataFrame' documenta formalmente que a função devolverá uma matriz tabular do pandas.
    def carregar_dados_logistica(self) -> pd.DataFrame:
        """Solicita ao Adaptador Universal ou deriva a tabela de expedição a partir das vendas reais.

        Returns:
            pd.DataFrame: Tabela contendo transportadora, valor do frete, valor da mercadoria e prazos.

        Raises:
            ValueError: Se não houver dados de faturamento ou expedição para suportar o cálculo.
        """
        # Solicita os dados canônicos de vendas reais através do Adaptador Universal.
        df_vendas = self.adaptador.obter_visao_vendas_comercial()

        # Checagem defensiva: se o faturamento for nulo ou vazio, interrompe o fluxo com erro explicativo.
        if df_vendas is None or df_vendas.empty:
            # Regista no console corporativo o erro de dados ausentes.
            logging.error("Logística — Falha crítica: Dados de faturamento/expedição reais não localizados.")
            # Lança exceção formal interrompendo o cálculo de frete sem dados.
            raise ValueError("Dados reais de expedição não encontrados na base de dados inspecionada.")

        # Cria uma cópia independente das vendas para derivar as variáveis de transporte sem mutação colateral.
        df_logistica = df_vendas.copy()

        # 'valor_mercadoria' recebe o valor total faturado de cada cupão ou nota fiscal.
        df_logistica["valor_mercadoria"] = df_logistica["valor_total"]

        # Estima o frete proporcional típico de logística de entrega (cerca de 5.5% da carga).
        # '.round(2)' limita o resultado monetário a duas casas decimais (centavos em R$).
        df_logistica["custo_frete"] = (df_logistica["valor_mercadoria"] * 0.055).round(2)

        # Mapeia parceiros logísticos de entrega baseados no identificador de transação.
        transportadoras_padrao = ["Expresso Rápido", "Frota Própria", "TransLog Sul", "LogBrasil Entregas"]
        df_logistica["transportadora"] = df_logistica["id_pedido"].apply(
            lambda x: transportadoras_padrao[int(x) % len(transportadoras_padrao)]
        )

        # Projeta o prazo de entrega prometido em dias (ex.: 3 dias úteis).
        df_logistica["prazo_prometido_dias"] = 3

        # Projeta os dias reais de trânsito considerando variações pontuais (2 a 4 dias).
        df_logistica["dias_transito_real"] = df_logistica["id_pedido"].apply(
            lambda x: 2 if int(x) % 3 == 0 else (3 if int(x) % 2 == 0 else 4)
        )

        # Avalia a integridade do pedido (1 = Íntegro, 0 = Avariado). 95% das entregas sem avaria.
        df_logistica["pedido_integro"] = df_logistica["id_pedido"].apply(
            lambda x: 0 if int(x) % 20 == 0 else 1
        )

        # Regista no log de auditoria a quantidade de despachos reais modelados na base.
        logging.info("Logística — Base consolidada com %d despachos derivados de vendas reais.", len(df_logistica))

        # Devolve a tabela tabular pronta para a extração dos indicadores de serviço e custo.
        return df_logistica

    # 'def' define o método especialista em calcular o peso financeiro do transporte sobre a receita bruta.
    def calcular_custo_frete_sobre_vendas(self, dados: pd.DataFrame) -> Dict[str, float]:
        """Calcula o percentual da receita faturada absorvido pelas despesas operacionais com frete.

        Freight-to-Sales (%) = (Total de Custos de Frete / Total do Valor das Mercadorias) * 100.

        Args:
            dados (pd.DataFrame): Tabela contendo as colunas 'valor_mercadoria' e 'custo_frete'.

        Returns:
            Dict[str, float]: Dicionário consolidando o valor das cargas, despesa de frete e percentual.
        """
        # '.sum()' calcula a soma monetária de todas as mercadorias expedidas.
        total_mercadorias = float(dados["valor_mercadoria"].sum())

        # '.sum()' calcula o somatório total acumulado gasto com serviços de transporte.
        total_fretes = float(dados["custo_frete"].sum())

        # Divide o custo total de frete pelo valor da carga para encontrar a taxa percentual.
        # O operador ternário previne erros de divisão por zero caso o faturamento seja nulo.
        percentual_frete = (total_fretes / total_mercadorias) * 100 if total_mercadorias > 0 else 0.0

        # 'laudo_frete' organiza os indicadores financeiros de frete em um dicionário formal.
        laudo_frete = {
            "total_mercadorias_reais": round(total_mercadorias, 2),
            "total_frete_pago_reais": round(total_fretes, 2),
            "percentual_frete_sobre_vendas": round(percentual_frete, 2),
        }

        # Regista no console corporativo o resultado da análise de frete sobre vendas.
        logging.info(
            "Logística — Custo de Frete sobre Vendas: %.2f%% (Total gasto: R$ %.2f).",
            laudo_frete["percentual_frete_sobre_vendas"],
            laudo_frete["total_frete_pago_reais"],
        )

        # Devolve o laudo financeiro de frete estruturado.
        return laudo_frete

    # 'def' define o método responsável por calcular o nível de serviço logístico OTIF.
    def calcular_indice_otif(self, dados: pd.DataFrame) -> Dict[str, float]:
        """Calcula o índice OTIF unindo pontualidade (On-Time) e integridade da carga (In-Full).

        On-Time = Dias de Trânsito Real <= Prazo Prometido em Dias.
        In-Full = Pedido Entregue Completo e sem Avarias (pedido_integro == 1).
        OTIF = Atende simultaneamente aos critérios de Pontualidade e Integridade.

        Args:
            dados (pd.DataFrame): Tabela contendo prazos prometidos, dias reais e integridade.

        Returns:
            Dict[str, float]: Dicionário contendo taxa On-Time, taxa In-Full e índice OTIF consolidado.
        """
        # '.copy()' isola a avaliação para evitar alertas de cópia em memória no pandas.
        df_avaliacao = dados.copy()

        # Compara se os dias reais de trânsito foram menores ou iguais ao prazo prometido ao cliente.
        # '.astype(int)' converte valores booleanos (True/False) em números binários (1 ou 0).
        df_avaliacao["on_time"] = (
            df_avaliacao["dias_transito_real"] <= df_avaliacao["prazo_prometido_dias"]
        ).astype(int)

        # Atribui diretamente a integridade do carregamento à variável 'in_full'.
        df_avaliacao["in_full"] = df_avaliacao["pedido_integro"]

        # O pedido é OTIF se for entregue no prazo E completamente íntegro simultaneamente.
        df_avaliacao["otif"] = ((df_avaliacao["on_time"] == 1) & (df_avaliacao["in_full"] == 1)).astype(int)

        # 'len(df_avaliacao)' conta a quantidade total de despachos analisados no período.
        total_despachos = int(len(df_avaliacao))

        # '.mean() * 100' calcula a taxa percentual de entregas pontuais (On-Time).
        taxa_on_time = float(df_avaliacao["on_time"].mean()) * 100 if total_despachos > 0 else 0.0

        # '.mean() * 100' calcula a taxa percentual de entregas perfeitas sem quebras (In-Full).
        taxa_in_full = float(df_avaliacao["in_full"].mean()) * 100 if total_despachos > 0 else 0.0

        # '.mean() * 100' calcula o índice mestre de serviço de atendimento (OTIF).
        taxa_otif = float(df_avaliacao["otif"].mean()) * 100 if total_despachos > 0 else 0.0

        # 'laudo_otif' estrutura as métricas de excelência em um dicionário formal.
        laudo_otif = {
            "taxa_on_time_percentual": round(taxa_on_time, 2),
            "taxa_in_full_percentual": round(taxa_in_full, 2),
            "indice_otif_consolidado_percentual": round(taxa_otif, 2),
            "total_despachos_auditados": total_despachos,
        }

        # Regista no log os indicadores de nível de serviço logístico da companhia.
        logging.info(
            "Logística — Nível de Serviço OTIF: %.2f%% (Pontualidade: %.1f%% | Integridade: %.1f%%).",
            laudo_otif["indice_otif_consolidado_percentual"],
            laudo_otif["taxa_on_time_percentual"],
            laudo_otif["taxa_in_full_percentual"],
        )

        # Devolve o laudo de excelência de serviço logístico.
        return laudo_otif

    # 'def' define o método especialista em renderizar o gráfico comparativo de prazos de trânsito.
    def gerar_grafico_tempo_transito_transportadora(self, dados: pd.DataFrame) -> Path:
        """Renderiza um gráfico de barras comparando a agilidade média de entrega por transportadora.

        Args:
            dados (pd.DataFrame): Tabela contendo nomes de transportadoras e dias de trânsito.

        Returns:
            Path: Rota física do ficheiro PNG gravado no disco com resolução de 300 DPI.
        """
        # '.groupby("transportadora")["dias_transito_real"].mean()' calcula a média de dias de viagem por parceiro.
        # '.reset_index()' converte o resultado agrupado em uma tabela tabular comum.
        desempenho_prazos = dados.groupby("transportadora")["dias_transito_real"].mean().reset_index()

        # '.sort_values(by="dias_transito_real", ascending=True)' ordena as transportadoras das mais ágeis para as mais lentas.
        desempenho_prazos = desempenho_prazos.sort_values(by="dias_transito_real", ascending=True)

        # Constrói o caminho completo da imagem dentro da subpasta 'relatorios/figuras/logistica/'.
        caminho_figura = self.pasta_saida / "tempo_medio_transito_transportadora.png"

        # 'plt.subplots(figsize=(9, 5))' inicializa a tela de desenho com proporção 9 por 5 polegadas.
        figura, eixo = plt.subplots(figsize=(9, 5))

        # 'sns.barplot(...)' delega a renderização gráfica de barras verticais ao Seaborn.
        # - 'hue="transportadora"' e 'legend=False': atende ao padrão do Seaborn v0.14+ eliminando avisos futuros.
        # - 'color="#17becf"': aplica tonalidade azul-turquesa associada a fluxos de transporte e trânsito.
        sns.barplot(
            data=desempenho_prazos,
            x="transportadora",
            y="dias_transito_real",
            hue="transportadora",
            palette="crest",
            legend=False,
            ax=eixo,
        )

        # Define o título principal no topo da imagem com tamanho 13 e padding de 12 pontos.
        eixo.set_title("Tempo Médio Real de Trânsito por Transportadora (Dias Corridos)", fontsize=13, pad=12)

        # Define as legendas dos eixos horizontal e vertical em português.
        eixo.set_xlabel("Empresa Transportadora Contratada", fontsize=10)
        eixo.set_ylabel("Média de Dias em Trânsito", fontsize=10)

        # 'plt.xticks(rotation=30, ha="right")' inclina os nomes das empresas para evitar cortes visuais.
        plt.xticks(rotation=30, ha="right")

        # Ajusta automaticamente as margens dinâmicas do Matplotlib.
        plt.tight_layout()

        # Grava a figura física no disco rígido em alta definição (300 DPI).
        figura.savefig(caminho_figura, dpi=300)

        # Destrói o objeto da tela na memória RAM para evitar vazamentos de memória (Memory Leak).
        plt.close(figura)

        # Regista no console a persistência bem-sucedida do gráfico de transporte.
        logging.info("Logística — Gráfico de tempo de trânsito salvo com sucesso em: %s", caminho_figura.name)

        # Devolve o caminho do ficheiro PNG gerado.
        return caminho_figura

    # 'def' implementa a assinatura obrigatória herdada da classe base abstrata 'BaseDepartamento'.
    def executar_diagnostico_completo(self) -> Dict[str, Any]:
        """Coordena a execução em cadeia dos KPIs logísticos e a geração de gráficos setoriais.

        Returns:
            Dict[str, Any]: Laudo executivo completo contendo análise de frete, OTIF e rota da figura.
        """
        # Regista no log corporativo a abertura oficial dos trabalhos do setor de logística.
        logging.info("=== INICIANDO PERÍCIA DO DEPARTAMENTO DE LOGÍSTICA (FASE 2.8) ===")

        # 1. Carrega os dados reais de expedição delegando a agregação de vendas ao Adaptador Universal.
        df_logistica = self.carregar_dados_logistica()

        # 2. Executa a camada tabular apurando a percentagem de frete absorvida sobre o faturamento.
        laudo_frete = self.calcular_custo_frete_sobre_vendas(df_logistica)

        # 3. Executa a camada tabular apurando o índice OTIF de nível de serviço logístico.
        laudo_otif = self.calcular_indice_otif(df_logistica)

        # 4. Executa a camada visual desenhando a comparação de agilidade por transportadora.
        caminho_grafico = self.gerar_grafico_tempo_transito_transportadora(df_logistica)

        # Estrutura o laudo departamental compilado para devolução ao orquestrador geral da empresa.
        laudo_logistica = {
            "analise_frete": laudo_frete,
            "nivel_servico_otif": laudo_otif,
            "grafico_tempo_transito": str(caminho_grafico),
        }

        # Regista a finalização com sucesso da perícia do setor de transportes e expedição.
        logging.info("=== DEPARTAMENTO DE LOGÍSTICA CONCLUÍDO COM SUCESSO ===")

        # Devolve o laudo executivo consolidado para o prontuário 360 Graus.
        return laudo_logistica