# 🥇 `src/etapas/fase_05_avaliacao/pilar_01_podio_top3/` — Pódio técnico Top 3

> **Navegação:** [README raiz](../../../../README.md) · [src](../../../README.md) · [etapas](../../README.md) · [fase_05](../README.md)

## 🎯 Objetivo

Comparar os três finalistas da Fase 04 sob as mesmas condições de teste retido,
medindo qualidade estatística e latência, e gerar as evidências visuais comparativas.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | `catalogo_top3`, `X_teste` e `y_teste` da [fase_04](../../fase_04_modelagem/README.md). |
| **Processa** | Predições, probabilidades, métricas e tempo de inferência. |
| **Entrega para** | Pilar 4 (scorecard) e Pilar 2 (referência dos mesmos modelos). |
| **Quem consome** | `OrquestradorGovernanca`, scripts da Fase 05 e relatórios. |

## 🧩 Arquivos

| Arquivo | Classe | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `avaliador_metricas.py` | `AvaliadorMetricasTabulares` | Modelo, `X_teste`, `y_teste`. | F1, precisão, recall, ROC-AUC, PR-AUC e latência. | Linha de scorecard (`dict`/`DataFrame`). |
| `gerador_graficos_podio.py` | `GeradorGraficosPodio` | Modelos e teste. | Matrizes de confusão, curvas ROC e Precision-Recall. | 3 `.png` em `relatorios/figuras/fase_05_avaliacao/pilar_01_top3/`. |
| `orquestrador_podio_top3.py` | `OrquestradorPodioTop3` | Catálogo Top 3 + teste. | Coordena avaliador e gerador. | `dict` com `scorecard_tabular` e caminhos das figuras. |

## 📥 Entradas

| Entrada | Formato | Origem |
| :--- | :--- | :--- |
| Top 3 treinado | `dict[str, Any]` | Fase 04 |
| Matriz de teste | `np.ndarray` | Fase 03 |
| Vetor alvo | `np.ndarray` | Fase 03 |
| Rótulos amigáveis | `list[str]` | Configuração do script |

## 📤 Saídas

| Saída | Formato | Destino |
| :--- | :--- | :--- |
| Scorecard | `pd.DataFrame` | Pilar 4 |
| Matrizes de confusão | `.png` | `pilar_01_top3/comparativo_top3_matrizes_confusao.png` |
| Curvas ROC | `.png` | `pilar_01_top3/comparativo_top3_curvas_roc.png` |
| Curvas PR | `.png` | `pilar_01_top3/comparativo_top3_curvas_precision_recall.png` |

## 📊 Métricas

| Métrica | O que mede | Direção |
| :--- | :--- | :--- |
| F1-Score | Equilíbrio precisão/recall | Maior melhor |
| Precisão | Confiabilidade do alarme positivo | Maior melhor |
| Recall | Cobertura dos positivos reais | Maior melhor |
| ROC-AUC | Poder de separação | Maior melhor |
| PR-AUC | Desempenho em classes desbalanceadas | Maior melhor |
| Latência | Tempo de inferência | Menor melhor |

## 🔗 Ligações

- Orquestrador: [orquestrador_podio_top3.py](orquestrador_podio_top3.py).
- Próximo pilar: [pilar_02](../pilar_02_alinhamento_negocio/README.md).
- Voltar para [fase_05](../README.md).
