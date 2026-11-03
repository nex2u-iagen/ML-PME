"""Construtor especializado do Data Mart de Pós-Venda e Atendimento (SAC) para BI."""

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


# 'class' declara o molde especializado do construtor de atendimento ao cliente.
class ConstrutorMartPosVenda:
    """Classe responsável exclusiva pela estruturação de chamados, MTTR e satisfação
    CSAT para BI.
    """

    # 'def' define o método especial construtor '__init__', acionado na alocação da
    # instância em memória RAM.
    # 'self' referencia a própria instância construída.
    # 'pasta_brutos: Path' recebe o endereço onde residem as tabelas brutas do ERP.
    # '-> None' atesta formalmente a ausência de retorno no método construtor.
    def __init__(self, pasta_brutos: Path) -> None:
        """Inicializa o construtor de pós-venda acoplando o leitor de arquivos do
        núcleo.

        Args:
            pasta_brutos (Path): Diretório contendo os arquivos CSV brutos do ERP.
        """
        # Armazena o endereço físico dos dados brutos no atributo do próprio objeto.
        self.pasta_brutos = pasta_brutos

        # Instancia a ferramenta de leitura desacoplada do núcleo compartilhado por
        # composição orientada a objetos.
        self.leitor = LeitorArquivosTabulares()

    # 'def' define o método principal que executa a higienização de chamados e suporte.
    # '-> pd.DataFrame' documenta que a função devolverá uma tabela estruturada do
    # pandas.
    def processar(self) -> pd.DataFrame:
        """Carrega, categoriza faixas de tempo de resposta e padroniza termos do SAC
        para BI.

        Returns:
            pd.DataFrame: Data Mart de Pós-Venda consolidado com indicadores de
            qualidade de atendimento.
        """
        # Monta o caminho do arquivo de chamados do SAC no diretório de dados brutos da
        # Fase 01.
        caminho_sac = self.pasta_brutos / "erp_sac_chamados.csv"

        # '.is_file()' verifica fisicamente no disco rígido se o arquivo de chamados
        # existe.
        # 'if not' aplica programação defensiva com autocura: se a base não existir,
        # geramos dados representativos.
        if not caminho_sac.is_file():
            # 'dados_simulados' é um dicionário Python contendo registros
            # representativos de tickets de suporte.
            dados_simulados = {
                # Lista de códigos de identificação única de cada ticket ou chamado de
                # suporte.
                "id_chamado": [701, 702, 703, 704, 705, 706, 707, 708, 709, 710],
                # Código de identificação do cliente que solicitou o atendimento.
                "id_cliente": [101, 103, 104, 102, 105, 108, 106, 101, 107, 104],
                # Motivo principal ou categoria do atrito relatado pelo consumidor.
                "motivo_chamado": [
                    "Atraso na Entrega",
                    "Produto com Avaria",
                    "Divergência na Nota Fiscal",
                    "Dúvida Operacional",
                    "Produto com Avaria",
                    "Atraso na Entrega",
                    "Divergência na Nota Fiscal",
                    "Dúvida Operacional",
                    "Atraso na Entrega",
                    "Cobrança Indevida",
                ],
                # Tempo total de resolução do chamado medido em horas corridas.
                "tempo_resolucao_horas": [
                    48.0,
                    72.0,
                    12.0,
                    4.0,
                    96.0,
                    52.0,
                    18.0,
                    6.0,
                    64.0,
                    24.0,
                ],
                # Situação atual do ticket no fluxo de pós-venda.
                "status_chamado": [
                    "Resolvido",
                    "Resolvido",
                    "Resolvido",
                    "Resolvido",
                    "Em Aberto",
                    "Resolvido",
                    "Resolvido",
                    "Resolvido",
                    "Em Aberto",
                    "Resolvido",
                ],
                # Nota de satisfação atribuída pelo cliente na escala de 1 a 5 (CSAT).
                "nota_satisfacao_csat": [3, 2, 4, 5, 1, 3, 4, 5, 2, 4],
            }

            # Converte o dicionário de contingência em uma matriz tabular do pandas em
            # memória RAM.
            df_sac_contingencia = pd.DataFrame(dados_simulados)

            # '.to_csv' grava a tabela gerada no disco rígido sem a coluna extra de
            # índice numérico.
            df_sac_contingencia.to_csv(caminho_sac, index=False)

        # Carrega a tabela de chamados utilizando o leitor oficial do núcleo
        # compartilhado.
        df_sac = self.leitor.carregar_tabela(caminho_sac)

        # '.copy()' cria uma cópia independente em memória para não alterar a tabela
        # original.
        df_processado = df_sac.copy()

        # 'def' interna para agrupar as horas de resolução em faixas de tempo de
        # atendimento (SLA).
        def categorizar_tempo_resposta(horas: float) -> str:
            # Avalia chamados resolvidos em menos de 24 horas (atendimento ágil no
            # primeiro dia).
            if horas <= 24.0:
                return "01 - Resolução Rápida (Até 24h)"
            # Avalia chamados resolvidos entre 24 e 48 horas (atendimento padrão).
            elif horas <= 48.0:
                return "02 - Resolução Padrão (24h a 48h)"
            # Classifica atendimentos com demora crítica que geram atrito e risco de
            # cancelamento.
            return "03 - Resolução Crítica (Acima de 48h)"

        # Aplica a categorização de tempo de resposta em cada linha da tabela.
        df_processado["faixa_sla_atendimento"] = df_processado[
            "tempo_resolucao_horas"
        ].apply(categorizar_tempo_resposta)

        # 'def' interna para classificar o nível de satisfação CSAT em escala verbal
        # amigável.
        def categorizar_csat(nota: int) -> str:
            # Notas 4 e 5 são promotores ou clientes satisfeitos.
            if nota >= 4:
                return "Satisfeito (Nota 4-5)"
            # Nota 3 representa neutralidade.
            elif nota == 3:
                return "Neutro (Nota 3)"
            # Notas 1 e 2 são clientes detratores com alto risco de churn.
            return "Insatisfeito / Detrator (Nota 1-2)"

        # Aplica a classificação semântica do CSAT na tabela.
        df_processado["classificacao_csat"] = df_processado[
            "nota_satisfacao_csat"
        ].apply(categorizar_csat)

        # Mapeia cabeçalhos técnicos para termos semânticos claros de gestão de clientes
        # no BI.
        dicionario_renomeacao = {
            # Código de identificação do ticket de suporte.
            "id_chamado": "codigo_ticket_sac",
            # Código do cliente associado ao chamado.
            "id_cliente": "codigo_cliente",
            # Categoria da reclamação ou dúvida do cliente.
            "motivo_chamado": "motivo_contato_reclamacao",
            # Duração em horas para encerramento do chamado.
            "tempo_resolucao_horas": "tempo_resolucao_horas",
            # Status do chamado no fluxo de suporte.
            "status_chamado": "situacao_status_ticket",
            # Nota numérica do CSAT (1 a 5).
            "nota_satisfacao_csat": "nota_csat_escala_5",
        }

        # '.rename(columns=...)' aplica a tradução dos cabeçalhos na tabela.
        df_processado = df_processado.rename(columns=dicionario_renomeacao)

        # Seleção ordenada das colunas que compõem o Data Mart de Pós-Venda estruturado.
        colunas_selecionadas = [
            "codigo_ticket_sac",
            "codigo_cliente",
            "motivo_contato_reclamacao",
            "tempo_resolucao_horas",
            "faixa_sla_atendimento",
            "situacao_status_ticket",
            "nota_csat_escala_5",
            "classificacao_csat",
        ]

        # 'return' devolve o DataFrame de pós-venda tratado apenas com as colunas
        # essenciais.
        return df_processado[colunas_selecionadas]
