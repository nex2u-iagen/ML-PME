# 🏆 `src/etapas/fase_05_avaliacao/` — Avaliação, custo, XAI e governança

> **Navegação:** [README raiz](../../../README.md) · [src](../../README.md) · [etapas](../README.md) · **Anterior:** [fase_04](../fase_04_modelagem/README.md) · **Próxima:** [fase_06](../fase_06_implantacao/README.md)

## 🎯 Objetivo

Responder quatro perguntas sobre o Top 3 da Fase 04:

1. **Pilar 1 — Técnica:** qual modelo generaliza melhor?
2. **Pilar 2 — Financeira:** qual modelo gera o melhor resultado em R$?
3. **Pilar 3 — Explicabilidade:** por que o modelo decide?
4. **Pilar 4 — Governança:** o campeão está homologado para produção?

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Top 3 treinado, `X_teste`, `y_teste` e o pipeline campeão da [fase_04](../fase_04_modelagem/README.md). |
| **Processa** | Métricas, latência, matriz de custo, SHAP, regras de aceite e dossiê. |
| **Entrega para** | [fase_06_implantacao](../fase_06_implantacao/README.md): campeão homologado + evidências. |
| **Quem consome** | Patrocinador de negócio, auditoria, time de ML e API de produção. |

## 🧩 Pilares

| Pilar | README | Entrada | Saída | Artefatos |
| :--- | :--- | :--- | :--- | :--- |
| **1 — Pódio Top 3** | [README](pilar_01_podio_top3/README.md) | Top 3, `X_teste`, `y_teste`. | Scorecard técnico. | 3 figuras comparativas. |
| **2 — Alinhamento de negócio** | [README](pilar_02_alinhamento_negocio/README.md) | Top 3, `X_teste`, `y_teste`, premissas de custo. | Leaderboard financeiro. | Tabela em memória. |
| **3 — Explicabilidade XAI** | [README](pilar_03_explicabilidade_xai/README.md) | Função de probabilidade, `X_treino`, `X_avaliacao`. | Laudo SHAP global e local. | 2+ figuras. |
| **4 — Governança** | [README](pilar_04_governanca_homologacao/README.md) | Laudos 1–3 + campeão. | Parecer e dossiê executivo. | `dossie_homologacao_executiva.md` + figuras solo. |

## 🔁 Fluxo interno

```text
Fase 04 (Top 3 + teste retido)
        │
        ├──► Pilar 1: métricas + figuras comparativas
        │           │
        ├──► Pilar 2: matriz de confusão → R$
        │           │
        └──► Pilar 3: SHAP global/local
                    │
                    ▼
             Pilar 4: compila laudos, aplica regras de aceite,
             gera figuras solo do campeão e grava o dossiê
                    │
                    ▼
             Fase 06 (persistência e API)
```

## 📥 Entradas

| Entrada | Origem | Formato |
| :--- | :--- | :--- |
| Catálogo Top 3 | Fase 04 | `dict[str, estimador]` |
| Teste retido | Fase 03 | `X_teste`, `y_teste` |
| Pipeline campeão | Fase 04 | objeto Scikit-Learn |
| Premissas financeiras | Negócio | `ConfiguracaoCustoRisco` |
| Nomes das features | Fase 03 | `list[str]` |

## 📤 Saídas

| Saída | Destino | Consumidor |
| :--- | :--- | :--- |
| Scorecard técnico | memória | Pilar 4 / scripts |
| Leaderboard financeiro | memória | Pilar 4 / scripts |
| Laudo SHAP | memória + `.png` | Pilar 4 |
| Dossiê executivo | `relatorios/governanca/dossie_homologacao_executiva.md` | Auditoria / diretoria |
| Figuras do campeão | `relatorios/figuras/fase_05_avaliacao/campeao_solo/` | Dossiê |

## ▶️ Como executar

```bash
uv run python -m scripts.executores_arquivo.fase_05_pilar_01_top3
uv run python -m scripts.executores_arquivo.fase_05_pilar_02_custo
uv run python -m scripts.executores_arquivo.fase_05_pilar_03_shap
uv run python -m scripts.executores_arquivo.fase_05_pilar_04_governanca
```

## 📌 Regras

- Nenhum pilar pode usar o teste para treinar ou calibrar.
- O Pilar 1 é técnico; o Pilar 2 é financeiro. O campeão final pondera os dois.
- O SHAP precisa de uma função de probabilidade da classe positiva.
- O dossiê só é emitido se as regras de aceite do Pilar 4 forem atendidas.

## 🔗 Ligações

- Pódio técnico: [pilar_01](pilar_01_podio_top3/README.md).
- Impacto financeiro: [pilar_02](pilar_02_alinhamento_negocio/README.md).
- Explicabilidade: [pilar_03](pilar_03_explicabilidade_xai/README.md).
- Governança: [pilar_04](pilar_04_governanca_homologacao/README.md).
- Próxima fase: [fase_06](../fase_06_implantacao/README.md).
