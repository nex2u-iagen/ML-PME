# 'from' acessa a biblioteca padrão 'pathlib' para manipulação de diretórios no sistema operacional.
# 'import' traz a classe 'Path' para gerenciar rotas de arquivos.
from pathlib import Path

# 'import' traz o módulo 'logging' nativo para emitir mensagens com carimbo de tempo no console.
import logging

# 'import' traz a biblioteca externa 'pandas' para manipulação, agregação e recortes de datas.
import pandas as pd

# 'import' traz o módulo 'json' para leitura de arquivos de configuração por dataset.
import json

# Importação da superclasse abstrata que fornece leitor e resolvedor semântico por herança.
from src.etapas.fase_02_exploracao.adaptadores.extrator_base import ExtratorBase

# Importação do resolvedor semântico para casamento léxico de nomes de colunas.
from src.etapas.fase_02_exploracao.adaptadores.resolvedor_semantico import ResolvedorSemantico


# ===========================================================================
# PARÂMETROS DE NEGÓCIO — Defaults pré-fixados (agnósticos, sobrescritíveis)
# ===========================================================================
# Estes valores são médias de mercado pré-fixadas. Podem ser sobrescritas por
# dataset através de arquivo JSON: dados/registros/<dataset>/parametros_negocio.json
PARAMETROS_NEGOCIO_DEFAULT = {
    "cmv_taxa": 0.55,                    # Custo da Mercadoria Vendida (55%)
    "despesas_variaveis_taxa": 0.12,     # Despesas variáveis (12%)
    "icms_aliquota": 0.18,               # ICMS (18%)
    "pis_aliquota": 0.0165,              # PIS (1.65%)
    "cofins_aliquota": 0.076,            # COFINS (7.6%)
    "frete_taxa": 0.055,                 # Frete (5.5%)
    "encargos_sociais_taxa": 0.40,       # Encargos sociais (40%)
    "refugo_taxa": 0.04,                 # Refugo fixo (4%)
    "custos_fixos_mensais": 25000.00,    # Custos fixos mensais (R$)
    "prazo_pagamento_dias": 30,          # Prazo padrão de pagamento
    "prazo_entrega_dias_uteis": 3,       # Prazo prometido de entrega
}


def carregar_parametros_negocio(nome_dataset: str | None = None) -> dict:
    """Carrega parâmetros de negócio para um dataset específico.

    Ordem de precedência:
    1. Arquivo JSON por dataset: dados/registros/<dataset>/parametros_negocio.json
    2. Defaults pré-fixados (PARAMETROS_NEGOCIO_DEFAULT)

    Retorna um dict com todos os parâmetros, usando defaults para valores
    não sobrescritos no arquivo JSON.
    """
    parametros = dict(PARAMETROS_NEGOCIO_DEFAULT)

    if nome_dataset is not None:
        caminho_json = Path(f"dados/registros/{nome_dataset}/parametros_negocio.json")
        if caminho_json.is_file():
            try:
                with open(caminho_json, "r", encoding="utf-8") as f:
                    parametros_custom = json.load(f)
                parametros.update(parametros_custom)
                logging.getLogger(__name__).info(
                    f"Parâmetros de negócio carregados de {caminho_json}"
                )
            except Exception as e:
                logging.getLogger(__name__).warning(
                    f"Falha ao carregar parâmetros de {caminho_json}: {e}. "
                    f"Usando defaults."
                )

    return parametros


# ===========================================================================
# FUNÇÕES AUXILIARES — Detecção genérica de colunas
# ===========================================================================
def _descobrir_coluna_id(df: pd.DataFrame, resolvedor=None) -> str | None:
    """Tenta descobrir qual coluna serve como identificador único da tabela.

    Prioridade:
    1. Resolvedor semântico (papel 'idNFE' ou 'id')
    2. Colunas com 'nfe' no nome (chave de join com outras tabelas ERP)
    3. Nomes comuns de coluna ID
    4. Primeira coluna inteira e com valores únicos
    """
    if resolvedor is not None:
        try:
            col = (
                resolvedor.resolver_coluna(list(df.columns), "idNFE")
                or resolvedor.resolver_coluna(list(df.columns), "id")
            )
            if col and col in df.columns:
                return col
        except Exception:
            pass

    # Priorizar colunas com 'nfe' no nome
    for c in df.columns:
        cl = c.lower().strip()
        if "nfe" in cl:
            return c

    # Nomes comuns de coluna ID
    for nome in ("idnfe", "id_nfe", "idnf", "id", "idpedido", "id_pedido", "iddocumento", "id_documento"):
        if nome in df.columns:
            return nome

    # Último recurso: primeira coluna inteira e com valores únicos
    if len(df.columns) > 0:
        primeira = df.columns[0]
        try:
            if df[primeira].dtype in ("int64", "int32", "int16") and df[primeira].nunique() == len(df):
                return primeira
        except Exception:
            pass

    return None


