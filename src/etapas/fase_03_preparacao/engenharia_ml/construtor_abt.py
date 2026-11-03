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

# 'from' importa o resolvedor semântico que casa papéis de negócio com colunas físicas do ERP.
from src.etapas.fase_02_exploracao.adaptadores.resolvedor_semantico import ResolvedorSemantico

# 'from' importa as estruturas do contrato de problema que dirigem a construção genérica da ABT.
from src.nucleo.contratos.contrato_problema import (
    AgregacaoABT,
    ContratoProblema,
    FuncaoAgregacao,
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


# --------------------------------------------------------------------------------------
# CONSTRUTOR GENÉRICO DIRIGIDO POR CONTRATO DE PROBLEMA (PLATAFORMA AGNÓSTICA)
# --------------------------------------------------------------------------------------
class ConstrutorABTContratada:
    """Construtor de ABT genérico dirigido por um ContratoProblema declarativo.

    Substitui o alvo e a receita hardcoded (``alvo_inadimplente``) por uma especificação
    validada que descreve *qual pergunta de negócio* responder. As entidades e colunas
    físicas são descobertas via :class:`ResolvedorSemantico`, o que torna a plataforma
    capaz de operar sobre qualquer ERP compatível com o vocabulário canônico.
    """

    # 'PAPELIS_BASE' define o vocabulário de expressões semânticas sempre exposto no CTE base,
    # permitindo que a regra do alvo seja escrita em linguagem de negócio e não de banco.
    PAPELIS_BASE = (
        "id_grupo",
        "valor_item",
        "quantidade_item",
        "data_emissao",
        "data_vencimento",
        "data_pagamento",
        "id_cliente",
        "id_transacao",
        "codigo_sku",
        "uf_cliente",
        "nome_entidade",
        "status_cobranca",
        "descricao_item",
        "custo_unitario",
    )

    # 'ALIAS_EQUIVALENTES' traduz o nome do papel semântico usado no contrato para o
    # alias efetivamente exposto pelo CTE base, evitando divergência de nomenclatura.
    ALIAS_EQUIVALENTES = {
        "valor": "valor_item",
        "quantidade_estoque": "quantidade_item",
    }

    # 'EQUIVALENTES_INVERSOS' mapeia o alias canônico de volta ao papel de origem,
    # permitindo que uma coluna trazida por junção substitua o fallback da base.
    EQUIVALENTES_INVERSOS = {
        "valor_item": "valor",
        "quantidade_item": "quantidade_estoque",
    }

    def __init__(self, pasta_dados_banco: Path, contrato: "ContratoProblema") -> None:
        """Inicializa o construtor vinculando o motor DuckDB, o dataset e o contrato.

        Args:
            pasta_dados_banco (Path): Diretório contendo os CSVs extraídos do ERP.
            contrato (ContratoProblema): Contrato de problema que descreve a ABT a construir.
        """
        self.pasta_dados = Path(pasta_dados_banco)
        self.contrato = contrato

        # Instancia o motor analítico colunar com ancoragem explícita (sem subpastas[0]).
        self.motor_duckdb = ConectorAnaliticoDuckDB(
            pasta_dados=self.pasta_dados,
            ancorar_subpasta_automaticamente=False,
        )

        # Instancia o resolvedor semântico para casar papéis de negócio com colunas físicas.
        self.resolvedor = ResolvedorSemantico()

        logging.info(
            "Construtor de ABT Genericamente Contratado ativo — problema '%s' (%s) sobre '%s'.",
            contrato.id,
            contrato.tipo_tarefa.value,
            self.pasta_dados.name,
        )

    def _localizar_arquivo_base(self) -> Path:
        """Localiza o CSV correspondente à entidade canônica base do contrato.

        Returns:
            Path: Caminho absoluto do arquivo CSV base.

        Raises:
            FileNotFoundError: Quando a entidade canônica não existe no dataset.
        """
        caminho = self.resolvedor.localizar_arquivo_tabela(self.pasta_dados, self.contrato.receita.entidade_base)
        if caminho is None:
            raise FileNotFoundError(
                f"A entidade canônica '{self.contrato.receita.entidade_base}' não foi localizada "
                f"no dataset '{self.pasta_dados.name}'. Verifique o matching semântico."
            )
        return caminho

    def _montar_projection_base(self, cabecalho: List[str]) -> Dict[str, str]:
        """Resolve cada papel semântico do CTE base para uma expressão SQL defensiva.

        Args:
            cabecalho (List[str]): Colunas físicas do CSV base.

        Returns:
            Dict[str, str]: Mapa papel semântico -> expressão SQL já blindada.
        """
        projecoes: Dict[str, str] = {}

        # Mapeamento dos papéis com o catálogo de sinônimos oficial.
        mapa_tipos = {
            "valor": ("DOUBLE", "0.0"),
            "quantidade_estoque": ("DOUBLE", "0.0"),
            "quantidade_vendida": ("DOUBLE", "0.0"),
            "quantidade_entrada": ("DOUBLE", "0.0"),
            "quantidade_saida": ("DOUBLE", "0.0"),
            "valor_unitario": ("DOUBLE", "0.0"),
            "id_nfe": ("VARCHAR", "CAST(NULL AS VARCHAR)"),
            "id_nfe_detalhe": ("VARCHAR", "CAST(NULL AS VARCHAR)"),
            "data_emissao": ("DATE", "CAST(NULL AS DATE)"),
            "data_vencimento": ("DATE", "CAST(NULL AS DATE)"),
            "data_pagamento": ("DATE", "CAST(NULL AS DATE)"),
            "id_cliente": ("VARCHAR", "CAST(NULL AS VARCHAR)"),
            "id_transacao": ("VARCHAR", "CAST(NULL AS VARCHAR)"),
            "codigo_sku": ("VARCHAR", "CAST(NULL AS VARCHAR)"),
            "uf_cliente": ("VARCHAR", "CAST(NULL AS VARCHAR)"),
            "cidade_cliente": ("VARCHAR", "CAST(NULL AS VARCHAR)"),
            "nome_entidade": ("VARCHAR", "CAST(NULL AS VARCHAR)"),
            "status_cobranca": ("VARCHAR", "CAST(NULL AS VARCHAR)"),
            "descricao_item": ("VARCHAR", "CAST(NULL AS VARCHAR)"),
            "custo_unitario": ("DOUBLE", "0.0"),
        }

        for papel, (tipo_sql, fallback) in mapa_tipos.items():
            coluna = self.resolvedor.resolver_coluna(cabecalho, papel)
            if coluna:
                projecoes[papel] = f'TRY_CAST("{coluna}" AS {tipo_sql})'
            else:
                projecoes[papel] = fallback

        # Renomeia os papéis com alias canônico distinto para uniformizar a gramática SQL.
        projecoes["valor_item"] = projecoes["valor"]
        projecoes["quantidade_item"] = projecoes["quantidade_estoque"]

        return projecoes

    def _montar_expressao_bucket_temporal(self) -> Optional[str]:
        """Monta a expressão SQL do bucket temporal (dia/semana/mês/ano) do grão.

        Returns:
            Optional[str]: Fragmento SQL do bucket ou ``None`` quando a receita
                não declara granularidade temporal.
        """
        granularidade = self.contrato.receita.granularidade_temporal
        if not granularidade:
            return None

        formato_bucket = {
            "dia": "%Y-%m-%d",
            "semana": "%Y-%W",
            "mes": "%Y-%m",
            "ano": "%Y",
        }[granularidade]

        papel_data = self.contrato.receita.coluna_data
        return (
            f"COALESCE(strftime(TRY_CAST({papel_data} AS DATE), '{formato_bucket}'), 'sem_data')"
        )

    def _montar_expressao_agregacao(
        self,
        agregacao: AgregacaoABT,
        projecoes: Dict[str, str],
    ) -> str:
        """Monta a expressão SQL de uma agregação referenciando o alias semântico do CTE base.

        Args:
            agregacao (AgregacaoABT): Definição declarativa da agregação.
            projecoes (Dict[str, str]): Mapa papel semântico -> expressão SQL já resolvida.

        Returns:
            str: Fragmento SQL pronto para a cláusula SELECT do CTE agregado.
        """
        if agregacao.expressao_sql:
            # Expressões literais referenciam os aliases semânticos expostos pelo CTE base.
            return agregacao.montar_expressao_sql(None)

        if agregacao.coluna:
            # Traduz o papel do contrato para o alias canônico exposto pelo CTE base.
            alias = self.ALIAS_EQUIVALENTES.get(agregacao.coluna, agregacao.coluna)
            if alias in projecoes:
                return agregacao.montar_expressao_sql(alias)

            # Papel fora do vocabulário base: projeta-se como alias próprio para uso na agregação.
            return agregacao.montar_expressao_sql(alias)

        return agregacao.montar_expressao_sql(None)

    def _montar_juncoes(
        self,
        cabecalho_base: List[str],
        projecoes: Dict[str, str],
    ) -> tuple[str, List[str], List[str], List[str]]:
        """Resolve as junções declarativas do contrato em CTEs agregados e projeções.

        Cada tabela unida é pré-agregada pela chave de ligação, o que impede a
        multiplicação de linhas causada por relacionamentos um-para-muitos no ERP.
        As junções podem ser encadeadas: a chave de base de uma junção posterior
        pode ser um papel semântico trazido por uma junção anterior.

        Args:
            cabecalho_base (List[str]): Colunas físicas do CSV base.
            projecoes (Dict[str, str]): Mapa papel semântico -> expressão SQL do CTE base.

        Returns:
            tuple[str, List[str], List[str], List[str]]: (apelido da tabela base, CTEs de
            junção, cláusulas JOIN, projeções adicionais trazidas pelas tabelas unidas).
        """
        from_base = "b0"
        if not self.contrato.receita.juncoes:
            return from_base, [], [], []

        ctes_juncao: List[str] = []
        cl_joins: List[str] = []
        colunas_join: List[str] = []

        # Registro de chaves disponíveis: papel semântico -> (apelido, coluna exposta).
        # Permite encadear junções (vendas -> itens -> produto) sem codificação específica.
        chaves_disponiveis: Dict[str, tuple[str, str]] = {}
        for papel, expressao in projecoes.items():
            coluna_fisica = self._extrair_coluna_fisica(expressao)
            if coluna_fisica:
                chaves_disponiveis[papel] = (from_base, coluna_fisica)

        for indice, juncao in enumerate(self.contrato.receita.juncoes, start=1):
            caminho_join = self.resolvedor.localizar_arquivo_tabela(
                self.pasta_dados, juncao.entidade
            )
            if caminho_join is None:
                logging.warning(
                    "Entidade '%s' da junção não localizada no dataset '%s'. Junção ignorada.",
                    juncao.entidade,
                    self.pasta_dados.name,
                )
                continue

            cabecalho_join = list(pd.read_csv(caminho_join, nrows=0).columns)
            apelido = f"j{indice}"

            # Resolve a chave de base: prioriza um papel trazido por uma junção anterior.
            origem_base = chaves_disponiveis.get(juncao.chave_base)
            if origem_base is None:
                coluna_base = self.resolvedor.resolver_coluna(cabecalho_base, juncao.chave_base)
                if coluna_base:
                    origem_base = (from_base, coluna_base)

            coluna_join = self.resolvedor.resolver_coluna(cabecalho_join, juncao.chave_join)

            if origem_base is None or not coluna_join:
                logging.warning(
                    "Junção '%s' ignorada: chave base '%s' ou chave unida '%s' não localizada.",
                    juncao.entidade,
                    juncao.chave_base,
                    juncao.chave_join,
                )
                continue

            alias_origem, coluna_origem = origem_base

            # CTE pré-agregado: uma linha por chave de ligação, evitando fan-out.
            ctes_juncao.append(
                f"{apelido} AS (\n"
                f"                SELECT\n"
                f"                    TRY_CAST(\"{coluna_join}\" AS VARCHAR) AS chave_juncao,\n"
                f"                    {self._montar_projection_join(juncao, cabecalho_join)}\n"
                f"                FROM read_csv_auto('{{PASTA_CSV}}/{caminho_join.name}', ignore_errors=true)\n"
                f"                WHERE \"{coluna_join}\" IS NOT NULL\n"
                f"                GROUP BY \"{coluna_join}\"\n"
                f"            )"
            )

            cl_joins.append(
                f"{juncao.tipo.upper()} JOIN {apelido} "
                f"ON TRY_CAST({alias_origem}.\"{coluna_origem}\" AS VARCHAR) = {apelido}.chave_juncao"
            )

            # Registra as chaves trazidas por esta junção para permitir encadeamento.
            for papel in juncao.colunas:
                if self.resolvedor.resolver_coluna(cabecalho_join, papel):
                    chaves_disponiveis[papel] = (apelido, papel)

            # Projeta os papéis semânticos solicitados pela junção.
            for papel in juncao.colunas:
                coluna_fisica = self.resolvedor.resolver_coluna(cabecalho_join, papel)
                if coluna_fisica:
                    tipo = self._tipo_sql_papel(papel)
                    colunas_join.append(
                        f"TRY_CAST({apelido}.\"{papel}\" AS {tipo}) AS {papel}"
                    )
                    # O alias canônico equivalente passa a apontar para o valor da junção.
                    equivalente = self.EQUIVALENTES_INVERSOS.get(papel)
                    if equivalente and equivalente not in juncao.colunas:
                        colunas_join.append(
                            f"TRY_CAST({apelido}.\"{papel}\" AS "
                            f"{self._tipo_sql_papel(equivalente)}) AS {equivalente}"
                        )
                else:
                    colunas_join.append(f"CAST(NULL AS VARCHAR) AS {papel}")

        return from_base, ctes_juncao, cl_joins, colunas_join

    def _tipo_sql_papel(self, papel: str) -> str:
        """Retorna o tipo DuckDB adequado para um papel semântico projetado.

        Args:
            papel (str): Nome do papel semântico.

        Returns:
            str: Descritor de tipo SQL ('DOUBLE', 'DATE' ou 'VARCHAR').
        """
        if papel in {
            "valor",
            "valor_item",
            "quantidade_estoque",
            "quantidade_vendida",
            "quantidade_entrada",
            "quantidade_saida",
            "valor_unitario",
            "custo_unitario",
        }:
            return "DOUBLE"
        if papel in {"data_emissao", "data_vencimento", "data_pagamento"}:
            return "DATE"
        return "VARCHAR"

    def _extrair_coluna_fisica(self, expressao: str) -> Optional[str]:
        """Extrai o nome físico da coluna de uma expressão SQL de projeção.

        Args:
            expressao (str): Expressão SQL previamente montada.

        Returns:
            Optional[str]: Nome da coluna física ou ``None`` quando a expressão
                é um literal de fallback (sem coluna real).
        """
        import re

        casamento = re.search(r'"([^"]+)"', expressao)
        return casamento.group(1) if casamento else None

    def _montar_projection_join(self, juncao: "JuncaoReceita", cabecalho: List[str]) -> str:
        """Monta as projeções agregadas do CTE de uma tabela unida.

        Args:
            juncao (JuncaoReceita): Definição declarativa da junção.
            cabecalho (List[str]): Colunas físicas da tabela unida.

        Returns:
            str: Fragmento SQL com as colunas agregadas por papel semântico.
        """
        partes: List[str] = []
        papeis = list(juncao.colunas)

        # A chave de ligação também é exposta com o nome do papel, permitindo encadeamento.
        if juncao.chave_join not in papeis:
            papeis.append(juncao.chave_join)

        for papel in papeis:
            coluna_fisica = self.resolvedor.resolver_coluna(cabecalho, papel)
            if not coluna_fisica:
                partes.append(f"CAST(NULL AS VARCHAR) AS \"{papel}\"")
                continue

            tipo = self._tipo_sql_papel(papel)

            # MIN preserva o primeiro valor de forma estável e sem multiplicação de linhas.
            partes.append(
                f"MIN(TRY_CAST(\"{coluna_fisica}\" AS {tipo})) AS \"{papel}\""
            )

        return ",\n                    ".join(partes) if partes else "CAST(NULL AS VARCHAR) AS \"_vazio\""

    def _resolver_coluna_para_alias(
        self,
        papel: str,
        cabecalho: List[str],
        projecoes: Dict[str, str],
    ) -> Optional[str]:
        """Resolve um papel semântico para o nome físico usable em cláusula de junção.

        Args:
            papel (str): Papel semanticamente nomeado.
            cabecalho (List[str]): Colunas físicas disponíveis.
            projecoes (Dict[str, str]): Mapa papel -> expressão já projetada.

        Returns:
            Optional[str]: Nome físico da coluna ou ``None`` quando não localizada.
        """
        # Se o papel já está projetado, recupera o nome físico original.
        for papel_projetado, expressao in projecoes.items():
            if papel_projetado != papel:
                continue
            import re

            casamento = re.search(r'"([^"]+)"', expressao)
            if casamento:
                return casamento.group(1)

        return self.resolvedor.resolver_coluna(cabecalho, papel)

    def _montar_expressao_alvo(self) -> str:
        """Compõe a expressão SQL do vetor-alvo a partir do contrato.

        Returns:
            str: Fragmento SQL que produz o alvo dentro do CTE agregado.

        Raises:
            ValueError: Quando o contrato supervisionado não declara expressão de alvo.
        """
        alvo = self.contrato.alvo
        if alvo is None:
            raise ValueError("O contrato supervisionado não declara definição de alvo.")

        if alvo.tipo == "coluna":
            if not alvo.coluna:
                raise ValueError("Definição de alvo do tipo 'coluna' exige o campo 'coluna'.")
            return f'TRY_CAST("{alvo.coluna}" AS {alvo.tipo_dado})'

        if not alvo.expressao_sql:
            raise ValueError("Definição de alvo do tipo 'regra_sql' exige o campo 'expressao_sql'.")

        return f"TRY_CAST({alvo.expressao_sql} AS {alvo.tipo_dado})"

    def construir_abt(self) -> pd.DataFrame:
        """Constrói a Tabela Analítica de Modelagem guiado pelo contrato de problema.

        Returns:
            pd.DataFrame: ABT consolidada na grão declarada no contrato.
        """
        logging.info(
            "Construindo ABT contratada — problema '%s', grão '%s', entidade base '%s'.",
            self.contrato.id,
            self.contrato.grao_analise,
            self.contrato.receita.entidade_base,
        )

        caminho_base = self._localizar_arquivo_base()
        cabecalho = list(pd.read_csv(caminho_base, nrows=0).columns)

        projecoes = self._montar_projection_base(cabecalho)

        # RESOLVE AS JUNÇÕES DECLARATIVAS: cada entidade unida contribui com colunas
        # semânticas adicionais e exige o casamento das chaves de ligação.
        from_base, ctes_juncao, cl_joins, colunas_join = self._montar_juncoes(cabecalho, projecoes)

        # Papéis efetivamente conhecidos pelas junções (têm precedência sobre o fallback da base).
        papeis_de_join = {
            item.rsplit(" AS ", 1)[-1].strip() for item in colunas_join
        }

        # Os aliases canônicos equivalentes também são substituídos pela versão da junção.
        papeis_excluidos_base = set(papeis_de_join)
        for papel in papeis_de_join:
            equivalente = self.EQUIVALENTES_INVERSOS.get(papel)
            if equivalente:
                papeis_excluidos_base.add(equivalente)

        # A chave de grupo pode vir da própria base ou de uma tabela unida.
        nome_chave = self.contrato.receita.chave_grupo
        if nome_chave not in projecoes:
            coluna_chave = self.resolvedor.resolver_coluna(cabecalho, nome_chave)
            if coluna_chave:
                projecoes[nome_chave] = f'TRY_CAST("{coluna_chave}" AS VARCHAR)'

        if nome_chave not in projecoes and nome_chave not in papeis_de_join:
            raise FileNotFoundError(
                f"A coluna de agrupamento '{nome_chave}' não foi localizada em "
                f"'{self.pasta_dados.name}' nem nas tabelas unidas pelo contrato."
            )

        # Monta as projeções do CTE base usando os papéis semânticos resolvidos.
        # Papéis com a mesma expressão são mantidos sob aliases distintos para que
        # tanto o contrato quanto as regras de alvo referenciem nomes previsíveis.
        lista_projection: List[str] = [
            f"{expressao} AS {papel}"
            for papel, expressao in projecoes.items()
            if papel not in papeis_excluidos_base
        ]

        # Monta as agregações do CTE agregado.
        expressoes_agregacao = [
            f"{self._montar_expressao_agregacao(agregacao, projecoes)} AS {agregacao.nome}"
            for agregacao in self.contrato.receita.agregacoes
        ]

        # Colunas diretas (sem agregação) respeitam o primeiro valor por grupo.
        colunas_diretas = []
        for papel in self.contrato.receita.colunas_diretas:
            if papel in projecoes or papel in papeis_de_join:
                expressao = self._montar_expressao_agregacao(
                    AgregacaoABT(
                        nome=papel,
                        funcao=FuncaoAgregacao.MAX,
                        coluna=papel,
                        tipo_resultado=self._tipo_sql_papel(papel),
                    ),
                    projecoes,
                )
                colunas_diretas.append(f"{expressao} AS {papel}")

        condicoes = [f"{nome_chave} IS NOT NULL", f"{nome_chave} <> ''"]
        if self.contrato.receita.filtro_sql:
            condicoes.append(f"({self.contrato.receita.filtro_sql})")

        # Linhas sem data não pertencem a nenhum período e não podem compor uma série
        # temporal: são excluídas quando a receita declara granularidade temporal.
        if self.contrato.receita.granularidade_temporal:
            coluna_periodo = self.contrato.receita.coluna_data
            condicoes.append(f"{coluna_periodo} IS NOT NULL")

        limite = f"LIMIT {int(self.contrato.receita.limite_linhas)}" if self.contrato.receita.limite_linhas else ""

        # Bloco FROM: tabela base com apelido e junções encadeadas.
        bloco_from = f"FROM read_csv_auto('{{PASTA_CSV}}/{caminho_base.name}', ignore_errors=true) AS {from_base}"
        if cl_joins:
            bloco_from += "\n                " + "\n                ".join(cl_joins)

        # Colunas trazidas pelas junções entram na projeção do CTE base.
        if colunas_join:
            lista_projection = lista_projection + colunas_join

        # GRUPO COMPOSTO: o grão é calculado em um CTE intermediário, combinando
        # a chave de grupo, as dimensões declaradas e o bucket temporal.
        expressao_bucket = self._montar_expressao_bucket_temporal()
        dimensoes = self.contrato.receita.dimensoes

        if expressao_bucket:
            partes_dimensao = [
                f"COALESCE(TRY_CAST({papel} AS VARCHAR), 'sem_dimensao')"
                for papel in dimensoes
            ]
            expressao_dimensao = " || '|' || ".join(partes_dimensao) if partes_dimensao else "CAST(NULL AS VARCHAR)"
            expressao_grão = (
                f"({expressao_dimensao}) || '|' || ({expressao_bucket})"
                if partes_dimensao
                else f"({expressao_bucket})"
            )
        else:
            expressao_dimensao = "CAST(NULL AS VARCHAR)"
            expressao_grão = f"COALESCE(TRY_CAST({nome_chave} AS VARCHAR), 'sem_grupo')"

        bloco_grupo = f"""
            com_grupo AS (
                SELECT
                    *,
                    {expressao_grão} AS id_grupo_calculado,
                    {expressao_dimensao} AS dim_grupo,
                    {expressao_bucket if expressao_bucket else "CAST(NULL AS VARCHAR)"} AS periodo_grupo
                FROM base
            )"""
        fonte_agregado = "com_grupo"
        coluna_grupo = "id_grupo_calculado"

        # ALVO DESLOCADO NO TEMPO: quando a receita declara deslocamento, o vetor-alvo
        # é o valor do período seguinte (evitando vazamento de informação).
        ctes_alvo: List[str] = []
        selecao_alvo_cte = ""
        selecao_alvo_final = ""
        if self.contrato.exige_alvo:
            expressao_alvo = self._montar_expressao_alvo()
            deslocamento = self.contrato.receita.deslocamento_alvo_periodos

            if deslocamento > 0 and expressao_bucket:
                particao = "PARTITION BY dim_grupo" if self.contrato.receita.dimensoes else ""
                ctes_alvo.append(
                    f"""agregado_alvo AS (
                SELECT
                    {coluna_grupo} AS id_grupo,
                    dim_grupo,
                    periodo_grupo,
                    {expressao_alvo} AS alvo_contratado
                FROM {fonte_agregado}
                GROUP BY {coluna_grupo}, dim_grupo, periodo_grupo
            )"""
                )
                ctes_alvo.append(
                    f"""alvo_deslocado AS (
                SELECT
                    id_grupo,
                    LEAD(alvo_contratado, {deslocamento}) OVER (
                        {particao} ORDER BY periodo_grupo
                    ) AS alvo_contratado
                FROM agregado_alvo
            )"""
                )
                selecao_alvo_final = ",\n                    s.alvo_contratado AS alvo_contratado"
                fonte_final = (
                    "FROM agregado AS t\n                LEFT JOIN alvo_deslocado AS s "
                    "ON t.id_grupo = s.id_grupo"
                )
            else:
                selecao_alvo_cte = f",\n                    {expressao_alvo} AS alvo_contratado"
                fonte_final = "FROM agregado AS t"
        else:
            fonte_final = "FROM agregado AS t"

        # MONTAGEM DA CLÁUSULA WITH: cada CTE é declarado antes do uso (regra do SQL).
        lista_ctes: List[str] = list(ctes_juncao)
        lista_ctes.append(
            f"""base AS (
                SELECT
                    {",\n                    ".join(lista_projection)}
                {bloco_from}
                WHERE {' AND '.join(condicoes)}
                {limite}
            )"""
        )
        lista_ctes.append(bloco_grupo)
        lista_ctes.append(
            f"""agregado AS (
                SELECT
                    {coluna_grupo} AS id_grupo{''.join(', ' + item for item in expressoes_agregacao)}{''.join(', ' + item for item in colunas_diretas)}{selecao_alvo_cte}
                FROM {fonte_agregado}
                GROUP BY {coluna_grupo}
            )"""
        )
        lista_ctes.extend(ctes_alvo)

        consulta_sql = f"""
            WITH {",\n            ".join(lista_ctes)}
            SELECT
                t.*{selecao_alvo_final}
            {fonte_final}
            ORDER BY id_grupo;
        """

        df_abt = self.motor_duckdb.consultar_sql(consulta_sql)

        if df_abt.empty:
            logging.warning(
                "ABT contratada retornou vazia para o problema '%s'. Verifique se a entidade base "
                "'%s' contém dados utilizáveis no dataset '%s'.",
                self.contrato.id,
                self.contrato.receita.entidade_base,
                self.pasta_dados.name,
            )
            return df_abt

        # Preenchimento defensivo de nulos para estabilidade matemática no Scikit-Learn.
        for coluna in df_abt.columns:
            if df_abt[coluna].isna().any():
                if pd.api.types.is_numeric_dtype(df_abt[coluna]):
                    df_abt[coluna] = df_abt[coluna].fillna(0)
                else:
                    df_abt[coluna] = df_abt[coluna].fillna("")

        if self.contrato.exige_alvo and "alvo_contratado" in df_abt.columns:
            df_abt["alvo_contratado"] = pd.to_numeric(df_abt["alvo_contratado"], errors="coerce").fillna(0)

        logging.info(
            "ABT contratada '%s' construída com sucesso: %d linhas x %d colunas.",
            self.contrato.id,
            len(df_abt),
            df_abt.shape[1],
        )
        return df_abt