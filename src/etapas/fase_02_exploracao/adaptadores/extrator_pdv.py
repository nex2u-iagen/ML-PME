"""Extrator das operações de PDV registradas no log de auditoria do ERP.

Responsabilidade Única: recuperar os lançamentos reais de venda por produto
(nome, quantidade, unidade e valor) a partir de ``erp_logs.csv`` e classificar
cada item no departamento de varejo correspondente.

Por que o log do PDV?
---------------------
O dump deste ERP não exporta a tabela de itens de nota (``nfedet``), de modo que
a massa de vendas documental (``erp_nfetotal``) não permite quebrar o
faturamento por produto. O log de auditoria, porém, registra cada lançamento do
caixa no formato::

    PDV DESKTOP-NDMLK58 lançou 0,354 KG PAO FRANCES, R$ 5,84

Isso viabiliza análises honestas de produto e de departamento de varejo sem
qualquer distribuição artificial de valores.
"""

# 'from pathlib import Path' manipula caminhos de arquivos de forma orientada a objetos.
from pathlib import Path

# 'import logging' registra eventos técnicos no console com carimbo de auditoria.
import logging

# 'import re' fornece as expressões regulares que descrevem o formato dos lançamentos.
import re

# 'import unicodedata' permite remover acentos antes de aplicar as regras de palavra-chave.
import unicodedata

# 'import pandas as pd' manipula a massa tabular extraída do log.
import pandas as pd

# Importação do leitor tolerante do núcleo compartilhado.
from src.nucleo.acesso_dados.leitor_arquivos import LeitorArquivosTabulares

# Padrão de um lançamento de item: '<estação> lançou <qtd> <un> <PRODUTO>, R$ <valor>'.
# 're.IGNORECASE' tolera variações de caixa e 'lançou'/ 'lancou' sem acento.
_PADRAO_ITEM = re.compile(
    r"lan[çc]ou\s+(?P<quantidade>[\d.,]+)\s+(?P<unidade>[A-Za-z]{1,4})\s+"
    r"(?P<produto>.+?),\s*R\$\s*(?P<valor>[\d.,]+)\s*$",
    re.IGNORECASE,
)

