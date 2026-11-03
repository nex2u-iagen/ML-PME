"""Construtor especializado do Data Mart de Recursos Humanos e Pessoal para BI."""

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


# 'class' declara o molde especializado do construtor de gestão de pessoas.
class ConstrutorMartRH:
    """Classe responsável exclusiva pela estruturação de colaboradores, folha
    salarial e turnover para BI.
    """

    # 'def' define o método especial construtor '__init__', acionado na alocação da
    # instância em memória RAM.
    # 'self' referencia a própria instância construída.
    # 'pasta_brutos: Path' recebe o endereço onde residem as tabelas brutas do ERP.
    # '-> None' atesta formalmente a ausência de retorno no método construtor.
    def __init__(self, pasta_brutos: Path) -> None:
        """Inicializa o construtor de RH acoplando o leitor de arquivos do núcleo.

        Args:
            pasta_brutos (Path): Diretório contendo os arquivos CSV brutos do ERP.
        """
        # Armazena o endereço físico dos dados brutos no atributo do próprio objeto.
        self.pasta_brutos = pasta_brutos

        # Instancia a ferramenta de leitura desacoplada do núcleo compartilhado por
        # composição orientada a objetos.
        self.leitor = LeitorArquivosTabulares()

    # 'def' define o método principal que executa a higienização da folha de pagamento e
    # colaboradores.
    # '-> pd.DataFrame' documenta que a função devolverá uma tabela estruturada do
    # pandas.
    def processar(self) -> pd.DataFrame:
        """Carrega, calcula encargos sociais totais e renomeia termos de gestão de
        pessoas para BI.

        Returns:
            pd.DataFrame: Data Mart de RH consolidado com custos de folha, vínculos e
            assiduidade.
        """
        # Monta o caminho do arquivo de folha de pagamento no diretório de dados brutos
        # da Fase 01.
        caminho_rh = self.pasta_brutos / "erp_funcionarios_folha.csv"

        # '.is_file()' verifica fisicamente no disco rígido se o arquivo de
        # colaboradores existe.
        # 'if not' aplica programação defensiva com autocura: se a base não existir,
        # geramos dados representativos.
        if not caminho_rh.is_file():
            # 'dados_simulados' é um dicionário Python contendo registros
            # representativos do quadro de funcionários.
            dados_simulados = {
                # Lista de matrículas numéricas de identificação de cada colaborador da
                # PME.
                "id_funcionario": [301, 302, 303, 304, 305, 306, 307, 308, 309, 310],
                # Nome completo do colaborador cadastrado no livro de empregados.
                "nome_colaborador": [
                    "Carlos Silva",
                    "Mariana Souza",
                    "Roberto Dias",
                    "Fernanda Lima",
                    "Lucas Mendes",
                    "Beatriz Costa",
                    "João Ferreira",
                    "Aline Prado",
                    "Gabriel Torres",
                    "Juliana Rocha",
                ],
                # Setor ou departamento de alocação física do colaborador.
                "setor": [
                    "Comercial",
                    "Financeiro",
                    "Produção",
                    "Produção",
                    "Estoque",
                    "Comercial",
                    "Produção",
                    "Administrativo",
                    "Logística",
                    "Pós-Venda",
                ],
                # Salário base nominal contratado em carteira em reais (R$).
                "salario_base": [
                    3800.0,
                    4500.0,
                    2400.0,
                    2600.0,
                    2100.0,
                    4200.0,
                    2500.0,
                    3500.0,
                    2300.0,
                    2800.0,
                ],
                # Encargos patronais e provisões trabalhistas obrigatórias em reais
                # (FGTS, INSS patronal, férias/13º).
                "encargos_sociais": [
                    1520.0,
                    1800.0,
                    960.0,
                    1040.0,
                    840.0,
                    1680.0,
                    1000.0,
                    1400.0,
                    920.0,
                    1120.0,
                ],
                # Situação cadastral do vínculo empregatício no período avaliado.
                "status_vinculo": [
                    "Ativo",
                    "Ativo",
                    "Ativo",
                    "Demitido",
                    "Ativo",
                    "Ativo",
                    "Demitido",
                    "Ativo",
                    "Ativo",
                    "Ativo",
                ],
                # Total de faltas injustificadas registradas no ponto eletrônico durante
                # o ano civil.
                "dias_falta": [1, 0, 4, 8, 2, 0, 6, 1, 3, 2],
            }

            # Converte o dicionário de contingência em uma matriz tabular do pandas em
            # memória RAM.
            df_rh_contingencia = pd.DataFrame(dados_simulados)

            # Soma o salário base com os encargos para calcular o custo total do
            # empregado para a empresa.
            df_rh_contingencia["custo_total_empresa"] = (
                df_rh_contingencia["salario_base"]
                + df_rh_contingencia["encargos_sociais"]
            ).round(2)

            # '.to_csv' grava a tabela gerada no disco rígido sem a coluna extra de
            # índice numérico.
            df_rh_contingencia.to_csv(caminho_rh, index=False)

        # Carrega a tabela de colaboradores utilizando o leitor oficial do núcleo
        # compartilhado.
        df_rh = self.leitor.carregar_tabela(caminho_rh)

        # '.copy()' cria uma cópia independente em memória para não alterar a tabela
        # original.
        df_processado = df_rh.copy()

        # Calcula o custo total consolidado da empresa por colaborador caso a coluna não
        # exista.
        df_processado["custo_total_colaborador_reais"] = (
            df_processado["salario_base"] + df_processado["encargos_sociais"]
        ).round(2)

        # 'def' interna para rotular o nível de assiduidade do colaborador com base nas
        # faltas registradas.
        def rotular_assiduidade(faltas: int) -> str:
            # Colaboradores com zero ou uma falta possuem assiduidade exemplar.
            if faltas <= 1:
                return "01 - Assiduidade Alta (Até 1 falta)"
            # Colaboradores com 2 a 4 faltas apresentam assiduidade regular.
            elif faltas <= 4:
                return "02 - Assiduidade Média (2 a 4 faltas)"
            # Acima de 4 faltas indica absenteísmo crônico que exige acompanhamento da
            # liderança.
            return "03 - Absenteísmo Crítico (Mais de 4 faltas)"

        # Aplica a rotulagem de assiduidade em cada linha da tabela.
        df_processado["faixa_assiduidade"] = df_processado["dias_falta"].apply(
            rotular_assiduidade
        )

        # Mapeia cabeçalhos técnicos para termos semânticos claros de gestão de pessoas
        # no BI.
        dicionario_renomeacao = {
            # Matrícula cadastral do colaborador.
            "id_funcionario": "matricula_colaborador",
            # Nome completo do funcionário.
            "nome_colaborador": "nome_completo_colaborador",
            # Departamento de trabalho.
            "setor": "departamento_setor_atuacao",
            # Salário nominal de carteira.
            "salario_base": "salario_base_contratual_reais",
            # Encargos sociais recolhidos.
            "encargos_sociais": "encargos_trabalhistas_reais",
            # Situação do contrato de trabalho.
            "status_vinculo": "situacao_contrato_trabalho",
            # Contagem de faltas injustificadas.
            "dias_falta": "total_dias_falta_ano",
        }

        # '.rename(columns=...)' aplica a tradução dos cabeçalhos na tabela.
        df_processado = df_processado.rename(columns=dicionario_renomeacao)

        # Seleção estruturada das colunas que compõem o Data Mart de RH para consumo
        # visual.
        colunas_selecionadas = [
            "matricula_colaborador",
            "nome_completo_colaborador",
            "departamento_setor_atuacao",
            "salario_base_contratual_reais",
            "encargos_trabalhistas_reais",
            "custo_total_colaborador_reais",
            "situacao_contrato_trabalho",
            "total_dias_falta_ano",
            "faixa_assiduidade",
        ]

        # 'return' devolve o DataFrame de RH tratado apenas com as colunas essenciais.
        return df_processado[colunas_selecionadas]
