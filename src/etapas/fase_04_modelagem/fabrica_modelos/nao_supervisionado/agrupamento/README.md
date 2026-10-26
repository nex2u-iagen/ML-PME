# 🔵 `src/etapas/fase_04_modelagem/fabrica_modelos/nao_supervisionado/agrupamento/` — Agrupamento

> **Navegação:** [README raiz](../../../../../../README.md) · [src](../../../../../README.md) · [etapas](../../../../README.md) · [fase_04](../../../README.md) · [fabrica](../../README.md) · [nao_supervisionado](../README.md)

## 🎯 Objetivo

Catálogo de 5 algoritmos de clustering para segmentação de clientes, produtos ou
transações. A avaliação usa métricas geométricas intrínsecas, sem gabarito.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | `OrquestradorAgrupamento` / script de torneio, com `X` padronizado. |
| **Processa** | Ajuste dos grupos e extração de rótulos. |
| **Entrega para** | Leaderboard por silhueta e segmentos interpretáveis. |
| **Quem consome** | Torneio de agrupamento, testes e análise exploratória. |

## 🧩 Arquivos

| Arquivo | Classe | Método | Característica |
| :--- | :--- | :--- | :--- |
| `alg_kmeans_agrupamento.py` | `AlgoritmoKMeans` | Centroides | Rápido; exige `n_clusters`. |
| `alg_dbscan_agrupamento.py` | `AlgoritmoDBSCAN` | Densidade | Detecta ruído (`-1`); não exige `k`. |
| `alg_gmm_agrupamento.py` | `AlgoritmoGMM` | Mistura gaussiana | Probabilístico; permite sobreposição. |
| `alg_hierarquico_agrupamento.py` | `AlgoritmoHierarquico` | Aglomerativo | Dendrograma e fusão ascendente. |
| `alg_mean_shift_agrupamento.py` | `AlgoritmoMeanShift` | Modas | Janela de busca; descobre `k`. |

## 📥 Entradas e 📤 saídas

| Método | Entrada | Saída |
| :--- | :--- | :--- |
| `construir_estimador(42)` | Semente | Agrupador não treinado |
| `fit(X)` | Matriz padronizada | Modelo ajustado |
| `predict(X)` / `labels_` | Matriz padronizada | Rótulo inteiro por amostra |

## 📤 Métricas do orquestrador

| Métrica | Interpretação |
| :--- | :--- |
| **Silhueta** | Coesão interna vs. separação externa (quanto maior, melhor). |
| **Davies-Bouldin** | Similaridade entre clusters (quanto menor, melhor). |
| **Calinski-Harabasz** | Razão de variância entre/ intra clusters (quanto maior, melhor). |

## 📌 Regras

- Padronizar `X` antes de qualquer método baseado em distância.
- DBSCAN pode rotular amostras como ruído (`-1`); isso é esperado.
- O campeão é escolhido pela silhueta, mas a interpretação de negócio é obrigatória.
- Não use agrupamento para “descobrir” o target supervisionado.

## 🔗 Ligações

- Orquestrador: [fase_04](../../../README.md).
- Torneio executável: [scripts/README.md](../../../../../../scripts/README.md).
- Voltar para [nao_supervisionado](../README.md).
