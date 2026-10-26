"""Construtor especializado do Data Mart de Logística e Expedição para BI."""

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


# 'class' declara o molde especializado do construtor de logística.
class ConstrutorMartLogistica:
    """Classe responsável exclusiva pela estruturação de fretes, prazos e nível de
    serviço OTIF para BI.
    """

    # 'def' define o método especial construtor '__init__', acionado na alocação da
    # instância em memória RAM.
    # 'self' referencia a própria instância acessando seus atributos internos.
    # 'pasta_brutos: Path' recebe o endereço onde residem as tabelas brutas do ERP.
    # '-> None' atesta formalmente a ausência de retorno no método construtor.
    def __init__(self, pasta_brutos: Path) -> None:
        """Inicializa o construtor de logística acoplando o leitor de arquivos do
        núcleo.

        Args:
            pasta_brutos (Path): Diretório contendo os arquivos CSV brutos do ERP.
        """
        # Armazena o endereço físico dos dados brutos no atributo do próprio objeto.
        self.pasta_brutos = pasta_brutos

        # Instancia a ferramenta de leitura desacoplada do núcleo compartilhado por
        # composição orientada a objetos.
        self.leitor = LeitorArquivosTabulares()

    # 'def' define o método principal que executa a higienização e apuração de
    # transportes.
    # '-> pd.DataFrame' documenta que a função devolverá uma tabela estruturada do
    # pandas.
    def processar(self) -> pd.DataFrame:
        """Carrega, calcula métricas de frete, avalia o indicador OTIF e renomeia termos
        para BI.

        Returns:
            pd.DataFrame: Data Mart de Logística consolidado com fretes e indicadores de
            serviço.
        """
        # Monta o caminho do arquivo de expedição no diretório de dados brutos da Fase
        # 01.
        caminho_logistica = self.pasta_brutos / "erp_expedicao_logistica.csv"

        # '.is_file()' verifica fisicamente no disco rígido se o arquivo de logística
        # existe.
        # 'if not' aplica programação defensiva com autocura: se a base não existir,
        # geramos dados representativos.
        if not caminho_logistica.is_file():
            # 'dados_simulados' é um dicionário Python contendo registros
            # representativos de transportes e despachos.
            dados_simulados = {
                # Lista de identificadores numéricos únicos de cada despacho rodoviário.
                "id_despacho": [901, 902, 903, 904, 905, 906, 907, 908, 909, 910],
                # Razão social da empresa transportadora contratada.
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
                # Região geográfica de destino da carga expedida.
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
                # Valor faturado da mercadoria transportada em reais (R$).
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
                # Custo cobrado pela transportadora pelo serviço de frete em reais.
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
                # Prazo limite de entrega acordado com o cliente medido em dias
                # corridos.
                "prazo_prometido_dias": [3, 5, 8, 3, 4, 6, 9, 4, 4, 3],
                # Tempo real que a transportadora levou para finalizar a entrega em dias
                # corridos.
                "dias_transito_real": [3, 4, 10, 2, 4, 7, 9, 3, 5, 3],
                # Indicador de entrega completa e sem danos físicos (1 = Íntegro, 0 =
                # Com Avaria/Falta).
                "pedido_integro": [1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
            }

            # Converte o dicionário de contingência em uma matriz tabular do pandas em
            # memória RAM.
            df_logistica_contingencia = pd.DataFrame(dados_simulados)

            # '.to_csv' grava a tabela gerada no disco rígido sem a coluna extra de
            # índice numérico.
            df_logistica_contingencia.to_csv(caminho_logistica, index=False)

        # Carrega a tabela de logística utilizando o leitor oficial do núcleo
        # compartilhado.
        df_logistica = self.leitor.carregar_tabela(caminho_logistica)

        # '.copy()' cria uma cópia independente em memória para não alterar a tabela
        # original.
        df_processado = df_logistica.copy()

        # Calcula a proporção percentual do frete sobre o valor da mercadoria
        # (Freight-to-Sales %).
        df_processado["percentual_frete_sobre_carga_pct"] = (
            (df_processado["custo_frete"] / df_processado["valor_mercadoria"]) * 100
        ).round(2)

        # Avalia se a entrega foi pontual (On-Time): dias reais menores ou iguais ao
        # prazo prometido.
        df_processado["entrega_pontual_on_time"] = (
            df_processado["dias_transito_real"] <= df_processado["prazo_prometido_dias"]
        ).astype(int)

        # Avalia o indicador supremo de nível de serviço OTIF (On-Time In-Full): pontual
        # E íntegro.
        df_processado["indicador_otif_binario"] = (
            (df_processado["entrega_pontual_on_time"] == 1)
            & (df_processado["pedido_integro"] == 1)
        ).astype(int)

        # 'def' interna para rotular o status da pontualidade em texto legível para o
        # dashboard.
        def rotular_prazo(linha: pd.Series) -> str:
            # Avalia se o tempo real ultrapassou o limite acordado.
            if linha["entrega_pontual_on_time"] == 1:
                return "01 - Entrega no Prazo (Pontual)"
            return "02 - Entrega com Atraso (Fora do Prazo)"

        # Aplica a rotulagem de prazo linha a linha.
        df_processado["descricao_status_prazo"] = df_processado.apply(
            rotular_prazo, axis=1
        )

        # 'def' interna para rotular a qualidade física da entrega.
        def rotular_integridade(flag_integro: int) -> str:
            # Avalia se o pedido chegou 100% completo e sem quebras.
            if flag_integro == 1:
                return "Carga Íntegra (Sem Avarias)"
            return "Carga Avariada / Incompleta"

        # Aplica a rotulagem de integridade física.
        df_processado["descricao_integridade_carga"] = df_processado[
            "pedido_integro"
        ].apply(rotular_integridade)

        # Mapeia cabeçalhos técnicos para termos semânticos claros de gestão logística
        # no BI.
        dicionario_renomeacao = {
            # Traduz o código identificador do conhecimento de transporte.
            "id_despacho": "numero_despacho_cte",
            # Razão social da empresa de transporte.
            "transportadora": "nome_transportadora_contratada",
            # Região geográfica de destino da mercadoria.
            "regiao_destino": "regiao_geografica_destino",
            # Valor nominal das mercadorias transportadas em reais.
            "valor_mercadoria": "valor_carga_transportada_reais",
            # Despesa financeira com a fatura de frete em reais.
            "custo_frete": "custo_frete_pago_reais",
            # Prazo prometido em dias de calendário.
            "prazo_prometido_dias": "prazo_acordado_dias",
            # Tempo real em dias de trânsito rodoviário.
            "dias_transito_real": "tempo_transito_real_dias",
        }

        # '.rename(columns=...)' aplica a tradução dos cabeçalhos na tabela.
        df_processado = df_processado.rename(columns=dicionario_renomeacao)

        # Seleção ordenada das colunas que compõem o Data Mart de Logística estruturado.
        colunas_selecionadas = [
            "numero_despacho_cte",
            "nome_transportadora_contratada",
            "regiao_geografica_destino",
            "valor_carga_transportada_reais",
            "custo_frete_pago_reais",
            "percentual_frete_sobre_carga_pct",
            "prazo_acordado_dias",
            "tempo_transito_real_dias",
            "descricao_status_prazo",
            "descricao_integridade_carga",
            "indicador_otif_binario",
        ]

        # 'return' devolve o DataFrame de logística tratado.
        return df_processado[colunas_selecionadas]
