"""Módulo de Transformadores Customizados para Aprendizado de Máquina.

Implementa componentes de engenharia de atributos e limpeza de dados
aderentes ao protocolo formal do Scikit-Learn, garantindo integração
nativa com Pipelines e isolamento absoluto contra Data Leakage.
"""

# 'import' carrega o módulo interno 'logging' da biblioteca padrão do Python.
# O logging registra mensagens operacionais e de auditoria no terminal de forma
# profissional.
import logging

# 'from' acessa o módulo 'typing' da biblioteca padrão do Python.
# 'Self' (Python 3.11+) representa o tipo da própria classe retornada por seus métodos
# internos.
from typing import Self

# 'import' traz a biblioteca fundamental 'numpy', responsável pelo processamento
# matricial e vetorial rápido.
# 'as' define o apelido universal 'np', padrão consagrado pela comunidade científica.
import numpy as np

# 'import' traz a biblioteca 'pandas', padrão da indústria para manipulação tabular de
# dados.
# 'as' define o apelido clássico 'pd' para encurtar comandos de manipulação de tabelas.
# 'from' navega até o submódulo base do Scikit-Learn ('sklearn.base').
# 'BaseEstimator' concede ao nosso objeto compatibilidade com clonagem e otimizadores de
# hiperparâmetros.
# 'TransformerMixin' injeta automaticamente o método 'fit_transform()' combinando
# aprendizado e execução.
from sklearn.base import BaseEstimator, TransformerMixin