# REGRAS DE CLASSIFICAÇÃO POR DEPARTAMENTO DE VAREJO.
# Cada tupla vira uma expressão regular única; a PRIMEIRA que casar vence, por isso
# a ordem importa (ex.: 'PAO DE QUEIJO' é Padaria, não Laticínios; 'BATATA PALHA'
# é Mercearia, não Hortifrúti).
_REGRAS_DEPARTAMENTO = [
    (
        "Padaria",
        r"PAO|PIZZA|CROISSANT|MASSA|SONHO|ROCAMBOL|BROA|BOLA DE QUEIJO"
        r"|BISNAG|BAGUET|TORRADA|\bBOLO\b|\bLANCHE\b|COXINHA|\bPUDIM\b",
    ),
    (
        "Açougue",
        r"PATINHO|ACEM|PICANHA|CARNE|BIFE|FRANGO|COXHA|PERDIG|BOVINO|SUINO|PORCO"
        r"|LINGUICA|SALCHICH|HAMBURGUER|COSTELA|PANCADA|ALCATRA|\bFILE\b|PAIO"
        r"|CONTRAFILE|CORACAO|MOELA|\bPATO\b|COELHO|TRIPA|BACON|CALABRESA|COXAO"
        r"|\bCOXA\b|LING FINA|PRESUNTO DE PORCO",
    ),
    (
        "Frios e Laticínios",
        r"MUSSARELA|PRESUNTO|MORTAD|QUEIJO|LEITE|MANTEIGA|IOGURTE|REQUEIJAO"
        r"|CREME DE LEITE|SALAME|PEITO DE PERU|CHANTILLY|COALHADA|\bNATA\b"
        r"|GEMADA|CASEIRINHO|QUEIJADINHA|CHAMYTO|DELICINHO|REQUEIJI?O",
    ),
    (
        "Bebidas",
        r"REFRI|COCA|GUARANA|\bCERV|BEBIDA|\bSUCO\b|\bAGUA\b|\bVINHO\b|WHISKY"
        r"|AGUARDENTE|ENERGETICO|ENERG |ISOTONICO|\bGELO\b|SPRITE|FANTA|PEPSI"
        r"|\bSKOL\b|HEINEKEN|\bBRAHMA\b|BOHEMIA|CHAMPANHE|\bSODA\b|TONICA"
        r"|CERVEJA",
    ),
    (
        "Limpeza e Higiene",
        r"SABONETE|SHAMPOO|DENTAL|DETERGENTE|SABAO|ALVEJANTE|AMACIANTE"
        r"|PAPEL HIG|DESINFETANTE|LIMPA VIDRO|\bCLORO\b|BOMBRIL|ABSORVENTE"
        r"|FRALDA|REFIL|HIGIENIC|CREME CORPORAL|CONDICIONADOR",
    ),
    (
        "Congelados",
        r"SORVETE|PICOLE|CONGELAD|GRATIN|PETIT SUISSE|SALGADO CONGELADO"
        r"|GELADINHO",
    ),
    (
        "Doces e Salgados",
        r"\bBALA\b|PIRULITO|CHICLETE|GELATINA|\bDOCE\b|SALGAD|CHOCOLATE|\bCHOC\b"
        r"|MARSHMALLOW|KINDER|AMENDOIM|PASTILHA|GOMA DE MASCAR|TORTA|BROWNIE"
        r"|BRIGADEIRO|\bCAKE\b|PALHEIRO|TRIDENT|BOMBOM|HALLS|KITKAT|NUTELLA"
        r"|PRESTIGIO|BATON|PIPOCA|\bAMEN\b|\bSALG\b",
    ),
    (
        "Mercearia",
        r"ARROZ|FEIJAO|ACUCAR|\bCAFE\b|MACARRAO|\bMAC\b|OLEO|\bSAL\b|FARINHA"
        r"|MOLHO|AVEIA|\bBISC\b|BOLACHA|ACHOCOL|BATATA PALHA|ENLATAD|SARDINHA"
        r"|\bATUM\b|MAIONES|MOSTARDA|KETCHUP|FERMENTO|\bMIOJO\b|INSTANTANEO"
        r"|PAO DE ALHO|\bLANCHES?\b|\bLAMEN\b|SOPA|CREME DE ARROZ|\bFILTRO\b",
    ),
    (
        "Hortifrúti",
        r"BANANA|TOMATE|LIMAO|\bUVA\b|MELANCIA|LARANJA|MANGA|ABACAXI|CEBOLA"
        r"|\bALHO\b|BATATA|CENOURA|BROCOLIS|REPOLHO|ALFACE|PEPINO|\bPERA\b"
        r"|MAMAO|\bKIWI\b|MORANGO|GOIABA|ABACATE|BETERRABA|COUVE|\bJILO\b"
        r"|QUIABO|ESPINAFRE|COGUMELO|ERVILHA|\bFRUTA\b|\bMACA\b|PERSIMON|\bCAJU\b"
        r"|ACEROLA|RUCULA|PALMITO|MANDIOCA|INHAME|ABOBORA|MARACUJA|\bMELAO\b"
        r"|\bCOCO\b|TANGERINA|MEXERICA|PAPAYA|\bOVOS?\b|CHICORIA|SALSÃO"
        r"|\bMILHO\b|REQUEIJAO DE ALHO",
    ),
    (
        "Tabacaria",
        r"SAN MARINO|EGIPT|\bMACO\b|CIGARRO|HILTON|MALBORO|MAXXI|CHANCELA",
    ),
]

# Compila uma única vez cada expressão de departamento (evita recompilar por item).
_DEPARTAMENTOS_COMPILADOS = [
    (nome, re.compile(padrao, re.IGNORECASE))
    for nome, padrao in _REGRAS_DEPARTAMENTO
]

# SANIDADE DE LANÇAMENTO: o log já apresentou linhas corrompidas em que um código
# de barras foi registrado no lugar da quantidade (ex.: 2.012.700.006.044 UN),
# inflando o faturamento em ordens de grandeza. Um item de PDV de supermercado
# nunca excede esses tetos, então tais linhas são descartadas com alerta.
_LIMITE_QUANTIDADE = 5_000.0
_LIMITE_VALOR = 50_000.0

