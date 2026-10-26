"""Módulo de Diagnóstico Exploratório do Departamento Fiscal (Fase 2.6).

Implementa a apuração da Carga Tributária Efetiva sobre Vendas,
a distribuição de impostos por Estado (UF de destino), a identificação
de retenções tributárias na fonte e o diagnóstico de conformidade fiscal para PMEs.
"""

# 'import' é a palavra-chave reservada do Python para importar bibliotecas e módulos de
# código.
# Carrega o módulo 'logging' da biblioteca padrão para exibir mensagens com carimbo de
# auditoria no terminal.
import logging

# 'from' indica o módulo de origem; 'pathlib' gerencia arquivos e diretórios de forma
# orientada a objetos.
# 'import' traz a classe 'Path' para manipular endereços de pastas de forma compatível
# entre Windows, Linux e macOS.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão para documentar os tipos de dados
# esperados (Type Hints).
# 'import' carrega 'Any' (que aceita qualquer tipo de valor) e 'Dict' (dicionário
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
# 'AnalisadorFiscal' é o nome da nossa classe especializada em auditoria tributária,
# escrita em estilo PascalCase.
# '(BaseDepartamento)' entre parênteses estabelece herança: esta classe herda os
# recursos e o leitor da classe mãe.
class AnalisadorFiscal(BaseDepartamento):
    """Classe responsável pelo diagnóstico de impostos, alíquotas efetivas e
    conformidade fiscal do ERP.
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
        """Inicializa o departamento fiscal registrando a subpasta dedicada.

        Args:
            pasta_dados_brutos (Path): Diretório com as tabelas brutas do ERP.
            pasta_relatorios (Path): Diretório base de saída dos laudos analíticos.
        """
        # 'super().__init__' aciona formalmente o construtor da classe base mãe
        # BaseDepartamento.
        # Passamos as pastas e registramos o nome canônico 'fiscal' para criar
        # automaticamente a subpasta de figuras.
        super().__init__(
            pasta_dados_brutos=pasta_dados_brutos,
            pasta_relatorios=pasta_relatorios,
            nome_departamento="fiscal",
        )

    # 'def' define o método responsável por carregar notas fiscais e dados tributários
    # do disco rígido.
    # '-> pd.DataFrame' documenta que a função devolverá uma matriz tabular
    # bidimensional do pandas.
    def carregar_dados_fiscais(self) -> pd.DataFrame:
        """Carrega ou simula a tabela de notas fiscais com tributos detalhados (ICMS,
        PIS, COFINS, ISS).

        Returns:
            pd.DataFrame: Tabela contendo número da nota, UF de destino, valor bruto e
            impostos destacados.
        """
        # O operador '/' une os caminhos de forma nativa via Pathlib, gerando o endereço
        # exato do arquivo CSV fiscal.
        caminho_fiscal = self.pasta_dados_brutos / "erp_notas_fiscais.csv"

        # '.is_file()' verifica fisicamente se o arquivo existe gravado no disco.
        # 'if not' atua defensivamente: se o arquivo não existir, geramos uma base
        # didática representativa da PME.
        if not caminho_fiscal.is_file():
            # 'logging.info' emite um aviso no terminal informando que a base de
            # contingência fiscal foi iniciada.
            logging.info(
                "Fiscal — Base não localizada. Gerando registros de notas fiscais"
                "sintéticos..."
            )

            # 'dados_simulados' é um dicionário Python ('{}') contendo listas
            # estruturadas com notas fiscais e tributos.
            dados_simulados = {
                # Lista de identificadores numéricos das notas fiscais emitidas pela
                # PME.
                "numero_nf": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008],
                # Unidade Federativa (Estado) de destino da mercadoria para cálculo do
                # ICMS e DIFAL.
                "uf_destino": ["SP", "RJ", "MG", "SP", "PR", "SC", "RS", "BA"],
                # Valor bruto faturado de cada nota fiscal em reais (R$).
                "valor_faturado": [
                    15000.0,
                    22000.0,
                    18500.0,
                    8900.0,
                    34000.0,
                    12500.0,
                    29000.0,
                    45000.0,
                ],
                # Montante destacado de ICMS (Imposto sobre Circulação de Mercadorias e
                # Serviços) em reais.
                "valor_icms": [
                    2700.0,
                    2640.0,
                    2220.0,
                    1602.0,
                    4080.0,
                    1500.0,
                    3480.0,
                    3150.0,
                ],
                # Montante destacado de PIS (Programa de Integração Social) em reais.
                "valor_pis": [
                    247.50,
                    363.00,
                    305.25,
                    146.85,
                    561.00,
                    206.25,
                    478.50,
                    742.50,
                ],
                # Montante destacado de COFINS (Contribuição para o Financiamento da
                # Seguridade Social) em reais.
                "valor_cofins": [
                    1140.0,
                    1672.0,
                    1406.0,
                    676.40,
                    2584.0,
                    950.0,
                    2204.0,
                    3420.0,
                ],
                # Indicador binário se o produto está sob o regime de Substituição
                # Tributária (1 = Sim, 0 = Não).
                "possui_st": [0, 1, 0, 0, 1, 0, 0, 1],
            }

            # 'pd.DataFrame' converte a estrutura de dicionário em uma matriz tabular do
            # pandas em memória RAM.
            df_fiscal = pd.DataFrame(dados_simulados)

            # Soma os tributos individuais para calcular a coluna de carga total de
            # impostos por nota fiscal emitida.
            df_fiscal["total_impostos"] = (
                df_fiscal["valor_icms"]
                + df_fiscal["valor_pis"]
                + df_fiscal["valor_cofins"]
            ).round(2)

            # '.to_csv' grava a tabela gerada no disco rígido para permitir auditorias
            # posteriores.
            # 'index=False' impede que o pandas crie uma coluna extra de números
            # desnecessária no arquivo físico.
            df_fiscal.to_csv(caminho_fiscal, index=False)
        else:
            # Caso o arquivo já exista fisicamente no disco rígido, usamos o leitor
            # herdado da classe base.
            df_fiscal = self.leitor.carregar_tabela(caminho_fiscal)

        # 'logging.info' imprime no console o total de notas fiscais consolidadas para a
        # perícia.
        logging.info(
            "Fiscal — Base consolidada com %d notas fiscais auditadas.", len(df_fiscal)
        )

        # 'return' devolve a matriz tabular pronta para os cálculos tributários.
        return df_fiscal

    # KPI 51: Carga Tributária Efetiva sobre Vendas (Percentual Real de Impostos sobre a
    # Receita Bruta).
    # 'def' define a função especializada em calcular a mordida tributária global.
    def calcular_carga_tributaria_efetiva(
        self, dados: pd.DataFrame
    ) -> dict[str, float]:
        """Calcula o montante total de impostos pagos e a alíquota tributária média
        efetiva da PME.

        Carga Tributária Efetiva (%) = (Total de Impostos / Faturamento Bruto) * 100.

        Args:
            dados (pd.DataFrame): Tabela de notas fiscais com tributos e valores
            faturados.

        Returns:
            Dict[str, float]: Dicionário contendo faturamento bruto, impostos
            discriminados e alíquota efetiva.
        """
        # '.sum()' calcula a soma do faturamento bruto faturado; 'float()' garante
        # formato numérico decimal padrão.
        faturamento_total = float(dados["valor_faturado"].sum())

        # '.sum()' calcula o total acumulado recolhido aos cofres públicos a título de
        # ICMS.
        total_icms = float(dados["valor_icms"].sum())

        # '.sum()' calcula o montante acumulado pago de PIS.
        total_pis = float(dados["valor_pis"].sum())

        # '.sum()' calcula o montante acumulado pago de COFINS.
        total_cofins = float(dados["valor_cofins"].sum())

        # Soma os tributos federais e estaduais para apurar a carga tributária
        # consolidada da empresa.
        total_impostos = total_icms + total_pis + total_cofins

        # Divide o total de impostos pelo faturamento bruto para encontrar a alíquota
        # percentual real efetiva.
        # O operador ternário 'if faturamento_total > 0 else 0.0' previne erros de
        # divisão por zero caso a base esteja vazia.
        aliquota_efetiva_percentual = (
            (total_impostos / faturamento_total) * 100 if faturamento_total > 0 else 0.0
        )

        # 'laudo_fiscal' reúne os indicadores de peso tributário para o comitê executivo
        # e a controladoria.
        laudo_fiscal = {
            # 'round(..., 2)' arredonda o faturamento total em reais com precisão de
            # centavos.
            "faturamento_bruto_reais": round(faturamento_total, 2),
            # 'round(..., 2)' arredonda o recolhimento total de ICMS em reais.
            "total_icms_reais": round(total_icms, 2),
            # 'round(..., 2)' arredonda o recolhimento total de PIS em reais.
            "total_pis_reais": round(total_pis, 2),
            # 'round(..., 2)' arredonda o recolhimento total de COFINS em reais.
            "total_cofins_reais": round(total_cofins, 2),
            # 'round(..., 2)' arredonda o somatório geral de tributos em reais.
            "total_impostos_reais": round(total_impostos, 2),
            # 'round(..., 2)' arredonda a alíquota tributária média efetiva em
            # percentual (%).
            "aliquota_efetiva_percentual": round(aliquota_efetiva_percentual, 2),
        }

        # 'logging.info' imprime a Carga Tributária Efetiva no console para auditoria
        # contábil e fiscal.
        logging.info(
            "Fiscal — Carga Tributária Efetiva: %.2f%% (Total recolhido: R$ %.2f).",
            laudo_fiscal["aliquota_efetiva_percentual"],
            laudo_fiscal["total_impostos_reais"],
        )

        # 'return' devolve o dicionário estruturado com as métricas de peso tributário.
        return laudo_fiscal

    # KPI 55: Impacto Tributário e Volume de Impostos por Estado de Destino (UF).
    # 'def' define o método especialista em renderizar o gráfico comparativo de impostos
    # por região geográfica.
    def gerar_grafico_impostos_por_uf(self, dados: pd.DataFrame) -> Path:
        """Renderiza um gráfico de barras comparando o volume de tributos gerados por
        Estado (UF).

        Args:
            dados (pd.DataFrame): Tabela contendo notas fiscais, estados de destino e
            tributos.

        Returns:
            Path: Endereço físico do arquivo de imagem exportado em alta resolução (300
            DPI).
        """
        # '.groupby("uf_destino")' agrupa as notas fiscais pelo estado de entrega da
        # mercadoria.
        # '["total_impostos"].sum()' calcula o total de tributos recolhidos para cada
        # estado da federação.
        # '.reset_index()' converte o resultado agrupado em uma tabela com colunas
        # convencionais.
        tributos_por_uf = (
            dados.groupby("uf_destino")["total_impostos"].sum().reset_index()
        )

        # '.sort_values()' ordena os estados de forma decrescente pelo volume de
        # tributos gerados.
        # 'ascending=False' garante que as UFs com maior retenção fiscal fiquem no topo
        # da lista visual.
        tributos_por_uf = tributos_por_uf.sort_values(
            by="total_impostos", ascending=False
        )

        # 'self.pasta_saida' aponta para a pasta 'relatorios/figuras/fiscal/', criada
        # pelo construtor base.
        caminho_figura = self.pasta_saida / "carga_tributaria_por_uf.png"

        # 'plt.subplots()' inicializa uma moldura gráfica com 9 polegadas de largura por
        # 5 de altura.
        # 'figura' representa a tela global; 'eixo' é a área interna onde as barras
        # serão desenhadas.
        figura, eixo = plt.subplots(figsize=(9, 5))

        # 'sns.barplot' desenha as barras verticais no Seaborn representando o volume de
        # impostos por UF.
        # 'data=tributos_por_uf' fornece a tabela de dados que alimenta a visualização.
        # 'x="uf_destino"' posiciona os estados da federação no eixo horizontal.
        # 'y="total_impostos"' projeta a altura das barras correspondente ao valor em
        # reais no eixo vertical.
        # 'color="#8c564b"' aplica uma tonalidade marrom corporativa de auditoria
        # fiscal.
        # 'ax=eixo' manda o Seaborn desenhar dentro da moldura configurada no
        # matplotlib.
        sns.barplot(
            data=tributos_por_uf,
            x="uf_destino",
            y="total_impostos",
            color="#8c564b",
            ax=eixo,
        )

        # 'eixo.set_title' define o título no topo da imagem com tamanho 13 e
        # espaçamento de 12 pontos.
        eixo.set_title(
            "Volume de Tributos Recolhidos por Estado de Destino (UF)",
            fontsize=13,
            pad=12,
        )

        # 'eixo.set_xlabel' escreve o rótulo descritivo no eixo horizontal X.
        eixo.set_xlabel("Unidade Federativa (UF de Destino)", fontsize=10)

        # 'eixo.set_ylabel' escreve o rótulo financeiro no eixo vertical Y em moeda
        # corrente (R$).
        eixo.set_ylabel("Total de Impostos (R$)", fontsize=10)

        # 'plt.tight_layout()' faz o ajuste dinâmico automático de margens para não
        # cortar legendas da imagem.
        plt.tight_layout()

        # 'figura.savefig' grava o arquivo físico no disco rígido em resolução
        # industrial de 300 DPI.
        figura.savefig(caminho_figura, dpi=300)

        # 'plt.close(figura)' limpa e destrói o objeto gráfico da memória RAM para
        # prevenir vazamentos de memória.
        plt.close(figura)

        # 'logging.info' confirma no terminal que o gráfico foi renderizado e persistido
        # com sucesso.
        logging.info(
            "Fiscal — Gráfico de tributos por UF salvo em: %s", caminho_figura.name
        )

        # 'return' devolve o caminho físico do arquivo gravado.
        return caminho_figura

    # 'def' implementa a assinatura obrigatória herdada da classe base abstrata
    # 'BaseDepartamento'.
    # Este método orquestra a execução sequencial de todas as rotinas periciais do
    # departamento fiscal.
    def executar_diagnostico_completo(self) -> dict[str, Any]:
        """Coordena a apuração da carga tributária efetiva e a persistência dos gráficos
        fiscais.

        Returns:
            Dict[str, Any]: Laudo executivo completo do departamento fiscal.
        """
        # Emite log anunciando o início oficial da perícia fiscal da Fase 2.6.
        logging.info("=== INICIANDO PERÍCIA DO DEPARTAMENTO FISCAL (FASE 2.6) ===")

        # Invoca o método interno que carrega e valida as notas fiscais na memória RAM
        # uma única vez.
        df_fiscal = self.carregar_dados_fiscais()

        # Executa o cálculo da Carga Tributária Efetiva global e a discriminação de
        # impostos.
        laudo_carga = self.calcular_carga_tributaria_efetiva(df_fiscal)

        # Renderiza e salva o gráfico da carga tributária por estado de destino no
        # disco.
        caminho_grafico = self.gerar_grafico_impostos_por_uf(df_fiscal)

        # 'int(df_fiscal["uf_destino"].nunique())' conta quantos estados diferentes a
        # empresa atende comercialmente.
        total_ufs_atendidas = int(df_fiscal["uf_destino"].nunique())

        # 'int(df_fiscal["possui_st"].sum())' calcula a contagem total de notas com
        # Substituição Tributária destacada.
        total_notas_st = int(df_fiscal["possui_st"].sum())

        # 'laudo_fiscal' é o dicionário estruturado que consolida o laudo fiscal da
        # companhia.
        laudo_fiscal = {
            # Incorpora os indicadores de faturamento bruto e alíquotas calculados
            # anteriormente.
            "apuracao_impostos": laudo_carga,
            # Registra o número total de estados de destino analisados.
            "total_ufs_atendidas": total_ufs_atendidas,
            # Registra o volume de notas sujeitas ao regime especial de Substituição
            # Tributária.
            "total_notas_com_st": total_notas_st,
            # Registra o caminho do arquivo de imagem salvo para visualização em
            # relatórios ou BI.
            "grafico_impostos_por_uf": str(caminho_grafico),
        }

        # Emite log confirmando o encerramento da auditoria fiscal.
        logging.info("=== DEPARTAMENTO FISCAL CONCLUÍDO COM SUCESSO ===")

        # 'return' devolve o laudo consolidado de tributos para o orquestrador geral do
        # projeto.
        return laudo_fiscal
