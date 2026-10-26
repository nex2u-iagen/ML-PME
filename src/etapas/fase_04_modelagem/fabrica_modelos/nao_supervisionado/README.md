# 🧭 `src/etapas/fase_04_modelagem/fabrica_modelos/nao_supervisionado/` — Modelos não supervisionados

> **Navegação:** [README raiz](../../../../../README.md) · [src](../../../../README.md) · [etapas](../../../README.md) · [fase_04](../../README.md) · [fabrica](../README.md)

## 🎯 Objetivo

Agrupar algoritmos que trabalham apenas com `X`, sem rótulos. A pasta cobre três
famílias: agrupamento, detecção de anomalias e redução de dimensionalidade.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | `OrquestradorAgrupamento`, scripts de torneio e testes, sempre com `X` padronizado. |
| **Processa** | Ajuste não supervisionado, rótulos de cluster, scores de anomalia ou projeções. |
| **Entrega para** | Leaderboards, visualizações e análises exploratórias. |
| **Quem consome** | Torneio de agrupamento, testes e experimentos de segmentação. |

## 🧩 Subpastas

| Pasta | README | Pergunta que responde | Saída típica |
| :--- | :--- | :--- | :--- |
| `agrupamento/` | [README](agrupamento/README.md) | Quais grupos naturais existem? | Rótulo de cluster por amostra. |
| `deteccao_anomalias/` | [README](deteccao_anomalias/README.md) | Quais amostras fogem do padrão? | `+1` normal / `-1` anomalia. |
| `reducao_dimensionalidade/` | [README](reducao_dimensionalidade/README.md) | Como representar `X` em menos dimensões? | Matriz `X` reduzida. |

## 📥 Entradas e 📤 saídas

| Família | Entrada | Saída |
| :--- | :--- | :--- |
| Agrupamento | `X` numérico padronizado | `labels_` / `predict` |
| Anomalias | `X` numérico padronizado | `+1` / `-1` |
| Redução | `X` de alta dimensão | `X` de baixa dimensão |

## 📌 Regras

- Não há `y`; a avaliação é geométrica ou visual.
- A padronização é obrigatória para métodos baseados em distância.
- O resultado não é “verdade absoluta”: precisa de interpretação de negócio.

## 🔗 Ligações

- Agrupamento: [agrupamento/README.md](agrupamento/README.md).
- Anomalias: [deteccao_anomalias/README.md](deteccao_anomalias/README.md).
- Redução: [reducao_dimensionalidade/README.md](reducao_dimensionalidade/README.md).
- Voltar para [fabrica](../README.md).