# Colunas esperadas no DataFrame vazio de retorno (mantém o contrato estável).
_COLUNAS_ITENS = [
    "data",
    "ano_mes",
    "iddocumento",
    "produto",
    "quantidade",
    "unidade",
    "valor",
    "departamento",
]


def _para_float(texto: str) -> float:
    """Converte um número em formato brasileiro ('1.234,56') para float.

    Args:
        texto (str): Trecho numérico extraído do log.

    Returns:
        float: Valor convertido ou 0.0 quando não interpretável.
    """
    # Remove espaços residuais e trata entradas nulas.
    limpo = str(texto).strip()
    if not limpo:
        return 0.0

    # '1.234,56' → remove milhar e troca vírgula decimal por ponto.
    if "." in limpo and "," in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    # Somente vírgula decimal ('0,354') → ponto.
    elif "," in limpo:
        limpo = limpo.replace(",", ".")

    # Conversão resiliente: qualquer lixo textual vira 0.0 em vez de exceção.
    try:
        return float(limpo)
    except ValueError:
        return 0.0


def normalizar_produto(produto: str) -> str:
    """Remove acentos e padroniza o nome do produto em maiúsculas.

    Args:
        produto (str): Nome bruto do item vindo do PDV.

    Returns:
        str: Cadeia normalizada (ex.: 'Pão de Queijo' → 'PAO DE QUEIJO').
    """
    # 'unicodedata.normalize("NFD", ...)' decompõe os acentos em caracteres base.
    decompuesto = unicodedata.normalize("NFD", str(produto))

    # Mantém apenas as letras base, descartando marcas diacríticas.
    sem_acentos = "".join(
        caractere for caractere in decompuesto if not unicodedata.combining(caractere)
    )

    # Devolve a cadeia em maiúsculas pronta para casar com as regras.
    return sem_acentos.strip().upper()


def classificar_departamento(produto: str) -> str:
    """Mapeia o nome real do produto para o departamento de varejo correspondente.

    A classificação é puramente léxica e determinística: a primeira regra que
    casar com o nome normalizado vence. Itens sem correspondência caem em
    'Outros' (nada é inventado).

    Args:
        produto (str): Nome do item lançado no caixa.

    Returns:
        str: Rótulo do departamento ('Padaria', 'Hortifrúti', ..., 'Outros').
    """
    # Normaliza uma única vez para não repetir trabalho por item.
    nome = normalizar_produto(produto)

    # Percorre as regras na ordem declarada e devolve a primeira correspondência.
    for departamento, expressao in _DEPARTAMENTOS_COMPILADOS:
        if expressao.search(nome):
            return departamento

    # Fallback honesto para itens fora do catálogo de regras.
    return "Outros"


def localizar_log_pdv(pasta_dados: Path) -> Path | None:
    """Encontra o CSV de log de auditoria que contém os lançamentos do PDV.

    Args:
        pasta_dados (Path): Diretório do dataset (ex.: mercadinho-v4/).

    Returns:
        Path | None: Caminho do arquivo ou ``None`` quando não existir.
    """
    # Procura primeiro por nomes canônicos ('erp_logs.csv', 'logs.csv').
    for caminho in sorted(Path(pasta_dados).glob("*.csv")):
        nome_normalizado = re.sub(r"[^a-z0-9]", "", caminho.stem.lower())
        if nome_normalizado.endswith("logs") and "relatorio" not in nome_normalizado:
            # Confere rapidamente que há dados além do cabeçalho.
            try:
                with open(caminho, "r", encoding="utf-8", errors="ignore") as arquivo:
                    next(arquivo, None)
                    if next(arquivo, None) is not None:
                        return caminho
            except OSError:
                continue

    # Sem log de auditoria a extração é impossível — o chamador trata o vazio.
    return None


