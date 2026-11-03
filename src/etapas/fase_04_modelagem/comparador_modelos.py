"""Módulo de Comparação de Modelos de Classificação Supervisionada (Fase 4 - Modelagem).

Responsabilidade Única: Instanciar estimadores candidatos (Baseline Ingênuo,
Regressão Logística, Random Forest e Boosting), treinar estritamente sobre
a partição de treino e mensurar o desempenho na partição de validação.
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registros técnicos no console.
import logging

# 'import numpy as np' fornece manipulação de matrizes numéricas para as métricas.
import numpy as np

# 'from' acessa 'typing' da biblioteca padrão para anotação estática rigorosa de coleções.
from typing import Any, Dict, List, Optional, Tuple

# 'import' traz a biblioteca externa 'pandas' para compilação tabular do ranking de modelos[cite: 9, 12].
import pandas as pd

# 'from' importa estimadores supervisionados oficiais do Scikit-Learn (https://scikit-learn.org/stable/)[cite: 9, 10]:
# - 'DummyClassifier': provê a linha de base ingênua para garantir que os modelos aprendam além do acaso.
from sklearn.dummy import DummyClassifier, DummyRegressor

# - 'LogisticRegression' e 'Ridge': modelos lineares de referência com regularização L2[cite: 10].
from sklearn.linear_model import LogisticRegression, Ridge

# - Random Forest e Gradient Boosting: métodos de conjunto para relações não lineares[cite: 14].
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
    IsolationForest,
    RandomForestClassifier,
    RandomForestRegressor,
)

# - Agrupamento por KMeans e detecção de outliers por LOF.
from sklearn.cluster import KMeans
from sklearn.neighbors import LocalOutlierFactor

# - Métricas formais para avaliação rigorosa de classificação sob desbalanceamento:
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    silhouette_score,
)

# 'logging.basicConfig' parametriza a formatação dos registros operacionais no terminal.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(levelname)s] — %(message)s",
)


# 'class' declara o especialista na experimentação e benchmark automatizado de algoritmos[cite: 8].
class ComparadorModelosClassificacao:
    """Classe responsável pelo treinamento e ranqueamento comparativo de múltiplos algoritmos de IA."""

    # 'def __init__(...)' constrói a instância configurando os algoritmos candidatos e sementes estatísticas[cite: 9].
    def __init__(self, semente_aleatoria: int = 42) -> None:
        """Inicializa o catálogo de algoritmos supervisionados fixando sementes para reprodutibilidade[cite: 9].

        Args:
            semente_aleatoria (int, opcional): Semente pseudoaleatória (random_state). Padrão: 42[cite: 9].
        """
        # Armazena a semente de reprodutibilidade para todos os estimadores que suportam paralelismo estocástico[cite: 9].
        self.semente = semente_aleatoria

        # Catálogo estruturado contendo o nome canônico e a instância de cada modelo competidor[cite: 9, 10, 14]:
        self.modelos_candidatos: Dict[str, Any] = {
            # 1. Marco Zero Ingênuo: Prediz a classe majoritária para estabelecer a régua mínima de acurácia[cite: 9].
            "01_Baseline_Dummy": DummyClassifier(strategy="most_frequent"),
            # 2. Baseline Linear: Regressão Logística com solver lbfgs e regularização L2 clássica[cite: 10].
            "02_Regressao_Logistica": LogisticRegression(
                C=1.0,
                max_iter=1000,
                random_state=self.semente,
                class_weight="balanced",
            ),
            # 3. Floresta Aleatória: 100 árvores de decisão em paralelo para interações complexas[cite: 14].
            "03_Random_Forest": RandomForestClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=self.semente,
                class_weight="balanced",
                n_jobs=-1,
            ),
            # 4. Gradient Boosting Histórico: Algoritmo de boosting ultra-rápido baseado em histogramas[cite: 14].
            "04_Hist_Gradient_Boosting": HistGradientBoostingClassifier(
                max_iter=100,
                max_depth=5,
                random_state=self.semente,
                class_weight="balanced",
            ),
        }

        # Dicionário interno para preservar as instâncias de estimadores já ajustados (.fit)[cite: 9].
        self.modelos_treinados: Dict[str, Any] = {}

    # 'def executar_treinamento_e_benchmark(...)' itera pelos modelos, calcula métricas e monta o placar[cite: 9].
    def executar_treinamento_e_benchmark(
        self,
        X_treino: pd.DataFrame,
        y_treino: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
    ) -> Tuple[pd.DataFrame, Any, str]:
        """Treina os estimadores sobre o conjunto de treino e avalia o poder preditivo no conjunto de validação[cite: 9, 13].

        Args:
            X_treino (pd.DataFrame): Atributos preditivos normalizados da partição de treino[cite: 9].
            y_treino (pd.Series): Rótulo binário da partição de treino (0 = Em Dia, 1 = Inadimplente)[cite: 9].
            X_val (pd.DataFrame): Atributos preditivos da partição de validação[cite: 9].
            y_val (pd.Series): Rótulo binário da partição de validação[cite: 9].

        Returns:
            Tuple[pd.DataFrame, Any, str]: Tabela com o placar de métricas, objeto do modelo campeão e nome do campeão[cite: 9].
        """
        logging.info("Iniciando bateria de treinamento e avaliação sobre %d algoritmos...", len(self.modelos_candidatos))

        linhas_placar: List[Dict[str, Any]] = []

        # Itera por cada algoritmo candidato do catálogo[cite: 9].
        for nome_modelo, estimador in self.modelos_candidatos.items():
            logging.info("Treinando modelo: '%s'...", nome_modelo)

            # 1. Ajuste estrito do estimador utilizando EXCLUSIVAMENTE os dados de treino[cite: 9, 13]:
            estimador.fit(X_treino, y_treino)

            # Guarda o modelo ajustado na memória da instância[cite: 9].
            self.modelos_treinados[nome_modelo] = estimador

            # 2. Predição discreta (0 ou 1) sobre a partição de validação cega[cite: 9]:
            predicoes_classes = estimador.predict(X_val)

            # 3. Predição contínua de probabilidades P(y=1) para cômputo da Curva ROC-AUC[cite: 9, 10]:
            if hasattr(estimador, "predict_proba"):
                predicoes_probabilidades = estimador.predict_proba(X_val)[:, 1]
                # 'roc_auc_score' avalia a capacidade do modelo em ranquear clientes de maior risco no topo[cite: 9].
                valor_roc_auc = round(float(roc_auc_score(y_val, predicoes_probabilidades)), 4)
            else:
                valor_roc_auc = 0.5000

            # 4. Cálculo das métricas fundamentais de classificação em conformidade acadêmica[cite: 9]:
            acuracia = round(float(accuracy_score(y_val, predicoes_classes)), 4)
            precisao = round(float(precision_score(y_val, predicoes_classes, zero_division=0)), 4)
            revogacao = round(float(recall_score(y_val, predicoes_classes, zero_division=0)), 4)
            f1 = round(float(f1_score(y_val, predicoes_classes, zero_division=0)), 4)

            # Armazena o registro do competidor no placar executivo[cite: 9].
            linhas_placar.append({
                "modelo": nome_modelo,
                "acuracia": acuracia,
                "precisao": precisao,
                "recall": revogacao,
                "f1_score": f1,
                "roc_auc": valor_roc_auc,
            })

            logging.info(
                "Resultado '%s' — F1: %.4f | ROC-AUC: %.4f | Recall: %.4f | Precisão: %.4f",
                nome_modelo, f1, valor_roc_auc, revogacao, precisao
            )

        # Converte os resultados para DataFrame do pandas ordenando pelo F1-Score decrescente[cite: 9].
        df_placar = pd.DataFrame(linhas_placar).sort_values(by="f1_score", ascending=False).reset_index(drop=True)

        # Identifica o modelo campeão que atingiu a maior pontuação de F1 no conjunto de validação[cite: 9].
        nome_campeao = str(df_placar.iloc[0]["modelo"])
        objeto_campeao = self.modelos_treinados[nome_campeao]

        logging.info("Modelo campeão da bateria: '%s' com F1-Score de %.4f.", nome_campeao, df_placar.iloc[0]["f1_score"])
        return df_placar, objeto_campeao, nome_campeao


# ==================================================================================
# COMPARADOR DE REGRESSÃO (Etapa 6 — trilha real para problemas de previsão)
# ==================================================================================
class ComparadorModelosRegressao:
    """Classe responsável pelo torneio de modelos de regressão supervisionada.

    Mantém a mesma interface do comparador de classificação (``executar_treinamento_e_benchmark``),
    mas ordena o placar pela métrica ``r2`` e avalia com R², RMSE, MAE e MAPE.
    """

    def __init__(self, semente_aleatoria: int = 42) -> None:
        """Inicializa o catálogo de regressores candidatos.

        Args:
            semente_aleatoria (int, opcional): Semente para reprodutibilidade. Padrão: 42.
        """
        self.semente = semente_aleatoria

        self.modelos_candidatos: Dict[str, Any] = {
            "01_Baseline_Dummy": DummyRegressor(strategy="mean"),
            "02_Ridge": Ridge(alpha=1.0, random_state=self.semente),
            "03_Random_Forest": RandomForestRegressor(
                n_estimators=100,
                max_depth=6,
                random_state=self.semente,
                n_jobs=-1,
            ),
            "04_Hist_Gradient_Boosting": HistGradientBoostingRegressor(
                max_iter=100,
                max_depth=5,
                random_state=self.semente,
            ),
        }

        self.modelos_treinados: Dict[str, Any] = {}

    def executar_treinamento_e_benchmark(
        self,
        X_treino: pd.DataFrame,
        y_treino: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
    ) -> Tuple[pd.DataFrame, Any, str]:
        """Treina os regressores e ranqueia pelo R² na partição de validação.

        Args:
            X_treino (pd.DataFrame): Atributos preditivos da partição de treino.
            y_treino (pd.Series): Vetor alvo contínuo da partição de treino.
            X_val (pd.DataFrame): Atributos preditivos da partição de validação.
            y_val (pd.Series): Vetor alvo contínuo da partição de validação.

        Returns:
            Tuple[pd.DataFrame, Any, str]: Placar de métricas, modelo campeão e seu nome.
        """
        logging.info("Iniciando torneio de regressão sobre %d algoritmos...", len(self.modelos_candidatos))

        linhas_placar: List[Dict[str, Any]] = []

        for nome_modelo, estimador in self.modelos_candidatos.items():
            logging.info("Treinando regressor: '%s'...", nome_modelo)

            estimador.fit(X_treino, y_treino)
            self.modelos_treinados[nome_modelo] = estimador

            predicoes = estimador.predict(X_val)

            r2 = round(float(r2_score(y_val, predicoes)), 4)
            rmse = round(float(np.sqrt(mean_squared_error(y_val, predicoes))), 4)
            mae = round(float(mean_absolute_error(y_val, predicoes)), 4)

            # MAPE é indefinido quando o alvo real é zero: considera apenas valores não nulos.
            mascara_nao_zero = pd.Series(y_val).to_numpy() != 0
            if mascara_nao_zero.any():
                mape = round(
                    float(
                        np.mean(
                            np.abs(
                                (pd.Series(y_val).to_numpy()[mascara_nao_zero] - predicoes[mascara_nao_zero])
                                / pd.Series(y_val).to_numpy()[mascara_nao_zero]
                            )
                        )
                        * 100
                    ),
                    4,
                )
            else:
                mape = 0.0

            linhas_placar.append({
                "modelo": nome_modelo,
                "r2": r2,
                "rmse": rmse,
                "mae": mae,
                "mape": mape,
            })

            logging.info("Resultado '%s' — R²: %.4f | RMSE: %.4f | MAE: %.4f", nome_modelo, r2, rmse, mae)

        df_placar = pd.DataFrame(linhas_placar).sort_values(by="r2", ascending=False).reset_index(drop=True)
        nome_campeao = str(df_placar.iloc[0]["modelo"])
        objeto_campeao = self.modelos_treinados[nome_campeao]

        logging.info("Regressor campeão da bateria: '%s' com R² de %.4f.", nome_campeao, df_placar.iloc[0]["r2"])
        return df_placar, objeto_campeao, nome_campeao


# ==================================================================================
# COMPARADOR DE AGRUPAMENTO (Etapa 6 — problemas não supervisionados)
# ==================================================================================
class ComparadorModelosAgrupamento:
    """Torneio de modelos de agrupamento, variando o número de grupos (k)."""

    def __init__(self, semente_aleatoria: int = 42, numero_grupos: int = 4) -> None:
        """Inicializa o catálogo de agrupamentos candidatos.

        Args:
            semente_aleatoria (int, opcional): Semente para reprodutibilidade. Padrão: 42.
            numero_grupos (int, opcional): Número central de grupos desejado. Padrão: 4.
        """
        self.semente = semente_aleatoria
        self.numero_grupos = max(2, int(numero_grupos))

        # Candidatos: k-1, k e k+1 para que o humano escolha o número de grupos.
        self.modelos_candidatos: Dict[str, Any] = {
            f"01_KMeans_k{max(2, self.numero_grupos - 1)}": KMeans(
                n_clusters=max(2, self.numero_grupos - 1),
                random_state=semente_aleatoria,
                n_init=10,
            ),
            f"02_KMeans_k{self.numero_grupos}": KMeans(
                n_clusters=self.numero_grupos,
                random_state=semente_aleatoria,
                n_init=10,
            ),
            f"03_KMeans_k{self.numero_grupos + 1}": KMeans(
                n_clusters=self.numero_grupos + 1,
                random_state=semente_aleatoria,
                n_init=10,
            ),
        }

        self.modelos_treinados: Dict[str, Any] = {}

    def executar_treinamento_e_benchmark(
        self,
        X_treino: pd.DataFrame,
        y_treino: Optional[pd.Series] = None,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
    ) -> Tuple[pd.DataFrame, Any, str]:
        """Ajusta cada agrupamento e ranqueia pelo coeficiente de silhueta.

        Args:
            X_treino (pd.DataFrame): Atributos preditivos da partição de treino.
            y_treino (Optional[pd.Series]): Ignorado (tarefa não supervisionada).
            X_val (Optional[pd.DataFrame]): Ignorado (tarefa não supervisionada).
            y_val (Optional[pd.Series]): Ignorado (tarefa não supervisionada).

        Returns:
            Tuple[pd.DataFrame, Any, str]: Placar de métricas, modelo campeão e seu nome.
        """
        logging.info("Iniciando torneio de agrupamento sobre %d modelos...", len(self.modelos_candidatos))

        linhas_placar: List[Dict[str, Any]] = []

        for nome_modelo, estimador in self.modelos_candidatos.items():
            estimador.fit(X_treino)
            self.modelos_treinados[nome_modelo] = estimador

            rotulos = estimador.labels_
            # A silhueta exige ao menos duas amostras por grupo e mais de um grupo.
            if len(set(rotulos)) > 1 and len(rotulos) > len(set(rotulos)):
                silhueta = round(float(silhouette_score(X_treino, rotulos)), 4)
            else:
                silhueta = -1.0

            inercia = round(float(estimador.inertia_), 4)
            numero_grupos = int(estimador.n_clusters)

            linhas_placar.append({
                "modelo": nome_modelo,
                "silhueta": silhueta,
                "inercia": inercia,
                "numero_grupos": numero_grupos,
            })

            logging.info("Resultado '%s' — Silhueta: %.4f | Inércia: %.4f", nome_modelo, silhueta, inercia)

        df_placar = pd.DataFrame(linhas_placar).sort_values(by="silhueta", ascending=False).reset_index(drop=True)
        nome_campeao = str(df_placar.iloc[0]["modelo"])
        objeto_campeao = self.modelos_treinados[nome_campeao]

        logging.info("Agrupamento campeão: '%s' com silhueta de %.4f.", nome_campeao, df_placar.iloc[0]["silhueta"])
        return df_placar, objeto_campeao, nome_campeao


# ==================================================================================
# COMPARADOR DE DETECÇÃO DE ANOMALIAS (Etapa 6)
# ==================================================================================
class ComparadorModelosAnomalias:
    """Torneio de detectores de anomalias (Isolation Forest e variantes)."""

    def __init__(self, semente_aleatoria: int = 42, fator_contaminacao: float = 0.05) -> None:
        """Inicializa o catálogo de detectores de anomalia.

        Args:
            semente_aleatoria (int, opcional): Semente para reprodutibilidade. Padrão: 42.
            fator_contaminacao (float, opcional): Fração esperada de anomalias. Padrão: 0.05.
        """
        self.semente = semente_aleatoria
        self.fator_contaminacao = fator_contaminacao

        self.modelos_candidatos: Dict[str, Any] = {
            "01_Isolation_Forest": IsolationForest(
                n_estimators=100,
                contamination=fator_contaminacao,
                random_state=semente_aleatoria,
                n_jobs=-1,
            ),
            "02_Local_Outlier_Factor": LocalOutlierFactor(
                n_neighbors=20,
                contamination=fator_contaminacao,
            ),
        }

        self.modelos_treinados: Dict[str, Any] = {}

    def executar_treinamento_e_benchmark(
        self,
        X_treino: pd.DataFrame,
        y_treino: Optional[pd.Series] = None,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
    ) -> Tuple[pd.DataFrame, Any, str]:
        """Ajusta os detectores e ranqueia pela fração de anomalias detectadas.

        Args:
            X_treino (pd.DataFrame): Atributos preditivos da partição de treino.
            y_treino (Optional[pd.Series]): Ignorado (tarefa não supervisionada).
            X_val (Optional[pd.DataFrame]): Ignorado (tarefa não supervisionada).
            y_val (Optional[pd.Series]): Ignorado (tarefa não supervisionada).

        Returns:
            Tuple[pd.DataFrame, Any, str]: Placar de métricas, modelo campeão e seu nome.
        """
        logging.info("Iniciando torneio de detecção de anomalias sobre %d modelos...", len(self.modelos_candidatos))

        linhas_placar: List[Dict[str, Any]] = []

        for nome_modelo, estimador in self.modelos_candidatos.items():
            estimador.fit(X_treino)
            self.modelos_treinados[nome_modelo] = estimador

            Scores = estimador.decision_function(X_treino)
            anomalias = estimador.predict(X_treino)
            taxa_anomalia = round(float(np.mean(anomalias == -1)), 4)

            # Métrica de separação: quanto maior, melhor o isolamento dos outliers.
            separacao = round(float(np.std(Scores)), 4)

            linhas_placar.append({
                "modelo": nome_modelo,
                "taxa_anomalia": taxa_anomalia,
                "separacao": separacao,
                "fator_contaminacao": self.fator_contaminacao,
            })

            logging.info("Resultado '%s' — Taxa de anomalia: %.4f | Separação: %.4f", nome_modelo, taxa_anomalia, separacao)

        df_placar = pd.DataFrame(linhas_placar).sort_values(by="separacao", ascending=False).reset_index(drop=True)
        nome_campeao = str(df_placar.iloc[0]["modelo"])
        objeto_campeao = self.modelos_treinados[nome_campeao]

        logging.info("Detector campeão: '%s'.", nome_campeao)
        return df_placar, objeto_campeao, nome_campeao


# ==================================================================================
# FACHADA DE SELEÇÃO DO COMPARADOR (Etapa 6 — a esteira decide pelo contrato)
# ==================================================================================
def criar_comparador(
    tipo_tarefa: str,
    semente_aleatoria: int = 42,
    parametros: Optional[Dict[str, Any]] = None,
) -> Any:
    """Instancia o comparador compatível com a família de tarefa declarada.

    Args:
        tipo_tarefa (str): Identificador da tarefa ('classificacao', 'regressao',
            'agrupamento' ou 'deteccao_anomalias').
        semente_aleatoria (int, opcional): Semente para reprodutibilidade. Padrão: 42.
        parametros (Optional[Dict[str, Any]]): Parâmetros livres do contrato.

    Returns:
        Any: Instância do comparador correspondente à tarefa.

    Raises:
        ValueError: Quando a família de tarefa não é suportada.
    """
    parametros = parametros or {}
    tarefa = str(tipo_tarefa).strip().lower()

    if tarefa == "classificacao":
        return ComparadorModelosClassificacao(semente_aleatoria=semente_aleatoria)
    if tarefa == "regressao":
        return ComparadorModelosRegressao(semente_aleatoria=semente_aleatoria)
    if tarefa == "agrupamento":
        return ComparadorModelosAgrupamento(
            semente_aleatoria=semente_aleatoria,
            numero_grupos=int(parametros.get("numero_grupos", 4)),
        )
    if tarefa == "deteccao_anomalias":
        return ComparadorModelosAnomalias(
            semente_aleatoria=semente_aleatoria,
            fator_contaminacao=float(parametros.get("fator_contaminacao", 0.05)),
        )

    raise ValueError(f"Familia de tarefa não suportada: '{tipo_tarefa}'.")