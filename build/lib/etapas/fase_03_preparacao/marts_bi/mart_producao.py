"""Construtor especializado do Data Mart de Produção e Chão de Fábrica para BI."""

# 'from' indica a biblioteca de origem; 'pathlib' manipula diretórios e arquivos de
# forma orientada a objetos.
# 'import' traz a classe 'Path' para gerenciar endereços de pastas compatíveis com
# Windows, Linux e macOS.
from pathlib import Path

# 'import' traz a biblioteca externa 'pandas', padrão da indústria para manipulação
# tabular de dados.
# 'as' define o apelido clássico 'pd' para facilitar operações sobre DataFrames.
import pandas as pd

# 'from' navega até o submódulo de acesso a dados do nosso núcleo compartilhado.
# 'import' traz a classe 'LeitorArquivosTabulares', garantindo o reaproveitamento de
# código e baixo acoplamento.
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares


# 'class' declara o molde especializado do construtor de produção industrial.
class ConstrutorMartProducao:
    """Classe responsável exclusiva pela estruturação de ordens de produção, OEE e
    refugo fabril para BI.
    """

    # 'def' define o método especial construtor '__init__', acionado na alocação da
    # instância em memória RAM.
    # 'self' referencia a própria instância acessando seus atributos internos.
    # 'pasta_brutos: Path' recebe o endereço onde residem as tabelas brutas do ERP.
    # '-> None' atesta formalmente a ausência de retorno no método construtor.
    def __init__(self, pasta_brutos: Path) -> None:
        """Inicializa o construtor de produção acoplando o leitor de arquivos do núcleo.

        Args:
            pasta_brutos (Path): Diretório contendo os arquivos CSV brutos do ERP.
        """
        # Armazena o endereço físico dos dados brutos no atributo do próprio objeto.
        self.pasta_brutos = pasta_brutos

        # Instancia a ferramenta de leitura desacoplada do núcleo compartilhado por
        # composição orientada a objetos.
        self.leitor = LeitorArquivosTabulares()

    # 'def' define o método principal que executa a apuração dos indicadores de
    # manufatura.
    # '-> pd.DataFrame' documenta que a função devolverá uma tabela estruturada do
    # pandas.
    def processar(self) -> pd.DataFrame:
        """Carrega, calcula métricas de refugo, aproveitamento fabril e renomeia termos
        de chão de fábrica.

        Returns:
            pd.DataFrame: Data Mart de Produção consolidado com indicadores de
            eficiência fabril.
        """
        # Monta o caminho do arquivo de ordens de produção no diretório de dados brutos
        # da Fase 01.
        caminho_producao = self.pasta_brutos / "erp_ordens_producao.csv"

        # '.is_file()' verifica fisicamente no disco rígido se o arquivo de produção
        # existe.
        # 'if not' aplica programação defensiva com autocura: se a base não existir,
        # geramos dados representativos.
        if not caminho_producao.is_file():
            # 'dados_simulados' é um dicionário Python contendo registros
            # representativos de ordens fabris.
            dados_simulados = {
                # Lista de códigos de identificação das Ordens de Produção (OPs).
                "id_ordem_producao": [801, 802, 803, 804, 805, 806, 807, 808],
                # Descrição nominal do item que passou pela linha de manufatura.
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
                # Meta volumétrica estipulada pelo Planeamento e Controlo da Produção
                # (PCP).
                "quantidade_planejada": [50, 200, 30, 60, 250, 40, 80, 45],
                # Quantidade de peças físicas efetivamente fabricadas no turno.
                "quantidade_produzida": [48, 195, 28, 55, 230, 38, 74, 42],
                # Quantidade de peças que saíram com defeito e foram descartadas como
                # sucata/refugo.
                "quantidade_refugada": [3, 12, 2, 5, 18, 1, 6, 2],
                # Horas totais de expediente em que as máquinas estavam escaladas para
                # produzir.
                "horas_disponiveis": [40.0, 40.0, 40.0, 44.0, 44.0, 44.0, 40.0, 36.0],
                # Horas paradas por quebra mecânica, manutenção corretiva ou falta de
                # materiais.
                "horas_paradas": [4.5, 2.0, 6.0, 3.0, 5.5, 1.5, 4.0, 2.0],
            }

            # Converte o dicionário de contingência em uma matriz tabular do pandas em
            # memória RAM.
            df_producao_contingencia = pd.DataFrame(dados_simulados)

            # '.to_csv' grava a tabela gerada no disco rígido sem a coluna extra de
            # índice numérico.
            df_producao_contingencia.to_csv(caminho_producao, index=False)

        # Carrega a tabela de produção utilizando o leitor oficial do núcleo
        # compartilhado.
        df_producao = self.leitor.carregar_tabela(caminho_producao)

        # '.copy()' cria uma cópia independente em memória para não alterar a tabela
        # original.
        df_processado = df_producao.copy()

        # Calcula a quantidade de peças boas que foram aprovadas no controlo de
        # qualidade: Produzidas - Refugadas.
        df_processado["quantidade_aprovada_boa"] = (
            df_processado["quantidade_produzida"] - df_processado["quantidade_refugada"]
        )

        # Calcula a taxa percentual de refugo: (Quantidade Refugada / Quantidade
        # Produzida) * 100.
        df_processado["taxa_refugo_pct"] = (
            (
                df_processado["quantidade_refugada"]
                / df_processado["quantidade_produzida"]
            )
            * 100
        ).round(2)

        # Calcula o índice de cumprimento de meta do PCP: (Quantidade Produzida /
        # Quantidade Planejada) * 100.
        df_processado["cumprimento_meta_pcp_pct"] = (
            (
                df_processado["quantidade_produzida"]
                / df_processado["quantidade_planejada"]
            )
            * 100
        ).round(2)

        # Calcula o percentual de disponibilidade mecânica da máquina: ((Horas
        # Disponíveis - Horas Paradas) / Horas Disponíveis) * 100.
        horas_operando = (
            df_processado["horas_disponiveis"] - df_processado["horas_paradas"]
        )
        df_processado["disponibilidade_maquina_pct"] = (
            (horas_operando / df_processado["horas_disponiveis"]) * 100
        ).round(2)

        # 'dicionario_renomeacao' traduz nomes técnicos de chão de fábrica para
        # cabeçalhos descritivos de negócios.
        dicionario_renomeacao = {
            # Traduz o identificador numérico da Ordem de Produção.
            "id_ordem_producao": "numero_ordem_producao",
            # Traduz o nome nominal do material manufaturado.
            "descricao_produto": "nome_produto_manufaturado",
            # Traduz a meta volumétrica do PCP.
            "quantidade_planejada": "meta_planejada_unidades",
            # Traduz o volume físico total fabricado.
            "quantidade_produzida": "total_produzido_unidades",
            # Traduz as peças descartadas como sucata.
            "quantidade_refugada": "pecas_refugadas_descarte_unidades",
            # Traduz as horas de expediente programadas.
            "horas_disponiveis": "tempo_planejado_maquina_horas",
            # Traduz as horas de máquina parada por defeito ou setup.
            "horas_paradas": "tempo_parada_improdutiva_horas",
        }

        # '.rename(columns=...)' aplica a tradução dos cabeçalhos na tabela de produção.
        df_processado = df_processado.rename(columns=dicionario_renomeacao)

        # Seleção estruturada das colunas que compõem o Data Mart de Produção para
        # visualização no BI.
        colunas_selecionadas = [
            "numero_ordem_producao",
            "nome_produto_manufaturado",
            "meta_planejada_unidades",
            "total_produzido_unidades",
            "quantidade_aprovada_boa",
            "pecas_refugadas_descarte_unidades",
            "taxa_refugo_pct",
            "cumprimento_meta_pcp_pct",
            "tempo_planejado_maquina_horas",
            "tempo_parada_improdutiva_horas",
            "disponibilidade_maquina_pct",
        ]

        # 'return' devolve o DataFrame de produção tratado apenas com as colunas
        # essenciais.
        return df_processado[colunas_selecionadas]
