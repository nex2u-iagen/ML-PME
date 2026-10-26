"""Módulo de Diagnóstico Estatístico e Testes de Hipóteses.

Fornece ferramentas matemáticas padronizadas para validar pressupostos
de normalidade, calcular medidas de forma (assimetria e curtose), matrizes
de correlação e diagnóstico de multicolinearidade (VIF).
"""

# 'import' traz o módulo 'logging' da biblioteca padrão do Python.
# Ele serve para registrar eventos, avisos e etapas do cálculo no terminal com data e
# hora.
import logging

# 'from' acessa o módulo 'typing' da biblioteca padrão do Python.
# 'import' traz 'Any' (qualquer tipo) e 'Dict' (dicionário de chave e valor).
# Usamos essas ferramentas para documentar formalmente o que entra e o que sai das
# funções.
from typing import Any

# 'import' traz a biblioteca externa 'numpy', o motor matemático fundamental do Python.
# 'as' cria o apelido 'np', convenção mundial para operações com matrizes e vetores
# numéricos.
import numpy as np

# 'import' traz a biblioteca externa 'pandas', especialista em estruturas de dados
# tabulares.
# 'as' cria o apelido 'pd', padrão da indústria para manipulação de tabelas
# (DataFrames).
import pandas as pd

# 'import' traz a biblioteca 'statsmodels.api' (referência para modelos econométricos e
# testes).
# 'as' define o apelido reduzido 'sm' para chamar os testes estatísticos formais.
import statsmodels.api as sm

# 'from' acessa a biblioteca científica 'scipy' (Scientific Python).
# 'import' traz o submódulo 'stats', que contém funções especializadas em estatística
# teórica.
from scipy import stats

# 'from' navega dentro da estrutura profunda do statsmodels até a pasta de influência de
# outliers.
# 'import' traz a função 'variance_inflation_factor' para calcular o Fator de Inflação
# da Variância (VIF).
from statsmodels.stats.outliers_influence import variance_inflation_factor

