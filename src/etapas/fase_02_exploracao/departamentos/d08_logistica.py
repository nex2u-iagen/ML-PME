"""Módulo de Diagnóstico Exploratório do Departamento de Logística (Fase 2.8).

Implementa a apuração da relação Custo de Frete sobre Vendas (Freight-to-Sales),
o índice de entregas pontuais e completas (OTIF - On-Time In-Full),
a duração média de trânsito por transportadora e a persistência visual para PMEs.
"""

# 'import' é a palavra-chave reservada do Python para importar bibliotecas e recursos de
# código.
# Carrega o módulo 'logging' da biblioteca padrão para exibir mensagens com carimbo de
# auditoria no terminal.
import logging

# 'from' indica o módulo de origem; 'pathlib' manipula diretórios e arquivos de forma
# orientada a objetos.
# 'import' traz a classe 'Path' para gerenciar endereços de disco de modo compatível
# entre sistemas operacionais.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão, voltado para anotações de
# tipagem estática (Type Hints).
# 'import' carrega 'Any' (aceita qualquer tipo de valor) e 'Dict' (dicionário
# estruturado com chaves e valores).
from typing import Any

# 'import' traz o submódulo 'pyplot' da biblioteca 'matplotlib', responsável pelo
# controle de janelas e telas gráficas.
# 'as' define o apelido universal 'plt' para encurtar a sintaxe na criação de gráficos.
import matplotlib.pyplot as plt

# 'import' traz a biblioteca externa 'pandas', padrão mundial para criação e manipulação
# de tabelas de dados.
# 'as' define o apelido clássico 'pd' para facilitar operações sobre matrizes e
# DataFrames.
import pandas as pd

# 'import' traz a biblioteca externa 'seaborn', especializada na renderização de
# gráficos estatísticos corporativos.
# 'as' define o apelido 'sns'.
import seaborn as sns

# 'from' navega até o arquivo 'base_departamento.py' localizado na pasta pai de
# exploração.
# 'import' traz a classe abstrata 'BaseDepartamento' para herdarmos a infraestrutura
# pronta do núcleo compartilhado.
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento


