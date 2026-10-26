# 🗃️ `dados/` — Dados brutos e processados

> **Navegação:** [README raiz](../README.md) · **Subpastas:** [brutos](brutos/README.md) · [processados](processados/README.md) · **Consumidores:** [src/etapas/fase_01](../src/etapas/fase_01_ingestao/README.md) · [fase_02](../src/etapas/fase_02_exploracao/README.md) · [fase_03](../src/etapas/fase_03_preparacao/README.md)

## 🎯 Objetivo

Organizar o ciclo de vida do dado em duas camadas: **brutos** (imutáveis) e
**processados** (produtos analíticos e matrizes de ML).

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | Exportações do ERP (CSV) e dumps SQL. |
| **Processa** | Conversão, limpeza, joins, agregações e engenharia de atributos. |
| **Entrega para** | Fases 01–04, dashboards e artefatos de modelo. |
| **Quem consome** | `src/etapas`, scripts e ferramentas de BI. |

## 🧩 Estrutura

| Caminho | README | Papel | Mutabilidade | Conteúdo atual |
| :--- | :--- | :--- | :--- | :--- |
| `brutos/` | [README](brutos/README.md) | Camada de fontes imutáveis. | Somente leitura | 2 subpastas |
| `brutos/sql/` | [README](brutos/sql/README.md) | Dumps SQL do ERP. | Somente leitura | Vazio (`.gitkeep`) |
| `brutos/csv/` | [README](brutos/csv/README.md) | CSVs exportados/fatiados do ERP. | Somente leitura (fonte) | 9 arquivos `erp_*.csv` |
| `processados/` | [README](processados/README.md) | Camada de produtos analíticos. | Gerado | 2 subpastas |
| `processados/bi/` | [README](processados/bi/README.md) | Data Marts prontos para dashboards. | Gerado | 10 arquivos `data_mart_*.csv` |
| `processados/ml/` | [README](processados/ml/README.md) | ABT e partições de ML. | Gerado | 4 arquivos `.parquet` |

> Existem também as pastas `brutos/CSV/`, `brutos/SQL/` e `processados/ML/`, vazias.
> Elas são resquícios de padronização e podem ser removidas para evitar confusão,
> pois o código usa os caminhos em minúsculas.

## 📥 Entradas

| Arquivo bruto | Entidade | Consumidor |
| :--- | :--- | :--- |
| `erp_clientes.csv` | Cadastro de clientes | Comercial / ABT |
| `erp_pedidos_vendas.csv` | Pedidos de venda | Comercial, Financeiro, Contábil |
| `erp_pedidos_compras.csv` | Compras | Compras |
| `erp_saldos_estoque.csv` | Estoque | Estoque |
| `erp_notas_fiscais.csv` | Notas fiscais | Fiscal |
| `erp_ordens_producao.csv` | Produção | Produção |
| `erp_expedicao_logistica.csv` | Expedição | Logística |
| `erp_sac_chamados.csv` | SAC | Pós-venda |
| `erp_funcionarios_folha.csv` | Folha | RH |

## 📤 Saídas

| Caminho | Formato | Produtor | Consumidor |
| :--- | :--- | :--- | :--- |
| `brutos/csv/*.csv` | CSV | Fase 01 (conversão SQL) | Fase 02/03 |
| `processados/bi/*.csv` | CSV | Fase 03.1 | Power BI / Metabase |
| `processados/ml/abt_cliente_bruta.parquet` | Parquet | Fase 03.2 | Auditoria |
| `processados/ml/treino_processado.parquet` | Parquet | Fase 03.2 | Fase 04 |
| `processados/ml/validacao_processada.parquet` | Parquet | Fase 03.2 | Fase 04 |
| `processados/ml/teste_processado.parquet` | Parquet | Fase 03.2 | Fase 05 |

## 🔁 Fluxo

```text
ERP ──► brutos/sql ──► fase_01 ──► brutos/csv
                                      │
                                      ▼
                                   fase_02 (EDA)
                                      │
                                      ▼
                                   fase_03
                              ┌───────┴────────┐
                              ▼                ▼
                       processados/bi    processados/ml
                       (dashboards)      (treino/teste)
```

## 📌 Regras

- `dados/brutos/` é **somente leitura**. Nenhum script deve alterar a fonte.
- Dados sensíveis não podem ser versionados; `.gitignore` deve bloquear.
- Parquet é o formato oficial da trilha ML; CSV é o formato da trilha BI.
- Todo arquivo processado deve poder ser regenerado a partir dos brutos.
- Não grave credenciais, tokens ou dados pessoais identificáveis.

## 🔗 Ligações

- Fontes imutáveis: [brutos/README.md](brutos/README.md).
- CSV de origem: [brutos/csv/README.md](brutos/csv/README.md).
- Dumps SQL: [brutos/sql/README.md](brutos/sql/README.md).
- Produtos analíticos: [processados/README.md](processados/README.md).
- Data Marts: [processados/bi/README.md](processados/bi/README.md).
- Matrizes de ML: [processados/ml/README.md](processados/ml/README.md).
- Ingestão: [fase_01](../src/etapas/fase_01_ingestao/README.md).
- Preparação: [fase_03](../src/etapas/fase_03_preparacao/README.md).
- Núcleo de I/O: [acesso_dados](../src/nucleo/acesso_dados/README.md).