def _descobrir_coluna_valor(df: pd.DataFrame, resolvedor=None) -> str | None:
    """Tenta descobrir qual coluna representa o valor financeiro da transação."""
    if resolvedor is not None:
        try:
            col = (
                resolvedor.resolver_coluna(list(df.columns), "valor_total")
                or resolvedor.resolver_coluna(list(df.columns), "valor")
                or resolvedor.resolver_coluna(list(df.columns), "vNF")
                or resolvedor.resolver_coluna(list(df.columns), "valor_total")
            )
            if col and col in df.columns:
                return col
        except Exception:
            pass

    # Nomes comuns de coluna de valor
    for nome in ("vNF", "valor_total", "valor", "total", "montante", "amount", "preco", "preco_total"):
        if nome in df.columns:
            return nome

    # Último recurso: coluna numérica com maior média absoluta (heurística)
    melhores = []
    for col in df.columns:
        try:
            serie = pd.to_numeric(df[col], errors="coerce")
            if serie.notna().sum() > len(df) * 0.5:
                melhores.append((col, serie.abs().mean()))
        except Exception:
            continue

    if melhores:
        melhores.sort(key=lambda x: x[1], reverse=True)
        return melhores[0][0]

    return None


# ===========================================================================
# FUNÇÃO AUXILIAR — Busca resiliente de data (genérica — múltiplas tabelas)
# ===========================================================================
def _buscar_data_vendas_resiliente(
    df_vendas_bruto: pd.DataFrame,
    col_id: str | None = None,
    pasta_dados: str | Path = "dados/brutos/csv",
    nome_dataset: str | None = None,
    resolvedor=None,
) -> pd.Series:
    """Tenta encontrar a data de emissão de várias formas, garantindo resiliência.

    Estratégias (na ordem de prioridade):
    1. Coluna direta na tabela de vendas (nomes comuns de data)
    2. Detecção automática de qualquer coluna que parseie como data
    3. Join com outras tabelas na mesma pasta que tenham coluna de data + coluna de ID comum
    4. Fallback: retorna série com NaT e emite warning

    Returns:
        pd.Series: Série de datas (pode conter NaT se nenhuma estratégia encontrar dados).
    """
    import logging

    logger = logging.getLogger(__name__)

    pasta = Path(pasta_dados)

    # -----------------------------------------------------------
    # Estratégia 1: Coluna direta na tabela de vendas
    # -----------------------------------------------------------
    for col_name in ("data_emissao", "data", "dt_emissao", "data_emissao_nfe", "dt_emissao_nf", "emissao", "datahora"):
        if col_name in df_vendas_bruto.columns:
            serie = pd.to_datetime(df_vendas_bruto[col_name], errors="coerce")
            nonat = serie.notna().sum()
            if nonat > 0:
                logger.info(
                    f"Estratégia 1: Coluna direta '{col_name}' encontrada com {nonat} datas válidas"
                )
                return serie

    # -----------------------------------------------------------
    # Estratégia 2: Detecção automática de qualquer coluna de data
    # -----------------------------------------------------------
    for col_name in df_vendas_bruto.columns:
        if col_name in ("data_emissao", "data", "dt_emissao"):
            continue  # já testado acima
        # Pular colunas que são claramente IDs ou valores (não são datas)
        cl = col_name.lower().strip()
        # IDs e chaves
        if any(k in cl for k in ("id", "numero", "numero_nfe", "nfe")):
            continue
        # Colunas financeiras que começam com 'v' (padrão ERP: vBC, vICMS, vNF, etc.)
        if cl.startswith("v"):
            continue
        # Valores, preços, montantes
        if any(k in cl for k in ("valor", "preco", "montante", "total", "amount", "frete", "seg", "desconto")):
            continue
        try:
            serie = pd.to_datetime(df_vendas_bruto[col_name], errors="coerce")
            nonat = serie.notna().sum()
            if nonat > 0:
                # Sanity check: rejeitar se todas as datas são de 1970 (indicando
                # que são números inteiros interpretados como timestamp Unix)
                anos_detectados = serie.dt.year.dropna().unique()
                if len(anos_detectados) == 1 and anos_detectados[0] == 1970:
                    continue
                logger.info(
                    f"Estratégia 2: Coluna '{col_name}' detectada automaticamente como data com {nonat} datas válidas"
                )
                return serie
        except Exception:
            continue

    # -----------------------------------------------------------
    # Estratégia 3: Join com outras tabelas na pasta
    # -----------------------------------------------------------
    if col_id is None:
        col_id = _descobrir_coluna_id(df_vendas_bruto, resolvedor)

    # Lista de colunas de ID candidatas para tentar join (priorizar colunas com 'nfe')
    colunas_id_candidatas = [col_id] if col_id else []
    for c in df_vendas_bruto.columns:
        cl = c.lower().strip()
        if "nfe" in cl and c not in colunas_id_candidatas:
            colunas_id_candidatas.append(c)
    if "id" in df_vendas_bruto.columns and "id" not in colunas_id_candidatas:
        colunas_id_candidatas.append("id")

    if pasta.is_dir():
        try:
            arquivos_csv = sorted(pasta.glob("*.csv"))
            for arquivo in arquivos_csv:
                try:
                    df_outra = pd.read_csv(arquivo, nrows=5000)
                except Exception:
                    continue

                # Procurar coluna de ID comum na outra tabela
                col_id_outra = None
                # Primeira passagem: procurar colunas com 'nfe'
                for c in df_outra.columns:
                    cl = c.lower().strip()
                    if "nfe" in cl:
                        col_id_outra = c
                        break
                # Segunda passagem: nomes comuns de ID
                if col_id_outra is None:
                    for c in df_outra.columns:
                        cl = c.lower().strip()
                        if cl in (
                            "idnfe", "id_nfe", "idnf", "id", "idpedido", "id_pedido",
                            "iddocumento", "id_documento", "nfe", "nota", "notafiscal", "nota_fiscal",
                        ):
                            col_id_outra = c
                            break

                if col_id_outra is None:
                    continue

                # Procurar coluna de data na outra tabela
                col_data_outra = None
                for c in df_outra.columns:
                    cl = c.lower().strip()
                    if any(k in cl for k in (
                        "venc", "emissao", "dt_emissao", "data_emissao", "datahora",
                        "data", "dt_", "dven", "dtvenc", "dt_emissaonf",
                    )):
                        if any(k in cl for k in ("id", "valor", "vtotal", "vprod", "vdesc", "vicms", "ipi", "pis", "cofins")):
                            continue
                        col_data_outra = c
                        break

                if col_data_outra is None:
                    continue

                # Tentar cada coluna de ID candidata da tabela de vendas
                for cid in colunas_id_candidatas:
                    try:
                        ids_vendas = set(df_vendas_bruto[cid].astype(str))
                        ids_outra = set(df_outra[col_id_outra].astype(str))
                        ids_comum = ids_vendas.intersection(ids_outra)
                    except Exception:
                        continue

                    if len(ids_comum) > 50:
                        try:
                            # 'drop_duplicates' garante relação 1:1 no lado direito do join.
                            # Tabelas como 'erp_nfecob.csv' têm VÁRIAS linhas por NFE (uma
                            # por cobrança); sem deduplicar, o left join EXPLODE as linhas
                            # (114.975 -> 117.015), desalinha os índices e cria 'id_pedido'
                            # nulo espúrio na visão canônica (quebrando a Fase 02 no Fiscal).
                            df_vizinha = df_outra[[col_id_outra, col_data_outra]].drop_duplicates(
                                subset=[col_id_outra], keep="first"
                            )
                            df_merge = df_vendas_bruto.merge(
                                df_vizinha,
                                left_on=cid,
                                right_on=col_id_outra,
                                how="left",
                            )
                            data_join = pd.to_datetime(df_merge[col_data_outra], errors="coerce")
                            na_count = data_join.notna().sum()
                            if na_count > 0:
                                logger.info(
                                    f"Estratégia 3: Join com '{arquivo.name}' ({cid} -> {col_id_outra} -> {col_data_outra}) "
                                    f"({na_count} datas encontradas)"
                                )
                                return data_join
                        except Exception as e:
                            logger.debug(f"Estratégia 3 falhou para {arquivo.name} com coluna {cid}: {e}")
                            continue
        except Exception as e:
            logger.debug(f"Estratégia 3 falhou ao listar pasta {pasta}: {e}")

    # -----------------------------------------------------------
    # Estratégia 4: Fallback
    # -----------------------------------------------------------
    logger.warning(
        "Não foi possível encontrar coluna de data nem fazer join bem-sucedido. "
        "As datas virão como NaT."
    )
    return pd.Series([pd.NaT] * len(df_vendas_bruto))


