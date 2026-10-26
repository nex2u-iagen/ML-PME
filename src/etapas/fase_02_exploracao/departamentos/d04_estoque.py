"""Módulo de Diagnóstico Exploratório do Departamento de Estoque (Fase 2.4).

Implementa a classificação da Curva ABC por valor imobilizado, cálculo
de dias de cobertura de estoque, giro de mercadorias e alerta de ruptura
para Pequenas e Médias Empresas (PMEs).
"""

# 'import' é a palavra-chave reservada do Python utilizada para carregar bibliotecas
# externas ou nativas.
# Carregamos o módulo 'logging' da biblioteca padrão para registrar mensagens com nível
# de severidade no terminal.
import logging

# 'from' indica a biblioteca ou módulo de onde extrairemos uma ferramenta específica.
# 'pathlib' é o módulo padrão do Python para manipulação orientada a objetos de caminhos
# no sistema de arquivos.
# 'import' traz a classe 'Path' para representar diretórios e caminhos compatíveis com
# Windows, Linux e Mac.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão, voltado para anotações de
# tipagem estática (Type Hints).
# 'import' carrega 'Any' (que aceita qualquer tipo de objeto) e 'Dict' (que documenta
# dicionários de chave e valor).
from typing import Any

# 'import' traz o submódulo 'pyplot' da biblioteca 'matplotlib', responsável pelo
# controle de telas e figuras gráficas.
# 'as' cria o apelido reduzido 'plt', convenção universal na Ciência de Dados para
# economizar digitação.
import matplotlib.pyplot as plt

# 'import' traz a biblioteca externa 'pandas', a principal ferramenta para criação e
# manipulação de tabelas em memória.
# 'as' define o apelido oficial 'pd' para facilitar chamadas de métodos como DataFrames
# e Series.
import pandas as pd

# 'import' traz a biblioteca 'seaborn', especializada em renderizar gráficos
# estatísticos com acabamento visual corporativo.
# 'as' define o apelido clássico 'sns'.
import seaborn as sns

# 'from' navega até o arquivo 'base_departamento.py' localizado no diretório pai de
# exploração.
# 'import' traz a classe abstrata 'BaseDepartamento' para herdarmos a infraestrutura
# pronta do núcleo por herança OOP.
from src.etapas.fase_02_exploracao.base_departamento import BaseDepartamento


