# 🧬 `src/etapas/fase_03_preparacao/engenharia_ml/` — Engenharia da ABT

> **Navegação:** [README raiz](../../../../README.md) · [src](../../../README.md) · [etapas](../../README.md) · [fase_03](../README.md)

## 🎯 Objetivo

Construir a **Tabela Analítica de Modelagem (ABT)** no grão de cliente, cruzando os
Data Marts comerciais e financeiros e definindo o alvo supervisionado de
inadimplência.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | `data_mart_comercial.csv` e `data_mart_financeiro_titulos.csv`. |
| **Processa** | Agregações por cliente, features de comportamento e target binário. |
| **Entrega para** | `OrquestradorDadosML`, que faz o split e o pré-processamento. |
| **Quem consome** | Fase 04 (treino/validação) e Fase 05 (teste). |

## 🧩 Arquivos

| Arquivo | Classe / função | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `construtor_abt.py` | `ConstrutorABTCliente` | `pasta_bi: Path`. | Lê os marts, agrega por `id_cliente`, deriva features e target. | `pd.DataFrame` ABT (uma linha por cliente). |
| `montador_pipeline_prep.py` | — | — | Arquivo reservado (atualmente vazio). | — |

## 📥 Entradas

| Arquivo | Colunas-chave | Uso |
| :--- | :--- | :--- |
| `data_mart_comercial.csv` | `id_cliente`, faturamento, pedidos, ticket | Features comerciais |
| `data_mart_financeiro_titulos.csv` | `id_cliente`, status, atraso, valor | Target de inadimplência |

## 📤 Saídas

A ABT é devolvida em memória e persistida pelo orquestrador em:

```text
dados/processados/ml/abt_cliente_bruta.parquet
```

Estrutura conceitual:

| Coluna | Tipo | Papel |
| :--- | :--- | :--- |
| `id_cliente` | int/str | Chave |
| features comerciais | numérico | `X` |
| features financeiras | numérico | `X` |
| `inadimplente` | 0/1 | `y` |

## 🔁 Fluxo

```text
data_mart_comercial.csv ─┐
                         ├──► ConstrutorABTCliente.construir_abt()
data_mart_financeiro.csv ┘             │
                                       ▼
                              ABT (1 linha/cliente)
                                       │
                                       ▼
                         OrquestradorDadosML (split 70/15/15)
```

## 📌 Regras

- A ABT não pode conter o target como feature.
- O grão é sempre **um cliente por linha**.
- Nenhuma estatística do teste pode ser usada para construir features.
- `montador_pipeline_prep.py` está reservado para uma futura extração do
  `ColumnTransformer`; hoje a montagem vive em `etapa_03_02_dados_para_ml.py`.

## 🔗 Ligações

- Data Marts: [marts_bi](../marts_bi/README.md).
- Orquestrador: [fase_03](../README.md).
- Persistência: [aprendizado_maquina](../../../nucleo/aprendizado_maquina/README.md).