# 'logging.basicConfig' padroniza o formato visual das mensagens emitidas no console.
# 'level=logging.INFO' assegura que avisos informativos e confirmações de etapas sejam
# exibidos na tela.
# 'format' dita o modelo da mensagem: data/hora — [gravidade] — descrição detalhada do
# evento.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' é a palavra-chave que declara um novo molde estrutural orientado a objetos.
# 'TruncadorDeValoresExtremos' é o nome da nossa classe em Português do Brasil e estilo
# PascalCase.
# '(BaseEstimator, TransformerMixin)' indica 'Herança Múltipla': nossa classe herda as
# habilidades oficiais do scikit-learn.
class TruncadorDeValoresExtremos(BaseEstimator, TransformerMixin):
    """Transformador para truncamento (clipping) de valores atípicos baseado no IQR.

    Aprende os limites estatísticos estritamente sobre a partição de treino (fit)
    e os reaplica de maneira determinística nas partições de teste ou inferência
    (transform).
    """

    # 'def' define o método construtor '__init__', executado no momento da instanciação
    # da classe.
    # 'self' referencia a instância individual sendo gerada na memória do computador.
    # 'multiplicador_iqr: float = 1.5' exige um número decimal (float), fixando 1.5 como
    # sensibilidade padrão de Tukey.
    # '-> None' documenta que o construtor apenas inicializa atributos e não devolve
    # dados.
    def __init__(self, multiplicador_iqr: float = 1.5) -> None:
        """Inicializa o estimador configurando a sensibilidade da régua interquartil.

        Args:
            multiplicador_iqr (float, opcional): Fator multiplicador do IQR. Padrão: 1.5
            (Tukey).
        """
        # 'self.multiplicador_iqr' guarda o valor do multiplicador como um atributo
        # interno do objeto.
        self.multiplicador_iqr = multiplicador_iqr

        # 'self.limite_inferior_' guarda os pisos matemáticos calculados por coluna.
        # Por convenção estrita do Scikit-Learn, atributos aprendidos no fit terminam
        # com um sublinhado '_'.
        # Inicializamos com 'None' (vazio) pois o aprendizado ainda não ocorreu.
        self.limite_inferior_ = None

        # 'self.limite_superior_' guarda os tetos matemáticos calculados por coluna.
        # Também começa como 'None' até que o método fit seja formalmente executado.
        self.limite_superior_ = None

        # Emite log confirmando a configuração do estimador.
        logging.info(
            "Transformador IQR inicializado com multiplicador: %.2f",
            self.multiplicador_iqr,
        )

    # 'def' declara o método central de aprendizado 'fit'.
    # 'X' representa a matriz tabular contendo as variáveis preditoras contínuas
    # (DataFrame ou NumPy Array).
    # 'y=None' aceita o vetor alvo (opcional, exigido pela assinatura padrão do
    # scikit-learn).
    # '-> Self' documenta que o método devolve a própria instância calibrada para
    # permitir encadeamento.
    def fit(self, x, y=None) -> Self:
        """Calcula os limites estatísticos de corte exclusivamente a partir dos dados de
        treino.

        Args:
            x: Conjunto de dados contendo variáveis numéricas explicativas (Pandas
            DataFrame ou NumPy Array).
            y: Variável dependente/alvo (não utilizada em limpezas univariadas).

        Returns:
            Self: A própria instância do transformador com os limites aprendidos e
            memorizados.
        """
        # 'np.asarray' atua como vacina: converte qualquer formato (Pandas, listas) em
        # matriz pura do NumPy.
        x_array = np.asarray(x)

        # Emite log informando o início do cálculo dos limites interquartis.
        logging.info(
            "Iniciando aprendizado dos limites estatísticos (fit) em %d colunas...",
            x_array.shape[1],
        )

        # 'np.nanpercentile' calcula quartis com segurança na sintaxe universal do
        # NumPy, ignorando nulos residuais.
        # 'axis=0' garante que o cálculo seja feito coluna por coluna (verticalmente).
        primeiro_quartil = np.nanpercentile(x_array, 25, axis=0)
        terceiro_quartil = np.nanpercentile(x_array, 75, axis=0)

        # 'intervalo_interquartil' calcula o IQR (Q3 - Q1), que mede o espalhamento
        # central dos 50% intermediários.
        intervalo_interquartil = terceiro_quartil - primeiro_quartil

        # Calcula a barreira inferior: Q1 - (multiplicador * IQR).
        # Atribuímos ao atributo com sufixo '_' para selar a memorização no objeto.
        self.limite_inferior_ = primeiro_quartil - (
            self.multiplicador_iqr * intervalo_interquartil
        )

        # Calcula a barreira superior: Q3 + (multiplicador * IQR).
        # Qualquer dado além desta fronteira será considerado uma anomalia matemática.
        self.limite_superior_ = terceiro_quartil + (
            self.multiplicador_iqr * intervalo_interquartil
        )

        # Emite log confirmando a conclusão do treinamento.
        logging.info(
            "Limites de corte calculados e armazenados com sucesso no formato universal"
            "NumPy."
        )

        # 'return self' devolve o próprio objeto agora enriquecido com a memória
        # estatística.
        return self

    # 'def' define o método executor 'transform'.
    # 'X' recebe os dados que sofrerão o corte (seja treino, validação, teste ou novos
    # dados de produção).
    def transform(self, x, y=None):
        """Aplica o corte numérico (clipping) nos dados utilizando as regras memorizadas
        no fit.

        Args:
            x: Dados a serem transformados sem contaminação estatística (Pandas
            DataFrame ou NumPy Array).
            y: Argumento ignorado, presente para conformidade com a API do Scikit-Learn.

        Returns:
            np.ndarray: Nova matriz com os valores extremos aparados dentro dos limites.

        Raises:
            RuntimeError: Se o transform for executado antes do fit ter sido concluído.
        """
        # 'if' verifica defensivamente se os limites já existem na memória do objeto.
        if self.limite_inferior_ is None or self.limite_superior_ is None:
            # Emite log de erro crítico no terminal.
            logging.error("Tentativa de transformação antes do ajuste (fit).")
            # 'raise' interrompe o programa levantando uma exceção de estado de execução
            # inválido (RuntimeError).
            raise RuntimeError(
                "O transformador deve ser ajustado com o método 'fit()' antes de"
                "executar 'transform()'."
            )

        # Converte e cria uma cópia da matriz para não alterar os dados originais
        # acidentalmente na memória.
        x_array = np.asarray(x).copy()

        # 'np.clip' é uma função vetorizada do NumPy de extrema velocidade.
        # Ela substitui qualquer valor menor que o piso ou maior que o teto pelas
        # próprias barreiras matemáticas aprendidas.
        tabela_truncada = np.clip(x_array, self.limite_inferior_, self.limite_superior_)

        # 'return' entrega a nova matriz perfeitamente protegida contra anomalias
        # numéricas.
        return tabela_truncada

    # 'def' define o método exigido pelo Scikit-Learn para rastreabilidade de atributos
    # de saída.
    # 'input_features' recebe a lista original de nomes das colunas vindas da etapa
    # anterior do pipeline.
    def get_feature_names_out(self, input_features=None):
        """Repassa os nomes originais das colunas para manter a rastreabilidade no
        Scikit-Learn.

        Como o truncador apenas altera os valores internos sem criar ou deletar colunas,
        ele devolve a exata mesma lista de nomes que recebeu.

        Args:
            input_features (array-like, opcional): Lista ou array com os nomes das
            colunas de entrada.

        Returns:
            np.ndarray ou list: Nomes das colunas de saída (idênticos aos de entrada).
        """
        # Devolve os nomes originais para que o orquestrador consiga remontar o
        # DataFrame do Pandas com sucesso.
        return input_features
