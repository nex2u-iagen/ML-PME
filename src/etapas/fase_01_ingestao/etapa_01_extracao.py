"""Módulo de Orquestração da Ingestão de Dados (Fase 01 - CRISP-DM).

Responsável por orquestrar a carga de dados de ERPs de PMEs, convertendo dumps
estruturais SQL de múltiplos dialetos para arquivos tabulares CSV organizados
em subpastas isoladas com o nome do banco de dados, evitando contaminação.
"""

# 'from pathlib import Path' disponibiliza a manipulação orientada a objetos de pastas no sistema operacional.
from pathlib import Path

# 'from typing import Dict, List' documenta os tipos estáticos formais da biblioteca padrão[cite: 1].
from typing import Dict, List

# 'import logging' gerencia as mensagens de auditoria técnica no console corporativo[cite: 1].
import logging

# 'import re' permite sanitizar o nome da pasta a partir do nome do arquivo SQL.
import re

# 'import pandas as pd' manipula as matrizes tabulares em memória RAM[cite: 1].
import pandas as pd

# 'from sqlalchemy import inspect' importa a ferramenta oficial de introspecção dinâmica de esquemas[cite: 3].
from sqlalchemy import inspect

# Importa o conector relacional universal atualizado do núcleo compartilhado[cite: 1].
from src.nucleo.acesso_dados.conector_banco_relacional import ConectorBancoRelacional

# Importa o leitor defensivo de arquivos tabulares do núcleo compartilhado[cite: 1].
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares

# Importa o resolvedor semântico que casa as tabelas extraídas com as entidades canônicas.
from src.etapas.fase_02_exploracao.adaptadores.resolvedor_semantico import ResolvedorSemantico

# Importa o gerenciador de registro de datasets do núcleo compartilhado.
from src.nucleo.registro_datasets.gerenciador_datasets import GerenciadorDatasets

