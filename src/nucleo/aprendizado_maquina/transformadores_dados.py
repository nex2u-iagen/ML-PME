"""Módulo de Transformadores Customizados para Machine Learning (Núcleo Compartilhado).

Responsabilidade Única: Implementar transformadores matemáticos e adaptadores
de dados compatíveis com a API formal do Scikit-Learn (BaseEstimator e TransformerMixin),
permitindo serialização íntegra via Joblib e integração sem atritos de metadados[cite: 7, 8, 10].
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registro técnico no console.
import logging

# 'from' acessa as classes-base estruturais do Scikit-Learn para construção de estimadores compatíveis.
# 'BaseEstimator' provê métodos padrão de clonagem e inspeção de hiperparâmetros (get_params, set_params).
# 'TransformerMixin' injeta automaticamente o método composto 'fit_transform()' ao implementar 'fit()' e 'transform()'.
from sklearn.base import BaseEstimator, TransformerMixin

# 'import' traz a biblioteca externa 'numpy' para computação vetorizada e checagem de tipos primitivos[cite: 7, 8].
# 'as' define o apelido canônico 'np'[cite: 7, 8].
import numpy as np

# 'import' traz a biblioteca externa 'pandas' para manipulação tabular e criação de DataFrames com cabeçalho[cite: 7, 8].
# 'as' estabelece o apelido oficial 'pd'[cite: 7, 8].
import pandas as pd

# 'logging.basicConfig' parametriza a estética visual e criticidade dos registros no terminal.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara o transformador responsável pelo truncamento estatístico de anomalias (IQR)[cite: 7, 8].
class TruncadorDeValoresExtremos(BaseEstimator, TransformerMixin):
    """Transformador customizado que trunca valores discrepantes (outliers) pela Amplitude Interquartil (IQR)[cite: 7, 8]."""

    def __init__(self, multiplicador_iqr: float = 1.5) -> None:
        """Inicializa o truncador configurando o fator multiplicador do IQR[cite: 7, 8]."""
        self.multiplicador_iqr = multiplicador_iqr
        self.limites_inferiores_: dict[str, float] = {}
        self.limites_superiores_: dict[str, float] = {}

    def fit(self, X: pd.DataFrame | np.ndarray, y: pd.Series | None = None) -> "TruncadorDeValoresExtremos":
        """Calcula os quartis Q1, Q3 e as barreiras estatísticas estritamente sobre a partição de treino[cite: 7, 8]."""
        df_local = pd.DataFrame(X) if isinstance(X, np.ndarray) else X.copy()
        self.limites_inferiores_.clear()
        self.limites_superiores_.clear()

        for coluna in df_local.columns:
            serie_coluna = df_local[coluna].dropna()
            if serie_coluna.empty or not np.issubdtype(serie_coluna.dtype, np.number):
                continue

            q1 = float(serie_coluna.quantile(0.25))
            q3 = float(serie_coluna.quantile(0.75))
            iqr = q3 - q1

            chave_coluna = str(coluna)
            self.limites_inferiores_[chave_coluna] = q1 - (self.multiplicador_iqr * iqr)
            self.limites_superiores_[chave_coluna] = q3 + (self.multiplicador_iqr * iqr)

        return self

    def transform(self, X: pd.DataFrame | np.ndarray) -> pd.DataFrame | np.ndarray:
        """Aplica o ceifamento (clipping) limitando valores discrepantes às fronteiras de treino[cite: 7, 8]."""
        eh_numpy = isinstance(X, np.ndarray)
        df_transformado = pd.DataFrame(X).copy() if eh_numpy else X.copy()

        for coluna in df_transformado.columns:
            chave_coluna = str(coluna)
            if chave_coluna in self.limites_inferiores_ and chave_coluna in self.limites_superiores_:
                df_transformado[coluna] = df_transformado[coluna].clip(
                    lower=self.limites_inferiores_[chave_coluna],
                    upper=self.limites_superiores_[chave_coluna],
                )

        return df_transformado.to_numpy() if eh_numpy else df_transformado

    def get_feature_names_out(self, input_features: np.ndarray | list | None = None) -> np.ndarray:
        """Propaga os nomes das colunas sem alteração para manter o contrato do Pipeline[cite: 7, 8]."""
        if input_features is not None:
            return np.asarray(input_features, dtype=object)
        return np.array(list(self.limites_superiores_.keys()), dtype=object)


# 'class' declara o novo transformador formal especialista em reinserir cabeçalhos em arrays numéricos[cite: 7, 8, 10].
class AdaptadorRotulosDataFrame(BaseEstimator, TransformerMixin):
    """Adaptador de alto nível para compatibilidade entre transformadores NumPy e estimadores Pandas[cite: 8, 10]."""

    # 'def __init__(...)' instancia o adaptador registrando a sequência canônica de colunas da Fase 3.
    def __init__(self, nomes_colunas: list[str] | None = None) -> None:
        """Inicializa o adaptador configurando a lista ordenada de colunas esperadas pelo classificador[cite: 8, 10].

        Args:
            nomes_colunas (list[str], opcional): Lista com os nomes dos atributos gerados na Fase 3.
        """
        # Armazena a lista de colunas como atributo de instância serializável pelo Joblib/Pickle[cite: 8, 10].
        self.nomes_colunas = nomes_colunas

    # 'def fit(...)' atende ao contrato formal do Scikit-Learn sem reter parâmetros adicionais (Stateless)[cite: 8].
    def fit(self, X: pd.DataFrame | np.ndarray, y: pd.Series | None = None) -> "AdaptadorRotulosDataFrame":
        """Método de ajuste sem estado (Stateless) que retorna a própria instância calibrada[cite: 7, 8]."""
        return self

    # 'def transform(...)' re-encapsula o array do NumPy de volta para um DataFrame rotulado[cite: 8, 10].
    def transform(self, X: pd.DataFrame | np.ndarray) -> pd.DataFrame:
        """Converte a matriz bidimensional em DataFrame preservando os nomes das colunas de treino[cite: 8, 10].

        Args:
            X (pd.DataFrame ou np.ndarray): Matriz numérica produzida pelo ColumnTransformer[cite: 8, 10].

        Returns:
            pd.DataFrame: Tabela estruturada compatível com as regras de entrada do modelo campeão[cite: 8, 10].
        """
        # Se os dados já forem um DataFrame com colunas preservadas, devolve-os diretamente[cite: 8].
        if isinstance(X, pd.DataFrame):
            return X

        # Converte a matriz NumPy bruta em DataFrame associando as colunas oficiais homologadas[cite: 8, 10]:
        return pd.DataFrame(X, columns=self.nomes_colunas)

    # 'def get_feature_names_out(...)' assegura a propagação formal de metadados para a esteira[cite: 7, 8].
    def get_feature_names_out(self, input_features: np.ndarray | list | None = None) -> np.ndarray:
        """Propaga os nomes das colunas de saída para inspeção formal do Pipeline[cite: 7, 8]."""
        if self.nomes_colunas:
            return np.asarray(self.nomes_colunas, dtype=object)
        return np.asarray(input_features, dtype=object)