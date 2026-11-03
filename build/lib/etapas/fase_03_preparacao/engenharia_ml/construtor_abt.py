"""Módulo Construtor da Tabela Analítica de Modelagem (ABT - Fase 3.2).

Responsabilidade Única: Descobrir dinamicamente os nomes das colunas de ERPs,
cruzar entidades relacionais via DuckDB colunar e consolidar a Tabela Base Analítica (ABT)
no grão de clientes para classificação de risco e crédito com tolerância a variações de esquema.
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro estruturado no console.
import logging

# 'from' acessa a biblioteca nativa 'pathlib'; 'import' traz 'Path' para manipulação segura de diretórios.
from pathlib import Path

# 'from' acessa o módulo 'typing' da biblioteca padrão para anotação estática rigorosa de métodos.
from typing import List, Optional

# 'import' traz a biblioteca externa 'pandas' para leitura ultra-rápida de metadados e manipulação tabular.
# 'as' define o apelido oficial 'pd' padronizado na Ciência de Dados.
import pandas as pd

# 'from' importa o conector analítico colunar do núcleo compartilhado de acesso a dados.
from src.nucleo.acesso_dados.conector_analitico_duckdb import (
    ConectorAnaliticoDuckDB,
)

# 'logging.basicConfig' parametriza a formatação visual e os carimbos de auditoria exibidos no terminal.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara o molde arquitetural responsável pela consolidação dinâmica da ABT de Machine Learning.
class ConstrutorABTCliente:
    """Classe responsável pela descoberta dinâmica de esquemas e montagem resiliente da ABT via DuckDB."""

    # 'def' define o método construtor '__init__', acionado ao instanciar o construtor na memória RAM.
    # 'self' referencia a própria instância para vincular atributos internos e sessões analíticas.
    # 'pasta_dados_banco: Path' recebe o diretório onde repousam os arquivos CSVs do cliente sob análise.
    def __init__(self, pasta_dados_banco: Path) -> None:
        """Inicializa o construtor de ABT vinculando o motor DuckDB à pasta de arquivos do cliente.

        Args:
            pasta_dados_banco (Path): Diretório físico contendo os arquivos tabulares extraídos do ERP.
        """
        # Converte e armazena o caminho recebido garantindo a tipagem segura de objeto Path.
        self.pasta_dados = Path(pasta_dados_banco)

        # Instancia o motor analítico colunar do núcleo utilizando o construtor defensivo flexível.
        self.motor_duckdb = ConectorAnaliticoDuckDB(pasta_dados=self.pasta_dados)

        # Emite registro no console confirmando a ativação bem-sucedida do construtor.
        logging.info("Construtor de ABT inicializado para a base em: %s", self.pasta_dados.resolve())

    # 'def' define o método utilitário que inspeciona o cabeçalho de um arquivo CSV em menos de 1 milissegundo.
    def _obter_colunas_arquivo(self, nome_arquivo_csv: str) -> List[str]:
        """Lê estritamente a linha de cabeçalho do arquivo CSV para mapear os nomes reais das colunas.

        Args:
            nome_arquivo_csv (str): Nome do arquivo a ser inspecionado (ex.: 'erp_contasreceber.csv').

        Returns:
            List[str]: Lista contendo os nomes das colunas identificadas no arquivo físico.
        """
        # Monta o caminho direto do arquivo dentro da pasta oficial de dados do cliente.
        caminho_arquivo = self.pasta_dados / nome_arquivo_csv

        # Se o arquivo não existir diretamente na raiz da pasta, busca defensivamente em subníveis.
        if not caminho_arquivo.is_file():
            arquivos_encontrados = list(self.pasta_dados.glob(f"**/{nome_arquivo_csv}"))
            if arquivos_encontrados:
                caminho_arquivo = arquivos_encontrados[0]
            else:
                logging.warning("Arquivo '%s' não localizado para inspeção de cabeçalho.", nome_arquivo_csv)
                return []

        try:
            # 'pd.read_csv(..., nrows=0)' carrega zero linhas de dados, extraindo apenas os nomes dos campos.
            colunas_identificadas = list(pd.read_csv(caminho_arquivo, nrows=0).columns)
            logging.info("Cabeçalho de '%s' mapeado com %d colunas.", nome_arquivo_csv, len(colunas_identificadas))
            return colunas_identificadas
        except Exception as erro_leitura:
            logging.error("Falha ao ler cabeçalho de '%s': %s", nome_arquivo_csv, erro_leitura)
            return []

    # 'def' define o algoritmo pericial que casa termos conceituais de negócio com os nomes reais das colunas.
    @staticmethod
    def _casar_coluna(colunas_existentes: List[str], candidatos_sinonimos: List[str]) -> Optional[str]:
        """Compara a lista de colunas reais contra uma lista prioritária de termos equivalentes.

        Args:
            colunas_existentes (List[str]): Lista de cabeçalhos reais presentes no arquivo CSV.
            candidatos_sinonimos (List[str]): Termos conhecidos ordenados por relevância técnica.

        Returns:
            Optional[str]: O nome exato da coluna encontrada no arquivo ou None caso ausente.
        """
        # Cria um mapa auxiliar em minúsculas para permitir comparação insensível a maiúsculas e minúsculas.
        mapa_colunas_lower = {str(c).strip().lower(): c for c in colunas_existentes}

        # Prioridade 1: Correspondência exata normalizada.
        for termo in candidatos_sinonimos:
            termo_lower = str(termo).strip().lower()
            if termo_lower in mapa_colunas_lower:
                return mapa_colunas_lower[termo_lower]

        # Prioridade 2: Correspondência bidirecional por contenção (ex.: 'datapagto' encontra 'DataPagto').
        for termo in candidatos_sinonimos:
            termo_lower = str(termo).strip().lower()
            for col_lower, col_original in mapa_colunas_lower.items():
                if termo_lower in col_lower or col_lower in termo_lower:
                    return col_original

        return None

    # 'def' define a função principal que constrói a Tabela Analítica de Modelagem (ABT).
    def construir_abt_credito_cliente(self) -> pd.DataFrame:
        """Monta dinamicamente a consulta SQL analítica e gera a ABT consolidada por cliente via DuckDB.

        Returns:
            pd.DataFrame: Tabela plana de modelagem contendo atributos comportamentais e o alvo inadimplente.
        """
        logging.info("Iniciando descoberta dinâmica de esquema para a construção da ABT de Crédito...")

        # 1. MAPEAMENTO DINÂMICO DE COLUNAS EM 'erp_contasreceber.csv'
        colunas_cr = self._obter_colunas_arquivo("erp_contasreceber.csv")

        # Resolve o identificador do cliente com suporte a 'idpessoaautorizada' detectado no log.
        col_id_cli = self._casar_coluna(
            colunas_cr,
            ["idpessoaautorizada", "idpessoa", "id_pessoa", "idcliente", "id_cliente", "cod_cliente", "idpagrec", "id"],
        )

        # Resolve a chave do título financeiro.
        col_id_titulo = self._casar_coluna(
            colunas_cr, ["id", "id_titulo", "idcontasreceber", "idpagrec", "iddocumento", "codigo"]
        )

        # Resolve a coluna de valor financeiro.
        col_valor = self._casar_coluna(
            colunas_cr, ["valororiginal", "valortotal", "valor_total", "valor", "vltotal"]
        )

        # Resolve a data de vencimento do título.
        col_venc = self._casar_coluna(
            colunas_cr, ["vencimento", "datavencimento", "data_vencimento", "dtvencimento", "dtvenc"]
        )

        # Resolve a data de pagamento com suporte a 'DataPagto' revelado pelo Binder Error do DuckDB!
        col_pagto = self._casar_coluna(
            colunas_cr,
            ["datapagto", "data_pagto", "datapagamento", "data_pagamento", "dtpagamento", "dtpagto", "pagto", "liquidacao", "datapago"],
        )

        # Resolve o status descritivo da cobrança.
        col_status = self._casar_coluna(
            colunas_cr, ["statuscobranca", "status_cobranca", "status", "situacao", "situacaocobranca"]
        )

        logging.info(
            "Mapeamento Contas a Receber -> Cliente: '%s' | Título: '%s' | Valor: '%s' | Vencimento: '%s' | Pagto: '%s'",
            col_id_cli, col_id_titulo, col_valor, col_venc, col_pagto,
        )

        # GERAÇÃO DEFENSIVA DE EXPRESSÕES SQL:
        # Se uma coluna opcional não existir no arquivo CSV físico, gera literais seguros em vez de provocar Binder Error.
        expr_id_titulo = f'TRY_CAST("{col_id_titulo}" AS INTEGER)' if col_id_titulo else 'ROW_NUMBER() OVER ()'
        expr_id_cli = f'TRY_CAST("{col_id_cli}" AS INTEGER)' if col_id_cli else 'CAST(NULL AS INTEGER)'
        expr_valor = f'TRY_CAST("{col_valor}" AS DOUBLE)' if col_valor else '0.0'
        expr_venc = f'TRY_CAST("{col_venc}" AS DATE)' if col_venc else 'CAST(NULL AS DATE)'
        expr_pagto = f'TRY_CAST("{col_pagto}" AS DATE)' if col_pagto else 'CAST(NULL AS DATE)'
        expr_status = f'COALESCE(CAST("{col_status}" AS VARCHAR), \'Aberto\')' if col_status else "'Aberto'"
        where_valor = f'"{col_valor}" IS NOT NULL AND TRY_CAST("{col_valor}" AS DOUBLE) > 0' if col_valor else '1=1'

        # 2. MAPEAMENTO DINÂMICO DE COLUNAS EM 'erp_pessoas.csv'
        colunas_pes = self._obter_colunas_arquivo("erp_pessoas.csv")

        col_pes_id = self._casar_coluna(
            colunas_pes, ["id", "idpessoa", "id_pessoa", "idcliente", "codigo"]
        ) or "ID"

        col_pes_nome = self._casar_coluna(
            colunas_pes, ["nomerazao", "nome_razao", "nomefantasia", "nome", "razao_social"]
        )

        col_pes_cidade = self._casar_coluna(
            colunas_pes, ["cidade", "municipio", "nomecidade", "cidade_cliente"]
        )

        col_pes_uf = self._casar_coluna(
            colunas_pes, ["uf", "estado", "sigla_uf", "siglauf"]
        )

        sql_expressao_nome = f'COALESCE("{col_pes_nome}", \'Cliente sem Nome\')' if col_pes_nome else "'Cliente sem Nome'"
        sql_expressao_cidade = f'COALESCE("{col_pes_cidade}", \'Não Informada\')' if col_pes_cidade else "'Não Informada'"
        sql_expressao_uf = f'COALESCE("{col_pes_uf}", \'SP\')' if col_pes_uf else "'SP'"

        # 3. CONSTRUÇÃO DA CONSULTA SQL VETORIZADA NO DUCKDB (SEM COLUNAS FANTASMAS)
        consulta_sql_dinamica = f"""
            WITH titulos_limpos AS (
                SELECT 
                    {expr_id_titulo} AS id_titulo,
                    {expr_id_cli} AS id_cliente,
                    {expr_valor} AS valor_titulo,
                    {expr_venc} AS data_vencimento,
                    {expr_pagto} AS data_pagamento,
                    {expr_status} AS status_cobranca
                FROM read_csv_auto('{{PASTA_CSV}}/erp_contasreceber.csv', ignore_errors=true)
                WHERE {where_valor}
            ),
            metricas_por_cliente AS (
                SELECT 
                    id_cliente,
                    ROUND(SUM(valor_titulo), 2) AS volume_total_recebido,
                    ROUND(AVG(valor_titulo), 2) AS ticket_medio_titulo,
                    COUNT(id_titulo) AS total_titulos_emitidos,
                    MAX(CASE 
                        WHEN data_pagamento IS NOT NULL AND data_vencimento IS NOT NULL THEN (data_pagamento - data_vencimento)
                        WHEN data_vencimento IS NOT NULL THEN (CURRENT_DATE - data_vencimento)
                        ELSE 0
                    END) AS maximo_dias_atraso_historico,
                    MAX(CASE 
                        WHEN data_vencimento IS NOT NULL AND (CURRENT_DATE - data_vencimento) > 30 AND data_pagamento IS NULL THEN 1
                        ELSE 0
                    END) AS alvo_inadimplente
                FROM titulos_limpos
                WHERE id_cliente IS NOT NULL AND id_cliente > 0
                GROUP BY id_cliente
            ),
            cadastro_clientes AS (
                SELECT 
                    TRY_CAST("{col_pes_id}" AS INTEGER) AS id_cliente,
                    {sql_expressao_nome} AS razao_social_cliente,
                    {sql_expressao_cidade} AS cidade_cliente,
                    {sql_expressao_uf} AS uf_cliente
                FROM read_csv_auto('{{PASTA_CSV}}/erp_pessoas.csv', ignore_errors=true)
                WHERE "{col_pes_id}" IS NOT NULL
            )
            SELECT 
                m.id_cliente AS codigo_cliente,
                COALESCE(c.razao_social_cliente, 'Cliente #' || CAST(m.id_cliente AS VARCHAR)) AS razao_social_cliente,
                COALESCE(c.cidade_cliente, 'Não Informada') AS cidade_cliente,
                COALESCE(c.uf_cliente, 'SP') AS uf_cliente,
                m.volume_total_recebido,
                m.ticket_medio_titulo,
                m.total_titulos_emitidos,
                m.maximo_dias_atraso_historico,
                m.alvo_inadimplente
            FROM metricas_por_cliente m
            LEFT JOIN cadastro_clientes c ON m.id_cliente = c.id_cliente
            ORDER BY m.volume_total_recebido DESC;
        """

        # Executa a consulta compilada diretamente no motor DuckDB.
        df_abt = self.motor_duckdb.consultar_sql(consulta_sql_dinamica)

        # TRATAMENTO DE CONTINGÊNCIA DEFENSIVA:
        # Se a junção por cliente retornar vazia, agrega no grão de títulos individuais para manter o pipeline fluindo.
        if df_abt.empty:
            logging.warning("Agrupamento por cliente retornou vazio. Ativando plano de contingência no grão de títulos...")
            consulta_contingencia = f"""
                WITH titulos_limpos AS (
                    SELECT 
                        {expr_id_titulo} AS id_titulo,
                        {expr_valor} AS valor_titulo,
                        {expr_venc} AS data_vencimento,
                        {expr_pagto} AS data_pagamento
                    FROM read_csv_auto('{{PASTA_CSV}}/erp_contasreceber.csv', ignore_errors=true)
                    WHERE {where_valor}
                )
                SELECT 
                    id_titulo AS codigo_cliente,
                    'Título #' || CAST(id_titulo AS VARCHAR) AS razao_social_cliente,
                    'Não Informada' AS cidade_cliente,
                    'SP' AS uf_cliente,
                    ROUND(valor_titulo, 2) AS volume_total_recebido,
                    ROUND(valor_titulo, 2) AS ticket_medio_titulo,
                    1 AS total_titulos_emitidos,
                    CASE 
                        WHEN data_pagamento IS NOT NULL AND data_vencimento IS NOT NULL THEN (data_pagamento - data_vencimento)
                        WHEN data_vencimento IS NOT NULL THEN (CURRENT_DATE - data_vencimento)
                        ELSE 0
                    END AS maximo_dias_atraso_historico,
                    CASE 
                        WHEN data_vencimento IS NOT NULL AND (CURRENT_DATE - data_vencimento) > 30 AND data_pagamento IS NULL THEN 1
                        ELSE 0
                    END AS alvo_inadimplente
                FROM titulos_limpos
                LIMIT 5000;
            """
            df_abt = self.motor_duckdb.consultar_sql(consulta_contingencia)

        # Preenchimento defensivo final de nulos para assegurar estabilidade matemática no Scikit-Learn.
        df_abt["maximo_dias_atraso_historico"] = df_abt["maximo_dias_atraso_historico"].fillna(0)
        df_abt["alvo_inadimplente"] = df_abt["alvo_inadimplente"].fillna(0).astype(int)

        logging.info("ABT de Crédito consolidada com sucesso contendo %d linhas de observação.", len(df_abt))
        return df_abt

    # 'def' define método compatível com a interface legada para manter retrocompatibilidade com orquestradores.
    def construir_abt(self) -> pd.DataFrame:
        """Alias retrocompatível que aciona a construção da ABT de crédito."""
        return self.construir_abt_credito_cliente()