def carregar_itens_pdv(pasta_dados: Path) -> pd.DataFrame:
    """Extrai os itens reais lançados no PDV a partir do log de auditoria.

    Cada linha no formato ``<estação> lançou <qtd> <un> <PRODUTO>, R$ <valor>``
    vira um registro com produto, quantidade, unidade, valor e departamento.

    Args:
        pasta_dados (Path): Diretório com os CSVs brutos do dataset.

    Returns:
        pd.DataFrame: Tabela com as colunas de ``_COLUNAS_ITENS``. Retorna
        estrutura vazia (mesmas colunas) quando o log não está disponível.
    """
    # Localiza o arquivo de log; ausência gera DataFrame vazio, nunca exceção.
    caminho_log = localizar_log_pdv(pasta_dados)
    if caminho_log is None:
        logging.warning(
            "PDV — Nenhum log de auditoria ('*logs*.csv') encontrado em %s; "
            "análises por produto ficam indisponíveis.",
            pasta_dados,
        )
        return pd.DataFrame(columns=_COLUNAS_ITENS)

    # Carrega a massa bruta com o leitor padrão do núcleo.
    leitor = LeitorArquivosTabulares()
    df_log = leitor.carregar_tabela(caminho_log)

    # Localiza a coluna de descrição dos eventos de forma resiliente.
    colunas = list(df_log.columns)
    col_descricao = next(
        (c for c in colunas if c.lower() in ("descricao", "description", "mensagem")),
        None,
    )
    if col_descricao is None:
        logging.warning("PDV — Coluna de descrição não encontrada em %s.", caminho_log.name)
        return pd.DataFrame(columns=_COLUNAS_ITENS)

    # Aplica a expressão regular a todas as linhas de uma vez (extração vetorizada).
    extraido = df_log[col_descricao].astype(str).str.extract(_PADRAO_ITEM)

    # Mantém somente as linhas que casaram com o formato de lançamento de item.
    mascara = extraido["produto"].notna()
    if not mascara.any():
        logging.warning(
            "PDV — Nenhum lançamento de item reconhecido em %s.", caminho_log.name
        )
        return pd.DataFrame(columns=_COLUNAS_ITENS)

    # Seleciona as colunas auxiliares alinhadas às linhas válidas.
    col_data = next((c for c in colunas if c.lower() in ("data", "datahora", "criadoem")), None)
    col_doc = next((c for c in colunas if c.lower() in ("iddocumento", "documento")), None)

    df_itens = pd.DataFrame(
        {
            "data": (
                pd.to_datetime(df_log.loc[mascara, col_data], errors="coerce")
                if col_data
                else pd.NaT
            ),
            "iddocumento": (
                df_log.loc[mascara, col_doc].values if col_doc else 0
            ),
            "produto": extraido.loc[mascara, "produto"].map(normalizar_produto),
            "quantidade": extraido.loc[mascara, "quantidade"].map(_para_float),
            "unidade": extraido.loc[mascara, "unidade"].str.upper(),
            "valor": extraido.loc[mascara, "valor"].map(_para_float),
        }
    ).reset_index(drop=True)

    # Descarta linhas sem data ou sem valor econômico (lançamentos anulados).
    df_itens = df_itens.dropna(subset=["data"])
    df_itens = df_itens[df_itens["valor"] > 0].copy()

    # SANIDADE: elimina linhas corrompidas (código de barras registrado como
    # quantidade/valor), que distorceriam qualquer agregação em ordens de grandeza.
    mascara_saudavel = (
        (df_itens["quantidade"] <= _LIMITE_QUANTIDADE)
        & (df_itens["valor"] <= _LIMITE_VALOR)
    )
    if not mascara_saudavel.all():
        logging.warning(
            "PDV — %d lançamento(s) com montante/quantidade implausível descartado(s) "
            "(provável corrupção de registro no log).",
            int((~mascara_saudavel).sum()),
        )
        df_itens = df_itens[mascara_saudavel].copy()

    # Deriva o competência mensal para séries mês a mês.
    df_itens["ano_mes"] = df_itens["data"].dt.strftime("%Y-%m")

    # Classifica cada produto no departamento de varejo correspondente.
    df_itens["departamento"] = df_itens["produto"].map(classificar_departamento)

    # Confirma no log a volumetria efetivamente aproveitada para auditoria.
    logging.info(
        "PDV — %d lançamentos reais extraídos de %s (período %s a %s).",
        len(df_itens),
        caminho_log.name,
        df_itens["data"].min().date() if len(df_itens) else "-",
        df_itens["data"].max().date() if len(df_itens) else "-",
    )

    # Garante a ordem canônica de colunas independentemente do parsing.
    return df_itens[_COLUNAS_ITENS]
