"""Módulo do Conector Analítico DuckDB (Núcleo de Acesso a Dados).

Responsabilidade Única: Prover uma sessão analítica embutida e colunar de alto
desempenho para consulta e transformação de dados tabulares sem esgotamento de memória.
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro de auditoria operacional.
import logging

# 'from' acessa a biblioteca nativa 'pathlib'; 'import' traz 'Path' para manipulação segura de rotas físicas.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão para documentação de tipos estáticos formais[cite: 12].
from typing import Any, Optional

# 'import' traz a biblioteca externa 'duckdb', motor OLAP analítico colunar de altíssima performance.
import duckdb

# 'import' traz a biblioteca externa 'pandas' para intercâmbio de estruturas tabulares em memória RAM[cite: 12].
# 'as' estabelece o apelido oficial 'pd' padronizado na Ciência de Dados.
import pandas as pd

# 'logging.basicConfig' parametriza a formatação visual e a criticidade dos registros de auditoria no terminal[cite: 12].
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara o molde arquitetural orientado a objetos responsável pelo acesso analítico colunar[cite: 12].
class ConectorAnaliticoDuckDB:
    """Ferramenta especialista do núcleo para execução de consultas vetorizadas via DuckDB."""

    # 'def' define o método especial construtor '__init__', acionado ao instanciar o conector na memória RAM[cite: 12].
    # 'self' referencia a própria instância para vincular atributos e conexões em memória RAM[cite: 12].
    # 'pasta_dados: Path' recebe o endereço físico onde repousam os arquivos tabulares extraídos[cite: 12].
    # 'limite_memoria_ram: str' define o teto operacional de memória RAM (padrão de 4GB para evitar panes OOM).
    # '*args' e '**kwargs' fornecem blindagem defensiva para capturar variações de nomenclatura de argumentos[cite: 12].
    def __init__(
        self,
        pasta_dados: Optional[Path] = None,
        limite_memoria_ram: str = "4GB",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Inicializa o conector analítico em memória com ancoragem automática de subpastas do cliente[cite: 12].

        Args:
            pasta_dados (Optional[Path]): Diretório contendo os arquivos CSVs reais do banco de dados[cite: 12].
            limite_memoria_ram (str, opcional): Limite estrito de alocação de memória RAM. Padrão: '4GB'.
            *args: Argumentos posicionais capturados defensivamente[cite: 12].
            **kwargs: Argumentos nomeados capturados defensivamente (ex.: pasta_banco_dados, pasta_dados_banco)[cite: 12].
        """
        # RESOLUÇÃO DEFENSIVA DE ARGUMENTOS:
        # Se 'pasta_dados' não for fornecido posicionalmente, busca nas chaves alternativas aceitas[cite: 12].
        caminho_recebido = (
            pasta_dados
            or kwargs.get("pasta_banco_dados")
            or kwargs.get("pasta_dados_banco")
            or (args[0] if len(args) > 0 else None)
        )

        # Se nenhum caminho válido foi localizado, levanta erro informativo de configuração[cite: 12].
        if caminho_recebido is None:
            raise ValueError(
                "ConectorAnaliticoDuckDB: O diretório de dados do banco deve ser fornecido obrigatoriamente."
            )

        # Converte o caminho garantindo a tipagem segura de objeto Path[cite: 12].
        self.pasta_dados = Path(caminho_recebido)

        # RESOLUÇÃO DEFENSIVA DE SUBPASTAS:
        # Verifica se o diretório recebido contém subpastas isoladas de clientes (ex.: 'mercado_vencedor/')[cite: 12].
        subpastas_detectadas = [
            p
            for p in self.pasta_dados.iterdir()
            if p.is_dir() and not p.name.startswith(".") and p.name != "mocks"
        ]

        # Se houver uma subpasta de banco de dados isolada, ancora a esteira de consultas diretamente nela[cite: 12].
        if subpastas_detectadas:
            self.pasta_dados = subpastas_detectadas[0]

        # Extrai o nome canônico do cliente ou banco para inclusão nos laudos de rastreabilidade[cite: 12].
        self.nome_cliente = self.pasta_dados.name

        # Inicializa a conexão analítica nativa em memória RAM rápida (:memory:) sem arquivos de lock[cite: 12].
        self.conexao = duckdb.connect(database=":memory:")

        # Configura a alocação de threads paralelas para consumir eficientemente múltiplos núcleos da CPU.
        self.conexao.execute("SET threads TO 4;")

        # Habilita o teto de consumo de memória RAM, blindando o sistema operacional contra travamentos.
        self.conexao.execute(f"SET max_memory = '{limite_memoria_ram}';")

        # Emite log no console confirmando a ativação bem-sucedida do motor analítico colunar[cite: 12].
        logging.info(
            "Conector DuckDB ativo para o cliente: '%s' (Limite: %s)",
            self.nome_cliente,
            limite_memoria_ram,
        )

    # 'def' define o método executor de instruções SQL analíticas genéricas sobre arquivos delimitados[cite: 12].
    def consultar_sql(self, sql_query: str) -> pd.DataFrame:
        """Executa comandos SQL ANSI diretamente sobre os arquivos CSV sem cópias intermediárias na memória RAM[cite: 12].

        Args:
            sql_query (str): Instrução SQL analítica formatada com a marcação '{PASTA_CSV}'[cite: 12].

        Returns:
            pd.DataFrame: Resultado tabular consolidado pronto para visualização gráfica ou modelagem de ML[cite: 12].
        """
        # Substitui a marcação coringa '{PASTA_CSV}' pelo caminho físico absoluto resolvido no disco[cite: 12].
        sql_resolvido = sql_query.replace(
            "{PASTA_CSV}", str(self.pasta_dados.resolve())
        )

        # Executa a consulta vetorizada no motor DuckDB e converte a resposta diretamente para pandas DataFrame[cite: 12].
        return self.conexao.execute(sql_resolvido).df()

    # 'def' define o método especialista em fechar graciosamente os recursos da sessão analítica[cite: 12].
    def encerrar_conexao(self) -> None:
        """Fecha a conexão analítica liberando as estruturas alocadas em memória RAM[cite: 12]."""
        # Invoca o método de fechamento da biblioteca DuckDB[cite: 12].
        self.conexao.close()
        # Emite registro confirmando o encerramento seguro da sessão[cite: 12].
        logging.info("Sessão analítica do DuckDB encerrada com sucesso.")