# 'logging.basicConfig' configura a apresentação das mensagens no terminal.
# 'level=logging.INFO' garante que mensagens operacionais importantes sejam mostradas na
# tela.
# 'format' dita o padrão visual: ano-mês-dia hora:minuto:segundo — [NÍVEL] — texto da
# mensagem.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' é a palavra reservada para declarar um novo modelo ou molde de código.
# 'CalculadoraEstatistica' é o nome da nossa classe orientada a objetos em Português do
# Brasil.
class CalculadoraEstatistica:
    """Classe responsável por cálculos estatísticos e validação de hipóteses."""

    # O caractere '@' marca um decorador; 'staticmethod' avisa que o método é estático.
    # Métodos estáticos não usam 'self', ou seja, você não precisa criar um objeto na
    # memória para usá-los.
    @staticmethod
    # 'def' define a função 'diagnosticar_distribuicao'.
    # 'serie: pd.Series' é o parâmetro obrigatório: deve ser uma coluna unidimensional
    # de dados do pandas.
    # '-> Dict[str, Any]' avisa que a função devolverá um dicionário com chaves de texto
    # e valores variados.
    def diagnosticar_distribuicao(serie: pd.Series) -> dict[str, Any]:
        """Calcula parâmetros de distribuição e executa o teste de Jarque-Bera.

        Args:
            serie (pd.Series): Coluna contínua contendo os dados a serem diagnosticados.

        Returns:
            Dict[str, Any]: Dicionário com média, desvio, assimetria, curtose e p-valor.
        """
        # 'serie.dropna()' remove valores nulos/vazios da coluna para não corromper as
        # fórmulas matemáticas.
        # 'dados_limpos' é a nova variável do tipo Series armazenando apenas números
        # válidos.
        dados_limpos = serie.dropna()

        # 'np.mean()' calcula a Média Aritmética somando todos os termos e dividindo
        # pelo total.
        # 'float()' força a conversão do resultado em um número decimal de ponto
        # flutuante padrão do Python.
        media = float(np.mean(dados_limpos))

        # 'np.median()' calcula a Mediana, o valor exato que separa os 50% menores dos
        # 50% maiores dados.
        mediana = float(np.median(dados_limpos))

        # 'np.std()' calcula o Desvio Padrão Amostral (dispersão dos dados em relação à
        # média).
        # 'ddof=1' (Delta Degrees of Freedom) aplica a correção de Bessel para amostras
        # (divide por N-1).
        desvio_padrao = float(np.std(dados_limpos, ddof=1))

        # 'stats.skew()' calcula o Coeficiente de Assimetria (se a curva pende para a
        # esquerda ou direita).
        # Valor zero indica simetria perfeita; valores maiores que zero indicam cauda
        # longa à direita.
        assimetria = float(stats.skew(dados_limpos))

        # 'stats.kurtosis()' calcula a Curtose de Fisher (o achatamento da
        # distribuição).
        # Distribuições normais possuem curtose próxima de zero na convenção de Fisher.
        curtose = float(stats.kurtosis(dados_limpos))

        # 'sm.stats.stattools.jarque_bera()' executa o teste de hipótese formal de
        # Jarque-Bera.
        # Hipótese Nula (H0): Os dados seguem uma Distribuição Normal Gaussiana.
        # '[:2]' seleciona apenas os dois primeiros retornos: a estatística de teste e o
        # valor-p (p-valor).
        estatistica_jb, p_valor_jb = sm.stats.stattools.jarque_bera(dados_limpos)[:2]

        # 'logging.info' emite um registro no console com o resumo dos cálculos para
        # fins de auditoria.
        # 'serie.name' extrai o nome original da coluna analisada.
        logging.info(
            "Diagnóstico concluído para '%s'. Assimetria: %.2f | p-valor JB: %.4e",
            serie.name,
            assimetria,
            p_valor_jb,
        )

        # 'resultado' é uma variável do tipo dicionário Python (Dict) criada usando
        # chaves '{}'.
        # Mapeamos termos amigáveis para que qualquer usuário leia o laudo matemático
        # com facilidade.
        resultado = {
            "nome_variavel": str(serie.name),
            "total_amostras": int(len(dados_limpos)),
            "media": media,
            "mediana": mediana,
            "desvio_padrao": desvio_padrao,
            "coeficiente_assimetria": assimetria,
            "curtose": curtose,
            "estatistica_jarque_bera": float(estatistica_jb),
            "p_valor": float(p_valor_jb),
            # 'p_valor_jb > 0.05' avalia a hipótese nula com nível de significância
            # clássico alfa = 5%.
            # Se for Verdadeiro (True), não rejeitamos H0; assumimos que a variável é
            # aproximadamente Normal.
            "segue_distribuicao_normal": bool(p_valor_jb > 0.05),
        }

        # 'return' devolve o dicionário estruturado para quem chamou o método.
        return resultado

    # Segundo método estático da classe, dedicado a relações lineares entre colunas.
    @staticmethod
    # 'dados: pd.DataFrame' exige a tabela completa com as variáveis de negócio.
    # 'metodo: str = "pearson"' define a técnica padrão como correlação de Pearson
    # (linear).
    # '-> pd.DataFrame' documenta que o retorno será uma matriz quadrada em formato
    # tabular.
    def calcular_matriz_correlacao(
        dados: pd.DataFrame,
        metodo: str = "pearson",
    ) -> pd.DataFrame:
        """Gera a matriz de correlação univariada entre pares de colunas numéricas.

        Args:
            dados (pd.DataFrame): Tabela de dados contendo as variáveis a comparar.
            metodo (str, opcional): 'pearson' (linear) ou 'spearman' (postos). Padrão:
            'pearson'.

        Returns:
            pd.DataFrame: Matriz com coeficientes de correlação variando de -1.0 a +1.0.
        """
        # 'dados.select_dtypes()' filtra a tabela, mantendo apenas colunas que possuem
        # tipos numéricos.
        # 'include=[np.number]' garante que colunas de texto ou datas não quebrem a
        # matemática.
        dados_numericos = dados.select_dtypes(include=[np.number])

        # Emite log avisando quantas variáveis numéricas serão correlacionadas.
        logging.info(
            "Calculando matriz de correlação (%s) para %d colunas.",
            metodo,
            dados_numericos.shape[1],
        )

        # '.corr(method=metodo)' executa o cálculo matricial vetorizado no pandas.
        # 'return' entrega a matriz bidimensional resultante.
        return dados_numericos.corr(method=metodo)

    # Terceiro método estático da classe, focado em detectar redundâncias perigosas
    # entre atributos.
    @staticmethod
    # 'dados: pd.DataFrame' recebe a matriz de variáveis preditoras (sem a variável alvo
    # y).
    # '-> pd.DataFrame' devolve uma tabela listando cada coluna e seu respectivo índice
    # VIF.
    def calcular_fator_inflacao_variancia(dados: pd.DataFrame) -> pd.DataFrame:
        """Calcula o VIF (Variance Inflation Factor) para diagnosticar
        multicolinearidade.

        Um VIF acima de 5 ou 10 indica forte dependência linear entre variáveis,
        o que prejudica a estabilidade dos coeficientes em modelos lineares.

        Args:
            dados (pd.DataFrame): Tabela contendo apenas variáveis numéricas contínuas
            explicativas.

        Returns:
            pd.DataFrame: Tabela ordenada com o índice VIF de cada coluna.
        """
        # Filtra apenas colunas numéricas e remove linhas com valores faltantes para
        # permitir o cálculo.
        dados_numericos = dados.select_dtypes(include=[np.number]).dropna()

        # 'lista_vif' é uma lista vazia do Python ('[]') criada para acumular nossos
        # dicionários de dados.
        lista_vif = []

        # 'dados_numericos.shape[1]' retorna a contagem inteira de quantas colunas
        # existem na tabela.
        total_colunas = dados_numericos.shape[1]

        # 'dados_numericos.values' converte a tabela do pandas em uma matriz NumPy pura
        # de alta velocidade.
        matriz_valores = dados_numericos.values

        # 'for' itera por cada índice de coluna (0, 1, 2, ... até o total de colunas).
        # 'range(total_colunas)' gera a sequência de números inteiros para o laço.
        for indice_coluna in range(total_colunas):
            # 'dados_numericos.columns[indice_coluna]' recupera o nome em texto da
            # coluna atual.
            nome_coluna = dados_numericos.columns[indice_coluna]

            # 'variance_inflation_factor()' executa a regressão auxiliar de uma coluna
            # contra todas as outras.
            # O VIF é calculado como 1 / (1 - R²), medindo o quanto a variância do
            # coeficiente é inflada.
            valor_vif = float(variance_inflation_factor(matriz_valores, indice_coluna))

            # '.append()' adiciona um novo dicionário no final da nossa lista.
            lista_vif.append(
                {
                    "variavel": nome_coluna,
                    "indice_vif": valor_vif,
                    # Convenção estatística: VIF > 5.0 aponta risco moderado; VIF > 10.0
                    # aponta multicolinearidade severa.
                    "risco_multicolinearidade": bool(valor_vif > 5.0),
                }
            )

        # 'pd.DataFrame(lista_vif)' converte a lista de dicionários em uma tabela
        # organizada do pandas.
        tabela_vif = pd.DataFrame(lista_vif)

        # '.sort_values()' ordena as linhas da tabela pelo valor do VIF de forma
        # decrescente (do maior para o menor).
        # 'ascending=False' garante que as variáveis mais problemáticas fiquem no topo
        # da tabela.
        tabela_ordenada = tabela_vif.sort_values(
            by="indice_vif", ascending=False
        ).reset_index(drop=True)

        # 'return' devolve a tabela final de diagnóstico de redundância.
        return tabela_ordenada