# ===========================================================================
# FUNÇÃO AUXILIAR — Separação temporal: últimos 5 anos + últimos 12 meses
# ===========================================================================
def _aplicar_recortes_temporais(df: pd.DataFrame, col_data: str = "data_emissao") -> dict:
    """Aplica recortes temporais para análises exploratórias.

    Gera dois recortes:
    1. Últimos 5 anos (ano a ano) — para análise de tendência de longo prazo
    2. Últimos 12 meses (mês a mês) — para análise de curto prazo/sazonalidade

    Retorna um dict com:
    - 'df_5anos': DataFrame filtrado nos últimos 5 anos (com coluna 'ano')
    - 'df_12m': DataFrame filtrado nos últimos 12 meses (com coluna 'ano_mes')
    - 'anos_disponiveis': lista de anos únicos encontrados
    - 'meses_disponiveis': lista de ano_mes únicos encontrados
    - 'data_maxima': data máxima encontrada nos dados
    - 'data_minima': data mínima encontrada nos dados
    """
    import logging

    logger = logging.getLogger(__name__)

    if df.empty or col_data not in df.columns or df[col_data].notna().sum() == 0:
        return {
            "df_5anos": df.copy(),
            "df_12m": df.copy(),
            "anos_disponiveis": [],
            "meses_disponiveis": [],
            "data_maxima": None,
            "data_minima": None,
        }

    df_copia = df.copy()
    df_copia[col_data] = pd.to_datetime(df_copia[col_data], errors="coerce")
    df_copia = df_copia.dropna(subset=[col_data])

    if df_copia.empty:
        return {
            "df_5anos": df.copy(),
            "df_12m": df.copy(),
            "anos_disponiveis": [],
            "meses_disponiveis": [],
            "data_maxima": None,
            "data_minima": None,
        }

    data_maxima = df_copia[col_data].max()
    data_minima = df_copia[col_data].min()

    # Adicionar coluna 'ano' para análise ano a ano
    df_copia["ano"] = df_copia[col_data].dt.year

    # Recorte 1: Últimos 5 anos a partir da data máxima
    ano_corte_5anos = data_maxima.year - 4  # Inclui o ano atual + 4 anteriores
    df_5anos = df_copia[df_copia["ano"] >= ano_corte_5anos].copy()

    # Recorte 2: Últimos 12 meses a partir da data máxima
    data_corte_12m = data_maxima - pd.DateOffset(months=12)
    df_12m = df_copia[df_copia[col_data] >= data_corte_12m].copy()

    # Adicionar coluna 'ano_mes' para análise mês a mês
    df_12m["ano_mes"] = df_12m[col_data].dt.to_period("M").astype(str)

    anos_disponiveis = sorted(df_5anos["ano"].unique().tolist())
    meses_disponiveis = sorted(df_12m["ano_mes"].unique().tolist())

    logger.info(
        f"Recortes temporais: 5 anos ({anos_disponiveis[0] if anos_disponiveis else 'N/A'}-{anos_disponiveis[-1] if anos_disponiveis else 'N/A'}), "
        f"12 meses ({meses_disponiveis[0] if meses_disponiveis else 'N/A'}-{meses_disponiveis[-1] if meses_disponiveis else 'N/A'}), "
        f"registros 5 anos: {len(df_5anos)}, registros 12m: {len(df_12m)}"
    )

    return {
        "df_5anos": df_5anos,
        "df_12m": df_12m,
        "anos_disponiveis": anos_disponiveis,
        "meses_disponiveis": meses_disponiveis,
        "data_maxima": data_maxima,
        "data_minima": data_minima,
    }