# 'class' é a palavra-chave que declara um novo molde estrutural orientado a objetos.
# 'AnalisadorLogistica' é o nome da nossa classe especializada em auditoria de
# transportes, em estilo PascalCase.
# '(BaseDepartamento)' entre parênteses estabelece herança: esta classe herda os
# recursos e o leitor da classe mãe.
class AnalisadorLogistica(BaseDepartamento):
    """Classe responsável pelo diagnóstico de expedição, custos de frete e nível de
    serviço logístico (OTIF).
    """

    # 'def' define o método especial construtor '__init__', executado no instante em que
    # o objeto é criado na memória RAM.
    # 'self' referencia a própria instância acessando seus atributos internos.
    # 'pasta_dados_brutos: Path' é o parâmetro com anotação de tipo que exige o caminho
    # da pasta de dados CSV.
    # 'pasta_relatorios: Path' é o caminho raiz onde os laudos e imagens deste
    # departamento serão gravados.
    # '-> None' documenta formalmente que o método inicializador não retorna dados.
    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento de logística registrando a subpasta dedicada.

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas brutas do ERP.
            pasta_relatorios (Path): Diretório base de saída dos laudos analíticos.
        """
        # 'super().__init__' aciona formalmente o construtor da classe base mãe
        # BaseDepartamento.
        # Passamos as pastas e registramos o nome canônico 'logistica' para criar a
        # subpasta de figuras no disco.
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="logistica",
        )

    # 'def' define o método responsável por carregar conhecimentos de frete e despachos
    # do disco rígido.
    # '-> pd.DataFrame' documenta que a função devolverá uma matriz tabular
    # bidimensional do pandas.
    def carregar_dados_logistica(self) -> pd.DataFrame:
        """Carrega ou simula a tabela de expedição, fretes pagos, prazos e integridade
        de entrega.

        Returns:
            pd.DataFrame: Tabela contendo transportadora, valor do frete, valor da
            carga, prazos e status OTIF.
        """
        # O operador '/' une os caminhos de forma nativa via Pathlib, gerando o endereço
        # exato do arquivo CSV logístico.
        caminho_logistica = self.pasta_dados_brutos / "erp_expedicao_logistica.csv"

        # '.is_file()' verifica fisicamente no disco rígido se o arquivo existe.
        # 'if not' faz a checagem defensiva: se o arquivo não existir, geramos uma base
        # didática representativa da PME.
        if not caminho_logistica.is_file():
            # 'logging.info' emite um aviso no terminal informando que a base de
            # contingência logística foi iniciada.
            logging.info(
                "Logística — Base não localizada. Gerando despachos e conhecimentos de"
                "frete sintéticos..."
            )

            # 'dados_simulados' é um dicionário Python ('{}') contendo listas
            # estruturadas com despachos de transporte.
            dados_simulados = {
                # Lista de códigos identificadores únicos de cada conhecimento de
                # transporte (CT-e) despachado.
                "id_despacho": [
                    901,
                    902,
                    903,
                    904,
                    905,
                    906,
                    907,
                    908,
                    909,
                    910,
                ],
                # Nome da empresa transportadora contratada para realizar a
                # transferência rodoviária da carga.
                "transportadora": [
                    "Expresso Rodoviário",
                    "TransLog Rápido",
                    "Cargas Brasil",
                    "Expresso Rodoviário",
                    "LogSul Transportes",
                    "TransLog Rápido",
                    "Cargas Brasil",
                    "Expresso Rodoviário",
                    "LogSul Transportes",
                    "TransLog Rápido",
                ],
                # Região geográfica de destino da entrega para cálculo de tempos médios
                # de trânsito.
                "regiao_destino": [
                    "Sudeste",
                    "Sul",
                    "Nordeste",
                    "Sudeste",
                    "Sul",
                    "Centro-Oeste",
                    "Nordeste",
                    "Sudeste",
                    "Sul",
                    "Sudeste",
                ],
                # Valor da nota fiscal da mercadoria transportada dentro do caminhão em
                # reais (R$).
                "valor_mercadoria": [
                    15000.0,
                    22000.0,
                    18500.0,
                    8900.0,
                    34000.0,
                    12500.0,
                    29000.0,
                    45000.0,
                    9800.0,
                    16200.0,
                ],
                # Custo do frete contratado cobrado pela transportadora para realizar o
                # frete em reais.
                "custo_frete": [
                    950.0,
                    1800.0,
                    2400.0,
                    650.0,
                    2200.0,
                    1450.0,
                    3600.0,
                    2100.0,
                    850.0,
                    1100.0,
                ],
                # Prazo limite de entrega acordado com o cliente final medido em dias
                # corridos.
                "prazo_prometido_dias": [
                    3,
                    5,
                    8,
                    3,
                    4,
                    6,
                    9,
                    4,
                    4,
                    3,
                ],
                # Quantidade de dias corridos que a transportadora efetivamente levou
                # para entregar o produto.
                "dias_transito_real": [
                    3,
                    4,
                    10,
                    2,
                    4,
                    7,
                    9,
                    3,
                    5,
                    3,
                ],
                # Indicador binário se o pedido foi entregue completo e sem quebras (1 =
                # Íntegro, 0 = Avariado/Incompleto).
                "pedido_integro": [
                    1,
                    1,
                    0,
                    1,
                    1,
                    1,
                    0,
                    1,
                    1,
                    1,
                ],
            }

            # 'pd.DataFrame' converte a estrutura de dicionário em uma matriz tabular do
            # pandas em memória RAM.
            df_logistica = pd.DataFrame(dados_simulados)

            # '.to_csv' grava a tabela gerada no disco rígido para permitir auditorias
            # posteriores da expedição.
            # 'index=False' impede que o pandas crie uma coluna extra de números
            # desnecessária no arquivo físico.
            df_logistica.to_csv(caminho_logistica, index=False)
        else:
            # Caso o arquivo já exista fisicamente no disco rígido, usamos o leitor
            # herdado da classe base.
            df_logistica = self.leitor.carregar_tabela(caminho_logistica)

        # 'logging.info' imprime no console o total de despachos consolidados para a
        # auditoria de transportes.
        logging.info(
            "Logística — Base consolidada com %d despachos auditados.",
            len(df_logistica),
        )

        # 'return' devolve a matriz tabular pronta para os cálculos de indicadores de
        # expedição.
        return df_logistica

    # KPI 71: Custo de Frete sobre Vendas (Freight-to-Sales Ratio em Percentual).
    # 'def' define o método especialista em apurar o peso financeiro das transportadoras
    # sobre a receita.
    def calcular_custo_frete_sobre_vendas(
        self, dados: pd.DataFrame
    ) -> dict[str, float]:
        """Calcula o percentual do faturamento bruto absorvido pelas despesas com frete
        rodoviário.

        Freight-to-Sales (%) = (Total de Custos de Frete / Total do Valor das
        Mercadorias) * 100.

        Args:
            dados (pd.DataFrame): Tabela contendo valores de mercadorias e custos de
            frete.

        Returns:
            Dict[str, float]: Dicionário contendo valor das cargas, gasto de frete e a
            taxa percentual.
        """
        # '.sum()' calcula a soma do valor total das mercadorias despachadas; 'float()'
        # garante formato decimal.
        total_mercadorias = float(dados["valor_mercadoria"].sum())

        # '.sum()' calcula o total acumulado gasto com as faturas das transportadoras
        # rodoviárias.
        total_fretes = float(dados["custo_frete"].sum())

        # Divide o custo total de frete pelo valor das mercadorias para encontrar a taxa
        # percentual do frete.
        # O operador ternário 'if total_mercadorias > 0 else 0.0' previne erros de
        # divisão por zero caso a base esteja vazia.
        percentual_frete = (
            (total_fretes / total_mercadorias) * 100 if total_mercadorias > 0 else 0.0
        )

        # 'laudo_frete' organiza os indicadores financeiros de transporte para o comitê
        # executivo e a controladoria.
        laudo_frete = {
            # 'round(..., 2)' arredonda o valor total despachado em reais com precisão
            # de centavos.
            "total_mercadorias_reais": round(total_mercadorias, 2),
            # 'round(..., 2)' arredonda o custo total de fretes em reais.
            "total_frete_pago_reais": round(total_fretes, 2),
            # 'round(..., 2)' arredonda o percentual do frete sobre a receita bruta (%).
            "percentual_frete_sobre_vendas": round(percentual_frete, 2),
        }

        # 'logging.info' imprime o custo de frete no console para auditoria operacional
        # de expedição.
        logging.info(
            "Logística — Custo de Frete sobre Vendas: %.2f%% (Total gasto: R$ %.2f).",
            laudo_frete["percentual_frete_sobre_vendas"],
            laudo_frete["total_frete_pago_reais"],
        )

        # 'return' devolve o dicionário estruturado com as métricas de custo de frete.
        return laudo_frete

    # KPI 73: Índice de Entregas no Prazo e Completas (OTIF — On-Time In-Full em
    # Percentual).
    # 'def' declara a função especializada em calcular a métrica de excelência de
    # atendimento ao cliente.
    def calcular_indice_otif(self, dados: pd.DataFrame) -> dict[str, float]:
        """Calcula o índice OTIF unindo pontualidade (On-Time) e integridade da
        mercadoria (In-Full).

        On-Time = Dias de Trânsito Real <= Prazo Prometido em Dias.
        In-Full = Pedido Entregue Íntegro e Completo.
        OTIF = Pedido Atende Simultaneamente aos critérios On-Time E In-Full.

        Args:
            dados (pd.DataFrame): Tabela de expedição com prazos prometidos, reais e
            integridade.

        Returns:
            Dict[str, float]: Dicionário contendo taxa On-Time, taxa In-Full e o índice
            OTIF consolidado.
        """
        # '.copy()' cria uma cópia independente da tabela para criar colunas lógicas sem
        # alterar a matriz original.
        df_avaliacao = dados.copy()

        # Compara se os dias reais de trânsito foram menores ou iguais ao prazo
        # prometido ao cliente.
        # '.astype(int)' converte o resultado booleano (True/False) em número binário (1
        # para pontual, 0 para atrasado).
        df_avaliacao["on_time"] = (
            df_avaliacao["dias_transito_real"] <= df_avaliacao["prazo_prometido_dias"]
        ).astype(int)

        # 'in_full' utiliza o indicador de pedido íntegro e sem faltas já cadastrado na
        # tabela de dados.
        df_avaliacao["in_full"] = df_avaliacao["pedido_integro"]

        # O pedido é classificado como OTIF se for pontual (On-Time == 1) E íntegro
        # (In-Full == 1) simultaneamente.
        df_avaliacao["otif"] = (
            (df_avaliacao["on_time"] == 1) & (df_avaliacao["in_full"] == 1)
        ).astype(int)

        # 'int(len(df_avaliacao))' conta a quantidade total de despachos expedidos no
        # período.
        total_despachos = int(len(df_avaliacao))

        # '.mean() * 100' calcula a taxa percentual média de pontualidade das
        # transportadoras contratadas.
        taxa_on_time = (
            float(df_avaliacao["on_time"].mean()) * 100 if total_despachos > 0 else 0.0
        )

        # '.mean() * 100' calcula a taxa percentual de pedidos entregues sem itens
        # faltantes ou caixas amassadas.
        taxa_in_full = (
            float(df_avaliacao["in_full"].mean()) * 100 if total_despachos > 0 else 0.0
        )

        # '.mean() * 100' calcula a taxa percentual consolidada do índice OTIF geral da
        # PME.
        taxa_otif = (
            float(df_avaliacao["otif"].mean()) * 100 if total_despachos > 0 else 0.0
        )

        # 'laudo_otif' reúne as métricas fundamentais de nível de serviço logístico.
        laudo_otif = {
            # 'round(..., 2)' arredonda o percentual de entregas dentro do prazo
            # prometido (On-Time %).
            "taxa_on_time_percentual": round(taxa_on_time, 2),
            # 'round(..., 2)' arredonda o percentual de entregas completas e sem avarias
            # (In-Full %).
            "taxa_in_full_percentual": round(taxa_in_full, 2),
            # 'round(..., 2)' arredonda o indicador mestre de excelência operacional
            # (OTIF %).
            "indice_otif_consolidado_percentual": round(taxa_otif, 2),
            # Registra o volume total de entregas auditadas.
            "total_despachos_auditados": total_despachos,
        }

        # 'logging.info' imprime o indicador OTIF no console para auditoria da gerência
        # de operações.
        logging.info(
            "Logística — Nível de Serviço OTIF: %.2f%% (Pontualidade: %.1f%% |"
            "Integridade: %.1f%%).",
            laudo_otif["indice_otif_consolidado_percentual"],
            laudo_otif["taxa_on_time_percentual"],
            laudo_otif["taxa_in_full_percentual"],
        )

        # 'return' devolve o laudo consolidado de nível de serviço.
        return laudo_otif

    # KPI 76: Tempo Médio de Trânsito por Transportadora (Desempenho Comparativo de
    # Parceiros Logísticos).
    # 'def' define o método especialista em renderizar o gráfico comparativo de prazos
    # de trânsito em dias.
    def gerar_grafico_tempo_transito_transportadora(self, dados: pd.DataFrame) -> Path:
        """Renderiza um gráfico de barras comparando o tempo médio real de entrega por
        transportadora.

        Args:
            dados (pd.DataFrame): Tabela contendo nomes de transportadoras e dias reais
            de trânsito.

        Returns:
            Path: Endereço físico do arquivo de imagem exportado em alta resolução (300
            DPI).
        """
        # '.groupby("transportadora")' agrupa os fretes pelo nome do parceiro rodoviário
        # contratado.
        # '["dias_transito_real"].mean()' calcula a média aritmética de dias que a
        # transportadora leva para entregar.
        # '.reset_index()' converte a agregação em um DataFrame tabular com colunas
        # convencionais.
        desempenho_prazos = (
            dados.groupby("transportadora")["dias_transito_real"].mean().reset_index()
        )

        # '.sort_values()' ordena as transportadoras de forma crescente pelo tempo de
        # entrega (as mais rápidas no topo).
        desempenho_prazos = desempenho_prazos.sort_values(
            by="dias_transito_real", ascending=True
        )

        # 'self.pasta_saida' aponta para a pasta 'relatorios/figuras/logistica/', criada
        # pelo construtor base.
        caminho_figura = self.pasta_saida / "tempo_medio_transito_transportadora.png"

        # 'plt.subplots()' inicializa uma moldura gráfica com 9 polegadas de largura por
        # 5 de altura.
        # 'figura' representa a tela global; 'eixo' é a área interna onde as barras
        # serão desenhadas.
        figura, eixo = plt.subplots(figsize=(9, 5))

        # 'sns.barplot' desenha as barras horizontais ou verticais no Seaborn
        # representando a agilidade logística.
        # 'data=desempenho_prazos' fornece a tabela consolidada de tempos médios.
        # 'x="transportadora"' posiciona os nomes das empresas no eixo horizontal.
        # 'y="dias_transito_real"' projeta a altura das barras correspondente à média de
        # dias de viagem.
        # 'color="#17becf"' aplica uma tonalidade azul turquesa industrial para
        # representar fluxos de transporte.
        # 'ax=eixo' manda o Seaborn desenhar dentro da moldura configurada no
        # matplotlib.
        sns.barplot(
            data=desempenho_prazos,
            x="transportadora",
            y="dias_transito_real",
            color="#17becf",
            ax=eixo,
        )

        # 'eixo.set_title' define o título no topo da imagem com tamanho 13 e
        # espaçamento de 12 pontos.
        eixo.set_title(
            "Tempo Médio Real de Trânsito por Transportadora (Dias Corridos)",
            fontsize=13,
            pad=12,
        )

        # 'eixo.set_xlabel' escreve o rótulo descritivo no eixo horizontal X.
        eixo.set_xlabel("Empresa Transportadora Contratada", fontsize=10)

        # 'eixo.set_ylabel' escreve o rótulo do eixo vertical Y em contagem de dias
        # médios de transporte.
        eixo.set_ylabel("Média de Dias em Trânsito", fontsize=10)

        # 'plt.xticks(rotation=30, ha="right")' inclina levemente os textos para evitar
        # corte de palavras compridas.
        plt.xticks(rotation=30, ha="right")

        # 'plt.tight_layout()' faz o ajuste dinâmico automático de margens para não
        # cortar legendas da imagem.
        plt.tight_layout()

        # 'figura.savefig' grava o arquivo físico de imagem no disco rígido em resolução
        # industrial de 300 DPI.
        figura.savefig(caminho_figura, dpi=300)

        # 'plt.close(figura)' limpa e destrói o objeto gráfico da memória RAM para
        # prevenir vazamentos de memória.
        plt.close(figura)

        # 'logging.info' confirma no terminal que o gráfico foi renderizado e persistido
        # com sucesso.
        logging.info(
            "Logística — Gráfico de tempo de trânsito salvo em: %s",
            caminho_figura.name,
        )

        # 'return' devolve o caminho físico do arquivo gravado.
        return caminho_figura

    # 'def' implementa a assinatura obrigatória herdada da classe base abstrata
    # 'BaseDepartamento'.
    # Este método orquestra a execução sequencial de todas as rotinas periciais de
    # logística e expedição.
    def executar_diagnostico_completo(self) -> dict[str, Any]:
        """Coordena o cálculo do custo de frete, apuração do OTIF e persistência dos
        gráficos logísticos.

        Returns:
            Dict[str, Any]: Laudo executivo completo do departamento de logística.
        """
        # Emite log anunciando o início oficial da perícia logística da Fase 2.8.
        logging.info(
            "=== INICIANDO PERÍCIA DO DEPARTAMENTO DE LOGÍSTICA (FASE 2.8) ==="
        )

        # Invoca o método interno que carrega os despachos e fretes na memória RAM uma
        # única vez.
        df_logistica = self.carregar_dados_logistica()

        # Executa o cálculo da relação Custo de Frete sobre Vendas.
        laudo_frete = self.calcular_custo_frete_sobre_vendas(df_logistica)

        # Executa a apuração do índice OTIF consolidado (On-Time In-Full) e seus
        # componentes de serviço.
        laudo_otif = self.calcular_indice_otif(df_logistica)

        # Renderiza e salva o gráfico de tempos médios de trânsito por transportadora no
        # disco.
        caminho_grafico = self.gerar_grafico_tempo_transito_transportadora(df_logistica)

        # 'laudo_logistica' é o dicionário estruturado que consolida o laudo de
        # transportes da PME.
        laudo_logistica = {
            # Incorpora a apuração financeira do frete sobre a receita bruta faturada.
            "analise_frete": laudo_frete,
            # Incorpora o nível de serviço OTIF e as taxas de pontualidade e integridade
            # da carga.
            "nivel_servico_otif": laudo_otif,
            # Registra o caminho do arquivo de imagem exportado para visualização em
            # relatórios ou BI.
            "grafico_tempo_transito": str(caminho_grafico),
        }

        # Emite log confirmando o encerramento da auditoria logística.
        logging.info("=== DEPARTAMENTO DE LOGÍSTICA CONCLUÍDO COM SUCESSO ===")

        # 'return' devolve o laudo consolidado de logística para o orquestrador geral do
        # projeto.
        return laudo_logistica
