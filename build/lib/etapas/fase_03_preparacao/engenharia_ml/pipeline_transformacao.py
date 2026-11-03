"""Módulo de Construção de Pipelines de Transformação Matemática (Fase 3.2).

Responsabilidade Única: Encapsular a fábrica de pré-processamento do Scikit-Learn
utilizando o ColumnTransformer com a diretiva set_output(transform='pandas') ativada
desde a construção, garantindo que transformações numéricas e categóricas retenham
os nomes das colunas de treino até a inferência em produção sem atritos de metadados[cite: 8, 9, 10].
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro de auditoria no terminal[cite: 8].
import logging

# 'from' acessa 'typing' da biblioteca padrão para anotação estática rigorosa[cite: 8].
from typing import List

# 'from' acessa os estimadores compostos do Scikit-Learn voltados para segregação de colunas[cite: 9, 10]:
from sklearn.compose import ColumnTransformer

# 'from' importa os imputadores matemáticos oficiais do Scikit-Learn para dados ausentes (NaN)[cite: 9, 10]:
from sklearn.impute import SimpleImputer

# 'from' importa a classe 'Pipeline' para encadear operações seriais de transformação[cite: 9, 10].
from sklearn.pipeline import Pipeline

# 'from' acessa os pré-processadores estatísticos de padronização e codificação categórica[cite: 9, 10]:
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# 'from' importa o transformador customizado do núcleo para ceifar anomalias estatísticas por IQR[cite: 8].
from src.nucleo.aprendizado_maquina.transformadores_dados import (
    TruncadorDeValoresExtremos,
)

# 'logging.basicConfig' parametriza a formatação dos registros operacionais no terminal[cite: 8].
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara a fábrica estrutural especializada na montagem de pipelines modulares[cite: 8].
class ConstrutorPipelineTransformacao:
    """Fábrica de montagem de esteiras matemáticas de pré-processamento compatíveis com o Scikit-Learn[cite: 8, 9]."""

    @staticmethod
    def montar_pre_processador_completo(
        colunas_numericas: List[str],
        colunas_categoricas: List[str],
        aplicar_corte_outliers: bool = True,
    ) -> ColumnTransformer:
        """Monta o ColumnTransformer encapsulando imputação, truncamento IQR e codificação binária nativa em Pandas[cite: 8, 9].

        Args:
            colunas_numericas (List[str]): Lista com as variáveis contínuas numéricas mapeadas na base[cite: 8].
            colunas_categoricas (List[str]): Lista com as variáveis textuais nominais mapeadas na base[cite: 8].
            aplicar_corte_outliers (bool, opcional): Sinaliza se o truncador IQR deve ser ativado. Padrão: True[cite: 8].

        Returns:
            ColumnTransformer: Transformador modular com saída configurada nativamente para DataFrame do Pandas[cite: 8, 9, 10].
        """
        # Passos sequenciais da esteira numérica[cite: 8, 9]:
        passos_numericos = [
            ("imputador_mediana", SimpleImputer(strategy="median")),
        ]

        if aplicar_corte_outliers:
            passos_numericos.append(
                (
                    "truncador_iqr",
                    TruncadorDeValoresExtremos(multiplicador_iqr=1.5),
                )
            )

        passos_numericos.append(("escalonador_padrao", StandardScaler()))

        pipeline_numerico = Pipeline(steps=passos_numericos)

        # Passos sequenciais da esteira categórica[cite: 8, 9]:
        pipeline_categorico = Pipeline(
            steps=[
                (
                    "imputador_frequencia",
                    SimpleImputer(strategy="most_frequent"),
                ),
                (
                    "codificador_one_hot",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                ),
            ]
        )

        # Montagem do ColumnTransformer unificado[cite: 8, 9]:
        transformador_unificado = ColumnTransformer(
            transformers=[
                ("ramo_numerico", pipeline_numerico, colunas_numericas),
                ("ramo_categorico", pipeline_categorico, colunas_categoricas),
            ],
            remainder="drop",
        )

        # AJUSTE CIRÚRGICO NA RAIZ DA FASE 3:
        # Configura o transformador para operar e devolver Pandas DataFrames ANTES do fit[cite: 9, 10]!
        # Isso garante que todos os passos internos (Imputer, Truncador, Scaler, Encoder) aprendam
        # diretamente com nomes de features desde o primeiro instante.
        try:
            transformador_unificado.set_output(transform="pandas")
            logging.info("Saída nativa em Pandas configurada com sucesso no ColumnTransformer.")
        except Exception as erro:
            logging.debug("Versão do Scikit-Learn sem suporte nativo a set_output: %s", erro)

        logging.info(
            "Pipeline de Transformação montado: %d numéricas e %d categóricas configuradas.",
            len(colunas_numericas),
            len(colunas_categoricas),
        )

        return transformador_unificado