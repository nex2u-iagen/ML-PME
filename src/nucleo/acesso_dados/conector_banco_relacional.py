"""Módulo de Conexão Relacional e Extração de Dumps SQL.

Responsável por reconstruir a estrutura de bancos relacionais locais
a partir de arquivos de dump (.sql) de ERPs e exportar tabelas volumosas
de forma particionada via SQLAlchemy e pandas.
"""

# 'import' traz a biblioteca interna 'logging' para registrar mensagens de execução no
# terminal.
import logging

# 'import' traz a biblioteca nativa 'sqlite3', que permite criar bancos de dados
# relacionais em arquivo local.
import sqlite3

# 'from' acessa o módulo 'pathlib' da biblioteca padrão do Python.
# 'import' traz a classe 'Path' para manipulação segura de caminhos entre sistemas
# operacionais.
from pathlib import Path

# 'import' traz o 'pandas', biblioteca padrão para estruturar e processar matrizes e
# tabelas de dados.
# 'as' define o apelido reduzido 'pd' para economizar digitação no código.
import pandas as pd

# 'from' acessa a biblioteca externa 'sqlalchemy', o padrão da indústria para
# comunicação com bancos de dados.
# 'create_engine' é a função que cria o motor (ponte) de comunicação entre o Python e o
# banco relacional.
from sqlalchemy import create_engine

# 'Engine' é a anotação de tipo (Type Hint) que representa o objeto do motor de conexão
# ativo do SQLAlchemy.
from sqlalchemy.engine import Engine