# 'class' é a palavra-chave que declara um novo modelo estrutural orientado a objetos.
# 'AnalisadorEstoque' é o nome da nossa classe especializada em auditoria de materiais,
# em estilo PascalCase.
# '(BaseDepartamento)' entre parênteses estabelece herança formal: esta classe herda
# recursos da classe base mãe.
class AnalisadorEstoque(BaseDepartamento):
    """Classe responsável pelo diagnóstico de armazenagem, giro e curva ABC de
    produtos.
    """

    # 'def' define o método construtor especial '__init__', acionado no momento da
    # criação do objeto em memória RAM.
    # 'self' referencia a própria instância acessando seus atributos internos.
    # 'pasta_dados_brutos: Path' é um parâmetro obrigatório exigindo o caminho onde
    # estão as tabelas CSV do ERP.
    # 'pasta_relatorios: Path' é o caminho raiz onde os laudos e imagens deste
    # departamento serão gravados.
    # '-> None' atesta formalmente que o método inicializador não retorna nenhum dado.
    def __init__(self, pasta_dados_brutos: Path, pasta_relatorios: Path) -> None:
        """Inicializa o departamento de estoque registrando a subpasta dedicada.

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas brutas do ERP.
            pasta_relatorios (Path): Diretório base de saída dos laudos analíticos.
        """
        # 'super().__init__' aciona o construtor da classe mãe BaseDepartamento para
        # registrar pastas e ferramentas.
        # Passamos 'pasta_dados_brutos' e 'pasta_relatorios' e nomeamos o departamento
        # formalmente como 'estoque'.
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="estoque",
        )

    # 'def' define o método responsável por carregar a posição física e financeira do
    # estoque do ERP.
    # '-> pd.DataFrame' documenta que a função devolverá uma matriz tabular
    # bidimensional do pandas.
    def carregar_dados_estoque(self) -> pd.DataFrame:
        """Carrega a tabela de saldos de estoque e custos médios unitários do ERP.

        Returns:
            pd.DataFrame: Tabela contendo SKUs, quantidades em estoque, custo e consumo
            médio.
        """
        # O operador '/' une os caminhos de forma nativa via Pathlib, gerando o endereço
        # exato do arquivo CSV.
        caminho_estoque = self.pasta_dados_brutos / "erp_saldos_estoque.csv"

        # '.is_file()' testa fisicamente se o arquivo existe no disco rígido.
        # 'if not' atua defensivamente: se o arquivo não existir, geramos uma base
        # didática representativa da PME.
        if not caminho_estoque.is_file():
            # 'logging.info' emite um aviso no terminal informando que a base de
            # contingência foi iniciada.
            logging.info(
                "Estoque — Base não localizada. Gerando posições de inventário"
                "sintéticas..."
            )

            # 'dados_simulados' é um dicionário Python ('{}') contendo listas
            # estruturadas com produtos industriais.
            dados_simulados = {
                # Lista de códigos numéricos de identificação única de cada produto
                # (SKUs).
                "id_produto": [
                    201,
                    202,
                    203,
                    204,
                    205,
                    206,
                    207,
                    208,
                ],
                # Lista com as descrições textuais nominais dos materiais cadastrados no
                # almoxarifado.
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
                # Quantidade física de unidades atualmente armazenadas no depósito
                # físico da PME.
                "quantidade_saldo": [
                    12,
                    48,
                    25,
                    1200,
                    350,
                    40,
                    5,
                    800,
                ],
                # Custo contábil médio de aquisição ou fabricação unitária em reais
                # (R$).
                "custo_unitario": [
                    850.0,
                    180.0,
                    120.0,
                    0.45,
                    15.0,
                    45.0,
                    1400.0,
                    6.50,
                ],
                # Demanda ou consumo médio mensal de cada item nas operações da PME.
                "consumo_mensal_medio": [
                    4,
                    16,
                    8,
                    300,
                    90,
                    15,
                    2,
                    220,
                ],
            }

            # 'pd.DataFrame' converte a estrutura de dicionário em uma matriz tabular do
            # pandas em memória RAM.
            df_estoque = pd.DataFrame(dados_simulados)

            # Multiplica a quantidade em saldo pelo custo unitário para calcular o
            # capital imobilizado por SKU.
            # '.round(2)' arredonda o resultado financeiro para duas casas decimais
            # (centavos em R$).
            df_estoque["valor_imobilizado"] = (
                df_estoque["quantidade_saldo"] * df_estoque["custo_unitario"]
            ).round(2)

            # '.to_csv' grava a tabela gerada no disco rígido para permitir auditorias
            # posteriores.
            # 'index=False' impede que o pandas crie uma coluna extra de números
            # desnecessária no arquivo físico.
            df_estoque.to_csv(caminho_estoque, index=False)
        else:
            # Caso o arquivo já exista fisicamente no disco rígido, usamos o leitor
            # herdado da classe base.
            df_estoque = self.leitor.carregar_tabela(caminho_estoque)

        # 'logging.info' imprime no console o total de produtos monitorados no
        # almoxarifado.
        logging.info(
            "Estoque — Base consolidada com %d SKUs monitorados.", len(df_estoque)
        )

        # 'return' devolve a matriz tabular pronta para os cálculos estatísticos e de
        # negócio.
        return df_estoque

    # KPI 32: Cobertura de Estoque em Dias (Dias de Autonomia Operacional sem Novas
    # Compras).
    # 'def' define a função especializada em calcular a autonomia do estoque.
    def calcular_dias_cobertura(self, dados: pd.DataFrame) -> pd.DataFrame:
        """Calcula quantos dias o estoque atual dura considerando o consumo médio
        mensal.

        Args:
            dados (pd.DataFrame): Tabela contendo saldos e consumo médio.

        Returns:
            pd.DataFrame: Tabela enriquecida com a métrica 'dias_cobertura'.
        """
        # '.copy()' cria uma cópia profunda da tabela para evitar avisos de escrita
        # acidental em memória (SettingWithCopyWarning).
        dados_processados = dados.copy()

        # Divide o consumo médio mensal por 30.0 dias para encontrar o consumo diário
        # estimado.
        consumo_diario = dados_processados["consumo_mensal_medio"] / 30.0

        # Divide o saldo físico pelo consumo diário para encontrar quantos dias o
        # estoque suporta a operação.
        # '.round(1)' arredonda o número de dias com uma casa decimal (ex.: 45.2 dias).
        dados_processados["dias_cobertura"] = (
            dados_processados["quantidade_saldo"] / consumo_diario
        ).round(1)

        # 'logging.info' registra a conclusão do cálculo de dias de cobertura no log de
        # auditoria.
        logging.info("Estoque — Indicador de Dias de Cobertura calculado com sucesso.")

        # 'return' devolve a tabela atualizada com a nova coluna analítica.
        return dados_processados

    # KPI 34: Classificação da Curva ABC por Valor Financeiro Imobilizado (Princípio de
    # Pareto 80/15/5).
    # 'def' declara o método responsável pela segregação de materiais.
    def calcular_curva_abc(self, dados: pd.DataFrame) -> pd.DataFrame:
        """Classifica os produtos em classes A (80%), B (15%) e C (5%) segundo o capital
        preso.

        Args:
            dados (pd.DataFrame): Tabela de posições de estoque.

        Returns:
            pd.DataFrame: Tabela ordenada com a coluna 'classe_abc' devidamente
            calculada.
        """
        # '.sort_values()' ordena os produtos pelo valor imobilizado de forma
        # decrescente (do maior para o menor).
        # 'ascending=False' garante que os itens que prendem mais dinheiro fiquem no
        # topo da tabela.
        # '.copy()' isola a nova ordenação em uma estrutura independente.
        df_ordenado = dados.sort_values(by="valor_imobilizado", ascending=False).copy()

        # '.cumsum()' (Cumulative Sum) calcula a soma acumulada progressiva do capital
        # imobilizado linha a linha.
        df_ordenado["valor_acumulado"] = df_ordenado["valor_imobilizado"].cumsum()

        # '.sum()' calcula o valor financeiro total de todo o armazém da empresa;
        # 'float()' garante precisão numérica.
        total_estoque = float(df_ordenado["valor_imobilizado"].sum())

        # Calcula a porcentagem acumulada do estoque dividindo a soma progressiva pelo
        # valor total geral.
        # Multiplicamos por 100 para transformar em escala percentual (de 0.0% a
        # 100.0%).
        df_ordenado["percentual_acumulado"] = (
            df_ordenado["valor_acumulado"] / total_estoque
        ) * 100

        # 'def' define uma função auxiliar interna para classificar o percentual nas
        # três faixas de Pareto.
        def classificar_faixa(percentual: float) -> str:
            # 'if' avalia se o produto está dentro dos primeiros 80% do capital
            # acumulado da empresa.
            if percentual <= 80.0:
                # Retorna a categoria 'A' (os itens mais valiosos e críticos do
                # estoque).
                return "A"
            # 'elif' avalia se o produto compõe os 15% intermediários (entre 80% e 95%
            # do capital).
            elif percentual <= 95.0:
                # Retorna a categoria 'B' (itens de importância intermediária).
                return "B"
            # 'return' final classifica o restante dos produtos nos últimos 5% do
            # capital (muito volume, pouco dinheiro).
            return "C"

        # '.apply(classificar_faixa)' executa a função lógica linha por linha sobre a
        # coluna de percentual acumulado.
        df_ordenado["classe_abc"] = df_ordenado["percentual_acumulado"].apply(
            classificar_faixa
        )

        # 'logging.info' emite um resumo no console contabilizando quantos produtos
        # caíram em cada classe.
        logging.info(
            "Estoque — Curva ABC concluída. Itens Classe A: %d | Classe B: %d | Classe"
            "C: %d.",
            (df_ordenado["classe_abc"] == "A").sum(),
            (df_ordenado["classe_abc"] == "B").sum(),
            (df_ordenado["classe_abc"] == "C").sum(),
        )

        # 'return' devolve a tabela classificada com as faixas ABC.
        return df_ordenado

    # 'def' define o método especialista em renderizar o gráfico visual da Curva ABC.
    # 'caminho_figura' será devolvido como um objeto Path indicando o arquivo PNG
    # gravado no disco.
    def gerar_grafico_curva_abc(self, dados: pd.DataFrame) -> Path:
        """Renderiza o gráfico de barras da Curva ABC colorido pelas classes de
        criticidade.

        Args:
            dados (pd.DataFrame): Tabela classificada com as classes A, B e C.

        Returns:
            Path: Endereço do arquivo de imagem salvo em alta definição (300 DPI).
        """
        # 'self.pasta_saida' aponta para a pasta 'relatorios/figuras/estoque/', criada
        # pelo construtor base.
        caminho_figura = self.pasta_saida / "curva_abc_valor_imobilizado.png"

        # 'plt.subplots()' cria a moldura da figura gráfica com 10 polegadas de largura
        # por 5 de altura.
        # 'figura' representa a tela global; 'eixo' é a área interna onde as barras
        # serão desenhadas.
        figura, eixo = plt.subplots(figsize=(10, 5))

        # 'paleta_cores' é um dicionário que mapeia cores semânticas: Vermelho para
        # Classe A, Laranja para B e Azul para C.
        paleta_cores = {
            "A": "#d62728",
            "B": "#ff7f0e",
            "C": "#1f77b4",
        }

        # 'sns.barplot' desenha as barras verticais no Seaborn representando o valor
        # imobilizado por SKU.
        # 'data=dados' fornece a tabela de estoque ordenada.
        # 'x="descricao_produto"' define os nomes dos materiais no eixo horizontal.
        # 'y="valor_imobilizado"' projeta a altura das barras correspondente ao valor em
        # reais no eixo vertical.
        # 'hue="classe_abc"' colore cada barra de acordo com a sua classe de criticidade
        # de Pareto.
        # 'palette=paleta_cores' aplica as cores semânticas personalizadas que definimos
        # no dicionário.
        # 'dodge=False' mantém as barras alinhadas verticalmente sem deslocamentos
        # laterais indesejados.
        # 'ax=eixo' manda o Seaborn desenhar dentro da moldura que configuramos no
        # matplotlib.
        sns.barplot(
            data=dados,
            x="descricao_produto",
            y="valor_imobilizado",
            hue="classe_abc",
            palette=paleta_cores,
            dodge=False,
            ax=eixo,
        )

        # 'eixo.set_title' define o título no topo da imagem com tamanho 13 e
        # espaçamento de 12 pontos.
        eixo.set_title(
            "Curva ABC de Estoque por Valor Financeiro Imobilizado (R$)",
            fontsize=13,
            pad=12,
        )

        # 'eixo.set_xlabel' escreve o rótulo do eixo horizontal X.
        eixo.set_xlabel("Produto Cadastrado (SKU)", fontsize=10)

        # 'eixo.set_ylabel' escreve o rótulo do eixo vertical Y em moeda corrente (R$).
        eixo.set_ylabel("Capital Imobilizado (R$)", fontsize=10)

        # 'plt.xticks(rotation=45, ha="right")' inclina os nomes dos produtos em 45
        # graus alinhados à direita.
        # Esse comando impede a sobreposição de textos longos no rodapé da visualização.
        plt.xticks(rotation=45, ha="right")

        # 'plt.tight_layout()' ajusta dinamicamente as margens da figura para que
        # nenhuma legenda seja cortada.
        plt.tight_layout()

        # 'figura.savefig' grava fisicamente o arquivo de imagem no disco em resolução
        # industrial de 300 DPI.
        figura.savefig(caminho_figura, dpi=300)

        # 'plt.close(figura)' limpa e destrói o objeto gráfico da memória RAM para
        # prevenir vazamentos de memória (Memory Leak).
        plt.close(figura)

        # 'logging.info' confirma no terminal que o gráfico foi salvo com sucesso.
        logging.info(
            "Estoque — Gráfico da Curva ABC exportado para: %s", caminho_figura.name
        )

        # 'return' devolve o caminho do arquivo físico gerado.
        return caminho_figura

    # 'def' implementa a assinatura obrigatória herdada da classe base abstrata
    # 'BaseDepartamento'.
    # Este método orquestra a execução sequencial de todos os indicadores do
    # departamento de estoque.
    def executar_diagnostico_completo(self) -> dict[str, Any]:
        """Coordena a classificação ABC, cálculo de cobertura e gráficos de estoque.

        Returns:
            Dict[str, Any]: Laudo executivo do departamento de estoque.
        """
        # Emite log anunciando o início oficial da auditoria de estoque da Fase 2.4.
        logging.info("=== INICIANDO PERÍCIA DO DEPARTAMENTO DE ESTOQUE (FASE 2.4) ===")

        # Carrega a base de dados de estoque na memória RAM.
        df_bruto = self.carregar_dados_estoque()

        # Executa o cálculo de dias de cobertura e autonomia de matérias-primas.
        df_cobertura = self.calcular_dias_cobertura(df_bruto)

        # Aplica a rotulagem matemática da Curva ABC com base no capital imobilizado.
        df_abc = self.calcular_curva_abc(df_cobertura)

        # Renderiza e salva o gráfico da Curva ABC no disco.
        caminho_grafico = self.gerar_grafico_curva_abc(df_abc)

        # 'float(df_abc["valor_imobilizado"].sum())' soma todo o dinheiro preso em
        # estoque na PME.
        # 'round(..., 2)' arredonda o valor financeiro para centavos.
        total_capital = round(float(df_abc["valor_imobilizado"].sum()), 2)

        # 'int(len(df_abc))' calcula a contagem total inteira de SKUs monitorados.
        total_skus = int(len(df_abc))

        # 'float(df_abc["dias_cobertura"].mean())' calcula a média geral de dias de
        # autonomia da empresa.
        # 'round(..., 1)' arredonda a média com uma casa decimal.
        media_cobertura = round(float(df_abc["dias_cobertura"].mean()), 1)

        # 'laudo_estoque' é o dicionário estruturado com as métricas vitais para a
        # tomada de decisão da diretoria.
        laudo_estoque = {
            "capital_total_imobilizado_reais": total_capital,
            "total_skus_cadastrados": total_skus,
            "media_dias_cobertura_geral": media_cobertura,
            "grafico_curva_abc": str(caminho_grafico),
        }

        # Emite log marcando o término bem-sucedido da perícia de estoque.
        logging.info("=== DEPARTAMENTO DE ESTOQUE CONCLUÍDO COM SUCESSO ===")

        # 'return' devolve o laudo consolidado de estoque para o orquestrador geral do
        # projeto.
        return laudo_estoque