# ===========================================================================
# CLASSE PRINCIPAL — ExtratorVendas (genérica, agnóstica)
# ===========================================================================
class ExtratorVendas(ExtratorBase):
    """Especialista responsável pela extração de dados de vendas de forma genérica.

    Não assume nomes específicos de coluna, tabela ou pasta de dados.
    Tudo é descoberto dinamicamente via resolvedor semântico e heurísticas.
    Suporta parâmetros de negócio configuráveis por dataset e separação temporal
    de últimos 5 anos + últimos 12 meses.
    """

    def __init__(
        self,
        pasta_dados: str | Path = "dados/brutos/csv",
        nome_dataset: str | None = None,
        resolvedor=None,
        leitor=None,
    ):
        # Garante que pasta_dados seja um Path antes de passar para a classe base
        pasta_dados = Path(pasta_dados)
        # Inicializa a classe base (define self.resolvedor e self.leitor)
        super().__init__(pasta_dados, resolvedor if resolvedor else ResolvedorSemantico())
        self.nome_dataset = nome_dataset
        # Garante que self.leitor esteja sempre definido (mesmo que a classe base não o defina)
        if leitor is not None:
            self.leitor = leitor
        elif not hasattr(self, 'leitor') or self.leitor is None:
            self.leitor = LeitorArquivosTabulares()
        # Carregar parâmetros de negócio (defaults + sobrescritas por dataset)
        self.parametros_negocio = carregar_parametros_negocio(nome_dataset)
        # Garante que pasta_dados seja sempre um Path (proteção contra sobrescrita na classe base)
        self.pasta_dados = Path(pasta_dados)

    def localizar_arquivo_tabela(self, nome_arquivo: str | None = None) -> Path | None:
        """Localiza um arquivo de tabela na pasta de dados.

        Se nome_arquivo for None, tenta encontrar automaticamente o arquivo
        que pareça ser a tabela principal de vendas/faturamento.

        Prioridade:
        1. Arquivos com 'nfetotal', 'venda_total', 'faturamento' no nome (alta)
        2. Arquivos com 'nfe', 'venda', 'fatur' no nome (média)
        3. Qualquer arquivo CSV que tenha coluna de valor + coluna de data (baixa)
        """
        if nome_arquivo is not None:
            caminho = self.pasta_dados / nome_arquivo
            if caminho.is_file():
                return caminho
            return None

        if not self.pasta_dados.is_dir():
            return None

        candidatos_alta = []
        candidatos_media = []
        candidatos_baixa = []

        for arquivo in self.pasta_dados.glob("*.csv"):
            nome_lower = arquivo.name.lower()

            # Alta prioridade
            if any(p in nome_lower for p in ("nfetotal", "venda_total", "faturamento", "vendas_total")):
                candidatos_alta.append(arquivo)
                continue

            # Média prioridade
            if any(p in nome_lower for p in ("nfe", "venda", "fatur", "nota", "movimento_venda")):
                candidatos_media.append(arquivo)
                continue

            # Baixa prioridade: verificar se o arquivo tem coluna de valor + data
            try:
                df_teste = pd.read_csv(arquivo, nrows=100)
                colunas = [c.lower() for c in df_teste.columns]
                tem_valor = any(
                    k in c for c in colunas for k in ("vvalor", "vtotal", "valor", "montante", "total", "amount", "preco")
                )
                tem_data = any(
                    k in c for c in colunas for k in ("data", "emissao", "venc", "dt_", "datahora")
                )
                if tem_valor and tem_data:
                    candidatos_baixa.append(arquivo)
            except Exception:
                continue

        if candidatos_alta:
            return candidatos_alta[0]
        if candidatos_media:
            return candidatos_media[0]
        if candidatos_baixa:
            return candidatos_baixa[0]

        return None

    def extrair_visao_canonica(self) -> pd.DataFrame:
        """Extrai dados de vendas de forma genérica, agnóstica a modelo de negócio.

        Descobre dinamicamente:
        - Qual arquivo é a tabela de vendas
        - Qual coluna é o ID
        - Qual coluna é o valor financeiro
        - Qual coluna é a data (via estratégias múltiplas)

        Aplica recortes temporais:
        - Últimos 5 anos (ano a ano)
        - Últimos 12 meses (mês a mês)

        Returns:
            pd.DataFrame: DataFrame canônico com colunas id_pedido, data_emissao,
                         valor_total, ano, ano_mes, categoria_departamento.
                         Inclui atributo 'recortes_temporais' com os dados de ambos os recortes.
        """
        import logging as log_module

        logger = log_module.getLogger(__name__)

        # -----------------------------------------------------------
        # 1. Descobrir arquivo de vendas
        # -----------------------------------------------------------
        caminho_vendas = self.localizar_arquivo_tabela()
        if not caminho_vendas:
            raise FileNotFoundError(f"Tabela de vendas não encontrada em {self.pasta_dados}")

        logger.info(f"Tabela de vendas detectada: {caminho_vendas.name}")

        # -----------------------------------------------------------
        # 2. Carregar tabela bruta
        # -----------------------------------------------------------
        df_vendas_bruto = self.leitor.carregar_tabela(caminho_vendas)
        colunas_tabela = list(df_vendas_bruto.columns)

        logger.info(f"Colunas detectadas na tabela: {colunas_tabela}")

        # -----------------------------------------------------------
        # 3. Descobrir colunas dinamicamente
        # -----------------------------------------------------------
        col_id = _descobrir_coluna_id(df_vendas_bruto, self.resolvedor)
        col_valor = _descobrir_coluna_valor(df_vendas_bruto, self.resolvedor)

        if col_id is None:
            raise ValueError(
                f"Não foi possível identificar coluna de ID na tabela {caminho_vendas.name}. "
                f"Colunas disponíveis: {colunas_tabela}"
            )

        if col_valor is None:
            raise ValueError(
                f"Não foi possível identificar coluna de valor financeiro na tabela {caminho_vendas.name}. "
                f"Colunas disponíveis: {colunas_tabela}"
            )

        logger.info(f"Coluna ID detectada: {col_id}")
        logger.info(f"Coluna valor detectada: {col_valor}")

        # -----------------------------------------------------------
        # 4. Descobrir data de forma resiliente (genérica)
        # -----------------------------------------------------------
        data_encontrada = _buscar_data_vendas_resiliente(
            df_vendas_bruto,
            col_id=col_id,
            pasta_dados=self.pasta_dados,
            nome_dataset=self.nome_dataset,
            resolvedor=self.resolvedor,
        )

        if data_encontrada.notna().sum() > 0:
            logger.info(
                f"Data encontrada via estratégia resiliente: {data_encontrada.notna().sum()} datas válidas"
            )
            serie_datas = data_encontrada
        else:
            logger.warning("Nenhuma data válida encontrada. As datas serão NaT.")
            serie_datas = pd.Series([pd.NaT] * len(df_vendas_bruto))

        # -----------------------------------------------------------
        # 5. Converter valor financeiro
        # -----------------------------------------------------------
        serie_valores = pd.to_numeric(df_vendas_bruto[col_valor], errors="coerce")

        # -----------------------------------------------------------
        # 6. Montar DataFrame canônico
        # -----------------------------------------------------------
        # ALINHAMENTO DEFENSIVO: a série de datas precisa ter exatamente o mesmo
        # índice da tabela bruta. Se uma estratégia de data devolver mais (ou menos)
        # linhas que o original, o alinhamento por índice do pandas deslocaria as
        # datas e criaria 'id_pedido' nulo espúrio.
        if not serie_datas.index.equals(df_vendas_bruto.index):
            logger.warning(
                "Série de datas desalinhada da tabela bruta (%d vs %d linhas); "
                "realinhando pelo índice para evitar nulos espúrios em 'id_pedido'.",
                len(serie_datas),
                len(df_vendas_bruto),
            )
            serie_datas = serie_datas.groupby(level=0).first().reindex(df_vendas_bruto.index)

        df_vendas = pd.DataFrame(
            {
                "id_pedido": df_vendas_bruto[col_id],
                "data_emissao": serie_datas,
                "valor_total": serie_valores,
            }
        )

        # 'id_pedido' é convertido para numérico de forma resiliente: células vazias ou
        # não numéricas recebem um identificador determinístico derivado da posição.
        # Isso preserva as linhas e garante que os departamentos (Fiscal, Logística e
        # Pós-Venda), que aplicam 'int(x)' em paridades, nunca estourarem com
        # 'ValueError: cannot convert float NaN to integer'.
        ids_numericos = pd.to_numeric(df_vendas["id_pedido"], errors="coerce")
        mascara_nula = ids_numericos.isna()
        if mascara_nula.any():
            total_nulos = int(mascara_nula.sum())
            base = int(ids_numericos.max()) if ids_numericos.notna().any() else 0
            ids_numericos.loc[mascara_nula] = range(base + 1, base + 1 + total_nulos)
            logger.warning(
                "%d registro(s) sem identificador de transação válido em '%s'; "
                "atribuído(s) identificador(es) determinístico(s) derivado da posição.",
                total_nulos,
                caminho_vendas.name,
            )
        df_vendas["id_pedido"] = ids_numericos

        # -----------------------------------------------------------
        # 7. Remover transações sem data válida
        # -----------------------------------------------------------
        df_vendas = df_vendas.dropna(subset=["data_emissao"]).copy()

        if df_vendas.empty:
            logger.warning("Nenhuma transação com data válida após filtragem.")
            df_vendas["ano"] = pd.Series(dtype=int)
            df_vendas["ano_mes"] = pd.Series(dtype=str)
            df_vendas["categoria_departamento"] = pd.Series(dtype=str)
            # Adicionar atributo de recortes vazios
            df_vendas.attrs["recortes_temporais"] = {
                "df_5anos": df_vendas.copy(),
                "df_12m": df_vendas.copy(),
                "anos_disponiveis": [],
                "meses_disponiveis": [],
                "data_maxima": None,
                "data_minima": None,
            }
            return df_vendas

        # -----------------------------------------------------------
        # 8. Aplicar recortes temporais (5 anos + 12 meses)
        # -----------------------------------------------------------
        recortes = _aplicar_recortes_temporais(df_vendas, col_data="data_emissao")

        # Usar o recorte de 12 meses como resultado principal (compatibilidade)
        df_vendas_12m = recortes["df_12m"].copy()

        # Adicionar coluna 'ano' também ao resultado principal para consistência
        if "ano" not in df_vendas_12m.columns:
            df_vendas_12m["ano"] = df_vendas_12m["data_emissao"].dt.year

        # -----------------------------------------------------------
        # 9. Categoria de departamento (fallback genérico)
        # -----------------------------------------------------------
        caminho_deptos = self.localizar_arquivo_tabela("departamentos")
        if caminho_deptos is None:
            for arquivo in self.pasta_dados.glob("*.csv"):
                nome_lower = arquivo.name.lower()
                if any(p in nome_lower for p in ("depto", "categoria", "setor", "grupo")):
                    caminho_deptos = arquivo
                    break

        if caminho_deptos is not None:
            try:
                df_deptos = self.leitor.carregar_tabela(caminho_deptos)
                col_desc = (
                    self.resolvedor.resolver_coluna(list(df_deptos.columns), "descricao_item")
                    or self.resolvedor.resolver_coluna(list(df_deptos.columns), "descricao")
                    or df_deptos.columns[1] if len(df_deptos.columns) > 1 else df_deptos.columns[0]
                )
                lista_deptos = df_deptos[col_desc].dropna().unique().tolist()
                if lista_deptos and "id_departamento" in df_vendas_12m.columns:
                    df_vendas_12m["categoria_departamento"] = df_vendas_12m["id_departamento"].apply(
                        lambda x: str(lista_deptos[int(x) % len(lista_deptos)])
                    )
            except Exception:
                pass

        if "categoria_departamento" not in df_vendas_12m.columns:
            df_vendas_12m["categoria_departamento"] = "Não informada"

        # -----------------------------------------------------------
        # 10. Arredondar valores
        # -----------------------------------------------------------
        df_vendas_12m["valor_total"] = df_vendas_12m["valor_total"].round(2)

        # -----------------------------------------------------------
        # 11. Armazenar recortes temporais como atributo da instância
        #     (não usar DataFrame.attrs para evitar problemas de compatibilidade)
        # -----------------------------------------------------------
        self._ultimos_recortes = recortes

        return df_vendas_12m

    def obter_recortes_temporais(self) -> dict | None:
        """Retorna os recortes temporais da última extração.

        Returns:
            dict com df_5anos, df_12m, anos_disponiveis, meses_disponiveis,
            data_maxima, data_minima. Ou None se não houver extração prévia.
        """
        return getattr(self, "_ultimos_recortes", None)

    def get_parametro_negocio(self, chave: str, default=None):
        """Retorna um parâmetro de negócio específico.

        Args:
            chave: Nome do parâmetro (ex: 'cmv_taxa', 'icms_aliquota')
            default: Valor padrão caso a chave não exista

        Returns:
            Valor do parâmetro ou default
        """
        return self.parametros_negocio.get(chave, default)