# 'logging.basicConfig' parametriza a saída dos logs informativos no terminal.
# 'level=logging.INFO' garante que avisos gerais, alertas e erros sejam exibidos.
# 'format' padroniza a mensagem: hora exata, gravidade do log e a descrição do que está
# acontecendo.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara a criação de um molde orientado a objetos.
# 'ConectorBancoRelacional' é o nome da nossa classe, focado em responsabilidade única
# (coesão com bancos SQL).
class ConectorBancoRelacional:
    """Classe responsável por restaurar esquemas SQL e extrair dados em lotes."""

    # 'def' define o método construtor '__init__', executado no instante em que a classe
    # é instanciada.
    # 'self' representa o próprio objeto acessando suas propriedades internas.
    # 'tamanho_lote: int = 50_000' define que o lote padrão terá 50 mil linhas (número
    # inteiro).
    # '-> None' documenta que o método construtor não retorna nenhum dado.
    def __init__(self, tamanho_lote: int = 50_000) -> None:
        """Inicializa a classe configurando o tamanho de lote padrão para extrações.

        Args:
            tamanho_lote (int, opcional): Quantidade de linhas por bloco. Padrão:
            50.000.
        """
        # 'self.tamanho_lote' armazena o valor recebido dentro da memória interna do
        # próprio objeto.
        self.tamanho_lote = tamanho_lote

        # 'logging.info' emite um aviso no terminal informando que o conector foi
        # iniciado com sucesso.
        logging.info(
            "Conector relacional inicializado com lote de: %d linhas.",
            self.tamanho_lote,
        )

    # 'def' cria o método responsável por pegar o script de texto .sql e transformá-lo
    # em um banco SQLite.
    # 'caminho_script_sql: Path' exige o caminho onde o arquivo de backup .sql está
    # salvo.
    # 'caminho_banco_sqlite: Path' exige o caminho onde o novo arquivo de banco (.db)
    # será construído.
    # '-> Engine' avisa que o retorno será um motor pronto de conexão do SQLAlchemy.
    def reconstruir_banco_sqlite(
        self,
        caminho_script_sql: Path,
        caminho_banco_sqlite: Path,
    ) -> Engine:
        """Executa um dump SQL completo e instancia um banco de dados relacional SQLite
        local.

        Args:
            caminho_script_sql (Path): Caminho do arquivo .sql bruto contendo comandos
            DDL/DML.
            caminho_banco_sqlite (Path): Caminho do arquivo .db local a ser gerado.

        Returns:
            Engine: Motor de conexão SQLAlchemy pronto para consultas.

        Raises:
            FileNotFoundError: Se o arquivo .sql original não for localizado no disco.
            sqlite3.OperationalError: Se o script contiver comandos corrompidos ou
            sintaxe SQL inválida.
        """
        # 'if not' faz o teste defensivo: confere se o arquivo .sql realmente existe
        # antes de tentar lê-lo.
        if not caminho_script_sql.is_file():
            # Registra no log a falha de localização do dump.
            logging.error("Arquivo de dump SQL não encontrado: %s", caminho_script_sql)
            # Lança uma exceção formal interrompendo a rotina com uma mensagem
            # explicativa.
            raise FileNotFoundError(
                f"Dump SQL inexistente: {caminho_script_sql.resolve()}"
            )

        # Informa no terminal que a restauração física do banco foi iniciada.
        logging.info(
            "Reconstruindo banco de dados a partir do dump: %s", caminho_script_sql.name
        )

        # 'try' abre um bloco de captura protegida contra falhas operacionais do banco
        # de dados.
        try:
            # 'with' é um gerenciador de contexto: abre a conexão com o SQLite e fecha
            # automaticamente ao terminar.
            # 'sqlite3.connect' cria ou abre o arquivo físico de banco de dados no disco
            # rígido.
            with sqlite3.connect(caminho_banco_sqlite) as conexao_nativa:
                # 'with open' abre o arquivo de texto .sql em modo de leitura com
                # codificação padrão universal UTF-8.
                with open(caminho_script_sql, encoding="utf-8") as ponteiro_arquivo:
                    # 'ponteiro_arquivo.read()' extrai todo o texto contendo os comandos
                    # SQL do ERP.
                    conteudo_sql = ponteiro_arquivo.read()
                    # 'conexao_nativa.executescript' processa todas as tabelas e
                    # inserções descritas no texto.
                    conexao_nativa.executescript(conteudo_sql)

        # 'except' captura especificamente erros operacionais do motor SQLite (sintaxe
        # errada, tipos inválidos).
        except sqlite3.OperationalError as erro_sql:
            # Emite log com a descrição da falha gerada pelo banco.
            logging.error("Falha ao executar comandos DDL/DML no SQLite: %s", erro_sql)
            # Relança o erro para alertar o desenvolvedor de que o script precisa de
            # correção.
            raise erro_sql

        # Log informando que o banco de dados foi construído com sucesso no disco.
        logging.info(
            "Banco SQLite intermediário criado com sucesso em: %s",
            caminho_banco_sqlite.name,
        )

        # Monta a URL de conexão no padrão exigido pelo SQLAlchemy para SQLite local ('sqlite:///caminho').
        url_conexao = f"sqlite:///{caminho_banco_sqlite.resolve()}"

        # 'create_engine' instancia o motor do SQLAlchemy utilizando a URL
        # recém-construída.
        motor_banco = create_engine(url_conexao)

        # 'return' entrega o motor pronto para que outras funções possam executar
        # consultas.
        return motor_banco

    # 'def' define o método especialista em retirar uma tabela específica do banco e
    # convertê-la em CSV.
    # 'motor_banco: Engine' recebe o motor do SQLAlchemy criado pelo método anterior.
    # 'nome_tabela: str' exige uma string com o nome da tabela no banco (ex.:
    # 'pedidos_venda').
    # 'caminho_csv_destino: Path' é o endereço final do arquivo .csv que será gravado no
    # disco.
    # '-> Path' devolve o caminho do arquivo gerado para auditoria.
    def exportar_tabela_para_csv(
        self,
        motor_banco: Engine,
        nome_tabela: str,
        caminho_csv_destino: Path,
    ) -> Path:
        """Exporta os registros de uma tabela relacional para CSV de modo particionado
        em lotes.

        Args:
            motor_banco (Engine): Motor de conexão ativo do SQLAlchemy.
            nome_tabela (str): Nome da tabela relacional a ser consultada.
            caminho_csv_destino (Path): Caminho onde o arquivo CSV será salvo.

        Returns:
            Path: Endereço do arquivo CSV gerado.
        """
        # Monta a consulta SQL em texto buscando todas as colunas da tabela indicada.
        # Consulta interna e controlada: o nome da tabela vem da allowlist do conector.
        consulta_sql = f"SELECT * FROM {nome_tabela}"

        # Log informativo sobre a tabela e o destino do arquivo.
        logging.info(
            "Extraindo tabela '%s' em lotes de %d para '%s'...",
            nome_tabela,
            self.tamanho_lote,
            caminho_csv_destino.name,
        )

        # Variável booleana (True/False) usada como marcador para controlar a criação do
        # cabeçalho do CSV.
        primeiro_lote = True

        # 'pd.read_sql' com 'chunksize' executa a consulta de forma paginada via cursor
        # do banco.
        # Ele devolve um bloco de dados por vez em vez de carregar milhões de linhas na
        # memória RAM.
        for pedaco_df in pd.read_sql(
            consulta_sql, con=motor_banco, chunksize=self.tamanho_lote
        ):
            # 'modo_escrita': no primeiro lote usamos 'w' (write / escrever novo); nos
            # outros usamos 'a' (append / anexar).
            modo_escrita = "w" if primeiro_lote else "a"

            # 'pedaco_df.to_csv' grava o pedaço tabular diretamente no arquivo físico.
            # 'index=False' impede que o pandas crie uma coluna extra de números
            # desnecessária no arquivo.
            # 'header=primeiro_lote' escreve os nomes das colunas apenas na primeira vez
            # que o arquivo é aberto.
            pedaco_df.to_csv(
                caminho_csv_destino,
                mode=modo_escrita,
                index=False,
                header=primeiro_lote,
            )

            # Atualiza o marcador para False, garantindo que os próximos blocos não
            # repitam o cabeçalho.
            primeiro_lote = False

        # Emite log confirmando a conclusão da extração sem esgotamento de memória.
        logging.info("Tabela '%s' convertida com êxito para CSV.", nome_tabela)

        # Devolve o caminho do arquivo gerado para controle do pipeline.
        return caminho_csv_destino

    # 'def' define o método para consultas pontuais rápidas (ex.: verificar a contagem
    # de clientes).
    # 'consulta_sql: str' recebe a instrução SQL escrita em texto.
    # '-> pd.DataFrame' documenta que o retorno será uma tabela do pandas.
    def consultar_tabela(
        self,
        motor_banco: Engine,
        consulta_sql: str,
    ) -> pd.DataFrame:
        """Executa uma instrução SQL direta e retorna o resultado em um DataFrame.

        Args:
            motor_banco (Engine): Motor de conexão ativo do SQLAlchemy.
            consulta_sql (str): Comando SQL a ser executado.

        Returns:
            pd.DataFrame: Resultado tabular da consulta.
        """
        # Emite log registrando o início da consulta direta.
        logging.info("Executando consulta analítica direta no banco de dados...")

        # 'pd.read_sql' executa a consulta através do motor e devolve um DataFrame
        # pronto para análise exploratória.
        return pd.read_sql(consulta_sql, con=motor_banco)
