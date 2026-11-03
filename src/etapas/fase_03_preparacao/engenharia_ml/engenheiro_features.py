"""Módulo de Engenharia de Atributos para Machine Learning (Fase 3.2).

Responsabilidade Única: Extrair, enriquecer e derivar variáveis preditoras matemáticas,
temporais e comportamentais (Features) a partir de históricos transacionais brutos,
atendendo tanto a problemas de séries temporais quanto a análises tabulares estáticas.
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registros técnicos e operacionais no terminal.
import logging

# 'from' indica a biblioteca de origem; 'typing' fornece os tipos estáticos formais da linguagem Python.
# 'import' carrega 'List' e 'Optional' para documentar assinaturas de métodos e garantir legibilidade estrita.
from typing import List, Optional

# 'import' traz a biblioteca externa 'pandas' para manipulação vetorial e janelas de cálculo temporal em memória RAM.
# 'as' define o apelido oficial 'pd' padronizado na Ciência de Dados corporativa.
import pandas as pd

# 'logging.basicConfig' parametriza a apresentação visual e o nível de criticidade dos registros no console.
# 'level=logging.INFO' assegura que notificações informativas e marcos de processamento sejam exibidos.
# 'format' dita o padrão com carimbo temporal auditável, gravidade da mensagem e conteúdo textual descritivo.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' é a palavra-chave reservada que define a estrutura de um molde orientado a objetos na linguagem Python.
# 'EngenheiroFeatures' centraliza com alta coesão todas as transformações de derivação e enriquecimento de dados.
class EngenheiroFeatures:
    """Classe especialista responsável pelo cálculo e enriquecimento de features preditivas para modelos de IA."""

    # 'def' define a função estática encarregada de extrair propriedades do calendário gregoriano a partir de datas.
    # '@staticmethod' dispensa a necessidade de manter instâncias acopladas na memória RAM do computador.
    @staticmethod
    def derivar_atributos_calendario(
        dados: pd.DataFrame, coluna_data: str
    ) -> pd.DataFrame:
        """Extrai componentes temporais (dia da semana, dia do mês, trimestre e flag de fim de semana).

        Args:
            dados (pd.DataFrame): Matriz tabular contendo ao menos uma série cronológica de eventos.
            coluna_data (str): Identificador textual da coluna contendo os carimbos de data/hora a processar.

        Returns:
            pd.DataFrame: Cópia isolada da tabela enriquecida com as novas colunas temporais de calendário.
        """
        # '.copy()' gera uma bifurcação independente na memória RAM, prevenindo o erro SettingWithCopyWarning do pandas.
        df_processado = dados.copy()

        # 'pd.to_datetime()' assegura a conversão forçada da coluna indicada para o tipo temporal Timestamp nativo.
        # 'errors="coerce"' substitui registos de texto corrompidos por valores nulos NaT de forma defensiva.
        df_processado[coluna_data] = pd.to_datetime(
            df_processado[coluna_data], errors="coerce"
        )

        # '.dt.day_name()' extrai a nomenclatura textual do dia da semana (ex.: 'Monday', 'Tuesday') para o OneHotEncoder.
        df_processado["dia_semana_nome"] = df_processado[
            coluna_data
        ].dt.day_name()

        # '.dt.day' isola a grandeza numérica ordinal do dia no mês corrente (valores contínuos de 1 a 31).
        df_processado["dia_do_mes"] = df_processado[coluna_data].dt.day

        # '.dt.month' extrai o mês de competência da transação financeira ou venda (valores de 1 a 12).
        df_processado["numero_mes"] = df_processado[coluna_data].dt.month

        # '.dt.quarter' identifica o trimestre comercial em que a operação ocorreu (valores discretos de 1 a 4).
        df_processado["trimestre_ano"] = df_processado[coluna_data].dt.quarter

        # '.dt.dayofweek' extrai o índice numérico do dia (onde 5=Sábado e 6=Domingo na convenção ISO).
        # '.isin([5, 6]).astype(int)' assinala uma flag binária (1 para fins de semana e 0 para dias úteis).
        df_processado["eh_fim_de_semana"] = (
            df_processado[coluna_data].dt.dayofweek.isin([5, 6]).astype(int)
        )

        # 'logging.info' documenta no terminal corporativo a conclusão da extração dos sinais de calendário.
        logging.info(
            "Engenharia de Features: Atributos de calendário derivados com sucesso sobre a coluna '%s'.",
            coluna_data,
        )

        # Devolve a matriz tabular enriquecida com os novos sinais cronológicos.
        return df_processado

    # 'def' define a função especialista em gerar variáveis com defasagem no tempo (Lag Features).
    @staticmethod
    def gerar_defasagens_temporais(
        dados: pd.DataFrame,
        coluna_alvo: str,
        defasagens_dias: Optional[List[int]] = None,
    ) -> pd.DataFrame:
        """Gera atributos com defasagem cronológica (Lags) para capturar dependência serial em séries temporais.

        Args:
            dados (pd.DataFrame): Tabela cronologicamente ordenada contendo o histórico de consumo ou faturamento.
            coluna_alvo (str): Nome da variável métrica sobre a qual as defasagens passadas serão calculadas.
            defasagens_dias (Optional[List[int]], opcional): Lista com os saltos de dias passados. Padrão: [1, 7, 14].

        Returns:
            pd.DataFrame: Tabela estruturada contendo as colunas de lag alinhadas no tempo.
        """
        # Se a lista de defasagens não for informada, define por padrão o dia anterior (1) e semanas anteriores (7 e 14).
        if defasagens_dias is None:
            defasagens_dias = [1, 7, 14]

        # '.copy()' isola as mutações na memória RAM para garantir idoneidade científica do processo.
        df_lags = dados.copy()

        # Itera ordenadamente por cada salto de defasagem solicitado pelo cientista de dados.
        for salto in defasagens_dias:
            # Constrói o nome canónico da nova coluna derivativa (ex.: 'demanda_lag_1d', 'demanda_lag_7d').
            nome_coluna_lag = f"{coluna_alvo}_lag_{salto}d"

            # '.shift(salto)' desloca a série para baixo no eixo vertical, puxando o valor de N dias passados para a linha atual.
            df_lags[nome_coluna_lag] = df_lags[coluna_alvo].shift(salto)

        # 'logging.info' registra a quantidade de colunas de defasagem agregadas à matriz.
        logging.info(
            "Engenharia de Features: %d atributos de defasagem (Lags) gerados sobre a variável '%s'.",
            len(defasagens_dias),
            coluna_alvo,
        )

        # Retorna a tabela provida das variáveis de memória histórica.
        return df_lags

    # 'def' define o método especialista no cálculo de médias móveis sobre janelas deslizantes (Rolling Windows).
    @staticmethod
    def calcular_medias_moveis(
        dados: pd.DataFrame,
        coluna_alvo: str,
        janelas_dias: Optional[List[int]] = None,
    ) -> pd.DataFrame:
        """Computa médias móveis deslizantes protegidas contra vazamento de dados através de defasagem prévia.

        Args:
            dados (pd.DataFrame): Tabela contendo a série temporal de medições ordenada.
            coluna_alvo (str): Métrica numérica base para o cálculo das janelas móveis de tendência.
            janelas_dias (Optional[List[int]], opcional): Extensão das janelas em dias. Padrão: [7, 15, 30].

        Returns:
            pd.DataFrame: Tabela enriquecida com os indicadores de tendência suavizada por média móvel.
        """
        # Se as extensões de janela não forem parametrizadas, assume 7 dias (semanal), 15 dias e 30 dias (mensal).
        if janelas_dias is None:
            janelas_dias = [7, 15, 30]

        # Cria uma cópia independente dos dados em memória.
        df_medias = dados.copy()

        # Itera sobre cada tamanho de janela cronológica configurada.
        for tamanho in janelas_dias:
            nome_coluna_media = f"{coluna_alvo}_media_movel_{tamanho}d"

            # '.shift(1)' aplica uma defasagem protetora fundamental: garante que o cálculo NUNCA enxergue o próprio dia (Anti-Leakage).
            # '.rolling(window=tamanho)' estabelece o horizonte móvel deslizante sobre as linhas passadas.
            # '.mean()' extrai a média aritmética dos valores contidos dentro da janela deslizante.
            # '.round(2)' limita a precisão numérica a duas casas decimais para rigor monetário e volumétrico.
            df_medias[nome_coluna_media] = (
                df_medias[coluna_alvo]
                .shift(1)
                .rolling(window=tamanho)
                .mean()
                .round(2)
            )

        # Emite log confirmando a geração bem-sucedida das variáveis de tendência móvel.
        logging.info(
            "Engenharia de Features: %d médias móveis deslizantes geradas com proteção anti-vazamento.",
            len(janelas_dias),
        )

        # Devolve o DataFrame consolidado com as novas métricas de tendência.
        return df_medias