# 🗄️ `src/nucleo/acesso_dados/` — Entrada e saída de dados

> **Navegação:** [README raiz](../../../README.md) · [src](../../README.md) · [nucleo](../README.md)

## 🎯 Objetivo

Isolar toda a interface física com o sistema operacional e com bancos relacionais:
leitura de CSV, restauração de dumps SQL, exportação particionada e simulação de
tributos. Nenhuma fase deve abrir arquivo diretamente; ela usa este submódulo.

## 🔄 Posição no fluxo

| Pergunta | Resposta |
| :--- | :--- |
| **Recebe de** | `dados/brutos/csv/`, `dados/brutos/sql/` e chamadas das fases 01–03 e 06. |
| **Processa** | Leitura integral ou em lotes, restauração SQLite, consultas SQLAlchemy, exportação CSV e cálculo de CBS/IBS. |
| **Entrega para** | Fase 01 (tabelas e CSVs), Fase 02 (tabelas para EDA), Fase 03 (tabelas para Data Marts/ABT) e Fase 06 (lotes de scoring). |
| **Quem consome** | `etapa_01_extracao`, `BaseDepartamento`, `ConstrutorABTCliente`, `ConstrutorMart*`, `AdaptadorUniversalBI`. |

## 🧩 Arquivos

| Arquivo | Classe principal | Recebe | Processa | Entrega |
| :--- | :--- | :--- | :--- | :--- |
| `leitor_arquivos.py` | `LeitorArquivosTabulares` | Caminho de CSV (e delimitador). | Lê tudo em memória ou em lotes de 50.000 linhas. | `pd.DataFrame` ou gerador de lotes. |
| `conector_banco_relacional.py` | `ConectorBancoRelacional` | Caminho de dump `.sql` e caminho do `.db`. | Executa DDL/DML, cria SQLite, consulta e exporta em chunks. | `Engine` SQLAlchemy, `pd.DataFrame`, `.csv`. |
| `calculadora_reforma_tributaria.py` | `CalculadoraReformaTributaria` | Valor da operação ou `DataFrame` fiscal. | Calcula CBS/IBS e compara regime legado vs. IVA Dual. | `dict` financeiro ou `DataFrame` enriquecido. |

## 📥 Entradas

| Origem | Formato | Exemplo |
| :--- | :--- | :--- |
| `dados/brutos/csv/` | CSV delimitado por vírgula. | `erp_pedidos_vendas.csv` |
| `dados/brutos/sql/` | Dump SQL com DDL/DML. | `erp_backup.sql` |
| Fases | `Path`, `DataFrame`, valor monetário. | Tabela de notas fiscais. |

## 📤 Saídas

| Destino | Formato | Consumidor |
| :--- | :--- | :--- |
| Memória | `pd.DataFrame` | Fases 02 e 03 |
| `dados/brutos/csv/` | `.csv` gerado a partir do SQL | Fase 02 |
| Memória | `Engine` SQLAlchemy | Consultas e exportações |
| `dados/processados/bi/` | Colunas CBS/IBS | Data Mart fiscal |
| Memória | `dict` / `DataFrame` | Fase 03 e relatórios |

## 🔁 Fluxo interno

```text
dados/brutos/sql/*.sql
        │  reconstruir_banco_sqlite()
        ▼
   SQLite local (.db)
        │  exportar_tabela_para_csv()
        ▼
dados/brutos/csv/*.csv
        │  carregar_tabela() / carregar_em_lotes()
        ▼
   pd.DataFrame  ──►  fases 02, 03 e 06
```

## 📌 Regras

- `dados/brutos/` é **somente leitura**; a fase 01 pode gravar CSVs convertidos.
- Bases grandes devem usar `carregar_em_lotes()` para evitar `MemoryError`.
- Nenhuma credencial de banco deve ser embutida no código; use variáveis de ambiente.
- A calculadora tributária é determinística e não depende de serviços externos.

## 🔗 Ligações

- Contrato de leitura: [contratos](../contratos/README.md).
- Consumidor principal: [fase_01_ingestao](../../etapas/fase_01_ingestao/README.md).
- Voltar para [nucleo](../README.md).
