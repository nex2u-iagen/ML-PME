"""Módulo de Acesso e Manipulação de Arquivos Tabulares.

Este arquivo implementa a leitura física de arquivos delimitados (CSV),
fornecendo suporte tanto para cargas completas em memória quanto para
leitura fracionada em fluxo contínuo (streaming em lotes).
"""

# 'from' indica a biblioteca de origem; 'collections.abc' contém classes abstratas de
# coleções do Python.
# 'import' traz para o arquivo a ferramenta 'Generator' (Gerador).
# Um gerador é uma função especial que pausa e retoma sua execução, entregando um pedaço
# de dados por vez.
# 'import' traz o módulo 'logging' da biblioteca padrão do Python.
# O logging serve para emitir avisos, mensagens de sucesso e erros no terminal de forma
# rastreável e profissional.
import logging
from collections.abc import Generator

# 'from' acessa a biblioteca padrão 'pathlib' (especialista em manipulação de diretórios
# e arquivos).
# 'import' carrega a classe 'Path' para representar caminhos no Windows, Linux ou Mac de
# modo orientado a objetos.
from pathlib import Path

# 'import' traz a biblioteca externa 'pandas', a principal ferramenta de manipulação de
# dados tabulares do Python.
# 'as' cria o apelido reduzido 'pd', padrão internacional adotado pela comunidade de
# dados.
import pandas as pd

