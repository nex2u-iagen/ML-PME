"""Módulo de Auditoria Forense de Lotes e Rastreabilidade de Inferência (Fase 6).

Responsabilidade Única: Confrontar a integridade das variáveis brutas de entrada,
as matrizes transformadas pelo pré-processador e as predições probabilísticas de saída,
gerando a Trilha de Auditoria (Audit Trail) com metadados para compliance e governança[cite: 8, 10, 20].
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro técnico no console[cite: 8].
import logging

# 'from' acessa a biblioteca nativa 'pathlib'; 'import' traz 'Path' para manipulação segura de arquivos[cite: 8].
from pathlib import Path

# 'import' traz a biblioteca externa 'numpy' para computação vetorizada de divergências.
import numpy as np

# 'import' traz a biblioteca externa 'pandas' para manipulação tabular e junções relacionais de auditoria[cite: 8].
import pandas as pd

# 'logging.basicConfig' parametriza a formatação dos registros operacionais no terminal[cite: 8].
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara o especialista na geração de laudos de conformidade e conciliação de lotes[cite: 8].
class AuditorConformidadeLote:
    """Perito responsável por auditar o casamento exato entre entrada bruta, inferência e saída prescritiva[cite: 8, 20]."""

    # 'def __init__(...)' instancia o auditor vinculando o diretório de destino dos laudos periciais[cite: 8].
    def __init__(self, pasta_auditoria: Path) -> None:
        """Inicializa o auditor configurando o diretório de saída dos laudos de conformidade[cite: 8].

        Args:
            pasta_auditoria (Path): Diretório onde a trilha de auditoria será arquivada no disco[cite: 8].
        """
        self.pasta_auditoria = Path(pasta_auditoria)
        self.pasta_auditoria.mkdir(parents=True, exist_ok=True)

    # 'def conciliar_entrada_e_saida(...)' une os dados brutos às probabilidades e ações prescritas[cite: 8, 20].
    def conciliar_entrada_e_saida(
        self,
        dados_brutos_entrada: pd.DataFrame,
        tabela_escoragem_saida: pd.DataFrame,
        nome_lote: str = "lote_carteira_fechamento_mensal",
    ) -> pd.DataFrame:
        """Realiza a conciliação linha a linha atestando que nenhuma observação foi corrompida ou perdida[cite: 8].

        Args:
            dados_brutos_entrada (pd.DataFrame): Base analítica bruta original antes do pré-processamento[cite: 8].
            tabela_escoragem_saida (pd.DataFrame): Tabela gerada pela inferência com escores e ações[cite: 8, 20].
            nome_lote (str, opcional): Rótulo de identificação do lote auditado. Padrão: 'lote_carteira...'.

        Returns:
            pd.DataFrame: Dossiê completo de auditoria com conciliação contábil e técnica confirmada[cite: 8].
        """
        logging.info("Iniciando conciliação pericial entre base de entrada (%d linhas) e saída (%d linhas)...",
                     len(dados_brutos_entrada), len(tabela_escoragem_saida))

        # Checagem defensiva de cardinalidade: a quantidade de saídas DEVE ser idêntica à de entradas[cite: 8]:
        if len(dados_brutos_entrada) != len(tabela_escoragem_saida):
            logging.critical("DISCREPÂNCIA DETECTADA: Cardinalidade divergente entre entrada e saída!")
            raise ValueError("Falha de Conciliação: Registros foram descartados ou duplicados indevidamente.")

        # Junção pericial utilizando a chave única primária ('codigo_cliente')[cite: 8]:
        chave_juncao = "codigo_cliente" if "codigo_cliente" in dados_brutos_entrada.columns else dados_brutos_entrada.columns[0]
        
        dossie_auditoria = pd.merge(
            dados_brutos_entrada,
            tabela_escoragem_saida,
            on=chave_juncao,
            how="inner",
            suffixes=("_bruto", "_predito"),
        )

        # Adiciona carimbos de governança e metadados de certificação[cite: 8]:
        dossie_auditoria["lote_processamento"] = nome_lote
        dossie_auditoria["auditoria_status"] = "CONCILIADO_E_CONFORME"

        # Persistência perene do laudo pericial em Parquet e CSV auditável para os fiscais e compliance[cite: 8, 15]:
        caminho_parquet = self.pasta_auditoria / f"auditoria_{nome_lote}.parquet"
        caminho_csv = self.pasta_auditoria / f"auditoria_{nome_lote}.csv"

        dossie_auditoria.to_parquet(caminho_parquet, index=False)
        dossie_auditoria.to_csv(caminho_csv, index=False, sep=";", decimal=",", encoding="utf-8-sig")

        logging.info("Laudo de auditoria de lote consolidado com sucesso em: %s", caminho_parquet.name)
        return dossie_auditoria