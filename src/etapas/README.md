# 🚀 `src/etapas/` — Esteira CRISP-DM

> **Navegação:** [README raiz](../../README.md) · [src](../README.md) · **Fases:** [01](fase_01_ingestao/README.md) · [02](fase_02_exploracao/README.md) · [03](fase_03_preparacao/README.md) · [04](fase_04_modelagem/README.md) · [05](fase_05_avaliacao/README.md) · [06](fase_06_implantacao/README.md)

## 🎯 Objetivo

Orquestrar a transformação da matéria-prima transacional de ERPs de PMEs em
inteligência preditiva, seguindo o fluxo CRISP-DM. Cada subpasta representa uma
fase com entradas, processos e entregas explícitos.

## 🔄 Fluxo completo

```text
dados/brutos/ (sql/ e csv/)
        │
        ▼
[ fase_01_ingestao ] ────────► Extração em lotes e conversão para CSV
        │
        ▼
[ fase_02_exploracao ] ──────► Saúde dos dados + 10 diagnósticos departamentais
        │
        ▼
[ fase_03_preparacao ] ──────► Limpeza + bifurcação BI / ML
        │
        ├─────────────────────────────────┐
        ▼                                 ▼
dados/processados/bi/             dados/processados/ml/
(Data Marts para dashboards)      (ABT + treino/validação/teste)
                                          │
                                          ▼
[ fase_04_modelagem ] ──────► Baseline, torneios e calibração
                                          │
                                          ▼
[ fase_05_avaliacao ] ──────► Métricas, custo, SHAP e dossiê
                                          │
                                          ▼
[ fase_06_implantacao ] ────► Persistência, segurança, contratos e API
                                          │
                                          ▼
                          artefatos/modelos_producao/ + serviço HTTP
```

## 🧩 Fases

| Fase | README | Recebe | Entrega | Próxima |
| :--- | :--- | :--- | :--- | :--- |
| **01 — Ingestão** | [README](fase_01_ingestao/README.md) | Dumps `.sql` e CSVs brutos. | CSVs tabulares + `DataFrame`s em memória. | 02 |
| **02 — Exploração** | [README](fase_02_exploracao/README.md) | CSVs da Fase 01. | Laudos e figuras em `relatorios/figuras/`. | 03 |
| **03 — Preparação** | [README](fase_03_preparacao/README.md) | CSVs brutos/explorados. | `dados/processados/bi/*.csv` e `dados/processados/ml/*.parquet`. | 04 (ML) / BI |
| **04 — Modelagem** | [README](fase_04_modelagem/README.md) | `treino_processado.parquet` e `validacao_processada.parquet`. | Leaderboards, estimadores e baseline persistido. | 05 |
| **05 — Avaliação** | [README](fase_05_avaliacao/README.md) | Top 3, `X_teste`, `y_teste` e modelo campeão. | Scorecard, leaderboard financeiro, SHAP e dossiê. | 06 |
| **06 — Implantação** | [README](fase_06_implantacao/README.md) | Pipeline campeão + metadados. | `.joblib` + manifesto, JWT, contratos e API. | Produção |

## 🧠 Dependência do núcleo

Todas as fases consomem [src/nucleo](../nucleo/README.md):

| Fase | Módulos do núcleo |
| :--- | :--- |
| 01 | `acesso_dados` (leitor e conector SQL) |
| 02 | `acesso_dados`, `diagnostico_estatistico` |
| 03 | `acesso_dados`, `aprendizado_maquina` |
| 04 | `aprendizado_maquina` (persistência) |
| 05 | `diagnostico_estatistico` (apoio) e SHAP externo |
| 06 | `aprendizado_maquina` (persistência) e `acesso_dados` |

## 🧪 Como executar

A lógica das fases é acionada pelos executores:

```bash
# Fase 04 — calibração e serialização do campeão
uv run python -m scripts.executores_arquivo.fase_04_ajustar_campeao

# Fase 05 — pilares 1 a 4
uv run python -m scripts.executores_arquivo.fase_05_pilar_01_top3
uv run python -m scripts.executores_arquivo.fase_05_pilar_02_custo
uv run python -m scripts.executores_arquivo.fase_05_pilar_03_shap
uv run python -m scripts.executores_arquivo.fase_05_pilar_04_governanca

# Fase 06 — pilares 1 a 4
uv run python -m scripts.executores_arquivo.fase_06_pilar_01_persistencia
uv run python -m scripts.executores_arquivo.fase_06_pilar_02_seguranca
uv run python -m scripts.executores_arquivo.fase_06_pilar_03_contratos
uv run python -m scripts.executores_arquivo.fase_06_pilar_04_motor_api
```

O mapa completo está em [scripts/README.md](../../scripts/README.md).

## 🧭 Trilha BI × Trilha ML

| Dimensão | BI (`dados/processados/bi/`) | ML (`dados/processados/ml/`) |
| :--- | :--- | :--- |
| **Público** | Diretoria, gestores e analistas. | Algoritmos e API. |
| **Formato** | Textos, datas e R$. | Números codificados e padronizados. |
| **Consumo** | Power BI, Metabase, Excel. | Scikit-Learn, XGBoost, SHAP. |
| **Pergunta** | O que aconteceu? | O que vai acontecer? |

## 📌 Governança

1. Cada fase deve permanecer coesa: uma responsabilidade por arquivo.
2. Reutilize o núcleo; não duplique leitura, estatística ou persistência.
3. Nenhuma fase importa outra fase “de cima”; o fluxo é sempre para frente.
4. Toda saída relevante deve ser rastreável por caminho e metadados.

## 📚 Glossário técnico

| Termo | Tradução | Papel no pipeline |
| :--- | :--- | :--- |
| **Pipeline** | Esteira/encadeamento | Fluxo em que a saída de uma etapa alimenta a próxima. |
| **Data Ingestion** | Ingestão | Leitura e validação mecânica dos dados brutos. |
| **Data Leakage** | Vazamento de dados | Uso indevido de informação do teste/futuro no treino. |
| **Feature Engineering** | Engenharia de atributos | Criação e transformação de variáveis explicativas. |
| **Baseline** | Linha de base | Modelo simples de referência. |
| **Holdout** | Teste retido | Partição separada e usada só na avaliação final. |
| **Batch Scoring** | Escoragem em lote | Predição em massa para muitos registros. |
| **XAI** | IA explicável | Técnicas (ex.: SHAP) que explicam a decisão do modelo. |
| **ABT** | Tabela Analítica | Matriz final com features e target, uma linha por cliente. |
| **Dossiê** | Relatório formal | Documento de homologação com métricas e evidências. |

## 🔗 Ligações

- Código de infraestrutura: [nucleo](../nucleo/README.md).
- Executores das fases: [scripts](../../scripts/README.md).
- Dados de entrada e saída: [dados](../../dados/README.md).
- Voltar para [src](../README.md).