# 'logging.basicConfig' parametriza a formatação dos registros operacionais no terminal[cite: 1].
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class OrquestradorIngestao' centraliza a coordenação da Fase 1 da esteira[cite: 1].
class OrquestradorIngestao:
    """Classe responsável por coordenar a extração, conversão e isolamento de dados brutos[cite: 1]."""

    # 'def __init__(...)' constrói o orquestrador mapeando os diretórios oficiais de entrada e saída[cite: 1].
    def __init__(self, diretorio_raiz: Path, nome_dataset: str | None = None) -> None:
        """Inicializa o orquestrador configurando os ponteiros de diretórios oficiais[cite: 1].

        Args:
            diretorio_raiz (Path): Caminho absoluto da pasta raiz do projeto de dados[cite: 1].
            nome_dataset (str | None, opcional): Nome do dataset alvo desta execução.
                Quando informado, apenas o dump correspondente é processado e a extração
                é gravada exclusivamente na subpasta deste dataset, evitando a colisão
                entre múltiplas PMEs carregadas.
        """
        # Armazena o endereço físico base do projeto em memória[cite: 1].
        self.diretorio_raiz = diretorio_raiz

        # Aponta para o diretório onde residem os arquivos de backup brutos (.sql)[cite: 1].
        self.pasta_sql = self.diretorio_raiz / "dados" / "brutos" / "sql"

        # Aponta para a raiz do diretório de arquivos delimitados (.csv)[cite: 1].
        self.pasta_csv = self.diretorio_raiz / "dados" / "brutos" / "csv"

        # Armazena o dataset alvo desta execução (None = processa todos os dumps presentes).
        self.nome_dataset = nome_dataset

        # Composição com os especialistas do núcleo compartilhado[cite: 1].
        self.leitor_csv = LeitorArquivosTabulares()
        self.conector_sql = ConectorBancoRelacional(tamanho_lote=50_000)

        # Garante defensivamente que as pastas existam fisicamente no disco[cite: 1].
        self.pasta_sql.mkdir(parents=True, exist_ok=True)
        self.pasta_csv.mkdir(parents=True, exist_ok=True)

        logging.info(
            "Orquestrador de Ingestão ativo. SQL: %s | CSV: %s | Dataset alvo: %s",
            self.pasta_sql.name,
            self.pasta_csv.name,
            self.nome_dataset or "TODOS",
        )

    # 'def _gerar_nome_pasta_banco(...)' extrai um identificador amigável a partir do nome do arquivo SQL.
    def _gerar_nome_pasta_banco(self, nome_arquivo_sql: str) -> str:
        """Limpa o nome do dump removendo carimbos de data para gerar o namespace da pasta.

        Exemplo: 'MERCADO_VENCEDOR_20261005_120000.sql' -> 'mercado_vencedor'.
        """
        nome_base = Path(nome_arquivo_sql).stem.lower()
        # Remove sufixos numéricos típicos de timestamps de backup (_20261005_120000)
        nome_limpo = re.sub(r"_\d{8}(?:_\d+)?$", "", nome_base)
        return nome_limpo if nome_limpo else nome_base

    # 'def executar_fase_ingestao(...)' coordena o ciclo completo da Fase 1 com isolamento de diretório[cite: 1].
    def executar_fase_ingestao(self) -> Dict[str, pd.DataFrame]:
        """Executa o ciclo da Fase 01: descobre, restaura e isola as tabelas do dump em subpasta própria[cite: 1].

        Returns:
            Dict[str, pd.DataFrame]: Dicionário com as tabelas do ERP carregadas na memória RAM[cite: 1].
        """
        logging.info("=== INICIANDO EXECUÇÃO DA FASE 01: INGESTÃO E ISOLAMENTO DE DADOS ===")

        # 1. Varredura dos arquivos de backup SQL (.sql)[cite: 1].
        arquivos_sql_encontrados = list(self.pasta_sql.glob("*.sql"))

        # FILTRO POR DATASET: quando um dataset alvo é informado, descarta os dumps que
        # não correspondem a ele, impedindo que a extração contamine a base de outra PME.
        if self.nome_dataset:
            arquivos_sql_encontrados = [
                arquivo
                for arquivo in arquivos_sql_encontrados
                if self._gerar_nome_pasta_banco(arquivo.name) == self.nome_dataset
            ]
            if not arquivos_sql_encontrados:
                logging.warning(
                    "Nenhum dump SQL corresponde ao dataset '%s'. Verifique o upload em: %s",
                    self.nome_dataset,
                    self.pasta_sql,
                )

        pasta_destino_efetiva = self.pasta_csv

        if arquivos_sql_encontrados:
            for arquivo_sql in arquivos_sql_encontrados:
                # Cria a pasta isolada com o nome do banco de dados (ex.: dados/brutos/csv/mercado_vencedor/)
                nome_subpasta = self._gerar_nome_pasta_banco(arquivo_sql.name)
                pasta_banco_isolada = self.pasta_csv / nome_subpasta
                pasta_banco_isolada.mkdir(parents=True, exist_ok=True)
                pasta_destino_efetiva = pasta_banco_isolada

                logging.info(
                    "Dump identificado: %s. Isolando extração em: %s...",
                    arquivo_sql.name,
                    pasta_banco_isolada.relative_to(self.diretorio_raiz),
                )

                caminho_banco_temp = self.pasta_sql / f"{arquivo_sql.stem}_intermediario.db"

                # Reconstrói a base local SQLite em streaming com o ConectorBancoRelacional
                motor_sql = self.conector_sql.reconstruir_banco_sqlite(
                    caminho_script_sql=arquivo_sql,
                    caminho_banco_sqlite=caminho_banco_temp,
                )

                # Introspecção dinâmica de todas as tabelas contidas no dump[cite: 3]
                inspetor = inspect(motor_sql)
                tabelas_no_banco = inspetor.get_table_names()
                logging.info("Tabelas identificadas no dump (%d entidades): %s", len(tabelas_no_banco), tabelas_no_banco[:5])

                # Exporta cada tabela encontrada exclusivamente para a subpasta isolada do banco[cite: 1, 3]
                for nome_tabela in tabelas_no_banco:
                    caminho_csv = pasta_banco_isolada / f"erp_{nome_tabela.lower()}.csv"
                    self.conector_sql.exportar_tabela_para_csv(
                        motor_banco=motor_sql,
                        nome_tabela=nome_tabela,
                        caminho_csv_destino=caminho_csv,
                    )

        # 2. Varredura das tabelas CSV presentes na pasta isolada[cite: 1]
        arquivos_csv_encontrados = sorted(list(pasta_destino_efetiva.glob("*.csv")))
        tabelas_carregadas: Dict[str, pd.DataFrame] = {}

        for caminho_arquivo in arquivos_csv_encontrados:
            nome_entidade = caminho_arquivo.stem
            dataframe_lido = self.leitor_csv.carregar_tabela(caminho_arquivo)
            tabelas_carregadas[nome_entidade] = dataframe_lido

        logging.info(
            "=== FASE 01 CONCLUÍDA: %d ENTIDADES ISOLADAS EM '%s' ===",
            len(tabelas_carregadas),
            pasta_destino_efetiva.name,
        )

        # 3. ATUALIZAÇÃO DO REGISTRO DE DATASETS (agnosticidade e rastreabilidade):
        # Persiste as entidades descobertas e o resultado do matching semântico para que
        # o frontend consiga exibir a cobertura canônica do dataset e o humano possa
        # ensinar mapeamentos ausentes.
        self._atualizar_registro_dataset(pasta_destino_efetiva, tabelas_carregadas)

        return tabelas_carregadas

    def _atualizar_registro_dataset(self, pasta_dados: Path, tabelas_carregadas: Dict[str, pd.DataFrame]) -> None:
        """Persiste no registro de datasets as entidades descobertas e o matching semântico.

        Args:
            pasta_dados (Path): Pasta onde residem os CSVs extraídos do dataset.
            tabelas_carregadas (Dict[str, pd.DataFrame]): Tabelas carregadas em memória.
        """
        gerenciador = GerenciadorDatasets(diretorio_raiz=self.diretorio_raiz)
        nome_dataset = self.nome_dataset or pasta_dados.name
        registro = gerenciador.obter_ou_criar(nome_dataset)

        # Grava as entidades tabulares efetivamente extraídas.
        registro.tabelas = sorted(tabelas_carregadas.keys())
        registro.marcar_fase("01", "concluida")

        # Executa o matching semântico para mapear as entidades canônicas do negócio.
        resolvedor = ResolvedorSemantico()
        matching: Dict[str, str | None] = {}
        colunas_semanticas: Dict[str, Dict[str, str | None]] = {}

        for entidade_canonica in resolvedor.SINONIMOS_TABELAS:
            caminho_encontrado = resolvedor.localizar_arquivo_tabela(pasta_dados, entidade_canonica)
            matching[entidade_canonica] = caminho_encontrado.stem if caminho_encontrado else None

            if caminho_encontrado:
                cabecalho = list(tabelas_carregadas.get(caminho_encontrado.stem, pd.DataFrame()).columns)
                colunas_semanticas[caminho_encontrado.stem] = {
                    papel: resolvedor.resolver_coluna(cabecalho, papel)
                    for papel in resolvedor.SINONIMOS_COLUNAS
                }

        registro.matching_semantico = matching
        registro.colunas_semanticas = colunas_semanticas

        encontrados = sum(1 for valor in matching.values() if valor)
        registro.registrar_observacao(
            f"Fase 01 concluída: {len(registro.tabelas)} entidades extraídas, "
            f"{encontrados}/{len(matching)} entidades canônicas mapeadas."
        )

        gerenciador.salvar(registro)
        logging.info(
            "Registro do dataset '%s' atualizado — %d/%d entidades canônicas mapeadas.",
            nome_dataset,
            encontrados,
            len(matching),
        )


# Bloco de execução direta caso o arquivo seja chamado isoladamente[cite: 1].
if __name__ == "__main__":
    raiz_do_projeto = Path(__file__).resolve().parent.parent.parent.parent
    orquestrador = OrquestradorIngestao(diretorio_raiz=raiz_do_projeto)
    dados_ingeridos = orquestrador.executar_fase_ingestao()