# 🧪 `src/etapas/fase_04_modelagem/fabrica_modelos/supervisionado/classificacao/` — Classificadores

> **Navegação:** [README raiz](../../../../../../README.md) · [src](../../../../../README.md) · [etapas](../../../../README.md) · [fase_04](../../../README.md) · [fabrica](../../README.md) · [supervisionado](../README.md)

## 🎯 Objetivo

Catálogo de 11 classificadores binários. Todos seguem o contrato
[`ModeloBase`](../../base_modelo.py) e são elegíveis para o torneio de classificação.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | `OrquestradorTorneioClassificacao` / `OtimizadorHiperparametros`, com `X` e `y` preparados. |
| **Processa** | `fit`, `predict` e `predict_proba`. |
| **Entrega para** | Leaderboard de classificação e estimadores do Top 3 para a Fase 05. |
| **Quem consome** | Torneio de classificação, scripts de calibração e testes unitários. |

## 🧩 Arquivos

| Arquivo | Classe | Família | Observação |
| :--- | :--- | :--- | :--- |
| `alg_regressao_logistica.py` | `AlgoritmoRegressaoLogistica` | Linear | Baseline explicável. |
| `alg_lda_classificador.py` | `AlgoritmoLDA` | Linear/generativo | Assume normalidade e covariância comum. |
| `alg_qda_classificador.py` | `AlgoritmoQDA` | Generativo | Covariâncias por classe. |
| `alg_naive_bayes_classificador.py` | `AlgoritmoNaiveBayes` | Probabilístico | Suposição de independência. |
| `alg_knn_classificador.py` | `AlgoritmoKNN` | Baseado em instância | Sensível à escala. |
| `alg_svm_classificador.py` | `AlgoritmoSVM` | Margem máxima | Calibração explícita de probabilidade. |
| `alg_sgd_classificador.py` | `AlgoritmoSGD` | Linear iterativo | Gradiente estocástico. |
| `alg_arvore_decisao.py` | `AlgoritmoArvoreDecisao` | Árvore | Regras interpretáveis. |
| `alg_random_forest.py` | `AlgoritmoRandomForest` | Ensemble (bagging) | Muitas árvores. |
| `alg_adaboost_classificador.py` | `AlgoritmoAdaBoost` | Ensemble (boosting) | Aumento adaptativo de pesos. |
| `alg_xgboost_classificador.py` | `AlgoritmoXGBoost` | Ensemble (boosting) | Alto desempenho. |
| `__initi__.py` | — | — | Inicializador do pacote (grafia inconsistente; funciona por namespace). |

## 📥 Entradas e 📤 saídas

| Método | Entrada | Saída |
| :--- | :--- | :--- |
| `construir_estimador(42)` | Semente | Classificador não treinado |
| `fit(X, y)` | Matriz numérica + rótulos | Estimador ajustado |
| `predict(X)` | Matriz numérica | Classes 0/1 |
| `predict_proba(X)` | Matriz numérica | Probabilidades por classe |

## 📌 Regras

- `X` deve estar padronizado quando o algoritmo for sensível à escala (KNN, SVM,
  SGD, LDA/QDA).
- O alvo deve ser binário e codificado como 0/1.
- A calibração de probabilidade é obrigatória para modelos de margem (SVM/SGD).
- O arquivo `__initi__.py` deve ser renomeado para `__init__.py` em uma limpeza
  futura; hoje o pacote é resolvido como namespace.

## 🔗 Ligações

- Torneio: [fase_04](../../../README.md).
- Contrato: [ModeloBase](../../base_modelo.py).
- Testes: [testes/README.md](../../../../../../testes/README.md).
