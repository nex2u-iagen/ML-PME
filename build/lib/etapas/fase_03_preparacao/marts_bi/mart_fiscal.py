"""Construtor especializado do Data Mart Fiscal com suporte ao IVA Dual para BI.

Responsável por carregar notas fiscais do ERP, apurar tributos legados (ICMS, PIS,
COFINS),
aplicar a simulação da Reforma Tributária (CBS e IBS) via núcleo e exportar
a tabela comparativa de transição para dados/processados/bi/.
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

# 'from' acessa o módulo especializado de tributação que construímos no núcleo
# compartilhado.
# 'import' traz a classe 'CalculadoraReformaTributaria' para simularmos a CBS e o IBS
# sem duplicar regras.
from src.nucleo.acesso_dados.calculadora_reforma_tributaria import (
    CalculadoraReformaTributaria,
)

# 'from' navega até o submódulo de acesso a dados do nosso núcleo compartilhado.
# 'import' traz a ferramenta desacoplada de leitura tabular de arquivos.
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares


# 'class' é a palavra-chave que declara um novo molde estrutural orientado a objetos.
# 'ConstrutorMartFiscal' expressa a missão de estruturar os dados fiscais tanto no
# modelo legado quanto no novo.
class ConstrutorMartFiscal:
    """Classe responsável por consolidar impostos legados e projetar o novo IVA Dual
    para BI.
    """

    # 'def' define o método construtor '__init__', acionado na alocação da instância em
    # memória RAM.
    # 'self' referencia a própria instância construída acessando seus atributos
    # internos.
    # 'pasta_brutos: Path' recebe o endereço onde residem as tabelas brutas do ERP.
    # '-> None' atesta formalmente a ausência de retorno no método construtor.
    def __init__(self, pasta_brutos: Path) -> None:
        """Inicializa o construtor fiscal acoplando o leitor e a calculadora tributária
        do núcleo.

        Args:
            pasta_brutos (Path): Diretório contendo os arquivos CSV brutos do ERP.
        """
        # Armazena o endereço físico dos dados brutos no atributo do próprio objeto.
        self.pasta_brutos = pasta_brutos

        # Instancia a ferramenta de leitura desacoplada do núcleo por composição
        # orientada a objetos.
        self.leitor = LeitorArquivosTabulares()

        # Instancia a calculadora da reforma tributária com as alíquotas padrões
        # estimadas do novo IVA Dual.
        self.calculadora_reforma = CalculadoraReformaTributaria()

    # 'def' define o método principal que executa a apuração e consolidação dos regimes
    # fiscais.
    # '-> pd.DataFrame' documenta que a função devolverá uma tabela estruturada do
    # pandas.
    def processar(self) -> pd.DataFrame:
        """Carrega transações, computa impostos legados, simula o novo IVA Dual e
        calcula o diferencial.

        Returns:
            pd.DataFrame: Data Mart Fiscal com comparativo direto do modelo atual versus
            reforma tributária.
        """
        # Monta o caminho do arquivo de notas fiscais no diretório de dados brutos da
        # Fase 01.
        caminho_fiscal = self.pasta_brutos / "erp_notas_fiscais.csv"

        # '.is_file()' verifica fisicamente no disco se o arquivo de notas fiscais
        # existe.
        # 'if not' aplica programação defensiva com autocura: se a base não existir,
        # geramos dados representativos.
        if not caminho_fiscal.is_file():
            # 'dados_simulados' é um dicionário Python contendo notas fiscais emitidas
            # para múltiplos estados (UFs).
            dados_simulados = {
                # Lista com números de identificação das notas fiscais eletrônicas
                # (NF-e).
                "numero_nf": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008],
                # Unidade Federativa (UF) de destino da mercadoria para incidência
                # tributária.
                "uf_destino": ["SP", "RJ", "MG", "SP", "PR", "SC", "RS", "BA"],
                # Valor bruto faturado de cada nota fiscal em moeda corrente (R$).
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
                # Montante destacado de ICMS estadual em reais.
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
                # Montante destacado de PIS federal em reais.
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
                # Montante destacado de COFINS federal em reais.
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
                # Indicador binário se a nota possui Substituição Tributária destacada
                # (1 = Sim, 0 = Não).
                "possui_st": [0, 1, 0, 0, 1, 0, 0, 1],
            }

            # Converte o dicionário de contingência em uma matriz tabular do pandas em
            # memória RAM.
            df_fiscal_contingencia = pd.DataFrame(dados_simulados)

            # '.to_csv' grava a tabela gerada no disco rígido sem a coluna extra de
            # índice numérico.
            df_fiscal_contingencia.to_csv(caminho_fiscal, index=False)

        # Carrega a tabela fiscal utilizando o leitor oficial do núcleo compartilhado.
        df_fiscal = self.leitor.carregar_tabela(caminho_fiscal)

        # '.copy()' cria uma cópia independente em memória para não alterar a tabela
        # original.
        df_processado = df_fiscal.copy()

        # Calcula a soma acumulada de impostos do Regime Legado por nota fiscal emitida.
        df_processado["total_impostos_legados_reais"] = (
            df_processado["valor_icms"]
            + df_processado["valor_pis"]
            + df_processado["valor_cofins"]
        ).round(2)

        # Calcula a alíquota tributária efetiva do Regime Legado: (Impostos Legados /
        # Faturamento) * 100.
        df_processado["aliquota_efetiva_legada_pct"] = (
            (
                df_processado["total_impostos_legados_reais"]
                / df_processado["valor_faturado"]
            )
            * 100
        ).round(2)

        # Aciona o motor do núcleo para simular o cenário de IVA Dual sobre o valor
        # bruto faturado.
        df_processado = (
            self.calculadora_reforma.enriquecer_tabela_com_cenario_transicao(
                df=df_processado,
                coluna_valor="valor_faturado",
            )
        )

        # Calcula a diferença financeira entre os dois regimes: Novo IVA Dual menos os
        # Impostos Legados.
        # Valor positivo indica aumento da carga tributária; valor negativo indica
        # redução de impostos.
        df_processado["diferenca_impacto_tributario_reais"] = (
            df_processado["total_iva_dual_reais"]
            - df_processado["total_impostos_legados_reais"]
        ).round(2)

        # 'def' interna para classificar o impacto da reforma em rótulo qualitativo
        # legível para o BI.
        def classificar_impacto(diferenca: float) -> str:
            # Avalia se a nota sofrerá aumento de carga tributária no novo regime.
            if diferenca > 0:
                return "01 - Aumento de Carga Tributária (Necessita Reprecificação)"
            # Avalia se a nota terá benefício ou redução de carga.
            elif diferenca < 0:
                return "02 - Redução de Carga Tributária (Ganho de Margem)"
            # Caso neutro sem alteração.
            return "03 - Carga Neutra (Sem Variação)"

        # Aplica a classificação do impacto linha a linha sobre a coluna de diferença
        # monetária.
        df_processado["impacto_reforma_classificacao"] = df_processado[
            "diferenca_impacto_tributario_reais"
        ].apply(classificar_impacto)

        # 'dicionario_renomeacao' traduz os nomes técnicos originais para cabeçalhos
        # descritivos de negócios.
        dicionario_renomeacao = {
            # Traduz o identificador numérico da nota fiscal eletrônica.
            "numero_nf": "numero_nota_fiscal",
            # Traduz a sigla de Unidade Federativa para estado de destino.
            "uf_destino": "estado_destino_uf",
            # Traduz o valor bruto da operação para receita faturada em reais.
            "valor_faturado": "valor_bruto_faturado_reais",
            # Traduz a coluna do ICMS destacado.
            "valor_icms": "imposto_icms_legado_reais",
            # Traduz a coluna do PIS destacado.
            "valor_pis": "imposto_pis_legado_reais",
            # Traduz a coluna do COFINS destacado.
            "valor_cofins": "imposto_cofins_legado_reais",
            # Traduz a flag binária de Substituição Tributária.
            "possui_st": "indicador_st_regime_legado_binario",
            # Traduz a CBS federal projetada pela calculadora do núcleo.
            "cbs_projetada_reais": "cbs_federal_projetada_reais",
            # Traduz o IBS subnacional projetado pela calculadora do núcleo.
            "ibs_projetado_reais": "ibs_estadual_municipal_projetado_reais",
            # Traduz o somatório do novo IVA Dual.
            "total_iva_dual_reais": "total_iva_dual_projetado_reais",
        }

        # '.rename(columns=...)' aplica a tradução oficial dos cabeçalhos na tabela
        # final.
        df_processado = df_processado.rename(columns=dicionario_renomeacao)

        # Seleção ordenada e estruturada das colunas que compõem o Data Mart Fiscal
        # moderno e comparativo.
        colunas_selecionadas = [
            "numero_nota_fiscal",
            "estado_destino_uf",
            "valor_bruto_faturado_reais",
            "imposto_icms_legado_reais",
            "imposto_pis_legado_reais",
            "imposto_cofins_legado_reais",
            "total_impostos_legados_reais",
            "aliquota_efetiva_legada_pct",
            "cbs_federal_projetada_reais",
            "ibs_estadual_municipal_projetado_reais",
            "total_iva_dual_projetado_reais",
            "diferenca_impacto_tributario_reais",
            "impacto_reforma_classificacao",
            "indicador_st_regime_legado_binario",
        ]

        # 'return' devolve o DataFrame fiscal enriquecido com o comparativo de transição
        # tributária.
        return df_processado[colunas_selecionadas]
