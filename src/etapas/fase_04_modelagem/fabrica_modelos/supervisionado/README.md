# 🎯 `src/etapas/fase_04_modelagem/fabrica_modelos/supervisionado/` — Modelos supervisionados

> **Navegação:** [README raiz](../../../../../README.md) · [src](../../../../README.md) · [etapas](../../../README.md) · [fase_04](../../README.md) · [fabrica](../README.md)

## 🎯 Objetivo

Agrupar os algoritmos que aprendem com rótulos (`X`, `y`). A pasta é dividida em
classificação (alvo discreto) e regressão (alvo contínuo).

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Orquestradores de torneio, que passam `X` e `y` já preparados. |
| **Processa** | `fit`, `predict`, `predict_proba` (classificação) e `predict` (regressão). |
| **Entrega para** | Métricas de validação cruzada e o estimador ajustado para a Fase 05. |
| **Quem consome** | `OrquestradorTorneioClassificacao`, `OrquestradorTorneioRegressao`, `OtimizadorHiperparametros`. |

## 🧩 Subpastas

| Pasta | README | Alvo | Algoritmos |
| :--- | :--- | :--- | :--- |
| `classificacao/` | [README](classificacao/README.md) | Discreto (0/1) | AdaBoost, Árvore, KNN, LDA, Naive Bayes, QDA, Random Forest, Regressão Logística, SGD, SVM, XGBoost. |
| `regressao/` | [README](regressao/README.md) | Contínuo | Árvore, ElasticNet, Huber, Lasso, Random Forest, Regressão Linear, Ridge, SGD, SVR, XGBoost. |

## 📥 Entradas e 📤 saídas

| Tipo | Entrada de treino | Saída de predição |
| :--- | :--- | :--- |
| Classificação | `X` numérico + `y` binário | Classe e probabilidade |
| Regressão | `X` numérico + `y` contínuo | Valor contínuo |

## 📌 Regras

- Classificação deve expor `predict_proba` quando o algoritmo permitir; o SVM e o
  SGD usam calibração explícita.
- Regressão deve ser avaliada com R², RMSE e MAE.
- Todos os estimadores recebem `random_state=42` quando aplicável.

## 🔗 Ligações

- Classificação: [classificacao/README.md](classificacao/README.md).
- Regressão: [regressao/README.md](regressao/README.md).
- Contrato: [ModeloBase](../base_modelo.py).
- Voltar para [fabrica](../README.md).
