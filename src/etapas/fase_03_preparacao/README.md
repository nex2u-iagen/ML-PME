# 🧹 `src/etapas/fase_03_preparacao/` — Preparação e bifurcação BI/ML

> **Navegação:** [README raiz](../../../README.md) · [src](../../README.md) · [etapas](../README.md) · **Anterior:** [fase_02](../fase_02_exploracao/README.md) · **Próxima:** [fase_04](../fase_04_modelagem/README.md)

## 🎯 Objetivo

Transformar dados brutos em dois produtos distintos:

1. **Trilha BI:** Data Marts limpos, legíveis e prontos para dashboards.
2. **Trilha ML:** Tabela Analítica (ABT), partições 70/15/15 e pipeline de
   pré-processamento sem data leakage.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | CSVs da [fase_01](../fase_01_ingestao/README.md), já inspecionados na [fase_02](../fase_02_exploracao/README.md). |
| **Processa** | Limpeza, joins, KPIs de negócio, ABT por cliente, split estratificado e `ColumnTransformer`. |
| **Entrega para** | Dashboards (BI) e [fase_04_modelagem](../fase_04_modelagem/README.md) (ML). |
| **Quem consome** | Power BI/Metabase, `OrquestradorDadosML`, `etapa_04_01_orquestrador_baseline`. |

## 🧩 Arquivos

| Arquivo | Classe | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `etapa_03_01_dados_para_bi.py` | `OrquestradorDadosBI` | `pasta_dados_brutos`, `pasta_saida_bi`. | Instancia os 10 construtores de Data Mart e grava cada CSV. | 10 `.csv` em `dados/processados/bi/`. |
| `etapa_03_02_dados_para_ml.py` | `OrquestradorDadosML` | `pasta_bi`, `pasta_saida_ml`, `pasta_modelos`. | Constrói ABT, divide 70/15/15, aplica imputação/escala/one-hot, serializa. | ABT + `treino/validacao/teste_processado.parquet` + `pipeline_preparacao_ml.joblib/json`. |
| `marts_bi/` | 11 construtores | Tabelas brutas específicas. | Regras de negócio e renomeação semântica. | `DataFrame` por departamento. |
| `engenharia_ml/` | `ConstrutorABTCliente` | Data Marts comercial e financeiro. | Agregação no grão de cliente e definição do target. | ABT (`pd.DataFrame`). |
| `__init__.py` | — | — | Marca o pacote. | — |

## 📥 Entradas

| Origem | Arquivo | Usado por |
| :--- | :--- | :--- |
| Fase 01/02 | `dados/brutos/csv/*.csv` | Construtores de Data Marts |
| Fase 03.1 | `dados/processados/bi/data_mart_comercial.csv` | ABT |
| Fase 03.1 | `dados/processados/bi/data_mart_financeiro_titulos.csv` | ABT |

## 📤 Saídas

| Destino | Formato | Consumidor |
| :--- | :--- | :--- |
| `dados/processados/bi/` | `.csv` | Dashboards |
| `dados/processados/ml/abt_cliente_bruta.parquet` | Parquet | Auditoria / retreino |
| `dados/processados/ml/treino_processado.parquet` | Parquet | Fase 04 |
| `dados/processados/ml/validacao_processada.parquet` | Parquet | Fase 04 |
| `dados/processados/ml/teste_processado.parquet` | Parquet | Fase 05 |
| `modelos/pipeline_preparacao_ml.joblib` | Joblib | Reaplicação em inferência |
| `modelos/pipeline_preparacao_ml.json` | JSON | Governança do pipeline |

## 🔀 Bifurcação

```text
dados/brutos/csv/
        │
        ├──► etapa_03_01_dados_para_bi ──► dados/processados/bi/*.csv
        │
        └──► etapa_03_02_dados_para_ml
                    │ ConstrutorABTCliente (marts comercial + financeiro)
                    ▼
             abt_cliente_bruta.parquet
                    │ split 70/15/15 + ColumnTransformer
                    ▼
             treino / validacao / teste .parquet
                    │
                    ▼
             fase_04_modelagem
```

## ▶️ Como executar

```python
from pathlib import Path

from src.etapas.fase_03_preparacao.etapa_03_01_dados_para_bi import OrquestradorDadosBI
from src.etapas.fase_03_preparacao.etapa_03_02_dados_para_ml import OrquestradorDadosML

raiz = Path(".").resolve()

bi = OrquestradorDadosBI(
    pasta_dados_brutos=raiz / "dados/brutos/csv",
    pasta_saida_bi=raiz / "dados/processados/bi",
)
bi.executar_preparacao_bi_completa()

ml = OrquestradorDadosML(
    pasta_bi=raiz / "dados/processados/bi",
    pasta_saida_ml=raiz / "dados/processados/ml",
    pasta_modelos=raiz / "modelos",
)
ml.executar_preparacao_ml_completa()
```

## 📌 Regras

- O split é feito **antes** de qualquer `fit` de imputação/escala.
- `OneHotEncoder(handle_unknown="ignore")` evita erro em categorias novas.
- A ABT tem uma linha por cliente e target binário de inadimplência.
- O pipeline de preparação é persistido para reuso em produção.

## 🔗 Ligações

- Data Marts em detalhe: [marts_bi/README.md](marts_bi/README.md).
- Engenharia da ABT: [engenharia_ml/README.md](engenharia_ml/README.md).
- Núcleo de transformação: [aprendizado_maquina](../../nucleo/aprendizado_maquina/README.md).
- Próxima fase: [fase_04_modelagem](../fase_04_modelagem/README.md).
