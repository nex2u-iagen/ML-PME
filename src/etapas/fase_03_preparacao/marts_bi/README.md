# 🧮 `src/etapas/fase_03_preparacao/marts_bi/` — Data Marts de BI

> **Navegação:** [README raiz](../../../../README.md) · [src](../../../README.md) · [etapas](../../README.md) · [fase_03](../README.md)

## 🎯 Objetivo

Transformar cada entidade bruta do ERP em uma visão de negócio limpa, renomeada e
agregada, pronta para consumo por Power BI, Metabase ou Excel.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | `dados/brutos/csv/*.csv` (via `LeitorArquivosTabulares`). |
| **Processa** | Joins, conversão de datas, cálculos de margem/prazo/ABC, tradução de colunas. |
| **Entrega para** | `OrquestradorDadosBI`, que grava cada `DataFrame` em `dados/processados/bi/`. |
| **Quem consome** | Dashboards e a ABT da trilha ML. |

## 🧩 Arquivos

| Arquivo | Classe | Fonte(s) bruta(s) | Saída padrão |
| :--- | :--- | :--- | :--- |
| `mart_comercial.py` | `ConstrutorMartComercial` | `erp_pedidos_vendas.csv`, `erp_clientes.csv` | `data_mart_comercial.csv` |
| `mart_estoque.py` | `ConstrutorMartEstoque` | `erp_saldos_estoque.csv` | `data_mart_estoque_materiais.csv` |
| `mart_financeiro.py` | `ConstrutorMartFinanceiro` | `erp_pedidos_vendas.csv` | `data_mart_financeiro_titulos.csv` |
| `mart_compras.py` | `ConstrutorMartCompras` | `erp_pedidos_compras.csv` | `data_mart_compras_suprimentos.csv` |
| `mart_contabil.py` | `ConstrutorMartContabil` | `erp_pedidos_vendas.csv` | `data_mart_contabil_margem.csv` |
| `mart_fiscal.py` | `ConstrutorMartFiscal` | `erp_notas_fiscais.csv` | `data_mart_fiscal_tributos.csv` |
| `mart_producao.py` | `ConstrutorMartProducao` | `erp_ordens_producao.csv` | `data_mart_producao_operacoes.csv` |
| `mart_logistica.py` | `ConstrutorMartLogistica` | `erp_expedicao_logistica.csv` | `data_mart_logistica_expedicao.csv` |
| `mart_pos_venda.py` | `ConstrutorMartPosVenda` | `erp_sac_chamados.csv` | `data_mart_pos_venda_sac.csv` |
| `mart_rh.py` | `ConstrutorMartRH` | `erp_funcionarios_folha.csv` | `data_mart_recursos_humanos_folha.csv` |
| `mart_marketing_clientes.py` | `ConstrutorMartMarketing` | `erp_clientes.csv`, `erp_pedidos_vendas.csv` | Não é exportado pelo orquestrador padrão; disponível para uso opcional. |
| `adaptador_universal_nicho.py` | `AdaptadorUniversalBI` | CSV de ERP de qualquer nicho. | `DataFrame` canônico para os construtores. |
| `__init__.py` | — | — | Marca o pacote. |

## 📥 Entradas

Cada construtor recebe no `__init__` apenas a pasta de dados brutos:

```python
ConstrutorMartComercial(pasta_brutos=Path("dados/brutos/csv"))
```

O método padronizado é:

```python
df = construtor.processar()
```

## 📤 Saídas

| Nível | Formato | Quem grava |
| :--- | :--- | :--- |
| Construtor | `pd.DataFrame` | O próprio construtor |
| Arquivo final | `.csv` | `OrquestradorDadosBI` |

## 🧩 Adaptador universal

`AdaptadorUniversalBI` permite mapear nomes de colunas de ERPs de nichos diferentes
(clínicas, indústria, serviços) para o esquema canônico esperado pelos Data Marts.
Ele é opcional e não é acionado pelo fluxo padrão.

## 📌 Regras

- Um construtor = um domínio de negócio.
- Nenhum construtor grava arquivo; a persistência é responsabilidade do orquestrador.
- Colunas devem ter nomes legíveis em português (R$, datas, status).
- A trilha BI não usa one-hot nem padronização; os valores permanecem reais.

## 🔗 Ligações

- Orquestrador: [fase_03](../README.md).
- ABT: [engenharia_ml](../engenharia_ml/README.md).
- Núcleo de leitura: [acesso_dados](../../../nucleo/acesso_dados/README.md).