# 'logging.basicConfig' define o formato visual dos registros de log no terminal.
# 'level=logging.INFO' configura para exibir mensagens informativas, avisos e erros
# críticos.
# 'format' define a máscara de texto: data/hora atual — [nível do alerta] — mensagem
# descritiva.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' é a palavra-chave que declara uma nova classe de objetos.
# 'LeitorArquivosTabulares' é o nome da nossa classe em PascalCase (iniciais
# maiúsculas), indicando sua responsabilidade.
# Esta classe implementa o contrato que definimos anteriormente no arquivo de
# protocolos.
class LeitorArquivosTabulares:
    """Classe responsável pela leitura, validação e fatiamento de dados em disco."""

    # 'def' define o método 'carregar_tabela'.
    # 'self' referencia a própria instância da classe para que ela acerte suas funções
    # internas.
    # 'caminho_arquivo: Path' exige que o argumento seja um objeto Path apontando para o
    # arquivo físico.
    # 'delimitador: str = ","' define uma string como separador de colunas, assumindo a
    # vírgula como padrão.
    # '-> pd.DataFrame' documenta que a função devolverá uma tabela de dados estruturada
    # do pandas.
    def carregar_tabela(
        self,
        caminho_arquivo: Path,
        delimitador: str = ",",
    ) -> pd.DataFrame:
        """Carrega um arquivo delimitado integralmente para a memória principal.

        Args:
            caminho_arquivo (Path): O endereço físico do arquivo no computador.
            delimitador (str, opcional): Caractere separador de campos. Padrão é ','.

        Returns:
            pd.DataFrame: Conjunto de dados carregado em formato de tabela
            bidimensional.

        Raises:
            FileNotFoundError: Se o arquivo especificado não existir no disco.
        """
        # 'if' avalia uma condição booleana (Verdadeiro ou Falso).
        # 'not' inverte o valor lógico: se o arquivo NÃO existir, a expressão se torna
        # Verdadeira.
        # 'caminho_arquivo.is_file()' testa fisicamente se o caminho aponta para um
        # arquivo existente.
        if not caminho_arquivo.is_file():
            # 'logging.error' registra no terminal em nível de erro que o arquivo não
            # foi localizado.
            logging.error("Arquivo não localizado no disco: %s", caminho_arquivo)
            # 'raise' interrompe o programa imediatamente e lança uma exceção formal do
            # tipo FileNotFoundError.
            # 'caminho_arquivo.resolve()' converte o caminho relativo em um caminho
            # absoluto completo do sistema.
            raise FileNotFoundError(f"Arquivo inexistente: {caminho_arquivo.resolve()}")

        # 'logging.info' informa que a validação passou e o carregamento do arquivo
        # começou.
        # 'caminho_arquivo.name' extrai apenas o nome final do arquivo (ex.:
        # 'vendas.csv'), sem a pasta inteira.
        logging.info("Carregando arquivo tabular: %s", caminho_arquivo.name)

        # 'pd.read_csv' lê o arquivo do disco e transforma os registros de texto em um
        # DataFrame.
        # 'return' devolve a tabela recém-criada para quem chamou a função.
        return pd.read_csv(caminho_arquivo, sep=delimitador)

    # 'def' inicia a declaração do método focado em arquivos massivos (leitura em fluxo
    # contínuo).
    # 'tamanho_lote: int = 50_000' define um número inteiro padrão de 50 mil linhas
    # lidas por vez.
    # O sublinhado '50_000' é um recurso visual do Python para facilitar a leitura
    # humana de números grandes.
    # '-> Generator[pd.DataFrame, None, None]' indica que a função é um gerador que
    # entrega DataFrames parciais.
    def carregar_em_lotes(
        self,
        caminho_arquivo: Path,
        tamanho_lote: int = 50_000,
        delimitador: str = ",",
    ) -> Generator[pd.DataFrame, None, None]:
        """Lê arquivos massivos de forma fracionada através de geradores em memória.

        Args:
            caminho_arquivo (Path): Endereço físico do arquivo delimitado.
            tamanho_lote (int, opcional): Quantidade de linhas por lote. Padrão: 50.000.
            delimitador (str, opcional): Caractere separador de colunas. Padrão: ','.

        Yields:
            pd.DataFrame: Fragmento tabular (chunk) contendo o volume de linhas
            estipulado.

        Raises:
            FileNotFoundError: Se o arquivo não existir fisicamente no disco.
        """
        # Checagem defensiva: confirma se o arquivo massivo realmente existe antes de
        # abrir o cursor de leitura.
        if not caminho_arquivo.is_file():
            # Registro de log de falha de localização de arquivo.
            logging.error("Arquivo para streaming não localizado: %s", caminho_arquivo)
            # Interrompe o processo lançando a exceção de arquivo não encontrado.
            raise FileNotFoundError(f"Arquivo inexistente: {caminho_arquivo.resolve()}")

        # Emite um log informativo informando a quantidade de linhas configuradas por
        # lote.
        logging.info(
            "Iniciando streaming em blocos (%d registros por lote): %s",
            tamanho_lote,
            caminho_arquivo.name,
        )

        # 'pd.read_csv' com 'chunksize' não carrega o arquivo todo de uma vez na memória
        # RAM.
        # Ele cria um 'TextFileReader' (leitor iterável) que mantém o arquivo aberto no
        # disco.
        iterador_tabela = pd.read_csv(
            caminho_arquivo,
            sep=delimitador,
            chunksize=tamanho_lote,
        )

        # 'for' cria um laço de repetição que percorre cada bloco entregue pelo leitor.
        # 'enumerate(..., start=1)' numera cada passagem do laço começando do número 1.
        # 'indice_bloco' é uma variável numérica inteira (1, 2, 3...) que conta qual
        # lote está saindo.
        # 'pedaco_dados' é uma variável do tipo DataFrame contendo as 50.000 linhas
        # daquele lote específico.
        for indice_bloco, pedaco_dados in enumerate(iterador_tabela, start=1):
            # 'logging.debug' grava uma mensagem detalhada de depuração interna
            # indicando o lote atual.
            logging.debug("Bloco número %d emitido com sucesso.", indice_bloco)
            # 'yield' é a palavra-chave central dos geradores em Python.
            # Ao contrário do 'return' (que encerra a função), o 'yield' entrega o lote
            # atual para quem pediu,
            # pausa a execução e guarda o ponto exato onde parou, liberando a memória
            # RAM logo em seguida.
            yield pedaco_dados
