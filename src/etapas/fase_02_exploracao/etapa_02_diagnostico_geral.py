"""Módulo de Diagnóstico Estrutural Macro e Saúde dos Dados (Fase 02).

Responsável por realizar a triagem inicial das entidades do ERP,
identificando volumetria, integridade de tipos, incidência de valores
ausentes (missing values), linhas duplicadas e cardinalidade univariada.
"""

# 'import' traz o módulo 'logging' da biblioteca padrão do Python para registro
# rastreável de eventos.
import logging

# 'from' navega na biblioteca padrão 'pathlib'; 'import' traz a classe 'Path' para
# manipulação de diretórios.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão do Python para anotações de
# tipagem estática.
# 'Any' indica múltiplos tipos possíveis; 'Dict' indica dicionários; 'List' documenta
# listas de itens.
from typing import Any

# 'import' traz a biblioteca fundamental 'pandas' para manipulação e cálculo sobre
# estruturas tabulares.
# 'as' define o apelido universal 'pd', padrão absoluto da comunidade de dados.
import pandas as pd

# 'from' navega até a camada fundamental de acesso a dados do nosso projeto.
# 'import' reaproveita a classe 'LeitorArquivosTabulares' que construímos no núcleo,
# evitando duplicação de código.
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares

# 'logging.basicConfig' configura a formatação das mensagens no console do terminal.
# 'level=logging.INFO' assegura que avisos de progresso, relatórios e resumos sejam
# exibidos na tela.
# 'format' dita o molde visual: data/hora — [gravidade] — descrição detalhada do evento.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara um novo molde estrutural sob o paradigma de Orientação a Objetos.
# 'AuditorSaudeDados' é o nome da nossa classe em Português do Brasil e padrão
# PascalCase.
class AuditorSaudeDados:
    """Classe responsável por auditar a qualidade mecânica e estatística inicial das
    tabelas.
    """

    # 'def' define o método construtor '__init__', acionado no instante em que a classe
    # é instanciada.
    # 'self' referencia a instância individual sendo gerada na memória do computador.
    # 'pasta_dados_brutos: Path' exige receber o caminho onde estão armazenados os
    # arquivos CSV do ERP.
    # '-> None' atesta formalmente que o construtor apenas inicializa atributos e não
    # retorna valores.
    def __init__(self, pasta_dados_brutos: Path) -> None:
        """Inicializa o auditor configurando o diretório de dados e o leitor do núcleo.

        Args:
            pasta_dados_brutos (Path): Caminho do diretório contendo os arquivos CSV
            brutos.
        """
        # 'self.pasta_dados_brutos' armazena o caminho informado como atributo interno
        # do objeto.
        self.pasta_dados_brutos = pasta_dados_brutos

        # Aplicamos o padrão de Composição de Objetos: instanciamos a ferramenta de
        # leitura do núcleo.
        self.leitor = LeitorArquivosTabulares()

        # Emite um log no console confirmando a inicialização do auditor para a pasta
        # especificada.
        logging.info(
            "Auditor de Saúde de Dados configurado para: %s", self.pasta_dados_brutos
        )

    # 'def' define o método que audita uma tabela isolada a partir do seu endereço
    # físico.
    # 'caminho_arquivo_csv: Path' exige o caminho do arquivo tabular a ser periciado.
    # '-> Dict[str, Any]' avisa que o retorno será um dicionário contendo as métricas de
    # diagnóstico.
    def auditar_tabela(self, caminho_arquivo_csv: Path) -> dict[str, Any]:
        """Realiza um diagnóstico completo da integridade física e tipológica de uma
        tabela.

        Args:
            caminho_arquivo_csv (Path): Caminho físico do arquivo CSV no disco.

        Returns:
            Dict[str, Any]: Dicionário com volumetria, nulos, duplicatas e resumo de
            tipos.
        """
        # 'caminho_arquivo_csv.name' extrai apenas o nome final do arquivo para fins de
        # exibição amigável.
        nome_tabela = caminho_arquivo_csv.name

        # Emite um log informando o início da perícia estrutural na tabela atual.
        logging.info("Iniciando auditoria estrutural na tabela: %s", nome_tabela)

        # Utiliza o leitor do núcleo para carregar a tabela na memória RAM de forma
        # segura e defensiva.
        dados_tabela = self.leitor.carregar_tabela(caminho_arquivo_csv)

        # 'dados_tabela.shape[0]' retorna a contagem inteira de linhas (registros) da
        # matriz tabular.
        total_linhas = int(dados_tabela.shape[0])

        # 'dados_tabela.shape[1]' retorna a contagem inteira de colunas (atributos) da
        # matriz tabular.
        total_colunas = int(dados_tabela.shape[1])

        # 'dados_tabela.duplicated().sum()' identifica linhas perfeitamente repetidas em
        # todas as colunas e soma o total.
        total_duplicadas = int(dados_tabela.duplicated().sum())

        # 'dados_tabela.isnull().sum()' calcula a quantidade de valores vazios
        # (NaN/None) por coluna.
        contagem_nulos = dados_tabela.isnull().sum()

        # '(contagem_nulos / total_linhas) * 100' calcula o impacto percentual de
        # ausência para cada coluna.
        percentual_nulos = (
            (contagem_nulos / total_linhas) * 100
            if total_linhas > 0
            else contagem_nulos
        )

        # 'pd.concat' une a contagem absoluta e o percentual lado a lado em um novo
        # DataFrame de relatório.
        tabela_nulos = pd.concat([contagem_nulos, percentual_nulos], axis=1)

        # Define rótulos claros para as colunas do relatório de valores faltantes.
        tabela_nulos.columns = ["total_ausentes", "percentual_ausente"]

        # Filtra apenas atributos que possuem pelo menos 1 valor faltante para evitar
        # relatórios poluídos.
        colunas_com_nulos = tabela_nulos[tabela_nulos["total_ausentes"] > 0].to_dict(
            orient="index"
        )

        # 'lista_detalhes_colunas' é uma lista Python ('[]') para consolidar tipos e
        # valores únicos por coluna.
        lista_detalhes_colunas: list[dict[str, Any]] = []

        # 'for' itera por cada nome de coluna contido na lista de colunas da tabela
        # ('dados_tabela.columns').
        for nome_coluna in dados_tabela.columns:
            # 'dados_tabela[nome_coluna]' extrai a série unidimensional correspondente à
            # coluna atual.
            serie_coluna = dados_tabela[nome_coluna]

            # 'serie_coluna.dtype' extrai o tipo de dado primitivo do pandas (ex.:
            # int64, float64, object).
            tipo_dado = str(serie_coluna.dtype)

            # 'serie_coluna.nunique()' conta quantos valores distintos (cardinalidade)
            # existem no campo.
            cardinalidade = int(serie_coluna.nunique())

            # '.append()' adiciona o dicionário com os sinais vitais da coluna ao final
            # da nossa lista.
            lista_detalhes_colunas.append(
                {
                    "nome_coluna": nome_coluna,
                    "tipo_primitivo": tipo_dado,
                    "valores_unicos": cardinalidade,
                    # Um campo com cardinalidade igual ao total de linhas geralmente é
                    # um identificador/chave primária.
                    "provavel_identificador": bool(
                        cardinalidade == total_linhas and total_linhas > 0
                    ),
                }
            )

        # 'laudo_tabela' é o dicionário que reúne todas as descobertas da auditoria
        # estrutural da tabela.
        laudo_tabela: dict[str, Any] = {
            "nome_arquivo": nome_tabela,
            "total_linhas": total_linhas,
            "total_colunas": total_colunas,
            "linhas_duplicadas": total_duplicadas,
            "colunas_com_valores_nulos": colunas_com_nulos,
            "resumo_atributos": lista_detalhes_colunas,
        }

        # Emite log resumindo as conclusões da auditoria estrutural da tabela.
        logging.info(
            "Laudo de '%s': %d linhas | %d colunas | %d duplicadas | %d colunas com"
            "nulos.",
            nome_tabela,
            total_linhas,
            total_colunas,
            total_duplicadas,
            len(colunas_com_nulos),
        )

        # 'return' devolve o laudo técnico da tabela periciada.
        return laudo_tabela

    # 'def' define o método orquestrador que executa a varredura completa em todas as
    # tabelas do diretório.
    # '-> Dict[str, Dict[str, Any]]' documenta que o retorno será um dicionário aninhado
    # mapeando arquivo -> laudo.
    def executar_diagnostico_completo(self) -> dict[str, dict[str, Any]]:
        """Executa a auditoria geral em todos os arquivos CSV presentes na pasta de
        dados brutos.

        Returns:
            Dict[str, Dict[str, Any]]: Dicionário consolidado com o laudo de cada
            entidade do ERP.
        """
        # Emite log marcando o início da perícia geral da Fase 02.
        logging.info("=== INICIANDO FASE 02: DIAGNÓSTICO GERAL DE SAÚDE DOS DADOS ===")

        # 'self.pasta_dados_brutos.glob("*.csv")' pesquisa todos os arquivos com
        # extensão '.csv' no diretório.
        # 'sorted()' ordena a lista alfabeticamente para garantir execução reprodutível
        # e determinística.
        arquivos_csv = sorted(list(self.pasta_dados_brutos.glob("*.csv")))

        # 'if not' faz a checagem defensiva: alerta caso não existam arquivos na pasta
        # de dados brutos.
        if not arquivos_csv:
            logging.error(
                "Nenhum arquivo CSV encontrado para auditoria em: %s",
                self.pasta_dados_brutos,
            )
            raise FileNotFoundError(
                f"Diretório sem arquivos CSV: {self.pasta_dados_brutos.resolve()}"
            )

        # 'relatorio_consolidado' é o dicionário vazio que armazenará os laudos de todas
        # as tabelas.
        relatorio_consolidado: dict[str, dict[str, Any]] = {}

        # 'for' percorre ordenadamente cada caminho de arquivo CSV localizado no pátio
        # de dados brutos.
        for caminho_csv in arquivos_csv:
            # 'caminho_csv.stem' extrai o nome base do arquivo sem a terminação '.csv'
            # (ex.: 'erp_clientes').
            chave_tabela = caminho_csv.stem

            # Executa a auditoria na tabela individual chamando o método especialista
            # anterior.
            laudo_individual = self.auditar_tabela(caminho_csv)

            # Guarda o laudo técnico no dicionário consolidado sob o identificador da
            # tabela.
            relatorio_consolidado[chave_tabela] = laudo_individual

        # Emite log confirmando a conclusão bem-sucedida do diagnóstico macro.
        logging.info(
            "=== FASE 02 (DIAGNÓSTICO GERAL) CONCLUÍDA: %d TABELAS AUDITADAS ===",
            len(relatorio_consolidado),
        )

        # 'return' entrega o relatório consolidado pronto para subsidiar a formulação de
        # hipóteses de negócio.
        return relatorio_consolidado


# '__name__ == "__main__"' permite executar este módulo diretamente via terminal como um
# script Python.
if __name__ == "__main__":
    # '__file__' aponta para este arquivo; '.resolve()' gera o endereço absoluto no
    # sistema de arquivos.
    # Subimos 4 níveis na árvore de pastas: 'fase_02_exploracao' -> 'etapas' -> 'src' ->
    # raiz do repositório.
    raiz_do_projeto = Path(__file__).resolve().parent.parent.parent.parent

    # Aponta para a pasta oficial onde a Fase 01 descarregou os dados delimitados do
    # ERP.
    diretorio_csv_brutos = raiz_do_projeto / "dados" / "brutos" / "csv"

    # Instancia a nossa classe pericial passando o caminho dos dados brutos.
    auditor = AuditorSaudeDados(pasta_dados_brutos=diretorio_csv_brutos)

    # Dispara a execução completa da auditoria macro e captura o laudo final.
    laudo_final = auditor.executar_diagnostico_completo()
