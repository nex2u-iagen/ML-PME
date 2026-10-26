# 📜 `src/etapas/fase_05_avaliacao/pilar_04_governanca_homologacao/` — Governança e dossiê

> **Navegação:** [README raiz](../../../../README.md) · [src](../../../README.md) · [etapas](../../README.md) · [fase_05](../README.md)

## 🎯 Objetivo

Consolidar os laudos dos Pilares 1–3, aplicar regras de aceite e emitir o **Dossiê
Executivo de Homologação** com evidências visuais exclusivas do modelo campeão.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Scorecard técnico (P1), leaderboard financeiro (P2), laudo SHAP (P3) e pipeline campeão. |
| **Processa** | Cruzamento dos laudos, regras de aceite, figuras solo e redação Markdown. |
| **Entrega para** | Fase 06 e stakeholders (diretoria, auditoria, compliance). |
| **Quem consome** | `scripts.executores_arquivo.fase_05_pilar_04_governanca` e a Fase 06. |

## 🧩 Arquivos

| Arquivo | Classe | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `compilador_scorecard_geral.py` | `CompiladorScorecardGeral` | Laudos 1–3. | Unifica métricas, custos e SHAP em uma visão única. | `pd.DataFrame` consolidado. |
| `emissor_parecer_tecnico.py` | `EmissorParecerTecnico` | Scorecard consolidado. | Aplica regras de aceite e emite status. | Parecer (`dict`) com status e justificativa. |
| `gerador_graficos_campeao.py` | `GeradorGraficosCampeao` | Campeão, `X_teste`, `y_teste`. | Matriz de confusão, ROC e PR somente do campeão. | 3 `.png` em `campeao_solo/`. |
| `formatador_dossie_markdown.py` | `FormatadorDossieMarkdown` | Scorecard, parecer, laudo SHAP e rotas das figuras. | Monta o Markdown com tabelas e imagens relativas. | Texto Markdown. |
| `orquestrador_governanca.py` | `OrquestradorGovernanca` | Todos os laudos + campeão. | Coordena compilação, parecer, figuras e gravação. | `dict` + `dossie_homologacao_executiva.md`. |

## 📥 Entradas

| Entrada | Origem | Formato |
| :--- | :--- | :--- |
| Scorecard técnico | Pilar 1 | `pd.DataFrame` |
| Leaderboard financeiro | Pilar 2 | `pd.DataFrame` |
| Laudo de explicabilidade | Pilar 3 | `dict` |
| Estimador campeão | Fase 04 / Pilar 1 | pipeline ajustado |
| Teste retido | Fase 03 | `X_teste`, `y_teste` |

## 📤 Saídas

| Saída | Destino | Consumidor |
| :--- | :--- | :--- |
| Dossiê executivo | `relatorios/governanca/dossie_homologacao_executiva.md` | Diretoria / auditoria |
| Matriz solo | `relatorios/figuras/fase_05_avaliacao/campeao_solo/campeao_matriz_confusao_solo.png` | Dossiê |
| ROC solo | `.../campeao_curva_roc_solo.png` | Dossiê |
| PR solo | `.../campeao_curva_precision_recall_solo.png` | Dossiê |
| Parecer | `dict` | Fase 06 |

## ✅ Regras de aceite (conceito)

O parecer considera, entre outros:

- desempenho técnico mínimo no teste retido;
- resultado financeiro líquido positivo;
- consistência da explicabilidade;
- ausência de sinais claros de overfitting ou data leakage.

O status final e a justificativa são gravados no dossiê.

## 🔗 Ligações

- Pilar 1: [pilar_01](../pilar_01_podio_top3/README.md).
- Pilar 2: [pilar_02](../pilar_02_alinhamento_negocio/README.md).
- Pilar 3: [pilar_03](../pilar_03_explicabilidade_xai/README.md).
- Próxima fase: [fase_06](../../fase_06_implantacao/README.md).
- Dossiê gerado: [`relatorios/governanca/`](../../../../relatorios/README.md).
