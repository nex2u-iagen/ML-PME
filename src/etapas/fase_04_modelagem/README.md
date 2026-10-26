# 🤖 `src/etapas/fase_04_modelagem/` — Modelagem e torneios

> **Navegação:** [README raiz](../../../README.md) · [src](../../README.md) · [etapas](../README.md) · **Anterior:** [fase_03](../fase_03_preparacao/README.md) · **Próxima:** [fase_05](../fase_05_avaliacao/README.md)

## 🎯 Objetivo

Treinar, comparar e calibrar estimadores. A fase cobre desde um baseline linear
explicável até torneios completos de classificação, regressão e agrupamento, usando
a fábrica de modelos como catálogo de algoritmos.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | `dados/processados/ml/treino_processado.parquet` e `validacao_processada.parquet`. |
| **Processa** | Baselines, validação cruzada, GridSearchCV, comparação de métricas e calibração. |
| **Entrega para** | [fase_05_avaliacao](../fase_05_avaliacao/README.md): estimadores ajustados, leaderboards e artefatos de baseline. |
| **Quem consome** | Fase 05, scripts de torneio e testes de algoritmos. |

## 🧩 Arquivos

| Arquivo | Classe / função | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `etapa_04_01_orquestrador_baseline.py` | `executar_triagem_baseline()` | `treino_processado.parquet`, `validacao_processada.parquet`. | Treina Regressão Logística, calibra e avalia. | `modelos/modelo_baseline_logreg*.joblib` + `.json`. |
| `orquestrador_torneio_classificacao.py` | `OrquestradorTorneioClassificacao` | Catálogo de classificadores, `X`, `y`. | Validação cruzada K-Fold estratificada e 5 métricas. | Leaderboard (`pd.DataFrame`) ordenado por F1. |
| `orquestrador_torneio_regressao.py` | `OrquestradorTorneioRegressao` | Catálogo de regressores, `X`, `y` contínuo. | K-Fold e cálculo de R², RMSE e MAE. | Leaderboard ordenado por R². |
| `orquestrador_agrupamento.py` | `OrquestradorAgrupamento` | Catálogo de agrupadores, `X` sem `y`. | Ajuste e métricas geométricas (silhueta, Davies-Bouldin, Calinski-Harabasz). | Leaderboard ordenado por silhueta. |
| `otimizador_hiperparametros.py` | `OtimizadorHiperparametros` | Estimador, `X_treino`, `y_treino`, grade opcional. | `GridSearchCV` com validação cruzada. | Melhor estimador, melhores parâmetros e melhor score. |
| `fabrica_modelos/` | Catálogo | Nenhum dado em tempo de importação. | Instancia algoritmos e grades. | Estimadores não treinados + grades. |
| `__init__.py` | — | — | Marca o pacote. | — |

## 📥 Entradas

| Entrada | Formato | Origem |
| :--- | :--- | :--- |
| Treino | `treino_processado.parquet` | Fase 03 |
| Validação | `validacao_processada.parquet` | Fase 03 |
| Catálogo de modelos | Classes `ModeloBase` | Fábrica de modelos |
| Grade de hiperparâmetros | `dict[str, list]` | Cada algoritmo / otimizador |

## 📤 Saídas

| Saída | Formato | Consumidor |
| :--- | :--- | :--- |
| Baseline treinado | `.joblib` + `.json` | Auditoria / comparação |
| Leaderboard de classificação | `pd.DataFrame` | Escolha do Top 3 |
| Leaderboard de regressão | `pd.DataFrame` | Escolha do campeão contínuo |
| Leaderboard de agrupamento | `pd.DataFrame` | Escolha do campeão não supervisionado |
| Estimador campeão | objeto em memória | Fase 05 |
| Parâmetros ótimos | `dict` | Governança e reprodutibilidade |

## 🏁 Torneios disponíveis

| Script | Executor | Algoritmos |
| :--- | :--- | :--- |
| Classificação | `scripts.executores_projeto.torneio_classificacao` | 11 classificadores da fábrica |
| Regressão | `scripts.executores_projeto.torneio_regressao` | 10 regressores da fábrica |
| Agrupamento | `scripts.executores_projeto.torneio_agrupamento` | 5 agrupadores da fábrica |

```bash
uv run python -m scripts.executores_projeto.torneio_classificacao
uv run python -m scripts.executores_projeto.torneio_regressao
uv run python -m scripts.executores_projeto.torneio_agrupamento
```

## 📌 Regras

- A validação cruzada nunca pode ver o teste retido.
- A semente aleatória padrão é `42` para reprodutibilidade.
- Hiperparâmetros são calibrados apenas no treino/validação.
- O baseline é uma referência explicável; modelos complexos precisam superá-lo.
- O campeão só é promovido após passar pela Fase 05.

## 🔗 Ligações

- Catálogo de algoritmos: [fabrica_modelos/README.md](fabrica_modelos/README.md).
- Núcleo de persistência: [aprendizado_maquina](../../nucleo/aprendizado_maquina/README.md).
- Próxima fase: [fase_05_avaliacao](../fase_05_avaliacao/README.md).