# ===========================================================================
# FUNÇÕES DE VALIDAÇÃO E PERSISTÊNCIA DE PARÂMETROS (Etapa 1)
# ===========================================================================
def validar_parametros_negocio(parametros: dict) -> dict:
    """Valida parâmetros de negócio antes de salvar.

    Regras de validação:
    - Taxas (cmv_taxa, despesas_variaveis_taxa, icms_aliquota, pis_aliquota,
      cofins_aliquota, frete_taxa, encargos_sociais_taxa, refugo_taxa):
      devem estar entre 0 e 1
    - Valores monetários (custos_fixos_mensais): devem ser positivos
    - Prazos (prazo_pagamento_dias, prazo_entrega_dias_uteis):
      devem ser inteiros positivos

    Args:
        parametros: dict com os parâmetros a validar

    Returns:
        dict com chaves 'valido' (bool) e 'erros' (dict campo -> mensagem)
    """
    erros = {}

    # Campos que são taxas (0 a 1)
    campos_taxa = [
        "cmv_taxa",
        "despesas_variaveis_taxa",
        "icms_aliquota",
        "pis_aliquota",
        "cofins_aliquota",
        "frete_taxa",
        "encargos_sociais_taxa",
        "refugo_taxa",
    ]

    for campo in campos_taxa:
        if campo in parametros:
            valor = parametros[campo]
            try:
                valor_float = float(valor)
                if valor_float < 0 or valor_float > 1:
                    erros[campo] = f"Deve estar entre 0 e 1 (atual: {valor})"
            except (TypeError, ValueError):
                erros[campo] = f"Valor inválido: {valor}"

    # Campos monetários (devem ser positivos)
    campos_monetarios = ["custos_fixos_mensais"]

    for campo in campos_monetarios:
        if campo in parametros:
            valor = parametros[campo]
            try:
                valor_float = float(valor)
                if valor_float <= 0:
                    erros[campo] = f"Deve ser positivo (atual: {valor})"
            except (TypeError, ValueError):
                erros[campo] = f"Valor inválido: {valor}"

    # Campos de prazo (inteiros positivos)
    campos_prazo = ["prazo_pagamento_dias", "prazo_entrega_dias_uteis"]

    for campo in campos_prazo:
        if campo in parametros:
            valor = parametros[campo]
            try:
                valor_int = int(valor)
                if valor_int <= 0:
                    erros[campo] = f"Deve ser um inteiro positivo (atual: {valor})"
                # Verificar se é realmente inteiro (não 30.5)
                if float(valor) != float(valor_int):
                    erros[campo] = f"Deve ser um número inteiro (atual: {valor})"
            except (TypeError, ValueError):
                erros[campo] = f"Valor inválido: {valor}"

    return {
        "valido": len(erros) == 0,
        "erros": erros,
    }


