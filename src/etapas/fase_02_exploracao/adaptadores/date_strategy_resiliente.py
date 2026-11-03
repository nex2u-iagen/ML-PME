"""Estratégias múltiplas para encontrar coluna de data em tabelas de vendas.

Esta abordagem é projetada para ser resiliente a diferentes padrões de dados,
tentando várias fontes de data antes de falhar graciosamente.
"""

import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)


def _try_direct_date_column(df: pd.DataFrame, date_col_names: list) -> pd.Series | None:
    """Tenta encontrar uma coluna de data diretamente no DataFrame.
    
    Testa nomes de colunas comuns de data e retorna a série de datas se bem-sucedida.
    """
    for col_name in date_col_names:
        if col_name in df.columns:
            series = pd.to_datetime(df[col_name], errors="coerce")
            # Verifica se conseguiu parsear datas significativas (não todas NaT)
            nonat_count = series.notna().sum()
            if nonat_count > 0:
                # Evita aceitar se for quase todas NaT (ex: IDs sendo parseados como data)
                if nonat_count < len(df) * 0.8:
                    logger.info(f"Data column found directly: '{col_name}' ({nonat_count} valid dates)")
                    return series
    return None


def _try_join_date_from_related_tables(
    df_vendas: pd.DataFrame,
    tabela_nome: str,
    id_col_vendas: str,
    id_col_outra: str,
    date_col_outra: str,
    data_original: pd.Series | None = None,
) -> pd.Series | None:
    """Tenta encontrar data fazendo join com outra tabela relacionada.
    
    Tabela de estratégias supportadas:
    - 'nfecob': join em idNFE -> dVenc (data de cancelamento/retorno)
    - 'nfehistorico': join em idNFE -> datahora (data/hora emissão)
    - 'outros': join geral com colunas idNFE/idnfe
    """
    try:
        # Mapeamento de quais tabelas têm quais colunas
        tabela_configs = {
            "nfecob": {
                "id_col_outra": "idNFE",
                "date_col_outra": "dVenc",
                "desc": "Tabela de cancelamento/retorno de NFE",
            },
            "nfehistorico": {
                "id_col_outra": "idnfe",
                "date_col_outra": "datahora",
                "desc": "Tabela histórica de NFE",
            },
        }

        if tabela_nome not in tabela_configs:
            logger.warning(f"Tabela '{tabela_nome}' não configurada para join de data")
            return None

        config = tabela_configs[tabela_nome]
        outra_tabela = Path(f"dados/brutos/csv/mercadinho-t3/{tabela_nome}.csv")

        if not outra_tabela.is_file():
            logger.warning(f"Tabela '{tabela_nome}' não encontrada em dados/brutos/csv/")
            return None

        df_outra = pd.read_csv(outra_tabela, dtype=str)
        
        # Verificar se as colunas existem
        if config["id_col_outra"] not in df_outra.columns:
            logger.warning(f"Coluna '{config['id_col_outra']}' não existe em {tabela_nome}")
            return None
        if config["date_col_outra"] not in df_outra.columns:
            logger.warning(f"Coluna '{config['date_col_outra']}' não existe em {tabela_nome}")
            return None

        # Fazer o join
        df_merge = df_vendas.merge(
            df_outra[[config["id_col_outra"], config["date_col_outra"]]],
            left_on=id_col_vendas,
            right_on=config["id_col_outra"],
            how="left",
        )

        data_join = pd.to_datetime(df_merge[config["date_col_outra"]], errors="coerce")
        nonat_count = data_join.notna().sum()

        if nonat_count > 0:
            logger.info(
                f"Data encontrada via join com {tabela_nome}: {nonat_count} datas de {len(df_merge)} linhas"
            )
            return data_join
        else:
            logger.info(f"Join com {tabela_nome} não retornou datas válidas")
            return None

    except Exception as e:
        logger.warning(f"Erro ao tentar join com {tabela_nome}: {e}")
        return None


def _fallback_to_most_recent_date(df_vendas: pd.DataFrame, data_original: pd.Series | None = None) -> pd.Series:
    """Usa a data mais recente encontrada como fallback.
    
    Tenta extrair datas de qualquer coluna que pareça ter datas,
    ou usa a data original se fornecida.
    """
    try:
        # Se já temos uma data original (do tentar direto), usa ela
        if data_original is not None and data_original.notna().sum() > 0:
            logger.info("Usando data original como fallback")
            return data_original

        # Tenta encontrar qualquer coluna com datas em todo o DataFrame
        for col in df_vendas.columns:
            series = pd.to_datetime(df_vendas[col], errors="coerce")
            nonat = series.notna().sum()
            if nonat > 0 and nonat < len(df_vendas) * 0.9:  # Não é toda a tabela
                logger.info(f"Usando data fallback da coluna '{col}': {nonat} datas")
                return series

        # Último recurso: todas as NaT, retorna série de NaT
        logger.warning("Não foi possível encontrar nenhuma coluna com data válida")
        return pd.Series([pd.NaT] * len(df_vendas))

    except Exception as e:
        logger.error(f"Erro no fallback de data: {e}")
        return pd.Series([pd.NaT] * len(df_vendas))


def extrair_data_vendas_resiliente(
    df_vendas: pd.DataFrame,
    id_col: str = "idNFE",
    data_original: pd.Series | None = None,
) -> pd.Series:
    """Extrai datas de vendas usando estratégias múltiplas e resilientes.
    
    Ordem de tentativa:
    1. Coluna direta 'data_emissao' (ou similar)
    2. Join com tabela 'nfecob' (data de cancelamento/retorno)
    3. Fallback para data mais recente encontrada
    
    Returns:
        Série pandas com datas (pode conter NaT se nenhuma estratégia funcionar)
    """
    logger.info("Iniciando extração resiliente de datas de vendas")

    # Estratégia 1: Coluna direta
    data_direta = _try_direct_date_column(
        df_vendas,
        ["data_emissao", "data", "data_emissao_nfe", "dt_emissao", "data_emissao_nf"],
    )
    if data_direta is not None and data_direta.notna().sum() > 0:
        logger.info("Estratégia 1 bem-sucedida: coluna direta de data")
        return data_direta

    # Estratégia 2: Join com tabela nfecob
    data_join = _try_join_date_from_related_tables(
        df_vendas,
        tabela_nome="nfecob",
        id_col_vendas=id_col,
        id_col_outra="idNFE",
        date_col_outra="dVenc",
    )
    if data_join is not None and data_join.notna().sum() > 0:
        # Nota: dVenc é data de cancelamento/retorno, não emissão
        # Mas é uma data real associada à NFE, então é melhor que nada
        logger.info(
            f"Estratégia 2 bem-sucedida: join com nfecob ({data_join.notna().sum()} datas de cancelamento/retorno)"
        )
        return data_join

    # Estratégia 3: Outras tabelas
    for tabela in ["nfehistorico", "nfemit", "nfetransmissao"]:
        data_outra = _try_join_date_from_related_tables(
            df_vendas,
            tabela_nome=tabela,
            id_col_vendas=id_col,
            id_col_outra="idnfe" if tabela != "nfemit" else "idNFE",
            date_col_outra="datahora" if tabela == "nfehistorico" else ("dataenvio" if tabela == "nfetransmissao" else None),
        )
        if data_outra is not None and data_outra.notna().sum() > 0:
            logger.info(f"Estratégia 3 bem-sucedida via {tabela}")
            return data_outra

    # Fallback final
    logger.warning("Nenhuma estratégia de data encontrou datas válidas")
    return _fallback_to_most_recent_date(df_vendas, data_original)
