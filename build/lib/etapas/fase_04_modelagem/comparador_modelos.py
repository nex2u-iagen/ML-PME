"""Módulo de Comparação de Modelos de Classificação Supervisionada (Fase 4 - Modelagem).

Responsabilidade Única: Instanciar estimadores candidatos (Baseline Ingênuo,
Regressão Logística, Random Forest e Boosting), treinar estritamente sobre
a partição de treino e mensurar o desempenho na partição de validação.
"""

# 'import' traz o módulo 'logging' nativo da biblioteca padrão para registros técnicos no console.
import logging

# 'from' acessa 'typing' da biblioteca padrão para anotação estática rigorosa de coleções.
from typing import Any, Dict, List, Tuple

# 'import' traz a biblioteca externa 'pandas' para compilação tabular do ranking de modelos[cite: 9, 12].
import pandas as pd

# 'from' importa estimadores supervisionados oficiais do Scikit-Learn (https://scikit-learn.org/stable/)[cite: 9, 10]:
# - 'DummyClassifier': provê a linha de base ingênua para garantir que os modelos aprendam além do acaso.
from sklearn.dummy import DummyClassifier

# - 'LogisticRegression': modelo linear de referência da indústria de crédito com regularização L2[cite: 10].
from sklearn.linear_model import LogisticRegression

# - 'RandomForestClassifier' e 'HistGradientBoostingClassifier': métodos de conjunto para relações não lineares[cite: 14].
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier

# - Métricas formais para avaliação rigorosa de classificação sob desbalanceamento:
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
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