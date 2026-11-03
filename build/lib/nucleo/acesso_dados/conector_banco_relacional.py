"""Módulo de Conexão Relacional Universal e Extração de Dumps SQL em Streaming (Núcleo).

Responsabilidade Única: Prover interface unificada de comunicação com bancos relacionais,
gerenciando conexões com PostgreSQL, MySQL e SQLite, realizando a sanitização de dialetos
e reconstrução de dumps SQL através de streaming contínuo linha por linha para garantir
consumo estável de memória RAM (O(1)) mesmo em arquivos de grande porte.
"""

from collections.abc import Generator
from pathlib import Path
from typing import Any, Dict, Optional, Union
import logging
import re
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


class ConectorBancoRelacional:
    """Ferramenta especialista em conexões multi-banco e extrações particionadas em lotes."""

    def __init__(self, tamanho_lote: int = 50_000) -> None:
        """Inicializa o conector relacional definindo o tamanho padrão dos lotes em memória.

        Args:
            tamanho_lote (int, opcional): Quantidade de linhas por bloco. Padrão: 50.000.
        """
        self.tamanho_lote = int(tamanho_lote)
        logging.info("Conector relacional inicializado com lote padrão de: %d linhas.", self.tamanho_lote)

    def criar_conexao_banco(
        self,
        driver_banco: str,
        usuario: Optional[str] = None,
        senha: Optional[str] = None,
        host: Optional[str] = "localhost",
        porta: Optional[Union[int, str]] = None,
        nome_banco: Optional[str] = None,
        caminho_sqlite: Optional[Path] = None,
    ) -> Engine:
        """Cria um motor de conexão SQLAlchemy para múltiplos bancos de dados relacionais.

        Args:
            driver_banco (str): Tipo do banco ('postgresql', 'mysql', 'sqlite').
            usuario (Optional[str]): Usuário autenticado.
            senha (Optional[str]): Senha privada de acesso.
            host (Optional[str]): Endereço IP ou hostname. Padrão: 'localhost'.
            porta (Optional[Union[int, str]]): Porta de rede de comunicação.
            nome_banco (Optional[str]): Nome da base de dados relacional.
            caminho_sqlite (Optional[Path]): Caminho físico do arquivo .db para SQLite.

        Returns:
            Engine: Objeto Engine homologado do SQLAlchemy para consultas.
        """
        driver_normalizado = driver_banco.lower().strip()
        logging.info("Configurando motor relacional para o driver: '%s'...", driver_normalizado)

        if driver_normalizado in ["sqlite", "sqlite3"]:
            if caminho_sqlite is None:
                url_conexao = "sqlite:///:memory:"
            else:
                url_conexao = f"sqlite:///{caminho_sqlite.resolve()}"

        elif driver_normalizado in ["postgres", "postgresql", "psycopg2"]:
            porta_efetiva = porta if porta else 5432
            url_conexao = f"postgresql://{usuario}:{senha}@{host}:{porta_efetiva}/{nome_banco}"

        elif driver_normalizado in ["mysql", "mariadb", "pymysql"]:
            porta_efetiva = porta if porta else 3306
            url_conexao = f"mysql+pymysql://{usuario}:{senha}@{host}:{porta_efetiva}/{nome_banco}"

        else:
            raise ValueError(f"Driver '{driver_banco}' não suportado. Use 'postgresql', 'mysql' ou 'sqlite'.")

        return create_engine(url_conexao)

    def _sanitizar_instrucao_individual(self, instrucao_sql: str) -> Optional[str]:
        """Sanitiza uma única instrução SQL pontual para adequação ao dialeto SQLite.

        Args:
            instrucao_sql (str): Comando SQL completo isolado.

        Returns:
            Optional[str]: Instrução limpa pronta para execução ou None se for descartável.
        """
        texto = instrucao_sql.strip()

        # Descarta comandos vazios ou comentários residuais
        if not texto or texto.startswith("--") or texto.startswith("/*"):
            return None

        # Descarta diretivas de sessão e bloqueio exclusivas do MySQL
        padrao_descarte = re.compile(
            r"(?i)^(SET\s+|LOCK\s+TABLES|UNLOCK\s+TABLES|ALTER\s+TABLE\s+.*(?:ENABLE|DISABLE)\s+KEYS)",
            re.DOTALL,
        )
        if padrao_descarte.match(texto):
            return None

        # Sanitizações específicas para comandos CREATE TABLE
        if re.match(r"(?i)^CREATE\s+TABLE", texto):
            # Remove palavras-chave AUTO_INCREMENT e variações de engines MySQL
            texto = re.sub(r"(?i)\bAUTO_INCREMENT\b", "", texto)
            texto = re.sub(r"\)\s*(?:ENGINE|DEFAULT\s+CHARSET|COLLATE|AUTO_INCREMENT|ROW_FORMAT)\s*=[^;]*;", ");", texto, flags=re.IGNORECASE)
            texto = re.sub(r",\s*(?:FULLTEXT\s+|SPATIAL\s+)?KEY\s+[`\w]+\s*\([^)]+\)", "", texto, flags=re.IGNORECASE)
            texto = re.sub(r",\s*INDEX\s+[`\w]+\s*\([^)]+\)", "", texto, flags=re.IGNORECASE)
            texto = re.sub(r",\s*\)", ")", texto)
            texto = re.sub(r"(?i)\b(?:tinyint|smallint|mediumint|int|bigint)\s*\(\d+\)", "INTEGER", texto)
            texto = re.sub(r"(?i)\bSERIAL\s+PRIMARY\s+KEY\b", "INTEGER PRIMARY KEY", texto)
            texto = re.sub(r"(?i)\b(?:datetime|timestamp\s+with(?:out)?\s+time\s+zone)\b", "TEXT", texto)

        # Sanitizações para comandos INSERT INTO
        elif re.match(r"(?i)^INSERT\s+INTO", texto):
            # Converte escape de aspas simples do MySQL (\') para padrão SQL ANSI ('')
            texto = texto.replace(r"\'", "''")

        return texto

    def _gerar_instrucoes_do_arquivo(self, caminho_arquivo_sql: Path) -> Generator[str, None, None]:
        """Lê o arquivo de dump em streaming linha a linha gerando instruções SQL limpas.

        Args:
            caminho_arquivo_sql (Path): Localização física do arquivo de dump .sql.

        Yields:
            str: Instrução SQL completa e compatível com SQLite.
        """
        # Detecta codificação inicial testando leitura da primeira linha
        codificacao = "utf-8"
        try:
            with open(caminho_arquivo_sql, "r", encoding="utf-8") as teste_leitura:
                teste_leitura.readline()
        except UnicodeDecodeError:
            codificacao = "latin1"

        logging.info("Lendo dump SQL em streaming contínuo com codificação '%s'...", codificacao)

        buffer_linhas = []
        em_comentario_multilinha = False

        # Itera linha a linha preservando a memória RAM estável
        with open(caminho_arquivo_sql, "r", encoding=codificacao, errors="replace") as ponteiro:
            for linha in ponteiro:
                linha_formatada = linha.strip()

                if not linha_formatada:
                    continue

                # Ignora blocos de comentários extensos /* ... */
                if linha_formatada.startswith("/*") and not linha_formatada.startswith("/*!"):
                    if "*/" not in linha_formatada:
                        em_comentario_multilinha = True
                        continue
                if em_comentario_multilinha:
                    if "*/" in linha_formatada:
                        em_comentario_multilinha = False
                    continue

                # Ignora comentários simples e condicionais do MySQL
                if linha_formatada.startswith("--") or linha_formatada.startswith("#") or linha_formatada.startswith("/*!"):
                    continue

                buffer_linhas.append(linha)

                # O ponto e vírgula na extremidade direita encerra a instrução SQL
                if linha_formatada.endswith(";"):
                    instrucao_completa = "".join(buffer_linhas)
                    buffer_linhas = []

                    instrucao_limpa = self._sanitizar_instrucao_individual(instrucao_completa)
                    if instrucao_limpa:
                        yield instrucao_limpa

    def reconstruir_banco_sqlite(
        self,
        caminho_script_sql: Path,
        caminho_banco_sqlite: Path,
    ) -> Engine:
        """Restaura o dump SQL em banco SQLite intermediário consumindo fluxo em streaming.

        Args:
            caminho_script_sql (Path): Endereço físico do arquivo de dump .sql.
            caminho_banco_sqlite (Path): Localização do banco SQLite intermediário gerado.

        Returns:
            Engine: Motor de conexão SQLAlchemy pronto para inspeção e extração.
        """
        if not caminho_script_sql.is_file():
            logging.error("Arquivo de dump SQL não localizado: %s", caminho_script_sql)
            raise FileNotFoundError(f"Dump inexistente: {caminho_script_sql.resolve()}")

        logging.info("Iniciando restauração otimizada em streaming: %s", caminho_script_sql.name)

        if caminho_banco_sqlite.is_file():
            caminho_banco_sqlite.unlink()

        # Abre conexão física nativa do SQLite para inicialização de tabelas
        conexao_nativa = sqlite3.connect(str(caminho_banco_sqlite))
        cursor = conexao_nativa.cursor()

        # Pragmas para máxima velocidade de ingestão e controle de memória RAM
        cursor.execute("PRAGMA synchronous = OFF;")
        cursor.execute("PRAGMA journal_mode = OFF;")
        cursor.execute("PRAGMA cache_size = 10000;")
        cursor.execute("PRAGMA temp_store = MEMORY;")

        total_executado = 0
        cursor.execute("BEGIN TRANSACTION;")

        # Consome o gerador streaming executando instrução por instrução
        for comando_sql in self._gerar_instrucoes_do_arquivo(caminho_script_sql):
            try:
                cursor.execute(comando_sql)
                total_executado += 1

                # Consolida lotes de 10.000 instruções para evitar transações infinitas
                if total_executado % 10_000 == 0:
                    conexao_nativa.commit()
                    cursor.execute("BEGIN TRANSACTION;")
                    logging.info("Processadas %d instruções SQL com sucesso na base local...", total_executado)
            except sqlite3.OperationalError as erro_sql:
                # Registra comandos secundários incompatíveis sem abortar a esteira
                logging.debug("Instrução ignorada: %.60s... | Detalhe: %s", comando_sql, erro_sql)

        conexao_nativa.commit()
        conexao_nativa.close()

        logging.info("Restauração concluída! Total de %d instruções processadas.", total_executado)

        url_conexao = f"sqlite:///{caminho_banco_sqlite.resolve()}"
        return create_engine(url_conexao)

    def exportar_tabela_para_csv(
        self,
        motor_banco: Engine,
        nome_tabela: str,
        caminho_csv_destino: Path,
    ) -> Path:
        """Exporta os registros de uma tabela relacional para CSV em lotes contidos de memória.

        Args:
            motor_banco (Engine): Motor de conexão ativo do SQLAlchemy.
            nome_tabela (str): Nome da tabela relacional a ser consultada.
            caminho_csv_destino (Path): Caminho onde o arquivo CSV será salvo.

        Returns:
            Path: Endereço do arquivo CSV gerado.
        """
        consulta_sql = f'SELECT * FROM "{nome_tabela}"'
        if motor_banco.dialect.name == "mysql":
            consulta_sql = f"SELECT * FROM `{nome_tabela}`"

        logging.info("Extraindo tabela '%s' em lotes de %d para '%s'...", nome_tabela, self.tamanho_lote, caminho_csv_destino.name)

        primeiro_lote = True
        total_registros = 0

        for pedaco_df in pd.read_sql(consulta_sql, con=motor_banco, chunksize=self.tamanho_lote):
            modo_escrita = "w" if primeiro_lote else "a"
            pedaco_df.to_csv(
                caminho_csv_destino,
                mode=modo_escrita,
                index=False,
                header=primeiro_lote,
                encoding="utf-8",
            )
            total_registros += len(pedaco_df)
            primeiro_lote = False

        logging.info("Tabela '%s' convertida com êxito para CSV (%d registros).", nome_tabela, total_registros)
        return caminho_csv_destino

    def consultar_tabela(
        self,
        motor_banco: Engine,
        consulta_sql: str,
    ) -> pd.DataFrame:
        """Executa instrução SQL direta e retorna DataFrame para análise exploratória.

        Args:
            motor_banco (Engine): Motor de conexão ativo do SQLAlchemy.
            consulta_sql (str): Instrução SQL a ser executada.

        Returns:
            pd.DataFrame: Resultado tabular em memória.
        """
        logging.info("Executando consulta SQL analítica através do conector...")
        return pd.read_sql(consulta_sql, con=motor_banco)