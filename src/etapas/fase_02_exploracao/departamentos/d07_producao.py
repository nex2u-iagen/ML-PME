"""Módulo de Diagnóstico Exploratório do Departamento de Produção (Fase 2.7).

Implementa a apuração da Eficiência Global dos Equipamentos (OEE),
a Taxa de Refugo e Desperdício (Scrap Rate), o índice de cumprimento
do plano fabril e a visualização do volume refugado por SKU para PMEs.
"""

# 'import' é a palavra-chave reservada do Python para importar módulos e bibliotecas.
# Importa o módulo 'logging' nativo para emitir registos auditáveis no terminal com data
# e hora.
import logging

# 'from' indica a biblioteca de origem; 'pathlib' manipula caminhos e pastas de forma
# orientada a objetos.
# 'import' traz a classe 'Path' para gerir endereços físicos no Windows, Linux ou macOS.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão, voltado para anotações de
# tipagem estática (Type Hints).
# 'import' carrega 'Any' (aceita qualquer tipo de valor) e 'Dict' (estrutura de
# dicionário com chaves e valores).
from typing import Any

# 'import' traz o submódulo 'pyplot' da biblioteca 'matplotlib' para controle de eixos e
# telas gráficas.
# 'as' define o atalho universal 'plt' para simplificar as chamadas de funções no
# código.
import matplotlib.pyplot as plt

# 'import' traz a biblioteca externa 'pandas', padrão da indústria para manipulação
# tabular de dados.
# 'as' define o atalho clássico 'pd' para encurtar a manipulação de DataFrames e Series.
import pandas as pd

# 'import' traz a biblioteca externa 'seaborn', especializada em gráficos estatísticos
# corporativos refinados.
# 'as' define o atalho 'sns' para estilização visual.
import seaborn as sns

# 'from' navega até o arquivo 'base_departamento.py' localizado na pasta pai de
# exploração.
# 'import' traz a classe abstrata 'BaseDepartamento' para herdarmos o leitor e
# ferramentas do núcleo compartilhado.
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento


