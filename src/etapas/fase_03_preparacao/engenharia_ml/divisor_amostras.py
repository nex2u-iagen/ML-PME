"""Módulo de Particionamento e Divisão de Amostras para Machine Learning (Fase 3.2).

Responsabilidade Única: Executar a separação física e metodológica das partições
de dados (Treino, Validação e Teste Real), implementando tanto a divisão estratificada
para problemas de classificação quanto o corte cronológico estrito para séries temporais.
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registros técnicos no console.
import logging

# 'from' acessa o módulo 'typing' da biblioteca padrão para anotação de tuplas heterogêneas de saída.
from typing import Tuple

# 'import' traz a biblioteca externa 'pandas' para manipulação tabular de matrizes de features e vetores-alvo.
import pandas as pd

# 'from' acessa o módulo de seleção de modelos do Scikit-Learn para fatiamento pseudoaleatório seguro[cite: 8, 12].
# 'train_test_split' divide matrizes em subconjuntos respeitando proporções pré-definidas e sementes estatísticas[cite: 8, 12].
from sklearn.model_selection import train_test_split

# 'logging.basicConfig' parametriza a formatação visual dos alertas técnicos no console corporativo.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara o molde arquitetural especialista na segregação de partições de dados para modelagem.
class DivisorAmostrasML:
    """Classe responsável pelo particionamento metodológico de dados para validação e treino de algoritmos[cite: 8, 12]."""

    # 'def' define o método especialista na divisão aleatória tripla estratificada (para Classificação e Crédito).
    @staticmethod
    def dividir_aleatorio_estratificado(
        x: pd.DataFrame,
        y: pd.Series,
        proporcao_teste: float = 0.15,
        proporcao_validacao: float = 0.15,
        semente_aleatoria: int = 42,
    ) -> Tuple[
        pd.DataFrame,
        pd.Series,
        pd.DataFrame,
        pd.Series,
        pd.DataFrame,
        pd.Series,
    ]:
        """Realiza o particionamento triplo estratificado (Treino / Validação / Teste) preservando a proporção de classes[cite: 8, 12].

        Args:
            x (pd.DataFrame): Matriz tabular de variáveis preditoras explicativas (Features).
            y (pd.Series): Vetor unidimensional contendo a variável dependente alvo (Target).
            proporcao_teste (float, opcional): Fração final reservada para teste cego. Padrão: 0.15 (15%).
            proporcao_validacao (float, opcional): Fração reservada para ajuste de hiperparâmetros. Padrão: 0.15 (15%).
            semente_aleatoria (int, opcional): Semente matemática para reprodutibilidade. Padrão: 42.

        Returns:
            Tuple: Coleção ordenada contendo (x_treino, y_treino, x_val, y_val, x_teste, y_teste)[cite: 12].
        """
        # Calcula a soma percentual das partições que ficarão fora do treinamento inicial (Holdout: Validação + Teste).
        proporcao_holdout = proporcao_teste + proporcao_validacao

        # CONTAGEM DEFENSIVA CONTRA BASES MINÚSCULAS:
        # Inspeciona a frequência da menor classe presente no vetor resposta y para avaliar a viabilidade de estratificação.
        tamanho_classe_minoria = y.value_counts().min()

        # Se a classe de menor frequência tiver menos de 2 exemplares, desativa a estratificação para impedir exceções de execução.
        if tamanho_classe_minoria < 2:
            estratificador_fase_1 = None
            logging.warning(
                "Divisão de Dados: Menor classe possui apenas %d registo(s). Estratificação desativada defensivamente.",
                tamanho_classe_minoria,
            )
        else:
            estratificador_fase_1 = y

        # PRIMEIRA DIVISÃO: Separa o subconjunto de Treino definitivo (ex.: 70%) da fatia de Holdout agregada (ex.: 30%)[cite: 12].
        x_treino, x_holdout, y_treino, y_holdout = train_test_split(
            x,
            y,
            test_size=proporcao_holdout,
            random_state=semente_aleatoria,
            stratify=estratificador_fase_1,
        )

        # Avalia novamente a proporção da minoria dentro da fatia de Holdout para a segunda segregação.
        tamanho_minoria_holdout = y_holdout.value_counts().min()

        # Condiciona a estratificação da segunda partição à presença de volume estatístico suficiente.
        if estratificador_fase_1 is None or tamanho_minoria_holdout < 2:
            estratificador_fase_2 = None
        else:
            estratificador_fase_2 = y_holdout

        # Calcula a fração relativa interna necessária para fatiar o Holdout proporcionalmente entre Validação e Teste[cite: 12].
        fator_corte_interno = proporcao_teste / proporcao_holdout

        # SEGUNDA DIVISÃO: Fatia o Holdout em duas metades perfeitamente balanceadas (Validação e Teste Real)[cite: 12].
        x_val, x_teste, y_val, y_teste = train_test_split(
            x_holdout,
            y_holdout,
            test_size=fator_corte_interno,
            random_state=semente_aleatoria,
            stratify=estratificador_fase_2,
        )

        # Registra a confirmação formal das volumetrias segregadas no terminal corporativo.
        logging.info(
            "Divisão Estratificada concluída: Treino=%d amostras | Validação=%d amostras | Teste=%d amostras.",
            len(x_treino),
            len(x_val),
            len(x_teste),
        )

        # Devolve as seis partições devidamente isoladas e blindadas.
        return x_treino, y_treino, x_val, y_val, x_teste, y_teste

    # 'def' define o método especialista na divisão cronológica de séries temporais (para Demanda de SKUs e Vendas).
    @staticmethod
    def dividir_aleatorio_simples(
        x: pd.DataFrame,
        proporcao_teste: float = 0.15,
        proporcao_validacao: float = 0.15,
        semente_aleatoria: int = 42,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Realiza o particionamento triplo aleatório para tarefas não supervisionadas.

        Utilizado por agrupamento e detecção de anomalias, onde não existe vetor-alvo
        e, portanto, não há classe minoritária a preservar na estratificação.

        Args:
            x (pd.DataFrame): Matriz tabular de variáveis preditoras explicativas.
            proporcao_teste (float, opcional): Fração final reservada para teste cego. Padrão: 0.15.
            proporcao_validacao (float, opcional): Fração reservada para validação. Padrão: 0.15.
            semente_aleatoria (int, opcional): Semente matemática para reprodutibilidade. Padrão: 42.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Coleção (x_treino, x_val, x_teste).
        """
        proporcao_holdout = proporcao_teste + proporcao_validacao
        fator_corte_interno = proporcao_teste / proporcao_holdout

        x_treino, x_holdout = train_test_split(
            x,
            test_size=proporcao_holdout,
            random_state=semente_aleatoria,
        )
        x_val, x_teste = train_test_split(
            x_holdout,
            test_size=fator_corte_interno,
            random_state=semente_aleatoria,
        )

        logging.info(
            "Divisão Simples (não supervisionada) concluída: Treino=%d | Validação=%d | Teste=%d.",
            len(x_treino),
            len(x_val),
            len(x_teste),
        )
        return x_treino, x_val, x_teste

    # 'def' define o método especialista na divisão cronológica de séries temporais (para Demanda de SKUs e Vendas).
    @staticmethod
    def dividir_cronologico_temporal(
        dados: pd.DataFrame,
        coluna_data: str,
        proporcao_teste: float = 0.15,
        proporcao_validacao: float = 0.15,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Realiza o corte temporal cronológico estrito garantindo que o futuro NUNCA seja utilizado para prever o passado.

        Args:
            dados (pd.DataFrame): Tabela de medições cronológicas ordenada de forma ascendente no tempo.
            coluna_data (str): Nome da coluna que dita a linha do tempo do negócio.
            proporcao_teste (float, opcional): Fração cronológica final destinada a teste. Padrão: 0.15.
            proporcao_validacao (float, opcional): Fração intermediária para validação. Padrão: 0.15.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Três blocos na ordem exata (df_treino, df_val, df_teste).
        """
        # Garante a ordenação cronológica rigorosa de forma ascendente pela coluna de data antes de qualquer corte[cite: 8].
        dados_ordenados = dados.sort_values(by=coluna_data).reset_index(
            drop=True
        )

        # Computa a contagem total de registros temporais existentes na série.
        total_linhas = len(dados_ordenados)

        # Define o ponto de corte do Treinamento histórico (ex.: até a linha que representa os primeiros 70%).
        ponto_corte_treino = int(
            total_linhas * (1.0 - (proporcao_teste + proporcao_validacao))
        )

        # Define o ponto de corte onde termina a Validação e tem início a janela de Teste Real.
        ponto_corte_val = int(total_linhas * (1.0 - proporcao_teste))

        # Fatia os dados utilizando fatiamento posicional explícito com '.iloc' do pandas.
        df_treino = dados_ordenados.iloc[:ponto_corte_treino].copy()
        df_val = dados_ordenados.iloc[ponto_corte_treino:ponto_corte_val].copy()
        df_teste = dados_ordenados.iloc[ponto_corte_val:].copy()

        # Emite log confirmando a aplicação do corte cronológico seguro contra fugas de dados[cite: 8].
        logging.info(
            "Divisão Temporal estrita: Treino (Linhas 0 a %d) | Validação (%d a %d) | Teste (%d a %d).",
            ponto_corte_treino,
            ponto_corte_treino,
            ponto_corte_val,
            ponto_corte_val,
            total_linhas,
        )

        # Devolve as três fatias temporais perfeitamente sequenciadas no tempo.
        return df_treino, df_val, df_teste