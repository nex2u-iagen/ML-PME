# 📈 `src/etapas/fase_04_modelagem/fabrica_modelos/supervisionado/regressao/` — Regressores

> **Navegação:** [README raiz](../../../../../../README.md) · [src](../../../../../README.md) · [etapas](../../../../README.md) · [fase_04](../../../README.md) · [fabrica](../../README.md) · [supervisionado](../README.md)

## 🎯 Objetivo

Catálogo de 10 regressores para alvos contínuos. Todos seguem o contrato
[`ModeloBase`](../../base_modelo.py) e participam do torneio de regressão.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | `OrquestradorTorneioRegressao` / `OtimizadorHiperparametros`, com `X` e `y` contínuo. |
| **Processa** | `fit` e `predict`. |
| **Entrega para** | Leaderboard de regressão (R², RMSE, MAE) e campeão contínuo. |
| **Quem consome** | Torneio de regressão, testes e experimentos. |

## 🧩 Arquivos

| Arquivo | Classe | Família | Regularização |
| :--- | :--- | :--- | :--- |
| `alg_regressao_linear.py` | `AlgoritmoRegressaoLinear` | Linear (OLS) | Nenhuma |
| `alg_ridge_regressao.py` | `AlgoritmoRidge` | Linear | L2 |
| `alg_lasso_regressao.py` | `AlgoritmoLasso` | Linear | L1 (seleção) |
| `alg_elasticnet_regressao.py` | `AlgoritmoElasticNet` | Linear | L1 + L2 |
| `alg_sgd_regressor.py` | `AlgoritmoSGDRegressor` | Linear iterativo | configurável |
| `alg_huber_regressor.py` | `AlgoritmoHuber` | Linear robusto | Resistente a outliers |
| `alg_svr_regressor.py` | `AlgoritmoSVR` | Margem máxima | Tubo insensível |
| `alg_arvore_regressao.py` | `AlgoritmoArvoreRegressao` | Árvore | Partições binárias |
| `alg_random_forest_regressao.py` | `AlgoritmoRandomForestRegressor` | Ensemble (bagging) | Muitas árvores |
| `alg_xgboost_regressao.py` | `AlgoritmoXGBoostRegressor` | Ensemble (boosting) | Alto desempenho |

## 📥 Entradas e 📤 saídas

| Método | Entrada | Saída |
| :--- | :--- | :--- |
| `construir_estimador(42)` | Semente | Regressor não treinado |
| `fit(X, y)` | Matriz numérica + alvo contínuo | Regressor ajustado |
| `predict(X)` | Matriz numérica | Valor contínuo estimado |

## 📌 Regras

- `X` deve ser numérico e, para modelos lineares/SVR/SGD, padronizado.
- Métricas oficiais: R² (principal), RMSE e MAE.
- O campeão é o maior R² médio, mas RMSE/MAE devem ser auditados.
- A grade de hiperparâmetros deve evitar combinações inválidas.

## 🔗 Ligações

- Torneio: [fase_04](../../../README.md).
- Contrato: [ModeloBase](../../base_modelo.py).
- Testes: [testes/README.md](../../../../../../testes/README.md).