# 'class' é a palavra-chave que declara um novo molde estrutural orientado a objetos.
# 'AnalisadorProducao' é o nome da nossa classe especializada em auditoria fabril,
# escrita em estilo PascalCase.
# '(BaseDepartamento)' entre parênteses define herança: esta classe herda os recursos e
# infraestrutura da classe base mãe.
class AnalisadorProducao(BaseDepartamento):
    """Classe responsável pelo diagnóstico de eficiência fabril, OEE e refugo
    industrial do ERP.
    """

    # 'def' define o método especial construtor '__init__', acionado ao criar uma
    # instância da classe em memória RAM.
    # 'self' referencia a própria instância que está sendo construída.
    # 'pasta_dados_brutos: Path' exige receber o caminho onde estão as tabelas CSV do
    # ERP.
    # 'pasta_relatorios: Path' exige o caminho raiz onde os relatórios e imagens deste
    # departamento serão gravados.
    # '-> None' atesta formalmente que o construtor inicializador não retorna dados.
    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento de produção registrando a subpasta dedicada.

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas brutas do ERP.
            pasta_relatorios (Path): Diretório base de saída dos laudos analíticos.
        """
        # 'super().__init__' aciona o construtor da classe base (mãe) BaseDepartamento.
        # Passamos as pastas e registramos o nome canônico 'producao' para criar a
        # subpasta de figuras.
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="producao",
        )

    # 'def' define o método responsável por carregar apontamentos de produção e ordens
    # fabris do disco.
    # '-> pd.DataFrame' documenta formalmente que a função devolverá uma tabela
    # bidimensional do pandas.
    def carregar_dados_producao(self) -> pd.DataFrame:
        """Carrega ou simula a tabela de ordens de produção (OPs) e apontamentos de
        máquinas.

        Returns:
            pd.DataFrame: Tabela contendo OPs, produtos, quantidades planejadas,
            produzidas e refugadas.
        """
        # O operador '/' une os caminhos de diretório via Pathlib, gerando o endereço
        # exato do arquivo CSV fabril.
        caminho_producao = self.pasta_dados_brutos / "erp_ordens_producao.csv"

        # '.is_file()' verifica fisicamente no disco rígido se o arquivo existe.
        # 'if not' faz a checagem defensiva: se a base não existir, geramos dados
        # didáticos representativos da fábrica.
        if not caminho_producao.is_file():
            # 'logging.info' emite um aviso no terminal informando que a base de
            # contingência fabril foi iniciada.
            logging.info(
                "Produção — Base não localizada. Gerando apontamentos de produção"
                "sintéticos..."
            )

            # 'dados_simulados' é um dicionário Python ('{}') com listas simulando
            # ordens de produção industriais.
            dados_simulados = {
                # Lista com números de identificação das Ordens de Produção (OPs)
                # abertas no chão de fábrica.
                "id_ordem_producao": [
                    801,
                    802,
                    803,
                    804,
                    805,
                    806,
                    807,
                    808,
                ],
                # Descrição nominal dos produtos que passaram pelas linhas de corte,
                # montagem e acabamento.
                "descricao_produto": [
                    "Mesa Jantar Carvalho",
                    "Cadeira Estofada Luxo",
                    "Armário 2 Portas",
                    "Mesa Jantar Carvalho",
                    "Cadeira Estofada Luxo",
                    "Armário 2 Portas",
                    "Painel Home Theater",
                    "Aparador Sala Estar",
                ],
                # Meta de volume de peças estipulada pelo Planejamento e Controle da
                # Produção (PCP).
                "quantidade_planejada": [
                    50,
                    200,
                    30,
                    60,
                    250,
                    40,
                    80,
                    45,
                ],
                # Volume físico real de peças que foram efetivamente fabricadas pelos
                # operadores no turno.
                "quantidade_produzida": [
                    48,
                    195,
                    28,
                    55,
                    230,
                    38,
                    74,
                    42,
                ],
                # Quantidade de peças que saíram defeituosas (trincadas, riscadas) e
                # viraram sucata/descarte.
                "quantidade_refugada": [
                    3,
                    12,
                    2,
                    5,
                    18,
                    1,
                    6,
                    2,
                ],
                # Total de horas de expediente em que as máquinas e funcionários estavam
                # escalados para produzir.
                "horas_disponiveis": [
                    40.0,
                    40.0,
                    40.0,
                    44.0,
                    44.0,
                    44.0,
                    40.0,
                    36.0,
                ],
                # Tempo total em horas que as máquinas ficaram paradas por quebra
                # mecânica, falta de energia ou setup.
                "horas_paradas": [
                    4.5,
                    2.0,
                    6.0,
                    3.0,
                    5.5,
                    1.5,
                    4.0,
                    2.0,
                ],
            }

            # 'pd.DataFrame' converte a estrutura de dicionário em uma matriz tabular do
            # pandas em memória RAM.
            df_producao = pd.DataFrame(dados_simulados)

            # '.to_csv' grava a tabela gerada no disco rígido para permitir auditorias
            # posteriores da fábrica.
            # 'index=False' impede que o pandas crie uma coluna extra de números
            # desnecessária no arquivo físico.
            df_producao.to_csv(caminho_producao, index=False)
        else:
            # Caso o arquivo já exista fisicamente no disco rígido, usamos o leitor
            # herdado da classe base.
            df_producao = self.leitor.carregar_tabela(caminho_producao)

        # 'logging.info' imprime no console o total de ordens fabris consolidadas para o
        # laudo pericial.
        logging.info(
            "Produção — Base consolidada com %d ordens fabris auditadas.",
            len(df_producao),
        )

        # 'return' devolve a matriz tabular pronta para os cálculos de eficiência
        # industrial.
        return df_producao

    # KPI 62: Taxa de Refugo e Desperdício de Materiais (Scrap Rate em Percentual).
    # 'def' define a função especializada em medir o volume de peças jogadas no lixo
    # fabril.
    def calcular_taxa_refugo(self, dados: pd.DataFrame) -> dict[str, float]:
        """Calcula o volume total produzido, total de peças refugadas e o índice
        percentual de refugo.

        Taxa de Refugo (%) = (Total Refugado / Total Produzido) * 100.

        Args:
            dados (pd.DataFrame): Tabela de apontamentos de produção com peças boas e
            refugadas.

        Returns:
            Dict[str, float]: Dicionário contendo volume produzido, volume descartado e
            índice percentual de refugo.
        """
        # '.sum()' calcula a soma de todas as peças físicas produzidas nas linhas de
        # manufatura.
        total_produzido = float(dados["quantidade_produzida"].sum())

        # '.sum()' calcula o total de peças descartadas por falhas de qualidade ou erros
        # de operação.
        total_refugo = float(dados["quantidade_refugada"].sum())

        # '.sum()' calcula o total planejado pelo PCP para avaliar se a fábrica atingiu
        # a meta volumétrica.
        total_planejado = float(dados["quantidade_planejada"].sum())

        # Calcula a taxa percentual de refugo dividindo as peças descartadas pelo total
        # fabricado.
        # O operador ternário 'if total_produzido > 0 else 0.0' previne divisão por zero
        # em bases vazias.
        taxa_refugo_percentual = (
            (total_refugo / total_produzido) * 100 if total_produzido > 0 else 0.0
        )

        # Calcula o percentual de cumprimento da meta fabril (Total Produzido / Total
        # Planejado).
        cumprimento_meta_percentual = (
            (total_produzido / total_planejado) * 100 if total_planejado > 0 else 0.0
        )

        # 'laudo_refugo' organiza os indicadores industriais para relatórios gerenciais
        # e dashboards.
        laudo_refugo = {
            # 'round(..., 1)' arredonda o total planejado em unidades inteiras.
            "total_planejado_unidades": round(total_planejado, 1),
            # 'round(..., 1)' arredonda o total de peças produzidas.
            "total_produzido_unidades": round(total_produzido, 1),
            # 'round(..., 1)' arredonda o total de peças descartadas como sucata.
            "total_refugo_unidades": round(total_refugo, 1),
            # 'round(..., 2)' arredonda a taxa percentual de refugo da fábrica (%).
            "taxa_refugo_percentual": round(taxa_refugo_percentual, 2),
            # 'round(..., 2)' arredonda a taxa de cumprimento do plano do PCP (%).
            "cumprimento_meta_percentual": round(cumprimento_meta_percentual, 2),
        }

        # 'logging.info' imprime a taxa de refugo no terminal para auditoria da gerência
        # industrial.
        logging.info(
            "Produção — Taxa de Refugo: %.2f%% (%d peças descartadas no lixo).",
            laudo_refugo["taxa_refugo_percentual"],
            laudo_refugo["total_refugo_unidades"],
        )

        # 'return' devolve o dicionário estruturado com as métricas de refugo.
        return laudo_refugo

    # KPI 61: Eficiência Global dos Equipamentos (OEE Estimado em Percentual).
    # 'def' define o método que calcula o OEE composto pelos três fatores vitais:
    # Disponibilidade, Performance e Qualidade.
    def calcular_oee_estimado(self, dados: pd.DataFrame) -> dict[str, float]:
        """Calcula o índice OEE agregando Disponibilidade, Performance Operacional e
        Índice de Qualidade.

        Disponibilidade (%) = ((Horas Disponíveis - Horas Paradas) / Horas Disponíveis)
        * 100.
        Performance (%) = (Quantidade Produzida / Quantidade Planejada) * 100.
        Qualidade (%) = ((Quantidade Produzida - Quantidade Refugada) / Quantidade
        Produzida) * 100.
        OEE (%) = (Disponibilidade * Performance * Qualidade) / 10000.

        Args:
            dados (pd.DataFrame): Tabela de apontamentos com horas de máquina e
            quantidades.

        Returns:
            Dict[str, float]: Dicionário contendo os 3 fatores fundamentais e o índice
            OEE consolidado.
        """
        # '.sum()' calcula as horas totais que a fábrica esteve aberta com operadores
        # disponíveis para trabalhar.
        horas_disponiveis = float(dados["horas_disponiveis"].sum())

        # '.sum()' calcula o total de horas perdidas com manutenções corretivas, setups
        # e quebras mecânicas.
        horas_paradas = float(dados["horas_paradas"].sum())

        # Calcula as horas produtivas reais subtraindo as paradas do total disponível.
        horas_operando = horas_disponiveis - horas_paradas

        # 1. Fator Disponibilidade: mede a fração do tempo escalado em que as máquinas
        # estavam girando.
        fator_disponibilidade = (
            (horas_operando / horas_disponiveis) * 100 if horas_disponiveis > 0 else 0.0
        )

        # 2. Fator Performance: mede se a produção atingiu a velocidade nominal esperada
        # pelo PCP.
        total_planejado = float(dados["quantidade_planejada"].sum())
        total_produzido = float(dados["quantidade_produzida"].sum())
        fator_performance = (
            (total_produzido / total_planejado) * 100 if total_planejado > 0 else 0.0
        )

        # 3. Fator Qualidade: mede a proporção de peças perfeitas que saíram de primeira
        # sem defeitos.
        total_refugo = float(dados["quantidade_refugada"].sum())
        total_boas = total_produzido - total_refugo
        fator_qualidade = (
            (total_boas / total_produzido) * 100 if total_produzido > 0 else 0.0
        )

        # OEE Consolidado: produto dos 3 fatores normalizado em base percentual (divide
        # por 10.000 para manter escala 0-100%).
        oee_consolidado = (
            fator_disponibilidade * fator_performance * fator_qualidade
        ) / 10000.0

        # 'laudo_oee' reúne os indicadores de eficiência global industrial.
        laudo_oee = {
            # 'round(..., 2)' arredonda o fator disponibilidade percentual.
            "fator_disponibilidade_percentual": round(fator_disponibilidade, 2),
            # 'round(..., 2)' arredonda o fator performance percentual.
            "fator_performance_percentual": round(fator_performance, 2),
            # 'round(..., 2)' arredonda o fator qualidade percentual.
            "fator_qualidade_percentual": round(fator_qualidade, 2),
            # 'round(..., 2)' arredonda o OEE consolidado final em percentual.
            "oee_consolidado_percentual": round(oee_consolidado, 2),
        }

        # 'logging.info' imprime o OEE no console com os componentes para auditoria
        # operacional.
        logging.info(
            "Produção — OEE Consolidado: %.2f%% (Disp: %.1f%% | Perf: %.1f%% | Qual:"
            "%.1f%%).",
            laudo_oee["oee_consolidado_percentual"],
            laudo_oee["fator_disponibilidade_percentual"],
            laudo_oee["fator_performance_percentual"],
            laudo_oee["fator_qualidade_percentual"],
        )

        # 'return' devolve o laudo de eficiência global.
        return laudo_oee

    # 'def' define o método especialista em renderizar o gráfico visual de refugo por
    # item fabricado.
    # 'caminho_figura' será devolvido como um objeto Path com o endereço da imagem
    # exportada no disco.
    def gerar_grafico_refugo_produtos(self, dados: pd.DataFrame) -> Path:
        """Renderiza um gráfico de barras destacando as perdas por refugo em cada
        produto.

        Args:
            dados (pd.DataFrame): Tabela contendo nomes de produtos e quantidades
            refugadas.

        Returns:
            Path: Endereço do arquivo de imagem salvo em alta definição (300 DPI).
        """
        # '.groupby("descricao_produto")' agrupa as ordens fabris pelo nome nominal do
        # produto.
        # '["quantidade_refugada"].sum()' soma todas as peças descartadas daquele item
        # no período.
        # '.reset_index()' converte o agrupamento em uma tabela com colunas
        # convencionais do pandas.
        refugo_produto = (
            dados.groupby("descricao_produto")["quantidade_refugada"]
            .sum()
            .reset_index()
        )

        # '.sort_values()' ordena os produtos pelo volume de refugo de forma decrescente
        # (do maior desperdício para o menor).
        # 'ascending=False' posiciona os itens com maior custo de perda no topo da
        # visualização.
        refugo_produto = refugo_produto.sort_values(
            by="quantidade_refugada", ascending=False
        )

        # 'self.pasta_saida' aponta para a pasta 'relatorios/figuras/producao/', criada
        # pelo construtor base.
        caminho_figura = self.pasta_saida / "desperdicio_refugo_produtos.png"

        # 'plt.subplots()' inicializa uma moldura gráfica com 9 polegadas de largura por
        # 5 de altura.
        # 'figura' representa a tela global; 'eixo' é a área interna onde as barras
        # serão desenhadas.
        figura, eixo = plt.subplots(figsize=(9, 5))

        # 'sns.barplot' desenha as barras verticais no Seaborn representando o volume de
        # descarte por SKU.
        # 'data=refugo_produto' fornece a tabela com os números consolidados.
        # 'x="descricao_produto"' define os nomes dos materiais no eixo horizontal.
        # 'y="quantidade_refugada"' projeta a altura das barras correspondente às
        # unidades perdidas no eixo vertical.
        # 'color="#d62728"' aplica a tonalidade vermelha destacada para indicar perdas e
        # desperdícios industriais.
        # 'ax=eixo' manda o Seaborn desenhar dentro da moldura configurada no
        # matplotlib.
        sns.barplot(
            data=refugo_produto,
            x="descricao_produto",
            y="quantidade_refugada",
            color="#d62728",
            ax=eixo,
        )

        # 'eixo.set_title' define o título no topo da imagem com tamanho 13 e
        # espaçamento de 12 pontos.
        eixo.set_title(
            "Volume de Refugo e Desperdício por Produto (Sucata Industrial)",
            fontsize=13,
            pad=12,
        )

        # 'eixo.set_xlabel' escreve o rótulo do eixo horizontal X em português.
        eixo.set_xlabel("Produto Manufaturado (SKU)", fontsize=10)

        # 'eixo.set_ylabel' escreve o rótulo do eixo vertical Y em contagem física de
        # unidades perdidas.
        eixo.set_ylabel("Quantidade Refugada (Unidades)", fontsize=10)

        # 'plt.xticks(rotation=45, ha="right")' inclina os nomes dos produtos em 45
        # graus para evitar corte de palavras.
        plt.xticks(rotation=45, ha="right")

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
        logging.info("Produção — Gráfico de refugo salvo em: %s", caminho_figura.name)

        # 'return' devolve o caminho físico do arquivo gravado.
        return caminho_figura

    # 'def' implementa a assinatura obrigatória herdada da classe base abstrata
    # 'BaseDepartamento'.
    # Este método orquestra a execução sequencial de todas as rotinas periciais da
    # produção fabril.
    def executar_diagnostico_completo(self) -> dict[str, Any]:
        """Coordena o cálculo do refugo, apuração do OEE e persistência dos gráficos
        fabris.

        Returns:
            Dict[str, Any]: Laudo executivo completo do departamento de produção.
        """
        # Emite log anunciando o início oficial da perícia de produção da Fase 2.7.
        logging.info("=== INICIANDO PERÍCIA DO DEPARTAMENTO DE PRODUÇÃO (FASE 2.7) ===")

        # Invoca o método interno que carrega as ordens fabris na memória RAM uma única
        # vez.
        df_producao = self.carregar_dados_producao()

        # Executa o cálculo da taxa de refugo e do cumprimento de metas do PCP.
        laudo_refugo = self.calcular_taxa_refugo(df_producao)

        # Executa a apuração do OEE estimado e seus três fatores componentes (Disp,
        # Perf, Qual).
        laudo_oee = self.calcular_oee_estimado(df_producao)

        # Renderiza e salva o gráfico de perdas por produto no disco.
        caminho_grafico = self.gerar_grafico_refugo_produtos(df_producao)

        # 'laudo_producao' é o dicionário estruturado que consolida o laudo operacional
        # da fábrica.
        laudo_producao = {
            # Incorpora os indicadores de peças produzidas, planejadas e taxa de refugo.
            "analise_refugo": laudo_refugo,
            # Incorpora os fatores de disponibilidade, performance, qualidade e o OEE
            # consolidado.
            "analise_oee": laudo_oee,
            # Registra o caminho da figura gerada para relatórios executivos ou
            # ferramentas de BI.
            "grafico_refugo_produtos": str(caminho_grafico),
        }

        # Emite log confirmando o encerramento da auditoria de produção.
        logging.info("=== DEPARTAMENTO DE PRODUÇÃO CONCLUÍDO COM SUCESSO ===")

        # 'return' devolve o laudo consolidado de produção para o orquestrador geral do
        # projeto.
        return laudo_producao