def salvar_parametros_negocio(
    nome_dataset: str,
    parametros: dict,
    pasta_registros: str | Path = "dados/registros",
) -> dict:
    """Salva parâmetros de negócio em arquivo JSON por dataset.

    Cria o arquivo: dados/registros/<dataset>/parametros_negocio.json

    Args:
        nome_dataset: Nome do dataset (ex: 'mercadinho-t3')
        parametros: Dict com os parâmetros a salvar
        pasta_registros: Caminho base para a pasta de registros

    Returns:
        dict com 'sucesso' (bool) e 'mensagem' (str) ou 'erro' (str)
    """
    try:
        pasta_destino = Path(pasta_registros) / nome_dataset
        pasta_destino.mkdir(parents=True, exist_ok=True)

        caminho_json = pasta_destino / "parametros_negocio.json"

        # Adicionar metadados
        dados_para_salvar = {
            "_descricao": f"Parâmetros de negócio para o dataset {nome_dataset}. Valores configuráveis via front-end.",
            "_versao": "1.0",
            "_atualizado_em": __import__("datetime").datetime.now().isoformat(),
        }
        dados_para_salvar.update(parametros)

        with open(caminho_json, "w", encoding="utf-8") as f:
            json.dump(dados_para_salvar, f, indent=2, ensure_ascii=False)

        return {
            "sucesso": True,
            "mensagem": f"Parâmetros salvos com sucesso em {caminho_json}",
            "caminho": str(caminho_json),
        }

    except Exception as e:
        return {
            "sucesso": False,
            "erro": str(e),
        }
